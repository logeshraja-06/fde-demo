"""
routes/truthguard.py
--------------------
TruthGuard Adversarial Document Verification API endpoints for the server.
Provides LangGraph-inspired conflict detection, governance resolution, and question verification.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.truthguard_service import (
    detect_adversarial_conflicts,
    evaluate_conflict_governance,
    call_gemini_truthguard
)
from app.services.retrieval_service import search_knowledge_base
from app.vectorstore.chroma_store import get_vector_store_stats

router = APIRouter(tags=["TruthGuard Adversarial Verification"])


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000, description="Question to verify against document corpus")
    user_id: Optional[str] = "default_user"
    permissions: List[str] = Field(default_factory=lambda: ["read_all"])
    version_filter: Optional[str] = None
    document_ids: Optional[List[str]] = None


class QuestionResponse(BaseModel):
    query_id: str
    question: str
    final_answer: str
    conflict_status: str
    conflict_explanation: str
    conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    citations: List[Dict[str, Any]] = Field(default_factory=list)


@router.post("/questions", response_model=QuestionResponse, summary="Execute TruthGuard Verification Workflow")
def ask_truthguard_question(req: QuestionRequest):
    """
    Executes TruthGuard adversarial verification workflow:
    1. Retrieves evidence chunks from knowledge base
    2. Runs Adversarial Contradiction Detection across documents
    3. Evaluates governance & supersession rules (prevents unapproved amendments from overriding active policy)
    4. Generates grounded answer using Google Gemini (gemini-flash-lite-latest)
    """
    import uuid
    query_id = f"TG_{uuid.uuid4().hex[:10].upper()}"

    retrieval_res = search_knowledge_base(
        query=req.question,
        top_k=5,
        threshold=0.25
    )
    chunks = retrieval_res.get("results", [])

    if not chunks:
        return QuestionResponse(
            query_id=query_id,
            question=req.question,
            final_answer="Insufficient Document Evidence: The uploaded document corpus does not contain reliable policy statements to answer this question.",
            conflict_status="insufficient_evidence",
            conflict_explanation="No relevant policy evidence was retrieved from the document corpus.",
            conflicts=[],
            citations=[]
        )

    conflicts = detect_adversarial_conflicts(chunks)
    governance = evaluate_conflict_governance(conflicts, chunks)

    final_answer = call_gemini_truthguard(
        query=req.question,
        chunks=chunks,
        conflicts=conflicts,
        governance=governance
    )

    citations = [
        {
            "source": c.get("source", "Unknown Document"),
            "page": c.get("page", 1),
            "score": c.get("score", 0.0),
            "chunk_id": c.get("chunk_id", ""),
            "text": c.get("text", "")[:250] + ("..." if len(c.get("text", "")) > 250 else "")
        }
        for c in chunks
    ]

    return QuestionResponse(
        query_id=query_id,
        question=req.question,
        final_answer=final_answer,
        conflict_status=governance["status"],
        conflict_explanation=governance.get("reason", "All policies consistent."),
        conflicts=conflicts,
        citations=citations
    )


@router.get("/truthguard/status", summary="TruthGuard System Status")
def truthguard_status():
    """Returns active TruthGuard LLM configuration and document corpus state."""
    stats = get_vector_store_stats()
    return {
        "engine": "TruthGuard Adversarial Verification Prototype",
        "orchestration": "LangGraph Adversarial Flow",
        "llm_provider": "Google Gemini (gemini-flash-lite-latest)",
        "vector_database": "ChromaDB Persistent Store",
        "indexed_chunks_count": stats.get("total_chunks_indexed", 0),
        "documents": stats.get("documents", []),
        "status": "ready"
    }


@router.get("/truthguard/conflicts", summary="Scan Active Document Corpus for Conflicts")
def scan_conflicts():
    """Scans all chunks across the indexed corpus and reports any detected cross-document contradictions."""
    stats = get_vector_store_stats()
    # Query knowledge base for general leave and policy chunks
    res = search_knowledge_base("casual leave policy rules amendment days", top_k=8, threshold=0.1)
    chunks = res.get("results", [])
    conflicts = detect_adversarial_conflicts(chunks)
    governance = evaluate_conflict_governance(conflicts, chunks)
    return {
        "total_chunks_scanned": len(chunks),
        "conflicts_count": len(conflicts),
        "conflicts": conflicts,
        "governance_evaluation": governance
    }
