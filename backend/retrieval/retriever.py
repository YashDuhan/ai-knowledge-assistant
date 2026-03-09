"""Retrieve relevant chunks for a query."""

from pathlib import Path
from typing import Optional

from backend.config import TOP_K
from backend.vectorstore.faiss_store import FAISSStore


def get_store(persist_dir: Optional[Path] = None) -> FAISSStore:
    """Get or create the FAISS store."""
    return FAISSStore(persist_dir=persist_dir)


def retrieve(query: str, top_k: int = TOP_K, persist_dir: Optional[Path] = None) -> list[dict]:
    """
    Retrieve top_k chunks for the query.
    Returns list of dicts: [{"text": str, "source": str, "page": int}]
    """
    store = get_store(persist_dir)
    results = store.search(query, top_k=top_k)
    return [chunk for chunk, _ in results]
