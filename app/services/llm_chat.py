from typing import Optional
from app.config import settings
from app.services.agents import build_agent_prompt

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore


def _format_recent_messages(recent_messages: list[dict]) -> str:
    if not recent_messages:
        return "No recent messages."
    return "\n".join(
        f"{m['role']}: {(m.get('content') or '')[:350]}"
        for m in recent_messages[-5:]
    )


def _format_knowledge_context(ctx: list[dict]) -> str:
    if not ctx:
        return "No matching knowledge documents uploaded for this query."

    chunks = []
    for idx, x in enumerate(ctx[:4], start=1):
        content = (x.get("content") or "").strip()
        if content:
            chunks.append(f"[Source #{idx}]\n{content[:750]}")

    return "\n\n".join(chunks) if chunks else "No matching knowledge documents uploaded for this query."


def _fallback_aurora_answer(
    user_message: str,
    knowledge_context: list[dict],
    agent: dict,
    route_reason: Optional[str],
    transferred_from_master: bool,
) -> str:
    """Provides a structured offline response when OPENAI_API_KEY is not yet configured."""
    header = (
        f"Hello! I'm **{agent['name']}** ({agent.get('badge', 'Aurora Specialist')})."
    )
    routing_note = (
        f"\n\n*Routing Insight:* {route_reason}."
        if route_reason
        else ""
    )

    if knowledge_context:
        top_chunk = (knowledge_context[0].get("content") or "").strip()[:500]
        kb_section = (
            f"\n\n**Matched Knowledge Base Context:**\n> {top_chunk}"
        )
    else:
        kb_section = (
            f"\n\nI'm ready to assist with your **{agent['name']}** request: "
            f"*\"{user_message}\"*."
        )

    setup_tip = (
        "\n\n---\n"
        "💡 *Tip: Add your `OPENAI_API_KEY` to `.env` to enable live GPT-4o-mini reasoning for Aurora Agent AI.*"
    )
    return f"{header}{routing_note}{kb_section}{setup_tip}"


def generate_answer(
    user_message: str,
    recent_messages: list[dict],
    knowledge_context: list[dict],
    customer: dict,
    conversation: dict,
    agent: dict,
    route_reason: Optional[str] = None,
    transferred_from_master: bool = False,
) -> str:
    if not settings.has_openai or OpenAI is None:
        return _fallback_aurora_answer(
            user_message=user_message,
            knowledge_context=knowledge_context,
            agent=agent,
            route_reason=route_reason,
            transferred_from_master=transferred_from_master,
        )

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    system_prompt = build_agent_prompt(agent)

    transfer_instruction = ""
    if agent["slug"] == "master":
        transfer_instruction = """
You are Aurora Master, the central orchestrator of Aurora Agent AI.
If the user greets you or asks what you can do:
Introduce yourself as Aurora Master and explain that you can assist directly or connect them to:
- Aurora Finance (Payroll, Invoices, Expenses, Budgets)
- Aurora HR (Leave, Hiring, Onboarding, Benefits, Policies)
- Aurora Sales (Leads, CRM, Pricing, Proposals, Deals)
- Aurora Operations (Inventory, Logistics, Vendors, SOPs)
""".strip()
    elif transferred_from_master:
        transfer_instruction = f"""
Aurora Master has routed this request to you ({agent['name']}).
Briefly acknowledge that you are {agent['name']} and then directly and thoroughly answer the user's request.
""".strip()

    user_prompt = f"""
{transfer_instruction}

Routing Context:
{route_reason or 'Direct conversation with agent'}

Recent Conversation History:
{_format_recent_messages(recent_messages)}

Retrieved Knowledge Base Context:
{_format_knowledge_context(knowledge_context)}

User Message:
{user_message}
""".strip()

    try:
        res = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=450,
        )
        return res.choices[0].message.content or ""
    except Exception as exc:
        print(f"⚠️ OpenAI completion error: {exc}")
        return _fallback_aurora_answer(
            user_message=user_message,
            knowledge_context=knowledge_context,
            agent=agent,
            route_reason=route_reason,
            transferred_from_master=transferred_from_master,
        )
