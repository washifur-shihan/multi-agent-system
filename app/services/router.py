from app.services.agents import get_agent_by_slug

DEPARTMENTS = {
    "finance": [
    "finance", "financial", "financial report", "financial reports",
    "payroll", "salary", "payment", "payments",
    "invoice", "invoices",
    "expense", "expenses",
    "reimbursement", "reimbursements",
    "budget", "budgets",
    "accounting", "tax", "revenue", "profit", "loss"
],
    "hr": [
        "hiring", "recruitment", "leave", "attendance", "onboarding",
        "employee policy", "benefits", "performance", "termination"
    ],
    "sales": [
        "lead", "customer", "crm", "deal", "quote", "pricing",
        "proposal", "follow up", "pipeline"
    ],
    "operations": [
        "inventory", "logistics", "vendor", "sop", "fulfillment",
        "delivery", "process", "workflow", "supply"
    ],
}


def rule_based_route(message: str):
    text = message.lower()
    scores = {}
    # DIRECT DEPARTMENT MENTION (highest priority)
    for dept in DEPARTMENTS.keys():
        if dept in text:
            return dept, f"User explicitly mentioned {dept}"

    for dept, keywords in DEPARTMENTS.items():
        scores[dept] = sum(1 for word in keywords if word in text)

    best = max(scores, key=scores.get)

    if scores[best] > 0:
        return best, f"Matched keywords for {best}"

    return None, "No clear department match"


def route_to_agent(message: str):
    slug, reason = rule_based_route(message)

    if slug is None:
        return None, reason

    return get_agent_by_slug(slug), reason