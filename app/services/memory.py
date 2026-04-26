from app.db.supabase import supabase


def get_or_create_customer_and_conversation(
    customer_key: str,
    channel: str,
    agent_id: str | None = None
):
    # Get or create customer
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

    # Reuse latest active conversation instead of creating new one every time
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

    # Create conversation only if none exists
    conversation = (
        supabase.table("conversations")
        .insert({
            "customer_id": customer["id"],
            "agent_id": agent_id,
            "channel": channel,
            "status": "active"
        })
        .execute()
        .data[0]
    )

    conversation["agent_slug"] = None

    return customer, conversation


def update_conversation_agent(conversation_id: str, agent_id: str):
    try:
        supabase.table("conversations").update({
            "agent_id": agent_id
        }).eq("id", conversation_id).execute()
    except Exception as e:
        print("⚠️ Conversation agent update failed:", str(e))


def save_message(conversation_id: str, role: str, content: str):
    try:
        supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "role": role,
            "content": content
        }).execute()
    except Exception as e:
        print("⚠️ Save message failed:", str(e))