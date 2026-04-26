import json
from app.db.supabase import supabase
from app.services.order_extractor import extract_order


def get_or_create_order(customer_id: str, conversation_id: str):
    res = (
        supabase.table("orders")
        .select("*")
        .eq("conversation_id", conversation_id)
        .eq("status", "draft")
        .execute()
    )

    if res.data:
        return res.data[0]

    order = (
        supabase.table("orders")
        .insert({
            "customer_id": customer_id,
            "conversation_id": conversation_id,
            "status": "draft",
            "items": []
        })
        .execute()
    )

    return order.data[0]


def update_order(order, extracted_json: str):
    data = json.loads(extracted_json)
    items = order.get("items") or []

    for new_item in data.get("items", []):
        items.append(new_item)

    updated = (
        supabase.table("orders")
        .update({"items": items})
        .eq("id", order["id"])
        .execute()
    )

    return updated.data[0]


def maybe_extract_order(customer_id, conversation_id, user_msg, assistant_msg):
    order = get_or_create_order(customer_id, conversation_id)

    try:
        extracted = extract_order(user_msg)
        update_order(order, extracted)
    except Exception as e:
        print("Order extraction failed:", e)