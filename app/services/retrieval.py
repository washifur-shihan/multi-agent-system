from app.db.supabase import supabase
from app.services.llm import embed_query


def search_knowledge(agent_id: str, query: str, match_count: int = 5):
    embedding = embed_query(query)

    result = supabase.rpc("match_knowledge_chunks", {
        "query_embedding": embedding,
        "agent_uuid": agent_id,
        "match_count": match_count
    }).execute()

    return result.data or []


def get_recent_messages(conversation_id: str, limit: int = 12):
    result = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return list(reversed(result.data or []))