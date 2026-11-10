import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple
from app.db.supabase import supabase
from app.services.agents import get_agent_by_id

# Local in-memory fallback store when Supabase is not configured or unreachable
_LOCAL_CUSTOMERS: dict[str, dict] = {}
_LOCAL_CONVERSATIONS: dict[str, dict] = {}
_LOCAL_MESSAGES: dict[str, list[dict]] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_or_create_customer_and_conversation(
    customer_key: str,
    channel: str,
    agent_id: Optional[str] = None,
) -> Tuple[dict, dict]:
    if supabase is not None:
        try:
            customer_res = (
                supabase.table("customers")
                .select("*")
                .eq("customer_key", customer_key)
                .execute()
            )

            if customer_res.data:
                customer = customer_res.data[0]
            else:
                customer = (
                    supabase.table("customers")
                    .insert({"customer_key": customer_key})
                    .execute()
                    .data[0]
                )

            conv_res = (
                supabase.table("conversations")
                .select("*, agents(slug)")
                .eq("customer_id", customer["id"])
                .eq("channel", channel)
                .eq("status", "active")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            if conv_res.data:
                conversation = conv_res.data[0]
                if conversation.get("agents"):
                    conversation["agent_slug"] = conversation["agents"]["slug"]
                else:
                    conversation["agent_slug"] = None
                return customer, conversation

            conversation = (
                supabase.table("conversations")
                .insert(
                    {
                        "customer_id": customer["id"],
                        "agent_id": agent_id,
                        "channel": channel,
                        "status": "active",
                    }
                )
                .execute()
                .data[0]
            )
            conversation["agent_slug"] = None
            return customer, conversation

        except Exception as exc:
            print(f"⚠️ Using in-memory session store (Supabase unavailable: {exc})")

    # Local fallback
    if customer_key not in _LOCAL_CUSTOMERS:
        _LOCAL_CUSTOMERS[customer_key] = {
            "id": str(uuid.uuid4()),
            "customer_key": customer_key,
            "created_at": _now_iso(),
        }
    customer = _LOCAL_CUSTOMERS[customer_key]

    conv_key = f"{customer_key}:{channel}"
    conversation = _LOCAL_CONVERSATIONS.get(conv_key)
    if not conversation or conversation.get("status") != "active":
        agent_obj = get_agent_by_id(agent_id) if agent_id else None
        conversation = {
            "id": str(uuid.uuid4()),
            "customer_id": customer["id"],
            "agent_id": agent_id,
            "agent_slug": agent_obj["slug"] if agent_obj else None,
            "channel": channel,
            "status": "active",
            "created_at": _now_iso(),
        }
        _LOCAL_CONVERSATIONS[conv_key] = conversation
        _LOCAL_MESSAGES[conversation["id"]] = []

    return customer, conversation


def update_conversation_agent(conversation_id: str, agent_id: str, agent_slug: Optional[str] = None):
    if supabase is not None:
        try:
            supabase.table("conversations").update({"agent_id": agent_id}).eq(
                "id", conversation_id
            ).execute()
        except Exception as exc:
            print("⚠️ Conversation agent update skipped:", str(exc))

    for conv in _LOCAL_CONVERSATIONS.values():
        if conv["id"] == conversation_id:
            conv["agent_id"] = agent_id
            if agent_slug:
                conv["agent_slug"] = agent_slug


def save_message(conversation_id: str, role: str, content: str, agent_slug: Optional[str] = None):
    if supabase is not None:
        try:
            supabase.table("messages").insert(
                {
                    "conversation_id": conversation_id,
                    "role": role,
                    "content": content,
                }
            ).execute()
        except Exception as exc:
            print("⚠️ Supabase save_message skipped:", str(exc))

    msgs = _LOCAL_MESSAGES.setdefault(conversation_id, [])
    msgs.append(
        {
            "id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "agent_slug": agent_slug,
            "created_at": _now_iso(),
        }
    )


def get_local_messages(conversation_id: str, limit: int = 8) -> list[dict]:
    msgs = _LOCAL_MESSAGES.get(conversation_id, [])
    return msgs[-limit:]


def reset_conversation(customer_key: str, channel: str = "chat") -> bool:
    """Mark active conversations as closed so the user starts a fresh session."""
    if supabase is not None:
        try:
            cust_res = (
                supabase.table("customers")
                .select("id")
                .eq("customer_key", customer_key)
                .execute()
            )
            if cust_res.data:
                cust_id = cust_res.data[0]["id"]
                supabase.table("conversations").update({"status": "closed"}).eq(
                    "customer_id", cust_id
                ).eq("channel", channel).eq("status", "active").execute()
        except Exception as exc:
            print("⚠️ Supabase reset_conversation skipped:", str(exc))

    conv_key = f"{customer_key}:{channel}"
    if conv_key in _LOCAL_CONVERSATIONS:
        conv_id = _LOCAL_CONVERSATIONS[conv_key]["id"]
        _LOCAL_CONVERSATIONS[conv_key]["status"] = "closed"
        _LOCAL_MESSAGES.pop(conv_id, None)
    return True
