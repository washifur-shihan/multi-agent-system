import json
from openai import OpenAI
from app.config import settings
from app.services.agents import get_agent_by_slug

client = OpenAI(api_key=settings.OPENAI_API_KEY)

MASTER_ROUTER_PROMPT = """
You are a master routing agent.

Route the user's message to exactly one department agent.

Available agents:
- finance: payroll, salaries, compensation payments, budgets, invoices, expenses, vendor payments, revenue, financial reports, accounting, tax, reimbursements
- hr: hiring, onboarding, leave, attendance, employee policies, benefits, employee relations, performance reviews, recruitment
- sales: leads, customers, CRM, pipeline, quotes, pricing, follow-ups, deals
- operations: logistics, inventory, SOPs, vendors, fulfillment, daily operations, processes

Important routing rules:
- If the message mentions payroll, salary payment, compensation payment, invoice, expense, reimbursement, accounting, or budget, route to finance.
- If the message mentions hiring, leave, attendance, onboarding, employee policy, benefits, or recruitment, route to hr.
- If both HR and Finance could apply, choose finance when money/payment/payroll is the main topic.

Return only valid JSON:
{
  "agent_slug": "finance|hr|sales|operations",
  "reason": "short reason"
}
"""


def route_to_agent(message: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": MASTER_ROUTER_PROMPT},
            {"role": "user", "content": message},
        ],
        temperature=0,
    )

    raw = response.choices[0].message.content or "{}"
    data = json.loads(raw)

    agent_slug = data.get("agent_slug", "operations")
    agent = get_agent_by_slug(agent_slug)

    return agent, data.get("reason", "")