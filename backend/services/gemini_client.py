"""Gemini API wrapper. All prompt construction and SDK calls live here."""

import os

from google import genai
from google.genai import errors as genai_errors

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


def _client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiError(
            "GEMINI_API_KEY is not set. Copy backend/.env.example to "
            "backend/.env and add a valid key."
        )
    return genai.Client(api_key=api_key)


def ping(prompt: str = PING_PROMPT) -> str:
    """Send `prompt` to Gemini and return the reply text."""
    client = _client()
    model_name = get_model_name()

    try:
        response = client.models.generate_content(
            model=model_name, contents=prompt
        )
        reply = (response.text or "").strip()
    except genai_errors.APIError as exc:
        raise GeminiError(f"Gemini call failed ({model_name}): {exc}") from exc
    except Exception as exc:  # transport/network failures below the SDK
        raise GeminiError(f"Gemini call failed ({model_name}): {exc}") from exc

    if not reply:
        raise GeminiError(f"Gemini returned an empty response ({model_name}).")
    return reply
