"""Stack smoke test route: frontend -> backend -> Gemini."""

from fastapi import APIRouter, HTTPException

from models import HealthResponse, PingGeminiResponse
from services import gemini_client

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ping-gemini", response_model=PingGeminiResponse)
def ping_gemini() -> PingGeminiResponse:
    """Send a hardcoded prompt to Gemini and return the live response."""
    try:
        reply = gemini_client.ping()
    except gemini_client.GeminiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return PingGeminiResponse(
        model=gemini_client.get_model_name(),
        prompt=gemini_client.PING_PROMPT,
        reply=reply,
    )
