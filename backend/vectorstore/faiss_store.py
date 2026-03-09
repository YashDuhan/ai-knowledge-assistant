"""FAISS vector store for chunks."""

import json
from pathlib import Path
from typing import Optional

import faiss
import numpy as np

from backend.embeddings.embedder import embed


class FAISSStore:
    """FAISS index for semantic search over document chunks."""

    def __init__(self, persist_dir: Optional[Path] = None, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.persist_dir = Path(persist_dir) if persist_dir else Path(__file__).parent.parent.parent / "vector_store"
        self.embedding_model = embedding_model
        self.index: Optional[faiss.IndexFlatL2] = None
        self.chunks: list[dict] = []
        self._load_if_exists()

    def _load_if_exists(self) -> None:
        """Load index and chunks from disk if they exist."""
        index_path = self.persist_dir / "index.faiss"
        chunks_path = self.persist_dir / "chunks.json"
        if index_path.exists() and chunks_path.exists():
            self.index = faiss.read_index(str(index_path))
            self.chunks = json.loads(chunks_path.read_text(encoding="utf-8"))

    def clear(self) -> None:
        """Clear the index and chunks."""
        self.index = None
        self.chunks = []
        for f in (self.persist_dir / "index.faiss", self.persist_dir / "chunks.json"):
            if f.exists():
                f.unlink()

    def add(self, chunks: list[dict]) -> None:
        """Add chunks to the index. Each chunk: {text, source, page}."""
        if not chunks:
            return
        texts = [c["text"] for c in chunks]
        embeddings = embed(texts, self.embedding_model)
        vectors = np.array(embeddings, dtype=np.float32)

        if self.index is None:
            dim = vectors.shape[1]
            self.index = faiss.IndexFlatL2(dim)

        self.index.add(vectors)
        self.chunks.extend(chunks)
        self._persist()

    def search(self, query: str, top_k: int = 5) -> list[tuple[dict, float]]:
        """Return (chunk, distance) pairs for the query."""
        if self.index is None or not self.chunks:
            return []

        q_vec = np.array([embed([query], self.embedding_model)[0]], dtype=np.float32)
        distances, indices = self.index.search(q_vec, min(top_k, len(self.chunks)))

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0:
                results.append((self.chunks[idx], float(dist)))
        return results

    def _persist(self) -> None:
        """Save index and chunks to disk."""
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        if self.index is not None:
            faiss.write_index(self.index, str(self.persist_dir / "index.faiss"))
            (self.persist_dir / "chunks.json").write_text(
                json.dumps(self.chunks, ensure_ascii=False, indent=0),
                encoding="utf-8",
            )
