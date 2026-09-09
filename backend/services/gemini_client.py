"""Gemini API wrapper. All prompt construction and SDK calls live here."""

import os

from google import genai
from google.genai import types

from models import AnalysisReport

DEFAULT_MODEL = "gemini-3.6-flash"

# Hardcoded smoke-test prompt. Deliberately trivial: it proves the API key,
# network path and SDK wiring work without exercising any feature logic.
PING_PROMPT = (
    "Reply with exactly one short sentence confirming you are reachable, "
    "and include the words 'Resume Analyzer'."
)

# Resumes and job descriptions are short documents; anything past this is
# almost certainly boilerplate, and trimming keeps the request predictable.
MAX_TEXT_CHARS = 20_000

ANALYSIS_INSTRUCTIONS = (
    "You are an experienced technical recruiter. Compare the candidate's "
    "resume against the job description and produce an honest, specific "
    "assessment.\n"
    "Ground every observation in what the resume actually says — never "
    "invent experience. Judge the resume only against this job description, "
    "and keep list items short and scannable. If the resume matches the job "
    "well on some axis, leave the corresponding gap list empty rather than "
    "padding it."
)


class GeminiError(RuntimeError):
    """Raised when Gemini cannot be reached or returns nothing usable."""


def get_model_name() -> str:
    return os.getenv("GEMINI_MODEL") or DEFAULT_MODEL


def _client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiError(
            "GEMINI_API_KEY is not set. Copy backend/.env.example to "
            "backend/.env and add a valid key."
        )
    return genai.Client(api_key=api_key)


def _generate(
    prompt: str, config: types.GenerateContentConfig | None = None
) -> types.GenerateContentResponse:
    """Call Gemini once, translating every failure into `GeminiError`."""
    model_name = get_model_name()
    # `client` must stay referenced for the whole call: the SDK's httpx
    # client closes itself on garbage collection, so letting the client go
    # out of scope mid-request kills the connection under it.
    client = _client()
    try:
        return client.models.generate_content(
            model=model_name, contents=prompt, config=config
        )
    except Exception as exc:
        # Covers SDK-level APIError plus the transport/network failures that
        # surface from underneath it.
        raise GeminiError(f"Gemini call failed ({model_name}): {exc}") from exc


def ping(prompt: str = PING_PROMPT) -> str:
    """Send `prompt` to Gemini and return the reply text."""
    reply = (_generate(prompt).text or "").strip()
    if not reply:
        raise GeminiError(
            f"Gemini returned an empty response ({get_model_name()})."
        )
    return reply


def _build_analysis_prompt(resume_text: str, jd_text: str) -> str:
    return (
        f"{ANALYSIS_INSTRUCTIONS}\n\n"
        "--- JOB DESCRIPTION ---\n"
        f"{jd_text[:MAX_TEXT_CHARS]}\n\n"
        "--- RESUME ---\n"
        f"{resume_text[:MAX_TEXT_CHARS]}"
    )


def analyze(resume_text: str, jd_text: str) -> AnalysisReport:
    """Score `resume_text` against `jd_text` and return a structured report.

    `AnalysisReport` is handed to Gemini as the response schema, so the SDK
    parses and validates the reply for us.
    """
    response = _generate(
        _build_analysis_prompt(resume_text, jd_text),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AnalysisReport,
        ),
    )

    report = response.parsed
    if not isinstance(report, AnalysisReport):
        # Reached when the reply was blocked, truncated, or failed schema
        # validation — surfaced as a 502 rather than a half-empty report.
        raise GeminiError(
            "Gemini did not return a usable analysis "
            f"({get_model_name()}). Please try again."
        )
    return report
