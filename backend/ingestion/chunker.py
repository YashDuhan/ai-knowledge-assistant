"""Text chunking with overlap."""

from typing import Generator

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
try:
    from backend.config import CHUNK_OVERLAP, CHUNK_SIZE
except ImportError:
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 150


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> Generator[str, None, None]:
    """Split text into overlapping chunks."""
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            yield chunk.strip()
        start = end - chunk_overlap


def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Chunk a list of page dicts (from load_pdf/load_txt).
    Returns: [{"text": str, "source": str, "page": int}]
    """
    chunks: list[dict] = []

    for page in pages:
        for chunk_text_str in chunk_text(page["text"]):
            chunks.append({
                "text": chunk_text_str,
                "source": page["source"],
                "page": page["page"],
            })

    return chunks
