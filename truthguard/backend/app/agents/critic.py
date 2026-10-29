import re
import json
from typing import List, Dict, Any, Tuple
from app.agents.llm_client import call_llm_chat
from app.schemas.verification import CriticOutput, SynthesizerOutput
from app.schemas.claims import ClaimEvaluation, ClaimVerdict, Contradiction, ConflictType


def extract_numbers_and_keywords(text: str) -> List[Tuple[str, str]]:
    """
    Extracts policy metrics like ('12', 'casual leave days'), ('15', 'casual leave days').
    """
    results = []
    # Pattern: number followed by terms like days, casual leave, leaves, etc.
    matches = re.finditer(r'\b(\d+)\s+([a-zA-Z\s]{3,25}?(?:leave|days|hours|percent|per\s+year|annually))\b', text, re.IGNORECASE)
    for m in matches:
        num = m.group(1).strip()
        subject = m.group(2).strip().lower()
        results.append((num, subject))
    return results


def critic_verify_answer(
    question: str,
    synthesizer_output: SynthesizerOutput,
    evidence_chunks: List[Dict[str, Any]],
    current_retrieval_count: int = 1
) -> CriticOutput:
    """
    Step 5/6: Adversarial verification of claims, contradiction detection between passages,
    freshness analysis, and determination of whether additional targeted retrieval is required.
    """
    chunk_map = {c["chunk_id"]: c for c in evidence_chunks}

    # Attempt LLM-based Critic if OpenAI key is present
    system_prompt = """You are TruthGuard's Adversarial Critic.
Your role is to challenge the draft answer and compare retrieved passages against each other to identify:
1. Contradictions between passages (e.g. Document A states 12 days while Document B states 15 days).
2. Hierarchy disagreements (e.g. Policy vs Amendment vs FAQ).
3. Unverified or unsupported claims that are not backed by cited passages.
4. Outdated vs newer document status.
Return ONLY valid JSON matching this schema:
{
  "claim_evaluations": [
    {
      "claim_id": "CLAIM_01",
      "verdict": "supported" | "contradicted" | "unsupported" | "unverified",
      "supporting_evidence_ids": ["CHUNK_ID"],
      "contradicting_evidence_ids": ["CHUNK_ID_2"],
      "freshness_or_version_concerns": "Notes on version or date",
      "citation_validity": true,
      "recommended_action": "keep" | "revise" | "dispute" | "eliminate"
    }
  ],
  "contradictions": [
    {
      "contradiction_id": "CONTRA_01",
      "topic": "Casual Leave Entitlement",
      "document_a_id": "DOC_A",
      "document_a_title": "Leave Policy v1",
      "chunk_a_id": "CHUNK_01",
      "value_a": "12 days",
      "document_b_id": "DOC_B",
      "document_b_title": "Leave Amendment v2",
      "chunk_b_id": "CHUNK_02",
      "value_b": "15 days",
      "conflict_type": "value_disagreement",
      "explanation": "Document A states 12 days while Document B states 15 days"
    }
  ],
  "needs_more_retrieval": false,
  "targeted_queries": [],
  "critic_reasoning": "Detailed breakdown"
}
"""
    evidence_summary = "\n\n".join(
        f"[{c['chunk_id']}] File: {c.get('filename')} (v: {c.get('version')}, Status: {c.get('status')})\n{c.get('text')}"
        for c in evidence_chunks
    )
    user_prompt = f"Question: {question}\n\nDraft Answer:\n{synthesizer_output.draft_answer}\n\nClaims:\n" + \
                  "\n".join(f"{cl.claim_id}: {cl.claim_text} (cited: {cl.evidence_ids})" for cl in synthesizer_output.claims) + \
                  f"\n\nAvailable Evidence Passages:\n{evidence_summary}"

    raw_response = call_llm_chat(
        system_prompt=system_prompt,
        user_prompt=user_prompt
    )
    if raw_response:
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
                cleaned = re.sub(r'\s*```$', '', cleaned)
            data = json.loads(cleaned)
            return CriticOutput(**data)
        except Exception:
            pass

    # Deterministic Critic Verification Engine
    contradictions: List[Contradiction] = []
    claim_evaluations: List[ClaimEvaluation] = []
    contra_counter = 1

    # 1. Compare retrieved chunks against each other for conflicting metrics / policy rules
    for i in range(len(evidence_chunks)):
        for j in range(i + 1, len(evidence_chunks)):
            c1 = evidence_chunks[i]
            c2 = evidence_chunks[j]

            # Compare from different documents
            if c1.get("document_id") == c2.get("document_id"):
                continue

            metrics1 = extract_numbers_and_keywords(c1.get("text", ""))
            metrics2 = extract_numbers_and_keywords(c2.get("text", ""))

            for num1, subj1 in metrics1:
                for num2, subj2 in metrics2:
                    # If same topic (e.g. leave days) but different numbers (e.g. 12 vs 15)
                    if num1 != num2 and ("leave" in subj1 and "leave" in subj2):
                        c_type = ConflictType.VALUE_DISAGREEMENT
                        auth1 = c1.get("authority_level", "Policy")
                        auth2 = c2.get("authority_level", "Policy")
                        if "Amendment" in auth1 or "Amendment" in auth2:
                            c_type = ConflictType.AMENDMENT_VS_POLICY
                        elif "FAQ" in auth1 or "FAQ" in auth2:
                            c_type = ConflictType.FAQ_VS_POLICY

                        contra_id = f"CONTRA_{contra_counter:02d}"
                        contradictions.append(
                            Contradiction(
                                contradiction_id=contra_id,
                                topic=f"Casual Leave Entitlement ({subj1.title()})",
                                document_a_id=c1.get("document_id", "DOC_A"),
                                document_a_title=c1.get("filename", "Doc A"),
                                chunk_a_id=c1["chunk_id"],
                                value_a=f"{num1} days ({c1.get('version', 'v1')})",
                                document_b_id=c2.get("document_id", "DOC_B"),
                                document_b_title=c2.get("filename", "Doc B"),
                                chunk_b_id=c2["chunk_id"],
                                value_b=f"{num2} days ({c2.get('version', 'v2')})",
                                conflict_type=c_type,
                                explanation=(
                                    f"'{c1.get('filename')}' ({c1.get('version', 'v1')}) states entitlement is {num1} days, "
                                    f"whereas '{c2.get('filename')}' ({c2.get('version', 'v2')}) states {num2} days."
                                )
                            )
                        )
                        contra_counter += 1

    # 2. Evaluate each claim against available evidence
    for claim in synthesizer_output.claims:
        cited_ids = claim.evidence_ids
        is_supported = False
        contradicting_chunks = []
        supporting_chunks = []

        for c_id in cited_ids:
            if c_id in chunk_map:
                supporting_chunks.append(c_id)
                is_supported = True

        # Check if any contradiction touches this claim
        c_verdict = ClaimVerdict.SUPPORTED if is_supported else ClaimVerdict.UNSUPPORTED
        rec_action = "keep"

        for contra in contradictions:
            if any(cid in cited_ids for cid in [contra.chunk_a_id, contra.chunk_b_id]):
                c_verdict = ClaimVerdict.CONTRADICTED
                rec_action = "dispute"
                if contra.chunk_a_id in cited_ids and contra.chunk_b_id not in contradicting_chunks:
                    contradicting_chunks.append(contra.chunk_b_id)
                elif contra.chunk_b_id in cited_ids and contra.chunk_a_id not in contradicting_chunks:
                    contradicting_chunks.append(contra.chunk_a_id)

        claim_evaluations.append(
            ClaimEvaluation(
                claim_id=claim.claim_id,
                verdict=c_verdict,
                supporting_evidence_ids=supporting_chunks,
                contradicting_evidence_ids=contradicting_chunks,
                freshness_or_version_concerns="Document version or superseding amendment conflict detected" if c_verdict == ClaimVerdict.CONTRADICTED else None,
                citation_validity=len(supporting_chunks) > 0,
                recommended_action=rec_action
            )
        )

    # 3. Determine if targeted retrieval is required (if conflict detected and haven't exceeded retry limit)
    needs_more = False
    targeted_queries: List[str] = []
    if contradictions and current_retrieval_count < 2:
        needs_more = True
        targeted_queries = ["casual leave amendment approval board ratification supersedes", "leave policy effective date"]

    return CriticOutput(
        claim_evaluations=claim_evaluations,
        contradictions=contradictions,
        needs_more_retrieval=needs_more,
        targeted_queries=targeted_queries,
        critic_reasoning=(
            f"Adversarial critic identified {len(contradictions)} cross-document policy contradictions. "
            f"Evaluated {len(claim_evaluations)} claims for factual support."
        )
    )
