"""
routes/rag.py
-------------
API routes for Phase 3 RAG Retrieval Pipeline.

Provides:
  POST /rag/search  (and /api/rag/search)  - Retrieve relevant chunks for a question
  GET  /rag/stats   (and /api/rag/stats)   - Get vector store & embedding metadata
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Any

from app.services.retrieval_service import search_knowledge_base, DEFAULT_SIMILARITY_THRESHOLD, DEFAULT_TOP_K
from app.services.embedding_service import get_model_info
from app.vectorstore.chroma_store import get_vector_store_stats

from app.models.errors import ErrorCode

router = APIRouter(tags=["RAG Retrieval Pipeline"])


# ── Request / Response Pydantic Schemas ──────────────────────────────────────

class SearchRequest(BaseModel):
    query: str = Field(..., description="The natural language question to search the knowledge base for.", min_length=1)
    top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=20, description="Number of top relevant chunks to retrieve.")
    threshold: float = Field(default=DEFAULT_SIMILARITY_THRESHOLD, ge=0.0, le=1.0, description="Minimum cosine similarity score (0.0 to 1.0).")
    domain: Optional[str] = Field(default=None, description="Optional knowledge domain filter (e.g. 'HR', 'Finance', 'IT', 'ALL').")


class SearchResultChunk(BaseModel):
    chunk_id: str
    source: str
    document_id: Optional[str] = None
    domain: Optional[str] = None
    page: Optional[int] = None
    score: float
    distance: Optional[float] = None
    text: str


class SearchResponse(BaseModel):
    success: bool = True
    query: str
    top_k: int
    threshold: float
    total_found: int
    results: List[SearchResultChunk]
    message: Optional[str] = None


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Retrieve semantically relevant chunks from the knowledge base",
    description="Embeds the user question, performs cosine similarity search in ChromaDB, and returns top-K matching chunks."
)
def search_endpoint(payload: SearchRequest):
    """
    Search knowledge base for chunks relevant to the given query.
    """
    try:
        results = search_knowledge_base(
            query=payload.query,
            top_k=payload.top_k,
            threshold=payload.threshold,
            domain=payload.domain
        )
        return results
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": ErrorCode.INVALID_INPUT, "message": str(exc)}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": ErrorCode.RAG_SEARCH_ERROR, "message": str(exc)}
        )


@router.get(
    "/stats",
    summary="Get RAG vector database & embedding model metadata"
)
def stats_endpoint():
    """
    Return statistics about indexed chunks and the local embedding model.
    """
    return {
        "embedding_model": get_model_info(),
        "vector_store": get_vector_store_stats(),
        "default_threshold": DEFAULT_SIMILARITY_THRESHOLD,
        "default_top_k": DEFAULT_TOP_K,
        "phase": "3 - RAG Retrieval Pipeline"
    }
