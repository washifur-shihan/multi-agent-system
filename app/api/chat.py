import uuid
from fastapi import APIRouter, Request, HTTPException, Query
from app.models.schemas import ChatRequest, ResetChatRequest
from app.services.memory import (
    get_or_create_customer_and_conversation,
    save_message,
    update_conversation_agent,
    reset_conversation,
)
from app.services.retrieval import search_knowledge, get_recent_messages
from app.services.llm_chat import generate_answer
from app.services.agents import get_agent_by_slug
from app.services.router import route_to_agent

router = APIRouter()


def get_safe_customer_key(body: dict, request: Request) -> str:
    raw_customer_key = body.get("customer_key")
    if raw_customer_key and raw_customer_key != "{{call.id}}":
        return str(raw_customer_key)

    return (
        (body.get("call") or {}).get("id")
        or body.get("callId")
        or request.headers.get("x-vapi-call-id")
        or request.headers.get("x-call-id")
        or f"aurora-{uuid.uuid4()}"
    )


@router.post("/")
async def chat(request: Request):
    try:
        raw_body = await request.json()
    except Exception:
        raw_body = {}

    body = raw_body.get("main", raw_body) if isinstance(raw_body, dict) else {}

    requested_slug = (body.get("agent_slug") or "master").strip().lower()
    auto_route = body.get("auto_route", True)

    req = ChatRequest(
        customer_key=get_safe_customer_key(body, request),
        message=(body.get("message") or "").strip(),
        channel=body.get("channel") or "chat",
        agent_slug=requested_slug,
        auto_route=bool(auto_route),
    )

    if not req.message:
        fallback_agent = get_agent_by_slug(req.agent_slug) or get_agent_by_slug("master")
        return {
            "reply": "I didn't catch that. Could you please share your question again?",
            "agent": fallback_agent["slug"],
            "agent_name": fallback_agent["name"],
            "agent_icon": fallback_agent.get("icon", "✨"),
            "route_reason": "Awaiting input",
            "transferred": False,
            "knowledge_used": 0,
            "conversation_id": None,
        }

    customer, conversation = get_or_create_customer_and_conversation(
        customer_key=req.customer_key,
        channel=req.channel,
    )

    last_agent_slug = conversation.get("agent_slug")
    routed_agent, route_reason = route_to_agent(req.message)
    transferred_from_master = False

    # Routing resolution:
    # 1. If the user is on the Master agent page, use router or sticky specialist
    if req.agent_slug == "master":
        current_specialist = (
            last_agent_slug if last_agent_slug and last_agent_slug != "master" else None
        )
        if current_specialist:
            if routed_agent and routed_agent["slug"] != current_specialist:
                old_agent = get_agent_by_slug(current_specialist)
                agent = routed_agent
                transferred_from_master = True
                old_name = old_agent["name"] if old_agent else current_specialist.title()
                route_reason = f"Switched from {old_name} → {agent['name']} ({route_reason})"
            else:
                agent = get_agent_by_slug(current_specialist)
                route_reason = f"Continuing session with {agent['name']}"
        else:
            if routed_agent is not None:
                agent = routed_agent
                transferred_from_master = True
            else:
                agent = get_agent_by_slug("master")
    else:
        # 2. User opened a dedicated specialist page (e.g. /a/finance)
        page_agent = get_agent_by_slug(req.agent_slug)
        if not page_agent:
            raise HTTPException(status_code=404, detail=f"Agent '{req.agent_slug}' not found")

        if req.auto_route and routed_agent and routed_agent["slug"] != page_agent["slug"]:
            agent = routed_agent
            transferred_from_master = True
            route_reason = (
                f"Auto-routed from {page_agent['name']} → {agent['name']} ({route_reason})"
            )
        else:
            agent = page_agent
            route_reason = f"Direct specialist session with {agent['name']}"

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    conversation["agent_slug"] = agent["slug"]
    update_conversation_agent(conversation["id"], agent["id"], agent["slug"])

    save_message(conversation["id"], "user", req.message, agent_slug=agent["slug"])

    knowledge_hits = []
    if agent["slug"] != "master":
        knowledge_hits = search_knowledge(agent["id"], req.message)

    recent = get_recent_messages(conversation["id"])

    department_answer = generate_answer(
        user_message=req.message,
        recent_messages=recent,
        knowledge_context=knowledge_hits,
        customer=customer,
        conversation=conversation,
        agent=agent,
        route_reason=route_reason,
        transferred_from_master=transferred_from_master,
    )

    if transferred_from_master and req.channel == "voice":
        final_answer = (
            f"Connecting you to {agent['name']}.\n\n{department_answer}"
        )
    else:
        final_answer = department_answer

    save_message(conversation["id"], "assistant", final_answer, agent_slug=agent["slug"])

    return {
        "reply": final_answer,
        "agent": agent["slug"],
        "agent_name": agent["name"],
        "agent_icon": agent.get("icon", "✨"),
        "route_reason": route_reason,
        "transferred": transferred_from_master,
        "knowledge_used": len(knowledge_hits),
        "conversation_id": conversation["id"],
    }


@router.get("/history")
async def chat_history(
    customer_key: str = Query(default="aurora-user"),
    channel: str = Query(default="chat"),
):
    _, conversation = get_or_create_customer_and_conversation(
        customer_key=customer_key,
        channel=channel,
    )
    messages = get_recent_messages(conversation["id"], limit=20)
    return {
        "conversation_id": conversation["id"],
        "agent_slug": conversation.get("agent_slug"),
        "messages": messages,
    }


@router.post("/reset")
async def reset_chat_session(payload: ResetChatRequest):
    reset_conversation(customer_key=payload.customer_key, channel=payload.channel)
    return {"ok": True, "message": "Conversation reset"}
