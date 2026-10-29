import pytest
from app.schemas.claims import Contradiction, ConflictType
from app.schemas.verification import ConflictStatus
from app.agents.resolver import resolve_cross_document_conflicts


def test_resolve_conflicts_unresolved_when_amendment_is_pending():
    contradictions = [
        Contradiction(
            contradiction_id="CONTRA_01",
            topic="Casual Leave Entitlement",
            document_a_id="DOC_POLICY_V1",
            document_a_title="Leave Policy v1.0",
            chunk_a_id="CHUNK_V1_001",
            value_a="12 days (v1)",
            document_b_id="DOC_AMENDMENT_V2",
            document_b_title="Leave Amendment v2.0",
            chunk_b_id="CHUNK_V2_001",
            value_b="15 days (v2)",
            conflict_type=ConflictType.AMENDMENT_VS_POLICY,
            explanation="Document A states 12 days, Document B states 15 days."
        )
    ]
    evidence_chunks = [
        {
            "chunk_id": "CHUNK_V1_001",
            "document_id": "DOC_POLICY_V1",
            "filename": "leave_policy_v1.txt",
            "version": "v1.0",
            "status": "Approved Policy",
            "authority_level": "Policy",
            "text": "Employees are entitled to 12 casual leave days per year."
        },
        {
            "chunk_id": "CHUNK_V2_001",
            "document_id": "DOC_AMENDMENT_V2",
            "filename": "leave_amendment_v2.docx",
            "version": "v2.0",
            "status": "Pending Board Ratification / Draft",
            "authority_level": "Amendment",
            "text": "Employees are entitled to 15 casual leave days per year. Scheduled to supersede Leave Policy v1.0 contingent upon final Board sign-off on April 1, 2025."
        }
    ]

    resolution = resolve_cross_document_conflicts(contradictions, evidence_chunks)

    # Must classify as UNRESOLVED because v2 is pending board ratification
    assert resolution.conflict_status == ConflictStatus.UNRESOLVED
    assert resolution.winning_document_id is None
    assert len(resolution.competing_positions) == 2
    assert "PendingCaveatRule" in str(resolution.applied_rules)


def test_resolve_conflicts_resolved_when_amendment_is_approved():
    contradictions = [
        Contradiction(
            contradiction_id="CONTRA_01",
            topic="Casual Leave Entitlement",
            document_a_id="DOC_POLICY_V1",
            document_a_title="Leave Policy v1.0",
            chunk_a_id="CHUNK_V1_001",
            value_a="12 days (v1)",
            document_b_id="DOC_AMENDMENT_V2",
            document_b_title="Leave Amendment v2.0",
            chunk_b_id="CHUNK_V2_001",
            value_b="15 days (v2)",
            conflict_type=ConflictType.AMENDMENT_VS_POLICY,
            explanation="Document A states 12 days, Document B states 15 days."
        )
    ]
    evidence_chunks = [
        {
            "chunk_id": "CHUNK_V1_001",
            "document_id": "DOC_POLICY_V1",
            "filename": "leave_policy_v1.txt",
            "version": "v1.0",
            "status": "Approved Policy",
            "authority_level": "Policy",
            "text": "Employees are entitled to 12 casual leave days per year."
        },
        {
            "chunk_id": "CHUNK_V2_001",
            "document_id": "DOC_AMENDMENT_V2",
            "filename": "leave_amendment_v2.docx",
            "version": "v2.0",
            "status": "Approved Policy",
            "authority_level": "Amendment",
            "text": "Employees are entitled to 15 casual leave days per year. Officially ratified and approved policy superseding all prior policies."
        }
    ]

    resolution = resolve_cross_document_conflicts(contradictions, evidence_chunks)

    # Now it must resolve to v2 because it is ratified and approved
    assert resolution.conflict_status == ConflictStatus.RESOLVED
    assert resolution.winning_document_id == "DOC_AMENDMENT_V2"
    assert resolution.resolved_policy_value is not None and "15 days" in resolution.resolved_policy_value
