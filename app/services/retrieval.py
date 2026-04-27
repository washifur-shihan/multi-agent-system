from openai import OpenAI
from app.config import settings
from app.db.supabase import supabase

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def search_knowledge(agent_id: str, query: str, match_count: int = 5):
    try:
        embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        ).data[0].embedding

        result = supabase.rpc("match_knowledge_chunks", {
            "query_embedding": embedding,
            "agent_uuid": agent_id,
            "match_count": match_count
        }).execute()

        return result.data or []

    except Exception as e:
        print("⚠️ Knowledge search failed:", str(e))
        return []


def get_recent_messages(conversation_id: str, limit: int = 6):
    try:
        result = (
            supabase.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return list(reversed(result.data or []))

    except Exception as e:
        print("⚠️ Recent messages fetch failed:", str(e))
        return []