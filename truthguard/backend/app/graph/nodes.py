import time
from typing import Dict, Any
from app.graph.state import TruthGuardGraphState
from app.guards.input_guard import validate_user_input
from app.guards.output_guard import validate_synthesizer_output
from app.guards.citation_guard import validate_citations
from app.retrieval.vector_store import search_evidence
from app.agents.synthesizer import synthesize_draft_answer
from app.agents.critic import critic_verify_answer
from app.agents.resolver import resolve_cross_document_conflicts
from app.schemas.verification import (
    ConflictStatus,
    AuditStep,
    SynthesizerOutput
)


def input_guard_node(state: TruthGuardGraphState) -> Dict[str, Any]:
    """Node 1: Validates question against prompt injection, emptiness, and length limits."""
    t0 = time.time()
    valid, err = validate_user_input(state["question"])
    duration = (time.time() - t0) * 1000

    audit = list(state.get("audit_trail", []))
    audit.append(
        AuditStep(
            node="input_guard",
            status="PASSED" if valid else "FAILED",
            details={"error": err} if err else {"input_length": len(state["question"])},
            duration_ms=round(duration, 2)
        )
    )

    return {
        "input_valid": valid,
        "input_error": err,
        "audit_trail": audit
    }


def retrieve_evidence_node(state: TruthGuardGraphState) -> Dict[str, Any]:
    """Node 2: Retrieves relevant evidence passages using hybrid vector + keyword search."""
    t0 = time.time()
    evidence = search_evidence(
        query=state["question"],
        document_ids=state.get("document_ids"),
        version_filter=state.get("version_filter")
    )
    duration = (time.time() - t0) * 1000

    audit = list(state.get("audit_trail", []))
    audit.append(
        AuditStep(
            node="retrieve_evidence",
            status="PASSED" if evidence else "NO_CHUNKS_FOUND",
            details={"retrieved_count": len(evidence), "retrieval_pass": 1},
            duration_ms=round(duration, 2)
        )
    )

    return {
        "evidence_chunks": evidence,
        "retrieval_count": 1,
        "audit_trail": audit
    }


def synthesize_answer_node(state: TruthGuardGraphState) -> Dict[str, Any]:
    """Node 3: LLM Synthesizer decomposes answer into structured claims with evidence IDs."""
    t0 = time.time()
    output = synthesize_draft_answer(
        question=state["question"],
        evidence_chunks=state.get("evidence_chunks", [])
    )
    duration = (time.time() - t0) * 1000

    audit = list(state.get("audit_trail", []))
    audit.append(
        AuditStep(
            node="synthesize_answer",
            status="SUCCESS",
            details={"claim_count": len(output.claims)},
            duration_ms=round(duration, 2)
        )
    )

    return {
        "synthesizer_output": output,
        "draft_answer": output.draft_answer,
        "claims": output.claims,
        "audit_trail": audit
    }


def output_guard_node(state: TruthGuardGraphState) -> Dict[str, Any]:
    """Node 4: Validates synthesizer JSON structure via Pydantic / Guardrails rules."""
    t0 = time.time()
    synth_output = state.get("synthesizer_output")
    passed, errors, validated = validate_synthesizer_output(synth_output)
    duration = (time.time() - t0) * 1000

    audit = list(state.get("audit_trail", []))
    audit.append(
        AuditStep(
            node="output_guard",
            status="PASSED" if passed else "FAILED",
            details={"validation_errors": errors} if errors else {"claims_verified": len(synth_output.claims if synth_output else [])},
            duration_ms=round(duration, 2)
        )
    )

    retry_count = state.get("output_retry_count", 0)
    if not passed:
        retry_count += 1

    return {
        "output_guard_passed": passed,
        "output_guard_errors": errors,
        "output_retry_count": retry_count,
        "audit_trail": audit
    }


def critic_verify_node(state: TruthGuardGraphState) -> Dict[str, Any]:
    """Node 5: Adversarial Critic compares passages, detects contradictions, challenges claims."""
    t0 = time.time()
    synth_output = state.get("synthesizer_output") or SynthesizerOutput(draft_answer="", claims=[])
    critic_out = critic_verify_answer(
        question=state["question"],
        synthesizer_output=synth_output,
        evidence_chunks=state.get("evidence_chunks", []),
        current_retrieval_count=state.get("retrieval_count", 1)
    )
    duration = (time.time() - t0) * 1000

    audit = list(state.get("audit_trail", []))
    audit.append(
        AuditStep(
            node="critic_verify",
            status="DISPUTES_FOUND" if critic_out.contradictions else "VERIFIED_CLEAN",
            details={
                "contradictions_count": len(critic_out.contradictions),
                "needs_targeted_retrieval": critic_out.needs_more_retrieval
            },
            duration_ms=round(duration, 2)
        )
    )

    return {
        "critic_output": critic_out,
        "claim_evaluations": critic_out.claim_evaluations,
        "contradictions": critic_out.contradictions,
        "needs_more_retrieval": critic_out.needs_more_retrieval,
        "targeted_queries": critic_out.targeted_queries,
        "audit_trail": audit
    }


def targeted_retrieve_node(state: TruthGuardGraphState) -> Dict[str, Any]:
    """Node 6: Conducts targeted search for supersession or approval evidence."""
    t0 = time.time()
    current_evidence = list(state.get("evidence_chunks", []))
    existing_chunk_ids = {c["chunk_id"] for c in current_evidence}

    targeted_queries = state.get("targeted_queries", [])
    new_chunks = []
    for q in targeted_queries:
        found = search_evidence(query=q, top_k=3)
        for c in found:
            if c["chunk_id"] not in existing_chunk_ids:
                existing_chunk_ids.add(c["chunk_id"])
                new_chunks.append(c)

    combined_evidence = current_evidence + new_chunks
    duration = (time.time() - t0) * 1000

    audit = list(state.get("audit_trail", []))
    audit.append(
        AuditStep(
            node="targeted_retrieve",
            status="SUCCESS",
            details={
                "new_chunks_added": len(new_chunks),
                "total_evidence_count": len(combined_evidence),
                "retrieval_pass": state.get("retrieval_count", 1) + 1
            },
            duration_ms=round(duration, 2)
        )
    )

    return {
        "evidence_chunks": combined_evidence,
        "retrieval_count": state.get("retrieval_count", 1) + 1,
        "needs_more_retrieval": False,
        "audit_trail": audit
    }


