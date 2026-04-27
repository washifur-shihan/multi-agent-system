from openai import OpenAI
from app.config import settings
from app.services.agents import build_agent_prompt

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def _format_recent_messages(recent_messages):
    if not recent_messages:
        return "No recent messages."
    return "\n".join(
        f"{m['role']}: {m['content'][:300]}"
        for m in recent_messages[-4:]
    )

def _format_knowledge_context(ctx):
    if not ctx:
        return "No matching knowledge."

    chunks = []
    for x in ctx[:3]:
        content = x.get("content", "")
        chunks.append(content[:700])

    return "\n\n".join(chunks)

def generate_answer(
    user_message,
    recent_messages,
    knowledge_context,
    customer,
    conversation,
    agent,
    route_reason=None,
    transferred_from_master=False,
):
    system_prompt = build_agent_prompt(agent)

    transfer_instruction = ""

    if agent["slug"] == "master":
        transfer_instruction = """
You are the Master Agent.

If user greets or asks who you are:
Say:
"Hello, you’ve reached the company assistant. I can connect you to Finance, HR, Sales, or Operations. How can I help you?"

Do NOT transfer unless needed.
"""

    elif transferred_from_master:
        transfer_instruction = f"""
The Master Agent has transferred the call to you.

Start with:
"Hello, this is the {agent['name']}. I can help you with this."

Then:
- If clear → answer directly
- If unclear → ask one follow-up question
"""

    user_prompt = f"""
{transfer_instruction}

User message:
{user_message}

Recent:
{_format_recent_messages(recent_messages)}

Knowledge:
{_format_knowledge_context(knowledge_context)}
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=300,
    )

    return res.choices[0].message.content or ""