from io import BytesIO
from pypdf import PdfReader
from app.db.supabase import supabase
from app.config import settings
from app.services.llm import embed_texts


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


def ingest_knowledge_pdf(agent_id: str, document_id: str, storage_path: str):
    response = supabase.storage.from_(settings.SUPABASE_BUCKET).download(storage_path)

    pdf = PdfReader(BytesIO(response))
    text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    chunks = chunk_text(text)
    embeddings = embed_texts(chunks)

    rows = []

    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        rows.append({
            "agent_id": agent_id,
            "document_id": document_id,
            "content": chunk,
            "embedding": emb
        })

    if rows:
        supabase.table("knowledge_chunks").insert(rows).execute()