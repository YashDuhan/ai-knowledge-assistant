"""PDF text extraction."""

from pathlib import Path

from PyPDF2 import PdfReader


def load_pdf(file_path: str | Path) -> list[dict]:
    """
    Extract text from a PDF file.
    Returns list of dicts: [{"text": str, "page": int, "source": str}]
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    reader = PdfReader(str(path))
    pages = []

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text and text.strip():
            pages.append({
                "text": text.strip(),
                "page": i,
                "source": path.name,
            })

    return pages
