from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def embed_texts(texts: list[str]) -> list[list[float]]:
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in res.data]

def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]