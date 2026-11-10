import re
from typing import Optional, Tuple
from app.services.agents import get_agent_by_slug

DEPARTMENT_KEYWORDS: dict[str, list[str]] = {
    "finance": [
        "finance", "financial", "financial report", "financial reports",
        "payroll", "salary", "salaries", "payslip", "compensation", "bonus",
        "payment", "payments", "invoice", "invoices", "billing", "bill",
        "expense", "expenses", "reimbursement", "reimbursements", "receipt",
        "budget", "budgets", "forecast", "accounting", "ledger",
        "tax", "taxes", "vat", "audit", "revenue", "profit", "loss", "cashflow",
    ],
    "hr": [
        "hr", "human resources", "people ops", "hiring", "recruitment", "recruiting",
        "candidate", "interview", "offer letter", "onboarding", "offboarding",
        "leave", "pto", "vacation", "sick day", "sick leave", "parental leave",
        "attendance", "timesheet", "time off", "holiday",
        "employee policy", "handbook", "code of conduct", "workplace",
        "benefits", "health insurance", "401k", "wellness",
        "performance review", "appraisal", "promotion", "termination", "resignation",
    ],
    "sales": [
        "sales", "lead", "leads", "prospect", "prospecting", "customer", "client",
        "crm", "hubspot", "salesforce", "deal", "deals", "opportunity",
        "quote", "quotation", "pricing", "discount", "tier", "contract",
        "proposal", "pitch", "demo", "follow up", "follow-up", "outreach",
        "pipeline", "quota", "commission", "upsell", "renewal", "closing",
    ],
    "operations": [
        "operations", "ops", "inventory", "stock", "sku", "warehouse",
        "logistics", "shipping", "freight", "shipment", "delivery", "dispatch",
        "vendor", "vendors", "supplier", "suppliers", "procurement", "sla",
        "sop", "standard operating procedure", "checklist",
        "fulfillment", "order fulfillment", "quality control", "maintenance",
        "process", "workflow", "supply chain", "incident", "escalation",
    ],
}


def _keyword_matches(text: str, keyword: str) -> bool:
    """Match whole words or phrases accurately so 'hr' never matches inside 'three'."""
    pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
    return bool(re.search(pattern, text))


def rule_based_route(message: str) -> Tuple[Optional[str], str]:
    if not message or not message.strip():
        return None, "Empty query"

    text = message.lower().strip()
    scores: dict[str, int] = {dept: 0 for dept in DEPARTMENT_KEYWORDS}
    matched_terms: dict[str, list[str]] = {dept: [] for dept in DEPARTMENT_KEYWORDS}

    # Direct explicit mention of switching/talking to a department gets priority boost
    for dept in DEPARTMENT_KEYWORDS:
        if _keyword_matches(text, dept):
            scores[dept] += 3
            matched_terms[dept].append(dept)

    for dept, keywords in DEPARTMENT_KEYWORDS.items():
        for kw in keywords:
            if _keyword_matches(text, kw):
                # Multi-word phrases carry higher specificity weight
                weight = 2 if " " in kw else 1
                scores[dept] += weight
                if kw not in matched_terms[dept]:
                    matched_terms[dept].append(kw)

    best_dept = max(scores, key=lambda d: scores[d])
    best_score = scores[best_dept]

    if best_score > 0:
        terms_preview = ", ".join(matched_terms[best_dept][:3])
        return best_dept, f"Matched {best_dept.upper()} signals ({terms_preview})"

    return None, "General inquiry handled by Aurora Master"


def route_to_agent(message: str) -> Tuple[Optional[dict], str]:
    slug, reason = rule_based_route(message)

    if slug is None:
        return None, reason

    return get_agent_by_slug(slug), reason
