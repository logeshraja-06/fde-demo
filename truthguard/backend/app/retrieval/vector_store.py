import re
import math
import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from app.database.repository import get_all_chunks_with_embeddings
from app.retrieval.embeddings import generate_embedding

logger = logging.getLogger("truthguard.vector_store")


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a, b in zip(v1, v2)))
    norm2 = math.sqrt(sum(b * b for a, b in zip(v1, v2)))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm1 * norm2)))


def compute_keyword_score(query: str, text: str) -> float:
    """Computes BM25-style lexical keyword overlap."""
    q_words = set(re.findall(r'\b[a-zA-Z0-9_-]+\b', query.lower()))
    if not q_words:
        return 0.0
    t_words = re.findall(r'\b[a-zA-Z0-9_-]+\b', text.lower())
    if not t_words:
        return 0.0

    matches = sum(1 for w in q_words if w in t_words)
    return min(1.0, matches / len(q_words))


def search_evidence(
    query: str,
    top_k: Optional[int] = None,
    document_ids: Optional[List[str]] = None,
    version_filter: Optional[str] = None,
    min_score: float = 0.1
) -> List[Dict[str, Any]]:
    """
    Hybrid retrieval:
    Combines semantic vector cosine similarity with lexical keyword search.
    Applies metadata filtering for document versions and document IDs.
    """
    top_k = top_k or settings.RAG_TOP_K
    all_chunks = get_all_chunks_with_embeddings()

    if not all_chunks:
        return []

    # Filter chunks based on document_ids and version_filter
    filtered_chunks = []
    for c in all_chunks:
        if document_ids and c["document_id"] not in document_ids:
            continue
        if version_filter and c.get("version") != version_filter:
            continue
        filtered_chunks.append(c)

    if not filtered_chunks:
        return []

    query_embedding = generate_embedding(query)
    scored_chunks = []

    for c in filtered_chunks:
        c_emb = c.get("embedding", [])
        sim = cosine_similarity(query_embedding, c_emb)
        kw = compute_keyword_score(query, c.get("text", ""))

        # Hybrid weighting: 65% semantic, 35% keyword
        hybrid_score = (0.65 * sim) + (0.35 * kw)

        if hybrid_score >= min_score or kw > 0.5:
            scored_chunks.append({
                **c,
                "similarity_score": round(sim, 4),
                "keyword_score": round(kw, 4),
                "hybrid_score": round(hybrid_score, 4)
            })

    # Sort descending by hybrid_score
    scored_chunks.sort(key=lambda x: x["hybrid_score"], reverse=True)
    return scored_chunks[:top_k]
