from typing import TypedDict, List, Dict, Any, Optional
from app.schemas.claims import FactualClaim, ClaimEvaluation, Contradiction
from app.schemas.verification import (
    ConflictStatus,
    SynthesizerOutput,
    CriticOutput,
    ConflictResolution,
    CitationValidation,
    AuditStep
)


class TruthGuardGraphState(TypedDict):
    # Input
    question: str
    user_id: Optional[str]
    permissions: List[str]
    document_ids: Optional[List[str]]
    version_filter: Optional[str]

    # Execution control & retries
    input_valid: bool
    input_error: Optional[str]
    retrieval_count: int
    output_retry_count: int
    audit_trail: List[AuditStep]
    start_time: float

    # Evidence
    evidence_chunks: List[Dict[str, Any]]
    targeted_queries: List[str]

    # Synthesizer
    synthesizer_output: Optional[SynthesizerOutput]
    draft_answer: str
    claims: List[FactualClaim]

    # Output Guard
    output_guard_passed: bool
    output_guard_errors: List[str]

    # Critic
    critic_output: Optional[CriticOutput]
    claim_evaluations: List[ClaimEvaluation]
    contradictions: List[Contradiction]
    needs_more_retrieval: bool

    # Conflict Resolver
    conflict_resolution: Optional[ConflictResolution]
    conflict_status: ConflictStatus
    conflict_explanation: str
    resolved_value: Optional[str]

    # Citation Guard
    citation_guard_passed: bool
    valid_citations: List[CitationValidation]
    invalid_citations: List[CitationValidation]

    # Final Output
    final_answer: str
    query_id: str
    execution_time_ms: float
