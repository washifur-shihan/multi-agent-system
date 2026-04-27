import uuid

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from app.services.memory import (
    get_or_create_customer_and_conversation,
    save_message,
    update_conversation_agent,
)
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


def get_safe_customer_key(body: dict, request: Request) -> str:
    raw_customer_key = body.get("customer_key")

    if raw_customer_key and raw_customer_key != "{{call.id}}":
        return raw_customer_key

    return (
        body.get("call", {}).get("id")
        or body.get("callId")
        or request.headers.get("x-vapi-call-id")
        or request.headers.get("x-call-id")
        or f"voice-{uuid.uuid4()}"
    )


@router.post("/")
async def chat(request: Request):
    raw_body = await request.json()
    body = raw_body.get("main", raw_body)

    print("====== RAW BODY ======")
    print(raw_body)

    req = ChatRequest(
        customer_key=get_safe_customer_key(body, request),
        message=body.get("message") or "",
        channel=body.get("channel") or "voice",
        agent_slug="master",
    )

    print("====== NORMALIZED REQUEST ======")
    print(req)

    if not req.message:
        return {
            "reply": "I didn't catch that. Could you repeat?",
            "agent": "master",
            "conversation_id": None,
        }

    customer, conversation = get_or_create_customer_and_conversation(
        customer_key=req.customer_key,
        channel=req.channel,
    )

    last_agent_slug = conversation.get("agent_slug")
    current_agent_slug = (
        last_agent_slug
        if last_agent_slug and last_agent_slug != "master"
        else None
    )

    transferred_from_master = False

    routed_agent, route_reason = route_to_agent(req.message)

    if current_agent_slug:
        if routed_agent and routed_agent["slug"] != current_agent_slug:
            old_agent = get_agent_by_slug(current_agent_slug)
            agent = routed_agent
            transferred_from_master = True
            route_reason = (
                f"User requested a switch from {old_agent['name']} "
                f"to {agent['name']}. {route_reason}"
            )
        else:
            agent = get_agent_by_slug(current_agent_slug)
            route_reason = "Continuing with previous agent"
    else:
        if routed_agent is None:
            agent = get_agent_by_slug("master")
        else:
            agent = routed_agent
            transferred_from_master = True

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    print("====== SELECTED AGENT ======")
    print(agent["slug"], route_reason)

    conversation["agent_slug"] = agent["slug"]
    update_conversation_agent(conversation["id"], agent["id"])

    save_message(conversation["id"], "user", req.message)

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

    if transferred_from_master:
        final_answer = (
            "I’ll let the Master Agent handle the transfer.\n\n"
            f"This is handled by {agent['name']}. "
            f"Let me direct the call to them.\n\n"
            f"{department_answer}"
        )
    else:
        final_answer = department_answer

    save_message(conversation["id"], "assistant", final_answer)

    return {
        "reply": final_answer,
        "agent": agent["slug"],
        "conversation_id": conversation["id"],
    }