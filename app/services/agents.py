from app.db.supabase import supabase
import json


def get_agent_by_id(agent_id: str):
    result = (
        supabase.table("agents")
        .select("*")
        .eq("id", agent_id)
        .single()
        .execute()
    )
    return result.data


def get_agent_by_slug(slug: str):
    result = (
        supabase.table("agents")
        .select("*")
        .eq("slug", slug)
        .single()
        .execute()
    )
    return result.data


def list_active_agents():
    result = (
        supabase.table("agents")
        .select("*")
        .eq("is_active", True)
        .order("created_at")
        .execute()
    )
    return result.data or []


def build_agent_prompt(agent: dict) -> str:
    return f"""
You are the {agent['name']}.

Rules:
- Answer only for your department.
- Use the provided knowledge context when available.
- Do not invent company policies, prices, processes, or facts.
- If another department is better, say which department should handle it.
- Be concise and helpful.

Department instructions:
{agent.get('prompt_instructions') or 'None'}
""".strip()


def build_widget_assistant_config(agent: dict) -> str:
    assistant_config = {
        "name": agent["slug"],
        "model": {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": build_agent_prompt(agent)
                }
            ],
        },
        "voice": {
            "provider": "vapi",
            "voiceId": "Elliot"
        },
        "firstMessage": f"Hello, I am the {agent['name']}. How can I help?"
    }

    return json.dumps(assistant_config)