import json
from typing import Optional
from app.db.supabase import supabase
from app.config import settings

DEFAULT_AGENTS: list[dict] = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "name": "Aurora Master",
        "slug": "master",
        "icon": "✨",
        "badge": "Neural Orchestrator",
        "accent": "aurora",
        "description": (
            "Central intelligence orchestrator that analyzes your intent in real time "
            "and seamlessly routes requests to Finance, HR, Sales, or Operations."
        ),
        "prompt_instructions": (
            "You are Aurora Master, the central orchestrator of Aurora Agent AI. "
            "Greet users warmly, answer general overview questions, clarify ambiguous requests, "
            "and seamlessly coordinate across Finance, HR, Sales, and Operations specialists."
        ),
        "sample_prompts": [
            "How do I submit a travel expense reimbursement?",
            "How many paid leave days do employees get per year?",
            "Draft a follow-up strategy for an enterprise CRM lead",
            "Our warehouse inventory for SKU-402 is running low",
        ],
        "is_master": True,
        "is_active": True,
    },
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "name": "Aurora Finance",
        "slug": "finance",
        "icon": "💎",
        "badge": "Financial Intelligence",
        "accent": "emerald",
        "description": (
            "Handles payroll cycles, vendor invoices, expense reimbursements, "
            "departmental budgets, tax compliance, and financial reporting."
        ),
        "prompt_instructions": (
            "You are Aurora Finance. Provide clear, accurate guidance on payroll schedules, "
            "invoice approvals, expense reimbursement policies, budget tracking, tax deductions, "
            "and financial statements. Cite uploaded financial policy documents whenever available."
        ),
        "sample_prompts": [
            "What is the policy for meal and travel reimbursements?",
            "When is the monthly payroll cutoff date?",
            "How do I submit a vendor invoice for approval?",
            "Help me structure a Q4 department budget review",
        ],
        "is_master": False,
        "is_active": True,
    },
    {
        "id": "00000000-0000-0000-0000-000000000003",
        "name": "Aurora HR",
        "slug": "hr",
        "icon": "🌿",
        "badge": "People & Culture",
        "accent": "violet",
        "description": (
            "Manages talent acquisition, PTO & leave balances, attendance policies, "
            "employee onboarding, health benefits, and performance reviews."
        ),
        "prompt_instructions": (
            "You are Aurora HR, the People & Culture specialist. Assist with leave policies, "
            "attendance guidelines, onboarding checklists, employee benefits, hiring workflows, "
            "and performance review cycles with empathy and clarity."
        ),
        "sample_prompts": [
            "How do I request annual leave or sick leave?",
            "What does the new hire onboarding checklist include?",
            "Explain our health insurance and wellness benefits",
            "How are quarterly performance reviews structured?",
        ],
        "is_master": False,
        "is_active": True,
    },
    {
        "id": "00000000-0000-0000-0000-000000000004",
        "name": "Aurora Sales",
        "slug": "sales",
        "icon": "🚀",
        "badge": "Revenue & Growth",
        "accent": "cyan",
        "description": (
            "Accelerates lead qualification, CRM pipeline management, custom pricing quotes, "
            "enterprise proposals, client follow-ups, and deal closing."
        ),
        "prompt_instructions": (
            "You are Aurora Sales, the Revenue & Growth specialist. Help qualify leads, "
            "prepare pricing quotes, structure proposals, manage CRM pipeline stages, "
            "and craft high-converting client follow-up communications."
        ),
        "sample_prompts": [
            "Write a follow-up message for a prospect after a demo",
            "How should we qualify an inbound enterprise lead?",
            "What discount tiers are available for annual contracts?",
            "Help me outline an executive proposal for a new client",
        ],
        "is_master": False,
        "is_active": True,
    },
    {
        "id": "00000000-0000-0000-0000-000000000005",
        "name": "Aurora Operations",
        "slug": "operations",
        "icon": "⚡",
        "badge": "Systems & Logistics",
        "accent": "amber",
        "description": (
            "Optimizes supply chain logistics, inventory restocking, vendor SLAs, "
            "standard operating procedures (SOPs), and daily fulfillment workflows."
        ),
        "prompt_instructions": (
            "You are Aurora Operations, the Systems & Logistics specialist. Guide users through "
            "standard operating procedures (SOPs), inventory management, vendor SLAs, "
            "shipping logistics, and incident resolution."
        ),
        "sample_prompts": [
            "What is the SOP when warehouse inventory drops below threshold?",
            "How do we onboard and evaluate a new logistics vendor?",
            "Create a fulfillment checklist for priority shipments",
            "How do we escalate a delayed supplier delivery?",
        ],
        "is_master": False,
        "is_active": True,
    },
]

