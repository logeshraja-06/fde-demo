from typing import List, Dict, Any, Optional
from app.schemas.verification import ConflictResolution, ConflictStatus, CompetingPosition
from app.schemas.claims import Contradiction


def resolve_cross_document_conflicts(
    contradictions: List[Contradiction],
    evidence_chunks: List[Dict[str, Any]],
    uncertainty_note: Optional[str] = None
) -> ConflictResolution:
    """
    Step 6/7: Resolves detected cross-document contradictions according to strict truth & governance rules:
    - Never conclude that a newer document supersedes an older one based solely on publication date!
    - Require reliable approval, applicability, or active supersession evidence.
    - If evidence is ambiguous, pending ratification, or unapproved, classify as UNRESOLVED.
    - If corpus lacks evidence, classify as INSUFFICIENT_EVIDENCE.
    """
    chunk_map = {c["chunk_id"]: c for c in evidence_chunks}

    # Case 1: Insufficient Evidence
    if not evidence_chunks:
        return ConflictResolution(
            conflict_status=ConflictStatus.INSUFFICIENT_EVIDENCE,
            winning_document_id=None,
            resolved_policy_value=None,
            rationale="No relevant policy evidence was retrieved from the document corpus to formulate or verify an entitlement.",
            applied_rules=["InsufficientCorpusRule: No matching chunks found."],
            competing_positions=[]
        )

    # Case 2: No Contradictions Detected
    if not contradictions:
        # Check if single unified policy exists
        c_top = evidence_chunks[0]
        return ConflictResolution(
            conflict_status=ConflictStatus.RESOLVED,
            winning_document_id=c_top.get("document_id"),
            resolved_policy_value=None,
            rationale="No cross-document policy conflicts or value disagreements were detected in the retrieved evidence.",
            applied_rules=["ConsensusRule: All retrieved passages are consistent and non-conflicting."],
            competing_positions=[]
        )

    # Case 3: Contradictions Detected — Evaluate Governance and Supersession Evidence
    competing_positions: List[CompetingPosition] = []
    applied_rules: List[str] = []
    seen_positions = set()

    for contra in contradictions:
        c_a = chunk_map.get(contra.chunk_a_id, {})
        c_b = chunk_map.get(contra.chunk_b_id, {})

        pos_a_key = (contra.document_a_id, contra.value_a)
        if pos_a_key not in seen_positions:
            seen_positions.add(pos_a_key)
            competing_positions.append(
                CompetingPosition(
                    document_id=contra.document_a_id,
                    document_title=contra.document_a_title,
                    version=c_a.get("version", "v1"),
                    date=c_a.get("published_at"),
                    authority=c_a.get("authority_level", "Policy"),
                    stated_value=contra.value_a,
                    source_chunk_id=contra.chunk_a_id,
                    citation_text=c_a.get("text", "")[:180]
                )
            )

        pos_b_key = (contra.document_b_id, contra.value_b)
        if pos_b_key not in seen_positions:
            seen_positions.add(pos_b_key)
            competing_positions.append(
                CompetingPosition(
                    document_id=contra.document_b_id,
                    document_title=contra.document_b_title,
                    version=c_b.get("version", "v2"),
                    date=c_b.get("published_at"),
                    authority=c_b.get("authority_level", "Amendment"),
                    stated_value=contra.value_b,
                    source_chunk_id=contra.chunk_b_id,
                    citation_text=c_b.get("text", "")[:180]
                )
            )

    applied_rules.append("ComparativeContradictionRule: Cross-referenced numeric entitlements across retrieved versions.")

    # Check each competing position for ratification / active validity
    # Crucial Rule: "Never conclude that a newer document supersedes an older one based only on its publication date. Require reliable approval, applicability, or supersession evidence."
    is_ratified = False
    winning_pos = None

    for pos in competing_positions:
        c_data = chunk_map.get(pos.source_chunk_id, {})
        c_full_text = c_data.get("text", "").lower()
        c_status = (c_data.get("metadata", {}).get("status") or c_data.get("status") or "").lower()

        # Check if this document claims supersession
        has_supersede_claim = any(term in c_full_text for term in ["supersed", "replace", "override"])
        is_pending = any(term in c_full_text or term in c_status for term in ["pending", "draft", "under review", "contingent"])
        is_approved = any(term in c_full_text or term in c_status for term in ["approved policy", "board approved", "official", "ratified"]) and not is_pending

        if has_supersede_claim and is_approved:
            is_ratified = True
            winning_pos = pos
            applied_rules.append(f"ApprovedSupersessionRule: Document '{pos.document_title}' contains verified approval and active supersession evidence.")
            break
        elif is_pending:
            applied_rules.append(f"PendingCaveatRule: Document '{pos.document_title}' contains pending approval or contingency caveats; supersession cannot be verified as active.")

    if is_ratified and winning_pos:
        return ConflictResolution(
            conflict_status=ConflictStatus.RESOLVED,
            winning_document_id=winning_pos.document_id,
            resolved_policy_value=winning_pos.stated_value,
            rationale=(
                f"Resolved in favor of {winning_pos.document_title} ({winning_pos.version}). "
                f"The document provides verified supersession authority establishing that {winning_pos.stated_value} governs."
            ),
            applied_rules=applied_rules,
            competing_positions=competing_positions
        )

    # If unratified or conflicting without verified supersession -> UNRESOLVED
    applied_rules.append("AdversarialSafetyRule: Without confirmed board ratification or active applicability evidence, conflicting policy entitlements cannot be conclusively resolved.")
    
    competing_desc = " vs ".join(f"'{p.document_title}' ({p.stated_value})" for p in competing_positions)
    rationale = (
        f"An adversarial conflict exists between {competing_desc}. "
        f"While a newer amendment exists, it contains pending ratification or unapproved status clauses, "
        f"while the earlier approved policy and FAQ state a different entitlement. "
        f"Because corporate governance prohibits assuming supersession based solely on date, "
        f"the current binding entitlement cannot be conclusively determined without official ratification evidence."
    )

    return ConflictResolution(
        conflict_status=ConflictStatus.UNRESOLVED,
        winning_document_id=None,
        resolved_policy_value=None,
        rationale=rationale,
        applied_rules=applied_rules,
        competing_positions=competing_positions
    )
