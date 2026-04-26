from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.services.memory import get_or_create_customer_and_conversation, save_message
from app.services.retrieval import search_knowledge, get_recent_messages
from app.services.llm_chat import generate_answer
from app.services.agents import get_agent_by_slug
from app.services.router import route_to_agent

router = APIRouter()


class ChatRequest(BaseModel):
    customer_key: str = "voice-user"
    message: str = ""
    channel: str = "chat"
    agent_slug: str = "master"


@router.post("/")
async def chat(request: Request):
    raw_body = await request.json()
    body = raw_body.get("main", raw_body)

    print("====== RAW CHAT BODY ======")
    print(raw_body)

    print("====== NORMALIZED BODY ======")
    print(body)

    req = ChatRequest(
        customer_key=(
            body.get("customer_key")
            or body.get("customerKey")
            or body.get("call", {}).get("customer", {}).get("number")
            or body.get("call", {}).get("id")
            or "voice-user"
        ),
        message=(
            body.get("message")
            or body.get("transcript")
            or body.get("input")
            or body.get("query")
            or body.get("parameters", {}).get("message")
            or body.get("arguments", {}).get("message")
            or body.get("toolCall", {})
                .get("function", {})
                .get("arguments", {})
                .get("message")
            or ""
        ),
        channel=(
            body.get("channel")
            or body.get("metadata", {}).get("channel")
            or "voice"
        ),
        agent_slug=(
            body.get("agent_slug")
            or body.get("agentSlug")
            or body.get("parameters", {}).get("agent_slug")
            or body.get("arguments", {}).get("agent_slug")
            or "master"
        ),
    )

    print("====== NORMALIZED CHAT REQUEST ======")
    print(req)

    if not req.message:
        return {
            "reply": "I did not receive your message. Please try again.",
            "agent": "master",
            "route_reason": "Missing message from request.",
            "conversation_id": None,
        }

    route_reason = None

    if req.agent_slug == "master":
        agent, route_reason = route_to_agent(req.message)
    else:
        agent = get_agent_by_slug(req.agent_slug)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    customer, conversation = get_or_create_customer_and_conversation(
        customer_key=req.customer_key,
        channel=req.channel,
        agent_id=agent["id"],
    )

    save_message(conversation["id"], "user", req.message)

    knowledge_hits = search_knowledge(
        agent_id=agent["id"],
        query=req.message,
        match_count=5,
    )

    recent = get_recent_messages(conversation["id"])

    answer = generate_answer(
        user_message=req.message,
        recent_messages=recent,
        knowledge_context=knowledge_hits,
        customer=customer,
        conversation=conversation,
        agent=agent,
        route_reason=route_reason,
    )

    save_message(conversation["id"], "assistant", answer)

    return {
        "reply": answer,
        "agent": agent["slug"],
        "route_reason": route_reason,
        "conversation_id": conversation["id"],
    }