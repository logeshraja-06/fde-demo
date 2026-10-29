import hashlib
import math
import logging
from typing import List
from app.config import settings

logger = logging.getLogger("truthguard.embeddings")


def _deterministic_local_embedding(text: str, dim: int = 1536) -> List[float]:
    """
    Deterministic normalized 1536-dimensional vector generator.
    Used when OPENAI_API_KEY is not configured or in offline test environments.
    Guarantees that similar texts have high cosine similarity.
    """
    words = text.lower().split()
    vec = [0.0] * dim

    for i, word in enumerate(words):
        # Hash word into bucket
        h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        # Directional sign
        sign = 1.0 if (h >> 16) % 2 == 0 else -1.0
        vec[idx] += sign * (1.0 + math.log(1.0 + len(word)))

        # Also add bigram hash
        if i > 0:
            bi = f"{words[i-1]}_{word}"
            h_bi = int(hashlib.sha256(bi.encode("utf-8")).hexdigest(), 16)
            idx_bi = h_bi % dim
            sign_bi = 1.0 if (h_bi >> 16) % 2 == 0 else -1.0
            vec[idx_bi] += sign_bi * 2.0

    # L2 normalize
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    else:
        vec[0] = 1.0

    return vec


def generate_embedding(text: str) -> List[float]:
    """Generates an embedding vector for a single text."""
    return generate_embeddings([text])[0]


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a batch of texts.
    Uses official OpenAI API if OPENAI_API_KEY is set; otherwise falls back to deterministic vector generator.
    """
    if not texts:
        return []

    if settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY.strip()) > 10:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            resp = client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=texts
            )
            return [data.embedding for data in resp.data]
        except Exception as exc:
            logger.warning(f"OpenAI embedding API call failed ({exc}). Falling back to deterministic local embeddings.")

    # Offline / local fallback
    return [_deterministic_local_embedding(t, settings.EMBEDDING_DIMENSION) for t in texts]
