from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ClaimVerdict(str, Enum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    UNSUPPORTED = "unsupported"
    UNVERIFIED = "unverified"


class FactualClaim(BaseModel):
    claim_id: str = Field(description="Unique claim identifier, e.g. CLAIM_01")
    claim_text: str = Field(description="The discrete factual assertion made in the draft answer")
    evidence_ids: List[str] = Field(default_factory=list, description="IDs of chunk evidence supporting this claim")


class ClaimEvaluation(BaseModel):
    claim_id: str
    verdict: ClaimVerdict
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    contradicting_evidence_ids: List[str] = Field(default_factory=list)
    freshness_or_version_concerns: Optional[str] = None
    citation_validity: bool = True
    recommended_action: str = Field(description="Action: keep, revise, dispute, or eliminate")


class ConflictType(str, Enum):
    VALUE_DISAGREEMENT = "value_disagreement"
    AMENDMENT_VS_POLICY = "amendment_vs_policy"
    FAQ_VS_POLICY = "faq_vs_policy"
    VERSION_MISSING = "version_missing"
    AUTHORITATIVE_DISPUTE = "authoritative_dispute"


class Contradiction(BaseModel):
    contradiction_id: str
    topic: str
    document_a_id: str
    document_a_title: str
    chunk_a_id: str
    value_a: str
    document_b_id: str
    document_b_title: str
    chunk_b_id: str
    value_b: str
    conflict_type: ConflictType
    explanation: str
