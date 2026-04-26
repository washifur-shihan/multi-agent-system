from app.db.supabase import supabase


def get_or_create_customer_and_conversation(
    customer_key: str,
    channel: str,
    agent_id: str | None = None
):
    res = (
        supabase.table("customers")
        .select("*")
        .eq("customer_key", customer_key)
        .execute()
    )

    if res.data:
        customer = res.data[0]
    else:
        customer = (
            supabase.table("customers")
            .insert({"customer_key": customer_key})
            .execute()
            .data[0]
        )

    conversation = (
        supabase.table("conversations")
        .insert({
            "customer_id": customer["id"],
            "agent_id": agent_id,
            "channel": channel
        })
        .execute()
        .data[0]
    )

    return customer, conversation


def save_message(conversation_id: str, role: str, content: str):
    supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "role": role,
        "content": content
    }).execute()