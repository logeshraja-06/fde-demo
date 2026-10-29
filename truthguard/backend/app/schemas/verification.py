from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.claims import FactualClaim, ClaimEvaluation, Contradiction


class ConflictStatus(str, Enum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class SynthesizerOutput(BaseModel):
    draft_answer: str = Field(description="Structured answer with factual claims")
    claims: List[FactualClaim] = Field(default_factory=list)
    uncertainty: Optional[str] = None


class CriticOutput(BaseModel):
    claim_evaluations: List[ClaimEvaluation] = Field(default_factory=list)
    contradictions: List[Contradiction] = Field(default_factory=list)
    needs_more_retrieval: bool = False
    targeted_queries: List[str] = Field(default_factory=list)
    critic_reasoning: str = ""


class CompetingPosition(BaseModel):
    document_id: str
    document_title: str
    version: Optional[str] = None
    date: Optional[str] = None
    authority: Optional[str] = None
    stated_value: str
    source_chunk_id: str
    citation_text: str


class ConflictResolution(BaseModel):
    conflict_status: ConflictStatus
    winning_document_id: Optional[str] = None
    resolved_policy_value: Optional[str] = None
    rationale: str
    applied_rules: List[str] = Field(default_factory=list)
    competing_positions: List[CompetingPosition] = Field(default_factory=list)


class CitationValidation(BaseModel):
    citation_id: str
    chunk_id: str
    document_id: str
    source_filename: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    exists_in_db: bool = True
    matches_context: bool = True
    excerpt: str = ""


class AuditStep(BaseModel):
    node: str
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: float = 0.0


class FinalTruthGuardReport(BaseModel):
    query_id: str
    question: str
    final_answer: str
    conflict_status: ConflictStatus
    conflict_explanation: str
    resolved_value: Optional[str] = None
    claim_evaluations: List[ClaimEvaluation] = Field(default_factory=list)
    contradictions: List[Contradiction] = Field(default_factory=list)
    competing_positions: List[CompetingPosition] = Field(default_factory=list)
    citations: List[CitationValidation] = Field(default_factory=list)
    audit_trail: List[AuditStep] = Field(default_factory=list)
    execution_time_ms: float = 0.0
