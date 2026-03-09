# Getting Started

 answers are returned as an SSE stream from `POST /ask/stream`.

The folders `data/` and `vector_store/` are **gitignored** (runtime-only), but are kept present via `.gitkeep` and are also created automatically by the backend on startup.

## Quick start (Docker Compose)

### 1) Start Ollama on your host

- Install and run Ollama.
- Ensure the model exists:

```bash
ollama pull phi3:mini
```

### 2) Run the stack

From the repo root:

```bash
docker compose up --build
```

- **Frontend**: `http://localhost:3000`


## Local dev (no Docker)

### Backend

```bash
pip install -r requirements.txt
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Troubleshooting

- **Backend says Ollama is not responding**: start Ollama on the host and verify `http://localhost:11434`.
