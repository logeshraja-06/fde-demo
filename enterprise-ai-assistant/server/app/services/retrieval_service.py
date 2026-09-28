"""
services/retrieval_service.py
------------------------------
The RAG Retrieval Service for Phase 3.

WHAT HAPPENS DURING RETRIEVAL?
------------------------------
When a user asks a question like "How many casual leaves do employees get?":

1. Validate the query (check it is not empty).
2. Pass the question through the Embedding Service to produce a 384-d vector.
3. Query ChromaDB to find the top-K chunks with the closest cosine distance.
4. Calculate similarity scores (from 0.0 to 1.0).
5. Apply a Relevance Threshold:
   - If the closest chunk is below the threshold, it means the knowledge base
     has NO relevant information on this topic.
   - We return an empty list with a clear message rather than feeding irrelevant
     garbage to the future LLM!
6. Return the top relevant chunks with their metadata and scores.

IMPORTANT FOR PHASE 3:
----------------------
We do NOT call an LLM here. We stop at returning the retrieved context chunks.
"""

from typing import List, Dict, Any, Optional
from app.services.embedding_service import get_embedding
from app.vectorstore.chroma_store import query_vector_store, get_vector_store_stats

# Default threshold for cosine similarity.
# Since normalized vectors with cosine similarity range from 0.0 (unrelated) to 1.0 (identical),
# a threshold around 0.30 - 0.40 reliably filters out unrelated queries (like cake recipes).
DEFAULT_SIMILARITY_THRESHOLD = 0.35
DEFAULT_TOP_K = 3


def search_knowledge_base(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search the vector database for chunks semantically relevant to the user query.
    Supports optional domain filtering (HR, Finance, IT).

    Args:
        query: The user's question or search phrase.
        top_k: Number of chunks to retrieve (e.g. 1 to 10).
        threshold: Minimum cosine similarity score required (0.0 to 1.0).
        domain: Optional knowledge domain filter.

    Returns:
        Dict matching the Phase 3 & Phase 8 specification with results and domain info.
    """
    # 1. Validate Query
    cleaned_query = (query or "").strip()
    if not cleaned_query:
        raise ValueError("Search query cannot be empty.")

    # Bound top_k to reasonable enterprise limits
    effective_k = max(1, min(20, int(top_k)))
    effective_threshold = max(0.0, min(1.0, float(threshold)))

    # 2. Convert user question into an embedding vector
    query_vector = get_embedding(cleaned_query)

    # 3. Retrieve nearest neighbors from ChromaDB (with optional domain filter)
    raw_results = query_vector_store(query_vector, top_k=effective_k, domain=domain)

    # 4. Filter by relevance threshold
    filtered_results = [
        item for item in raw_results
        if item.get("score", 0.0) >= effective_threshold
    ]

    # 5. Build response payload
    if not filtered_results:
        return {
            "success": True,
            "query": cleaned_query,
            "top_k": effective_k,
            "threshold": effective_threshold,
            "total_found": 0,
            "results": [],
            "message": "No sufficiently relevant information was found in the knowledge base."
        }

    return {
        "success": True,
        "query": cleaned_query,
        "top_k": effective_k,
        "threshold": effective_threshold,
        "total_found": len(filtered_results),
        "results": filtered_results,
        "message": f"Retrieved {len(filtered_results)} relevant chunk(s) from knowledge base."
    }
