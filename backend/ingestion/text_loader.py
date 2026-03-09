"""Plain text file extraction."""

from pathlib import Path


def load_txt(file_path: str | Path) -> list[dict]:
    """
    Extract text from a .txt file.
    Returns list of dicts: [{"text": str, "page": int, "source": str}]
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return []

    return [{
        "text": text,
        "page": 1,
        "source": path.name,
    }]
