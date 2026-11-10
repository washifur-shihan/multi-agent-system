import math
from app.db.supabase import supabase
from app.services.llm import embed_query
from app.services.memory import get_local_messages

# In-memory knowledge store fallback when Supabase is not configured
_LOCAL_DOCUMENTS: list[dict] = []
_LOCAL_CHUNKS: list[dict] = []


def register_local_document(doc: dict):
    _LOCAL_DOCUMENTS.append(doc)


def register_local_chunks(chunks: list[dict]):
    _LOCAL_CHUNKS.extend(chunks)


def list_knowledge_documents(agent_id: str) -> list[dict]:
    if supabase is not None:
        try:
            res = (
                supabase.table("knowledge_documents")
                .select("*")
                .eq("agent_id", agent_id)
                .order("created_at", desc=True)
                .execute()
            )
            if res.data is not None:
                return res.data
        except Exception as exc:
            print("⚠️ Supabase list_knowledge_documents fallback:", str(exc))

    return [d for d in reversed(_LOCAL_DOCUMENTS) if d.get("agent_id") == agent_id]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
    norm_b = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (norm_a * norm_b)


def search_knowledge(agent_id: str, query: str, match_count: int = 5) -> list[dict]:
    if not query or not query.strip():
        return []

    query_emb = embed_query(query)

    if supabase is not None:
        try:
            result = supabase.rpc(
                "match_knowledge_chunks",
                {
                    "query_embedding": query_emb,
                    "agent_uuid": agent_id,
                    "match_count": match_count,
                },
            ).execute()
            if result.data:
                return result.data
        except Exception as exc:
            print("⚠️ Supabase vector search fallback:", str(exc))

    # Local fallback vector + keyword search
    candidates = [c for c in _LOCAL_CHUNKS if c.get("agent_id") == agent_id]
    if not candidates:
        return []

    scored = []
    q_words = set(query.lower().split())
    for chunk in candidates:
        sim = _cosine_similarity(query_emb, chunk.get("embedding", []))
        content_lower = (chunk.get("content") or "").lower()
        lexical_overlap = sum(1 for w in q_words if len(w) > 2 and w in content_lower) * 0.08
        scored.append(
            {
                "id": chunk["id"],
                "document_id": chunk["document_id"],
                "content": chunk["content"],
                "similarity": round(min(0.99, max(0.0, sim + lexical_overlap)), 4),
            }
        )

    scored.sort(key=lambda r: r["similarity"], reverse=True)
    return scored[:match_count]


def get_recent_messages(conversation_id: str, limit: int = 6) -> list[dict]:
    if supabase is not None:
        try:
            result = (
                supabase.table("messages")
                .select("*")
                .eq("conversation_id", conversation_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            if result.data:
                return list(reversed(result.data))
        except Exception as exc:
            print("⚠️ Recent messages fetch fallback:", str(exc))

    return get_local_messages(conversation_id, limit=limit)
