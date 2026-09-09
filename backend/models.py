"""Pydantic request/response schemas shared across routes."""

from typing import Literal

from pydantic import BaseModel, Field

FitLabel = Literal["Strong fit", "Moderate fit", "Weak fit"]


class HealthResponse(BaseModel):
    """Liveness check for the API itself — does not touch Gemini."""

    status: str = Field(..., description="Always 'ok' when the API is up")


class PingGeminiResponse(BaseModel):
    """Result of the frontend -> backend -> Gemini smoke test."""

    model: str = Field(..., description="Gemini model that produced the reply")
    prompt: str = Field(..., description="Hardcoded prompt sent to Gemini")
    reply: str = Field(..., description="Text returned by Gemini")


class AnalysisReport(BaseModel):
    """Structured resume-vs-JD analysis.

    Doubles as the `response_schema` handed to Gemini, so the field
    descriptions below are what the model is told to produce.
    """

    fit_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall fitment of the resume for the job, 0-100.",
    )
    fit_label: FitLabel = Field(
        ...,
        description=(
            "Tier matching fit_score: 'Strong fit' for 75-100, "
            "'Moderate fit' for 45-74, 'Weak fit' for 0-44."
        ),
    )
    summary: str = Field(
        ...,
        description="Two or three sentences on how well the candidate matches.",
    )
    strengths: list[str] = Field(
        ...,
        description=(
            "Concrete strengths from the resume that match the job "
            "description, each one short phrase or sentence."
        ),
    )
    missing_keywords: list[str] = Field(
        ...,
        description=(
            "Specific terms, tools or technologies named in the job "
            "description that are absent from the resume."
        ),
    )
    skill_gaps: list[str] = Field(
        ...,
        description=(
            "Broader capabilities or experience the job needs that the "
            "resume does not evidence."
        ),
    )
    recommendations: list[str] = Field(
        ...,
        description=(
            "Actionable edits to improve this resume for this job — "
            "phrasing, emphasis, formatting or content to add."
        ),
    )


class AnalyzeResponse(BaseModel):
    """Envelope returned by POST /api/analyze."""

    model: str = Field(..., description="Gemini model that produced the report")
    resume_filename: str = Field(..., description="Name of the uploaded resume")
    jd_source: Literal["pasted text", "file"] = Field(
        ..., description="Where the job description text came from"
    )
    report: AnalysisReport = Field(..., description="The analysis itself")
