"""Sentence transformer embeddings."""

from typing import Optional

from sentence_transformers import SentenceTransformer


_encoder: Optional[SentenceTransformer] = None


def get_embedder(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> SentenceTransformer:
    """Lazy-load the embedding model."""
    global _encoder
    if _encoder is None:
        _encoder = SentenceTransformer(model_name)
    return _encoder


def embed(texts: list[str], model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> list[list[float]]:
    """Embed a list of texts. Returns list of vectors."""
    model = get_embedder(model_name)
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()


def embed_single(text: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> list[float]:
    """Embed a single string."""
    return embed([text], model_name)[0]