def resolve_conflicts_node(state: TruthGuardGraphState) -> Dict[str, Any]:
    """Node 7: Evaluates contradictions using strict governance, version, and supersession rules."""
    t0 = time.time()
    synth = state.get("synthesizer_output")
    synth_output = synth if synth is not None else SynthesizerOutput(draft_answer="")
    resolution = resolve_cross_document_conflicts(
        contradictions=state.get("contradictions", []),
        evidence_chunks=state.get("evidence_chunks", []),
        uncertainty_note=synth_output.uncertainty
    )
    duration = (time.time() - t0) * 1000

    audit = list(state.get("audit_trail", []))
    audit.append(
        AuditStep(
            node="resolve_conflicts",
            status=resolution.conflict_status.value.upper(),
            details={
                "conflict_status": resolution.conflict_status.value,
                "winning_document": resolution.winning_document_id,
                "applied_rules_count": len(resolution.applied_rules)
            },
            duration_ms=round(duration, 2)
        )
    )

    return {
        "conflict_resolution": resolution,
        "conflict_status": resolution.conflict_status,
        "conflict_explanation": resolution.rationale,
        "resolved_value": resolution.resolved_policy_value,
        "audit_trail": audit
    }


def citation_guard_node(state: TruthGuardGraphState) -> Dict[str, Any]:
    """Node 8: Validates all citations against stored evidence chunks."""
    t0 = time.time()
    all_cited_ids = []
    for cl in state.get("claims", []):
        all_cited_ids.extend(cl.evidence_ids)

    passed, valid_cits, invalid_cits = validate_citations(
        cited_chunk_ids=all_cited_ids,
        available_chunks=state.get("evidence_chunks", [])
    )
    duration = (time.time() - t0) * 1000

    audit = list(state.get("audit_trail", []))
    audit.append(
        AuditStep(
            node="citation_guard",
            status="PASSED" if passed else "FAILED",
            details={
                "valid_citations": len(valid_cits),
                "invalid_citations": len(invalid_cits)
            },
            duration_ms=round(duration, 2)
        )
    )

    return {
        "citation_guard_passed": passed,
        "valid_citations": valid_cits,
        "invalid_citations": invalid_cits,
        "audit_trail": audit
    }


def final_response_node(state: TruthGuardGraphState) -> Dict[str, Any]:
    """Node 9: Assembles the verified answer, conflict explanation, and citations."""
    t0 = time.time()
    start_t = state.get("start_time", t0)
    exec_time = (time.time() - start_t) * 1000

    # If input guard failed
    if not state.get("input_valid", True):
        audit = list(state.get("audit_trail", []))
        audit.append(
            AuditStep(
                node="final_response",
                status="REJECTED",
                details={"reason": state.get("input_error")},
                duration_ms=round((time.time() - t0) * 1000, 2)
            )
        )
        return {
            "final_answer": f"Request Rejected: {state.get('input_error')}",
            "conflict_status": ConflictStatus.INSUFFICIENT_EVIDENCE,
            "conflict_explanation": state.get("input_error", "Input rejected by guardrail."),
            "execution_time_ms": round(exec_time, 2),
            "audit_trail": audit
        }

    status = state.get("conflict_status", ConflictStatus.INSUFFICIENT_EVIDENCE)
    resolution = state.get("conflict_resolution")
    explanation = state.get("conflict_explanation", "")

    # Build final response text based on conflict status
    if status == ConflictStatus.RESOLVED:
        if resolution and resolution.resolved_policy_value:
            final_text = (
                f"Verified Answer: {resolution.resolved_policy_value}. "
                f"\n\nGovernance Note: {explanation}"
            )
        else:
            final_text = state.get("draft_answer", "Information verified against document corpus.")
    elif status == ConflictStatus.UNRESOLVED:
        positions_str = ""
        if resolution and resolution.competing_positions:
            pos_lines = [
                f"• {p.document_title} ({p.version or 'v?'}, {p.date or 'Date unrecorded'}): Stated value = {p.stated_value}"
                for p in resolution.competing_positions
            ]
            positions_str = "\n" + "\n".join(pos_lines) + "\n\n"

        final_text = (
            f"Adversarial Policy Conflict Detected:\n"
            f"{positions_str}"
            f"Why this is unresolved:\n{explanation}\n\n"
            f"Adversarial Governance Rule: A newer document cannot be assumed to supersede an active policy without verified board ratification or official effective sign-off."
        )
    else:  # INSUFFICIENT_EVIDENCE
        final_text = (
            "Insufficient Document Evidence: "
            "The uploaded document corpus does not contain reliable or conclusive policy statements to answer this question."
        )

    audit = list(state.get("audit_trail", []))
    audit.append(
        AuditStep(
            node="final_response",
            status="COMPLETED",
            details={"verdict": status.value, "total_execution_ms": round(exec_time, 2)},
            duration_ms=round((time.time() - t0) * 1000, 2)
        )
    )

    return {
        "final_answer": final_text,
        "conflict_status": status,
        "conflict_explanation": explanation,
        "execution_time_ms": round(exec_time, 2),
        "audit_trail": audit
    }
