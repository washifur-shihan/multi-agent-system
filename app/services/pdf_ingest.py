from io import BytesIO
import uuid
from app.db.supabase import supabase
from app.config import settings
from app.services.llm import embed_texts
from app.services.retrieval import register_local_chunks
from app.utils.text import chunk_text

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None  # type: ignore


def extract_pdf_text(pdf_bytes: bytes) -> str:
    if PdfReader is None:
        raise RuntimeError("pypdf is required for PDF extraction (pip install pypdf)")
    reader = PdfReader(BytesIO(pdf_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(p.strip() for p in pages if p.strip())


def ingest_knowledge_pdf(
    agent_id: str,
    document_id: str,
    storage_path: str,
    raw_bytes: bytes | None = None,
) -> int:
    try:
        if raw_bytes is None:
            if supabase is None:
                return 0
            raw_bytes = supabase.storage.from_(settings.SUPABASE_BUCKET).download(storage_path)

        text = extract_pdf_text(raw_bytes)
        chunks = chunk_text(text, chunk_size=750, overlap=120)
        if not chunks:
            print(f"⚠️ No extractable text found in PDF ({storage_path})")
            return 0

        embeddings = embed_texts(chunks)

        rows = []
        local_rows = []
        for chunk, emb in zip(chunks, embeddings):
            row = {
                "agent_id": agent_id,
                "document_id": document_id,
                "content": chunk,
                "embedding": emb,
            }
            rows.append(row)
            local_rows.append({"id": str(uuid.uuid4()), **row})

        register_local_chunks(local_rows)

        if supabase is not None and rows:
            try:
                supabase.table("knowledge_chunks").insert(rows).execute()
            except Exception as db_exc:
                print(f"⚠️ Saved chunks in local memory (Supabase insert skipped: {db_exc})")

        return len(rows)

    except Exception as exc:
        print(f"⚠️ PDF ingestion error for document {document_id}: {exc}")
        return 0
