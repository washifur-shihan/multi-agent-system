from openai import OpenAI
from app.config import settings
from app.services.agents import build_agent_prompt

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def _format_recent_messages(recent_messages: list[dict]) -> str:
    if not recent_messages:
        return "No recent messages."

    return "\n".join(
        f"{m.get('role', 'unknown')}: {m.get('content', '')}"
        for m in recent_messages
    )


def _format_knowledge_context(knowledge_context: list[dict]) -> str:
    if not knowledge_context:
        return "No matching knowledge found."

    return "\n\n".join(
        item.get("content", "")
        for item in knowledge_context
    )


def generate_answer(
    user_message: str,
    recent_messages: list[dict],
    knowledge_context: list[dict],
    customer: dict,
    conversation: dict,
    agent: dict,
    route_reason: str | None = None,
) -> str:
    system_prompt = build_agent_prompt(agent)

    user_prompt = f"""
Agent selected: {agent.get('name')}
Routing reason: {route_reason or 'N/A'}

Customer:
{customer}

Conversation:
{conversation}

Recent messages:
{_format_recent_messages(recent_messages)}

Knowledge context:
{_format_knowledge_context(knowledge_context)}

User message:
{user_message}
""".strip()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content or ""