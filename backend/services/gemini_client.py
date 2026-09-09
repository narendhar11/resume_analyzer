"""Gemini API wrapper. All prompt construction and SDK calls live here."""

import os

import google.generativeai as genai

DEFAULT_MODEL = "gemini-3.6-flash"

# Hardcoded smoke-test prompt. Deliberately trivial: it proves the API key,
# network path and SDK wiring work without exercising any feature logic.
PING_PROMPT = (
    "Reply with exactly one short sentence confirming you are reachable, "
    "and include the words 'Resume Analyzer'."
)


class GeminiError(RuntimeError):
    """Raised when Gemini cannot be reached or returns nothing usable."""


def get_model_name() -> str:
    return os.getenv("GEMINI_MODEL") or DEFAULT_MODEL


def _configure() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiError(
            "GEMINI_API_KEY is not set. Copy backend/.env.example to "
            "backend/.env and add a valid key."
        )
    genai.configure(api_key=api_key)


def ping(prompt: str = PING_PROMPT) -> str:
    """Send `prompt` to Gemini and return the reply text."""
    _configure()
    model_name = get_model_name()

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        reply = (response.text or "").strip()
    except Exception as exc:  # SDK raises a wide range of transport errors
        raise GeminiError(f"Gemini call failed ({model_name}): {exc}") from exc

    if not reply:
        raise GeminiError(f"Gemini returned an empty response ({model_name}).")
    return reply
