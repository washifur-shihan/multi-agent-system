from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def extract_order(text: str):
    prompt = f"""
Extract food order from this message.

Return valid JSON only:
{{
  "items": [
    {{
      "name": "",
      "quantity": 1,
      "notes": ""
    }}
  ]
}}

Message: "{text}"
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return res.choices[0].message.content