import time
import uuid
import logging
from typing import Optional, List
from langgraph.graph import StateGraph, END
from app.graph.state import TruthGuardGraphState
from app.graph.nodes import (
    input_guard_node,
    retrieve_evidence_node,
    synthesize_answer_node,
    output_guard_node,
    critic_verify_node,
    targeted_retrieve_node,
    resolve_conflicts_node,
    citation_guard_node,
    final_response_node
)
from app.schemas.verification import FinalTruthGuardReport, ConflictStatus
from app.database.repository import save_report

logger = logging.getLogger("truthguard.workflow")


def route_after_input_guard(state: TruthGuardGraphState) -> str:
    """Routes to final_response immediately if input guard failed."""
    if not state.get("input_valid", True):
        return "final_response"
    return "retrieve_evidence"


def route_after_output_guard(state: TruthGuardGraphState) -> str:
    """Retries synthesis up to 2 times if output schema validation fails."""
    if not state.get("output_guard_passed", True):
        if state.get("output_retry_count", 0) < 2:
            return "synthesize_answer"
    return "critic_verify"


def route_after_critic(state: TruthGuardGraphState) -> str:
    """Routes to targeted retrieval if adversarial critic requires more evidence (max 2 retries)."""
    if state.get("needs_more_retrieval", False) and state.get("retrieval_count", 1) < 2:
        return "targeted_retrieve"
    return "resolve_conflicts"


def build_truthguard_graph():
    """Assembles and compiles the 9-node TruthGuard LangGraph state machine."""
    workflow = StateGraph(TruthGuardGraphState)

    # Add all 9 nodes
    workflow.add_node("input_guard", input_guard_node)
    workflow.add_node("retrieve_evidence", retrieve_evidence_node)
    workflow.add_node("synthesize_answer", synthesize_answer_node)
    workflow.add_node("output_guard", output_guard_node)
    workflow.add_node("critic_verify", critic_verify_node)
    workflow.add_node("targeted_retrieve", targeted_retrieve_node)
    workflow.add_node("resolve_conflicts", resolve_conflicts_node)
    workflow.add_node("citation_guard", citation_guard_node)
    workflow.add_node("final_response", final_response_node)

    # Set Entry Point
    workflow.set_entry_point("input_guard")

    # Add conditional edges & transitions
    workflow.add_conditional_edges(
        "input_guard",
        route_after_input_guard,
        {
            "final_response": "final_response",
            "retrieve_evidence": "retrieve_evidence"
        }
    )

    workflow.add_edge("retrieve_evidence", "synthesize_answer")
    workflow.add_edge("synthesize_answer", "output_guard")

    workflow.add_conditional_edges(
        "output_guard",
        route_after_output_guard,
        {
            "synthesize_answer": "synthesize_answer",
            "critic_verify": "critic_verify"
        }
    )

    workflow.add_conditional_edges(
        "critic_verify",
        route_after_critic,
        {
            "targeted_retrieve": "targeted_retrieve",
            "resolve_conflicts": "resolve_conflicts"
        }
    )

    workflow.add_edge("targeted_retrieve", "resolve_conflicts")
    workflow.add_edge("resolve_conflicts", "citation_guard")
    workflow.add_edge("citation_guard", "final_response")
    workflow.add_edge("final_response", END)

    return workflow.compile()


# Compile global workflow runner
truthguard_graph = build_truthguard_graph()


def execute_truthguard_workflow(
    question: str,
    user_id: Optional[str] = "default_user",
    permissions: Optional[List[str]] = None,
    document_ids: Optional[List[str]] = None,
    version_filter: Optional[str] = None
) -> FinalTruthGuardReport:
    """
    Executes the full LangGraph workflow and persists the generated audit report.
    """
    query_id = f"QRY_{uuid.uuid4().hex[:10].upper()}"
    start_time = time.time()

    initial_state: TruthGuardGraphState = {
        "question": question,
        "user_id": user_id,
        "permissions": permissions or ["read_all"],
        "document_ids": document_ids,
        "version_filter": version_filter,
        "input_valid": True,
        "input_error": None,
        "retrieval_count": 0,
        "output_retry_count": 0,
        "audit_trail": [],
        "start_time": start_time,
        "evidence_chunks": [],
        "targeted_queries": [],
        "synthesizer_output": None,
        "draft_answer": "",
        "claims": [],
        "output_guard_passed": True,
        "output_guard_errors": [],
        "critic_output": None,
        "claim_evaluations": [],
        "contradictions": [],
        "needs_more_retrieval": False,
        "conflict_resolution": None,
        "conflict_status": ConflictStatus.INSUFFICIENT_EVIDENCE,
        "conflict_explanation": "",
        "resolved_value": None,
        "citation_guard_passed": True,
        "valid_citations": [],
        "invalid_citations": [],
        "final_answer": "",
        "query_id": query_id,
        "execution_time_ms": 0.0
    }

    final_state = truthguard_graph.invoke(initial_state)

    resolution = final_state.get("conflict_resolution")
    competing_positions = resolution.competing_positions if resolution else []

    report = FinalTruthGuardReport(
        query_id=query_id,
        question=question,
        final_answer=final_state.get("final_answer", ""),
        conflict_status=final_state.get("conflict_status", ConflictStatus.INSUFFICIENT_EVIDENCE),
        conflict_explanation=final_state.get("conflict_explanation", ""),
        resolved_value=final_state.get("resolved_value"),
        claim_evaluations=final_state.get("claim_evaluations", []),
        contradictions=final_state.get("contradictions", []),
        competing_positions=competing_positions,
        citations=final_state.get("valid_citations", []),
        audit_trail=final_state.get("audit_trail", []),
        execution_time_ms=final_state.get("execution_time_ms", 0.0)
    )

    # Persist report to database
    try:
        save_report(
            query_id=query_id,
            question=question,
            final_answer=report.final_answer,
            conflict_status=report.conflict_status.value,
            report_dict=report.model_dump()
        )
    except Exception as exc:
        logger.warning(f"Could not persist report to db: {exc}")

    return report
