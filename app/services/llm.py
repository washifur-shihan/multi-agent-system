import hashlib
import math
from typing import Any, Optional
from app.config import settings

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore


def _get_openai_client() -> Optional[Any]:
    if not settings.has_openai or OpenAI is None:
        return None
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def _fallback_embedding(text: str, dims: int = 1536) -> list[float]:
    """Deterministic local embedding vector when OpenAI API key is not configured."""
    tokens = [t for t in text.lower().split() if t]
    vec = [0.0] * dims
    if not tokens:
        return vec
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for i in range(0, len(digest), 2):
            idx = ((digest[i] << 8) | digest[i + 1]) % dims
            sign = 1.0 if (digest[i] & 1) == 0 else -1.0
            vec[idx] += sign
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    client = _get_openai_client()
    if client is not None:
        try:
            res = client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=texts,
            )
            return [item.embedding for item in res.data]
        except Exception as exc:
            print(f"⚠️ OpenAI embedding fallback activated ({exc})")

    return [_fallback_embedding(t) for t in texts]


def embed_query(text: str) -> list[float]:
    results = embed_texts([text])
    return results[0] if results else _fallback_embedding("")
