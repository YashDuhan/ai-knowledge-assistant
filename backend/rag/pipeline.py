"""RAG pipeline: retrieve → prompt → generate."""

from pathlib import Path
from typing import Iterator, Optional

from backend.config import TOP_K
from backend.llm.local_llm import generate_stream
from backend.retrieval.retriever import retrieve

RAG_PROMPT_TEMPLATE = """Answer the question based only on the following context. If the answer is not in the context, say so.

Context:
{context}

Question: {question}

Answer:"""


def _format_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        parts.append(f"[{c['source']} p.{c['page']}] {c['text']}")
    return "\n\n".join(parts)


def rag_answer_stream(
    question: str,
    top_k: int = TOP_K,
    persist_dir: Optional[Path] = None,
) -> tuple[Iterator[str], list[str]]:
    """
    Retrieve, build prompt, stream generate. Returns (token iterator, sources).
    """
    chunks = retrieve(question, top_k=top_k, persist_dir=persist_dir)
    if not chunks:
        # Return empty iterator and empty sources
        def empty_stream():
            yield "No relevant context found. Please upload documents first."

        return empty_stream(), []

    context = _format_context(chunks)
    prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=question)
    token_stream = generate_stream(prompt)
    sources = list(dict.fromkeys(f"{c['source']} (page {c['page']})" for c in chunks))

    return token_stream, sources
