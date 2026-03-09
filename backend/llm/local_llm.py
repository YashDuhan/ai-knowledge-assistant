"""Ollama local LLM client."""

import json
from typing import AsyncIterator, Iterator

import httpx

from backend.config import OLLAMA_BASE_URL, OLLAMA_MODEL

# Longer timeout for cold starts / slow hardware
OLLAMA_TIMEOUT = 300.0


def generate_stream(prompt: str, model: str = OLLAMA_MODEL, base_url: str = OLLAMA_BASE_URL) -> Iterator[str]:
    """Stream tokens from Ollama."""
    with httpx.Client(timeout=OLLAMA_TIMEOUT) as client:
        with client.stream(
            "POST",
            f"{base_url.rstrip('/')}/api/generate",
            json={"model": model, "prompt": prompt, "stream": True},
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done"):
                        break
                except json.JSONDecodeError:
                    continue


async def generate_stream_async(
    prompt: str, model: str = OLLAMA_MODEL, base_url: str = OLLAMA_BASE_URL
) -> AsyncIterator[str]:
    """Async stream tokens from Ollama."""
    async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
        async with client.stream(
            "POST",
            f"{base_url.rstrip('/')}/api/generate",
            json={"model": model, "prompt": prompt, "stream": True},
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done"):
                        break
                except json.JSONDecodeError:
                    continue
