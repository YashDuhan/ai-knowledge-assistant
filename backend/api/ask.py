"""Ask endpoint: streaming-only (SSE)."""

import json
from typing import AsyncIterator

import httpx
from fastapi import APIRouter
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from backend.config import TOP_K, VECTOR_STORE_DIR
from backend.llm.local_llm import generate_stream_async
from backend.rag.pipeline import _format_context
from backend.retrieval.retriever import retrieve

router = APIRouter(prefix="/ask", tags=["ask"])

OLLAMA_ERR_MSG = "Ollama is not responding. Ensure Ollama is running"


class AskRequest(BaseModel):
    question: str


async def _stream_tokens(question: str) -> AsyncIterator[dict]:
    """Generate SSE events for token streaming."""
    yield {"event": "status", "data": json.dumps({"status": "searching"})}

    chunks = retrieve(question, top_k=TOP_K, persist_dir=VECTOR_STORE_DIR)
    if not chunks:
        yield {"event": "token", "data": json.dumps({"t": "No relevant context found. Please upload documents first."})}
        yield {"event": "sources", "data": json.dumps([])}
        return

    yield {"event": "status", "data": json.dumps({"status": "generating"})}

    from backend.rag.pipeline import RAG_PROMPT_TEMPLATE

    context = _format_context(chunks)
    prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=question)
    sources = list(dict.fromkeys(f"{c['source']} (page {c['page']})" for c in chunks))

    try:
        async for token in generate_stream_async(prompt):
            yield {"event": "token", "data": json.dumps({"t": token})}
    except (httpx.ReadTimeout, httpx.ConnectError):
        yield {"event": "token", "data": json.dumps({"t": OLLAMA_ERR_MSG})}
    yield {"event": "sources", "data": json.dumps(sources)}


@router.post("/stream")
async def ask_stream(req: AskRequest):
    """Stream answer tokens via SSE."""
    async def event_generator():
        async for evt in _stream_tokens(req.question):
            yield evt

    return EventSourceResponse(event_generator())
