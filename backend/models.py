"""Pydantic request/response schemas shared across routes."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness check for the API itself — does not touch Gemini."""

    status: str = Field(..., description="Always 'ok' when the API is up")


class PingGeminiResponse(BaseModel):
    """Result of the frontend -> backend -> Gemini smoke test."""

    model: str = Field(..., description="Gemini model that produced the reply")
    prompt: str = Field(..., description="Hardcoded prompt sent to Gemini")
    reply: str = Field(..., description="Text returned by Gemini")
