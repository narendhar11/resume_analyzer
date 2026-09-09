"""Extract raw text from uploaded resume/JD files."""

import io
from pathlib import Path

import pdfplumber

# Resumes are PDF or Markdown per KAN-5; job descriptions may also arrive as
# plain .txt since they are usually copied straight out of a job posting.
RESUME_EXTENSIONS = (".pdf", ".md")
JD_EXTENSIONS = (".pdf", ".md", ".txt")

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB — generous for a resume or JD.


class FileParseError(ValueError):
    """Raised when an upload is unusable: wrong type, too big, or no text."""


def too_large(filename: str) -> FileParseError:
    """The error for an oversized upload, shared by every size check."""
    limit_mb = MAX_UPLOAD_BYTES // (1024 * 1024)
    return FileParseError(f"'{filename}' is larger than {limit_mb} MB.")


def _extract_pdf_text(data: bytes) -> str:
    try:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
    except Exception as exc:  # encrypted, truncated or not really a PDF
        raise FileParseError(f"Could not read the PDF: {exc}") from exc
    return "\n\n".join(pages)


def _extract_plain_text(data: bytes) -> str:
    # Markdown and .txt are read as plain text; replace undecodable bytes
    # rather than rejecting a file over one stray character.
    return data.decode("utf-8", errors="replace")


def extract_text(
    filename: str, data: bytes, allowed_extensions: tuple[str, ...]
) -> str:
    """Return the text content of an upload.

    Raises `FileParseError` if the extension is not allowed, the file is
    empty or oversized, or no text could be pulled out of it.
    """
    suffix = Path(filename or "").suffix.lower()
    if suffix not in allowed_extensions:
        allowed = ", ".join(allowed_extensions)
        raise FileParseError(
            f"Unsupported file type '{suffix or filename}'. Allowed: {allowed}."
        )

    if not data:
        raise FileParseError(f"'{filename}' is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise too_large(filename)

    text = _extract_pdf_text(data) if suffix == ".pdf" else _extract_plain_text(data)

    text = text.strip()
    if not text:
        raise FileParseError(
            f"No text could be extracted from '{filename}'. "
            "If it is a scanned or image-only PDF, try a text-based file."
        )
    return text
