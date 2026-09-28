"""
routes/chat.py
--------------
Chat endpoint for Phase 5: Guardrails and AI Safety.

3-Layer Protection Pipeline:
  Layer 1: Input Guardrail (Empty check, Length limit, Prompt injection regex)
       ↓
  Layer 2: RAG Retrieval + Grounding Guardrail (Relevance threshold cutoff)
       ↓
  Layer 3: LLM Context Restriction & Prompt Builder (Strict enterprise instructions)
       ↓
  Layer 4: Output Guardrail (Non-empty check, Source attachment, System leak prevention)
       ↓
  Structured Pipeline Response (No fake results, honest backend verification)
"""

import os
import time
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

from app.services.input_guardrail import validate_user_input, DEFAULT_MAX_INPUT_LENGTH, INJECTION_PATTERNS
from app.services.retrieval_service import search_knowledge_base, DEFAULT_SIMILARITY_THRESHOLD, DEFAULT_TOP_K
from app.services.prompt_builder import build_rag_prompt
from app.services.llm_service import generate_grounded_response, is_llm_configured, get_gemini_model_name
from app.services.output_guardrail import validate_llm_output
from app.services.analytics_service import record_chat_event
from app.services.config_service import get_customer_config

logger = logging.getLogger("enterprise_ai.chat")

router = APIRouter(tags=["AI Assistant Chat & Guardrails"])

# Configurable RAG grounding threshold from environment
RAG_GROUNDING_THRESHOLD = float(os.getenv("RAG_RELEVANCE_THRESHOLD", str(DEFAULT_SIMILARITY_THRESHOLD)))


# ── Schemas ──────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., description="User question or prompt for the AI assistant")
    top_k: Optional[int] = Field(default=None, ge=1, le=10)
    threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    domain: Optional[str] = Field(default=None, description="Optional domain filter (e.g. 'HR', 'Finance', 'IT', 'ALL')")


class SourceCitation(BaseModel):
    source: str
    page: Optional[int] = None
    domain: Optional[str] = None
    score: float
    chunk_id: str
    text: str


