"""Upload documents and add to index."""

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.config import DATA_DIR, VECTOR_STORE_DIR
from backend.ingestion import load_pdf, load_txt, chunk_pages
from backend.vectorstore.faiss_store import FAISSStore

router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


@router.post("")
async def upload_files(files: list[UploadFile] = File(...)):
    """
    Accept PDF and TXT files, save to data/, chunk, embed, add to FAISS.
    Returns list of processed filenames.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    processed = []

    for uf in files:
        ext = Path(uf.filename or "").suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {uf.filename}. Use .pdf or .txt",
            )
        path = DATA_DIR / (uf.filename or "unnamed")
        content = await uf.read()
        path.write_bytes(content)

        pages = []
        try:
            if ext == ".pdf":
                pages = load_pdf(path)
            else:
                pages = load_txt(path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse {uf.filename}: {e}")

        if not pages:
            continue

        chunks = chunk_pages(pages)
        store = FAISSStore(persist_dir=VECTOR_STORE_DIR)
        store.add(chunks)
        processed.append(uf.filename or "unnamed")

    return {"uploaded": processed}
