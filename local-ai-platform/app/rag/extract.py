"""Text extraction for uploaded files. Plain text formats are read
directly; PDF support uses pypdf via lazy import so the server still runs
if the dependency is missing (upload of a PDF then returns a clear error
instead of crashing at startup).
"""
from __future__ import annotations

from pathlib import Path

TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".csv", ".json", ".log", ".eml", ".html", ".htm"}


class ExtractionError(ValueError):
    pass


def extract_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in TEXT_EXTENSIONS:
        return path.read_text(encoding="utf-8", errors="replace")
    if ext == ".pdf":
        return _extract_pdf(path)
    raise ExtractionError(
        f"Unsupported file type '{ext}'. Supported: {sorted(TEXT_EXTENSIONS | {'.pdf'})}"
    )


def _extract_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception as e:  # ImportError or broken native deps
        raise ExtractionError(f"PDF support unavailable (install pypdf): {e}") from e
    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "") for page in reader.pages]
    text = "\n\n".join(pages).strip()
    if not text:
        raise ExtractionError("No extractable text in PDF (scanned image? OCR is not part of the MVP).")
    return text
