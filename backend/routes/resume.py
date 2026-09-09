"""Resume analysis route: upload a resume + job description, get a report."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from models import AnalyzeResponse
from services import file_parser, gemini_client

router = APIRouter(prefix="/api", tags=["resume"])

CHUNK_BYTES = 64 * 1024


async def _read_within_limit(upload: UploadFile) -> bytes:
    """Buffer an upload, bailing out as soon as it exceeds the size limit.

    Reading in chunks means an oversized file is rejected part-way through
    rather than after the whole thing has been pulled into memory.
    """
    data = bytearray()
    while chunk := await upload.read(CHUNK_BYTES):
        data.extend(chunk)
        if len(data) > file_parser.MAX_UPLOAD_BYTES:
            raise file_parser.too_large(upload.filename or "upload")
    return bytes(data)


async def _read_upload(upload: UploadFile, allowed_extensions: tuple[str, ...]) -> str:
    """Extract text from an upload, as a 400 on anything unusable."""
    try:
        data = await _read_within_limit(upload)
        return file_parser.extract_text(
            upload.filename or "", data, allowed_extensions
        )
    except file_parser.FileParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await upload.close()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    resume: UploadFile = File(..., description="Resume as .pdf or .md"),
    jd_text: str = Form("", description="Job description pasted as plain text"),
    jd_file: UploadFile | None = File(
        None, description="Job description as .pdf, .md or .txt"
    ),
) -> AnalyzeResponse:
    """Analyze a resume against a job description and return the report."""
    resume_text = await _read_upload(resume, file_parser.RESUME_EXTENSIONS)

    # An uploaded job description wins over pasted text when both arrive.
    if jd_file is not None and jd_file.filename:
        jd_source = "file"
        job_description = await _read_upload(jd_file, file_parser.JD_EXTENSIONS)
    elif jd_text.strip():
        jd_source = "pasted text"
        job_description = jd_text.strip()
    else:
        raise HTTPException(
            status_code=400,
            detail="A job description is required — paste the text or upload a file.",
        )

    try:
        report = gemini_client.analyze(resume_text, job_description)
    except gemini_client.GeminiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return AnalyzeResponse(
        model=gemini_client.get_model_name(),
        resume_filename=resume.filename or "resume",
        jd_source=jd_source,
        report=report,
    )