class PipelineStageInfo(BaseModel):
    status: str
    reason: Optional[str] = None
    score: Optional[float] = None
    threshold: Optional[float] = None
    results_count: Optional[int] = None
    model: Optional[str] = None
    checks: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    success: bool = True
    query: str
    answer: str
    sources: List[SourceCitation]
    retrieval_status: str
    model_used: Optional[str] = None
    pipeline: Dict[str, PipelineStageInfo]


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=ChatResponse,
    summary="Execute the Full 3-Layer Guardrail & RAG Chat Pipeline",
    description="Validates input, searches knowledge base, verifies grounding threshold, prompts LLM, and validates output."
)
def chat_endpoint(payload: ChatRequest):
    start_time = time.perf_counter()
    user_message = payload.message or ""

    # Load active runtime customer configuration
    cust_cfg = get_customer_config()
    max_input_len = cust_cfg.get("max_input_length", DEFAULT_MAX_INPUT_LENGTH)
    active_threshold = payload.threshold if payload.threshold is not None else float(cust_cfg.get("grounding_threshold", RAG_GROUNDING_THRESHOLD))
    effective_k = payload.top_k if payload.top_k is not None else int(cust_cfg.get("rag_top_k", DEFAULT_TOP_K))

    logger.info("Chat request received: query='%s' (top_k=%d, threshold=%.2f, domain=%s)", user_message[:60], effective_k, active_threshold, payload.domain)

    # =========================================================================
    # LAYER 1: INPUT GUARDRAILS
    # =========================================================================
    input_validation = validate_user_input(user_message, max_length=max_input_len)

    if not input_validation["passed"]:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        logger.warning("Chat request blocked by input guardrail: reason='%s'", input_validation["reason"])
        record_chat_event(
            query=user_message,
            status="blocked_input",
            response_time_ms=elapsed_ms,
            reason=input_validation["reason"],
            sources_count=0,
            pipeline_status={"input_guardrail": "blocked", "rag": "not_run", "grounding": "not_run", "llm": "not_run", "output_guardrail": "not_run"}
        )
        # Block immediately: Do NOT run RAG, Do NOT call LLM
        return ChatResponse(
            success=False,
            query=user_message,
            answer="I can't process that request.",
            sources=[],
            retrieval_status="input_blocked",
            model_used=None,
            pipeline={
                "input_guardrail": PipelineStageInfo(
                    status="blocked",
                    reason=input_validation["reason"],
                    checks=input_validation["checks"],
                ),
                "rag": PipelineStageInfo(status="not_run"),
                "grounding": PipelineStageInfo(status="not_run"),
                "llm": PipelineStageInfo(status="not_run"),
                "output_guardrail": PipelineStageInfo(status="not_run"),
            }
        )

    # =========================================================================
    # LAYER 2: RAG RETRIEVAL & GROUNDING GUARDRAIL
    # =========================================================================
    try:
        retrieval_res = search_knowledge_base(
            query=user_message,
            top_k=effective_k,
            threshold=active_threshold,
            domain=payload.domain
        )
    except Exception as exc:
        logger.error("RAG retrieval execution failure: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Knowledge base search failed. Please try again."
        )

    matched_chunks = retrieval_res.get("results", [])
    best_score = matched_chunks[0]["score"] if matched_chunks else 0.0
    logger.info("RAG retrieval completed: found %d chunks (best_score=%.4f)", len(matched_chunks), best_score)

    # If NO relevant context exists or score below threshold -> STOP pipeline
    if not matched_chunks or best_score < active_threshold:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        logger.warning("Grounding check blocked request: best_score=%.4f < threshold=%.4f", best_score, active_threshold)
        record_chat_event(
            query=user_message,
            status="insufficient_evidence",
            response_time_ms=elapsed_ms,
            reason="Insufficient relevant knowledge-base evidence",
            sources_count=0,
            best_score=best_score,
            pipeline_status={"input_guardrail": "passed", "rag": "completed", "grounding": "blocked", "llm": "not_run", "output_guardrail": "not_run"}
        )
        return ChatResponse(
            success=False,
            query=user_message,
            answer="I couldn't find enough information in the organization's knowledge base to answer that question.",
            sources=[],
            retrieval_status="insufficient_evidence",
            model_used=None,
            pipeline={
                "input_guardrail": PipelineStageInfo(
                    status="passed",
                    checks=input_validation["checks"],
                ),
                "rag": PipelineStageInfo(
                    status="completed",
                    results_count=len(matched_chunks),
                ),
                "grounding": PipelineStageInfo(
                    status="blocked",
                    score=round(best_score, 4),
                    threshold=active_threshold,
                    reason="Insufficient relevant knowledge-base evidence",
                ),
                "llm": PipelineStageInfo(status="not_run"),
                "output_guardrail": PipelineStageInfo(status="not_run"),
            }
        )

    # Format citations
    citations = [
        SourceCitation(
            source=chunk.get("source", "Unknown Document"),
            page=chunk.get("page"),
            domain=chunk.get("domain", "General"),
            score=chunk.get("score", 0.0),
            chunk_id=chunk.get("chunk_id", ""),
            text=chunk.get("text", "")
        )
        for chunk in matched_chunks
    ]

    # =========================================================================
    # LAYER 3: PROMPT CONSTRUCTION & LLM INVOCATION
    # =========================================================================
    prompt_payload = build_rag_prompt(
        user_query=user_message,
        retrieved_chunks=matched_chunks
    )

    try:
        llm_result = generate_grounded_response(
            system_instruction=prompt_payload["system_instruction"],
            user_prompt=prompt_payload["user_prompt"]
        )
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        logger.error("LLM Generation failed gracefully: %s", exc)
        record_chat_event(
            query=user_message,
            status="llm_failed",
            response_time_ms=elapsed_ms,
            reason="The AI generation service is currently unavailable.",
            sources_count=len(citations),
            best_score=best_score,
            pipeline_status={"input_guardrail": "passed", "rag": "passed", "grounding": "passed", "llm": "failed", "output_guardrail": "not_run"}
        )
        return ChatResponse(
            success=False,
            query=user_message,
            answer="The AI generation service is currently unavailable.",
            sources=citations,
            retrieval_status="llm_failed",
            model_used=None,
            pipeline={
                "input_guardrail": PipelineStageInfo(
                    status="passed",
                    checks=input_validation["checks"],
                ),
                "rag": PipelineStageInfo(
                    status="passed",
                    results_count=len(matched_chunks),
                ),
                "grounding": PipelineStageInfo(
                    status="passed",
                    score=round(best_score, 4),
                    threshold=active_threshold,
                ),
                "llm": PipelineStageInfo(
                    status="failed",
                    reason="The AI generation service is currently unavailable.",
                ),
                "output_guardrail": PipelineStageInfo(status="not_run"),
            }
        )

    raw_llm_answer = llm_result.get("answer", "")
    model_name = llm_result.get("model", get_gemini_model_name())
    logger.info("LLM generation completed with model='%s'", model_name)

    # =========================================================================
    # LAYER 4: OUTPUT GUARDRAILS
    # =========================================================================
    output_validation = validate_llm_output(
        generated_answer=raw_llm_answer,
        sources=matched_chunks,
        require_sources=True
    )

    if not output_validation["passed"]:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        logger.warning("Output guardrail blocked response: reason='%s'", output_validation["reason"])
        record_chat_event(
            query=user_message,
            status="blocked_output",
            response_time_ms=elapsed_ms,
            reason=output_validation["reason"],
            sources_count=len(citations),
            best_score=best_score,
            model_used=model_name,
            pipeline_status={"input_guardrail": "passed", "rag": "passed", "grounding": "passed", "llm": "completed", "output_guardrail": "blocked"}
        )
        # Block ungrounded / leaking output
        return ChatResponse(
            success=False,
            query=user_message,
            answer=output_validation["sanitized_answer"],
            sources=citations,
            retrieval_status="output_blocked",
            model_used=model_name,
            pipeline={
                "input_guardrail": PipelineStageInfo(
                    status="passed",
                    checks=input_validation["checks"],
                ),
                "rag": PipelineStageInfo(
                    status="passed",
                    results_count=len(matched_chunks),
                ),
                "grounding": PipelineStageInfo(
                    status="passed",
                    score=round(best_score, 4),
                    threshold=active_threshold,
                ),
                "llm": PipelineStageInfo(
                    status="completed",
                    model=model_name,
                ),
                "output_guardrail": PipelineStageInfo(
                    status="blocked",
                    reason=output_validation["reason"],
                    checks=output_validation["checks"],
                ),
            }
        )

    # All 4 Pipeline Stages Succeeded!
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    logger.info("Chat pipeline completed successfully in %.2f ms", elapsed_ms)
    record_chat_event(
        query=user_message,
        status="grounded",
        response_time_ms=elapsed_ms,
        sources_count=len(citations),
        best_score=best_score,
        model_used=model_name,
        pipeline_status={"input_guardrail": "passed", "rag": "passed", "grounding": "passed", "llm": "completed", "output_guardrail": "passed"}
    )
    return ChatResponse(
        success=True,
        query=user_message,
        answer=output_validation["sanitized_answer"],
        sources=citations,
        retrieval_status="relevant_context_found",
        model_used=model_name,
        pipeline={
            "input_guardrail": PipelineStageInfo(
                status="passed",
                checks=input_validation["checks"],
            ),
            "rag": PipelineStageInfo(
                status="passed",
                results_count=len(matched_chunks),
            ),
            "grounding": PipelineStageInfo(
                status="passed",
                score=round(best_score, 4),
                threshold=active_threshold,
            ),
            "llm": PipelineStageInfo(
                status="completed",
                model=model_name,
            ),
            "output_guardrail": PipelineStageInfo(
                status="passed",
                checks=output_validation["checks"],
            ),
        }
    )



@router.get(
    "/status",
    summary="Get Chat & Guardrail pipeline configuration status"
)
def chat_status_endpoint():
    return {
        "llm_configured": is_llm_configured(),
        "model": get_gemini_model_name(),
        "provider": "Google Gemini",
        "phase": "5 — Guardrails and AI Safety",
        "guardrails": {
            "max_input_length": DEFAULT_MAX_INPUT_LENGTH,
            "rag_relevance_threshold": RAG_GROUNDING_THRESHOLD,
            "injection_patterns_count": len(INJECTION_PATTERNS),
            "layers": [
                "Layer 1: Input Guardrails (Empty, Length, Prompt Injection Regex)",
                "Layer 2: RAG Grounding Guardrail (Cosine Similarity Cutoff)",
                "Layer 3: LLM Prompt Context Restriction (Strict Grounding Rules)",
                "Layer 4: Output Guardrails (Non-empty, Source Requirement, System Disclosure Check)"
            ]
        }
    }
