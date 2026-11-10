from typing import Any, Optional, Tuple
from app.config import settings
from app.services.agents import build_agent_prompt

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore


def _get_llm_providers() -> list[Tuple[str, Any, str]]:
    """Return ordered list of configured (provider_name, client, model) for automatic failover."""
    if OpenAI is None:
        return []

    providers: list[Tuple[str, Any, str]] = []
    if settings.has_mistral:
        providers.append(
            (
                "Mistral AI",
                OpenAI(api_key=settings.MISTRAL_API_KEY, base_url=settings.MISTRAL_BASE_URL),
                settings.MISTRAL_MODEL,
            )
        )
    if settings.has_groq:
        providers.append(
            (
                "Groq",
                OpenAI(api_key=settings.GROQ_API_KEY, base_url=settings.GROQ_BASE_URL),
                settings.GROQ_MODEL,
            )
        )
    if settings.has_openai:
        providers.append(
            (
                "OpenAI",
                OpenAI(api_key=settings.OPENAI_API_KEY),
                settings.OPENAI_MODEL,
            )
        )
    return providers


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
    """Provides a structured offline response when no LLM API key is configured yet."""
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
        "💡 *Tip: Add a free `MISTRAL_API_KEY` (from console.mistral.ai) to your `.env` file to enable live Mistral AI reasoning & embeddings!*"
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
    providers = _get_llm_providers()
    if not providers:
        return _fallback_aurora_answer(
            user_message=user_message,
            knowledge_context=knowledge_context,
            agent=agent,
            route_reason=route_reason,
            transferred_from_master=transferred_from_master,
        )

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

    for provider_name, client, model in providers:
        try:
            res = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=500,
            )
            return res.choices[0].message.content or ""
        except Exception as exc:
            print(f"⚠️ {provider_name} completion error ({exc}), trying next provider if available...")

    return _fallback_aurora_answer(
        user_message=user_message,
        knowledge_context=knowledge_context,
        agent=agent,
        route_reason=route_reason,
        transferred_from_master=transferred_from_master,
    )