_DEFAULTS_BY_SLUG = {a["slug"]: a for a in DEFAULT_AGENTS}
_DEFAULTS_BY_ID = {a["id"]: a for a in DEFAULT_AGENTS}


def _enrich_agent(raw: dict) -> dict:
    """Merge Supabase agent row with Aurora UI metadata defaults."""
    slug = (raw.get("slug") or "").lower()
    base = dict(_DEFAULTS_BY_SLUG.get(slug, {}))
    merged = {**base, **raw}

    # Ensure Aurora branding on generic names from older DB seeds
    name = merged.get("name") or base.get("name") or slug.title()
    if not name.lower().startswith("aurora"):
        clean = name.replace("Agent", "").strip()
        merged["name"] = f"Aurora {clean}"

    merged.setdefault("icon", base.get("icon", "🤖"))
    merged.setdefault("badge", base.get("badge", "Specialist Agent"))
    merged.setdefault("accent", base.get("accent", "aurora"))
    merged.setdefault("sample_prompts", base.get("sample_prompts", []))
    merged.setdefault("is_master", slug == "master" or bool(raw.get("is_master")))
    merged.setdefault("is_active", True)
    return merged


def list_active_agents() -> list[dict]:
    if supabase is not None:
        try:
            result = (
                supabase.table("agents")
                .select("*")
                .eq("is_active", True)
                .order("created_at")
                .execute()
            )
            if result.data:
                agents = [_enrich_agent(row) for row in result.data]
                # Put master first
                agents.sort(key=lambda a: (0 if a.get("slug") == "master" else 1))
                return agents
        except Exception as exc:
            print(f"⚠️ Using built-in Aurora agents (Supabase query skipped: {exc})")

    return [dict(a) for a in DEFAULT_AGENTS]


def get_agent_by_slug(slug: str) -> Optional[dict]:
    if not slug:
        return None
    normalized = slug.strip().lower()

    if supabase is not None:
        try:
            result = (
                supabase.table("agents")
                .select("*")
                .eq("slug", normalized)
                .limit(1)
                .execute()
            )
            if result.data:
                return _enrich_agent(result.data[0])
        except Exception as exc:
            print(f"⚠️ Fallback to built-in agent for slug '{normalized}': {exc}")

    default_agent = _DEFAULTS_BY_SLUG.get(normalized)
    return dict(default_agent) if default_agent else None


def get_agent_by_id(agent_id: str) -> Optional[dict]:
    if not agent_id:
        return None

    # Allow lookup by slug as well for convenience
    if agent_id.lower() in _DEFAULTS_BY_SLUG:
        return get_agent_by_slug(agent_id.lower())

    if supabase is not None:
        try:
            result = (
                supabase.table("agents")
                .select("*")
                .eq("id", agent_id)
                .limit(1)
                .execute()
            )
            if result.data:
                return _enrich_agent(result.data[0])
        except Exception as exc:
            print(f"⚠️ Fallback to built-in agent for id '{agent_id}': {exc}")

    default_agent = _DEFAULTS_BY_ID.get(agent_id)
    return dict(default_agent) if default_agent else None


def build_agent_prompt(agent: dict) -> str:
    return f"""
You are {agent['name']}, part of {settings.APP_NAME} — an intelligent multi-agent system created by Washifur Rahman.

Core Directives:
- Speak in a polished, clear, helpful, and proactive tone suitable for {agent['name']}.
- Ground your answers in the provided Knowledge Context whenever relevant documents exist.
- Never fabricate company policy numbers, exact figures, or compliance rules that aren't in the context; if a specific company policy detail isn't in the knowledge base yet, provide best-practice guidance and mention what document can be uploaded.
- Format responses cleanly using concise paragraphs or bullet points when helpful.
- If a question clearly belongs to another Aurora specialist (Finance, HR, Sales, or Operations), note how that specialist can help.

Specialist Instructions:
{agent.get('prompt_instructions') or 'Assist the user accurately and concisely.'}
""".strip()


def build_widget_assistant_config(agent: dict) -> str:
    assistant_config = {
        "name": f"aurora-{agent['slug']}",
        "model": {
            "provider": "openai",
            "model": settings.OPENAI_MODEL,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": build_agent_prompt(agent),
                }
            ],
        },
        "voice": {
            "provider": "vapi",
            "voiceId": "Elliot",
        },
        "firstMessage": f"Hello! I'm {agent['name']} from Aurora Agent AI. How can I help you today?",
    }

    return json.dumps(assistant_config)
