import hashlib
import math
from typing import Any, Optional, Tuple
from app.config import settings

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore

TARGET_EMBEDDING_DIMS = 1536


def _get_embedding_client_and_model() -> Tuple[Optional[Any], str]:
    """Return (client, embedding_model) preferring Mistral free tier, then OpenAI."""
    if OpenAI is None:
        return None, ""

    if settings.has_mistral:
        return (
            OpenAI(api_key=settings.MISTRAL_API_KEY, base_url=settings.MISTRAL_BASE_URL),
            settings.MISTRAL_EMBEDDING_MODEL,
        )

    if settings.has_openai:
        return (
            OpenAI(api_key=settings.OPENAI_API_KEY),
            settings.EMBEDDING_MODEL,
        )

    return None, ""


def _fit_dimensions(vec: list[float], target_dims: int = TARGET_EMBEDDING_DIMS) -> list[float]:
    """Ensure vector has exact target_dims (e.g. pad Mistral 1024-dim to 1536-dim for pgvector compatibility)."""
    if len(vec) == target_dims:
        return vec
    if len(vec) > target_dims:
        trimmed = vec[:target_dims]
        norm = math.sqrt(sum(v * v for v in trimmed)) or 1.0
        return [v / norm for v in trimmed]
    return vec + [0.0] * (target_dims - len(vec))


def _fallback_embedding(text: str, dims: int = TARGET_EMBEDDING_DIMS) -> list[float]:
    """Deterministic local embedding vector when no embedding API key is configured."""
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

    client, model = _get_embedding_client_and_model()
    if client is not None and model:
        try:
            res = client.embeddings.create(
                model=model,
                input=texts,
            )
            return [_fit_dimensions(item.embedding) for item in res.data]
        except Exception as exc:
            print(f"⚠️ Embedding API fallback activated ({exc})")

    return [_fallback_embedding(t) for t in texts]


def embed_query(text: str) -> list[float]:
    results = embed_texts([text])
    return results[0] if results else _fallback_embedding("")
