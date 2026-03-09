# AI Knowledge Assistant

RAG-based system to answer questions over uploaded documents (`.pdf`, `.txt`). Uses a local LLM (Ollama), FAISS for semantic search, and **streams responses via SSE** (streaming-only architecture).

For a step‑by‑step guide (including Docker and local dev), see **[`GETTING_STARTED.md`](GETTING_STARTED.md)**.

## Requirements

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai) running on your host (default model: `phi3:mini`)

## Quick start (overview)

- **Getting started**: follow [`GETTING_STARTED.md`](GETTING_STARTED.md) for detailed instructions.
- **Local dev**: run the backend (FastAPI) and frontend (Next.js) locally.
- **Docker**: run the full stack with `docker compose up --build`.