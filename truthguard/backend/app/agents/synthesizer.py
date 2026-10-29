import json
import re
from typing import List, Dict, Any
from app.agents.llm_client import call_llm_chat
from app.schemas.verification import SynthesizerOutput
from app.schemas.claims import FactualClaim


def synthesize_draft_answer(
    question: str,
    evidence_chunks: List[Dict[str, Any]]
) -> SynthesizerOutput:
    """
    Step 4/5: Synthesizes a draft answer decomposed into individual factual claims with evidence IDs.
    """
    if not evidence_chunks:
        return SynthesizerOutput(
            draft_answer="No relevant documents or policy passages were found in the uploaded corpus to answer this question.",
            claims=[],
            uncertainty="No evidence retrieved from document store."
        )

    # Format evidence blocks for prompt
    evidence_blocks = []
    for c in evidence_chunks:
        c_id = c["chunk_id"]
        fn = c.get("filename", "unknown")
        ver = c.get("version", "unknown")
        sec = c.get("section", "unknown")
        page = c.get("page_number", 1)
        txt = c.get("text", "").strip()
        evidence_blocks.append(f"[{c_id}] (File: {fn}, Version: {ver}, Section: {sec}, Page: {page})\n{txt}")

    context_str = "\n\n".join(evidence_blocks)

    system_prompt = """You are TruthGuard's Synthesizer agent.
Your objective:
1. Answer the user's question using ONLY the provided evidence passages.
2. Decompose your draft answer into individual factual claims.
3. Every claim MUST link to the specific chunk ID(s) where that fact was stated.
4. If different documents state conflicting facts, report the positions objectively.
5. Return ONLY a valid JSON object matching this schema:
{
  "draft_answer": "Complete readable draft answer citing [CHUNK_ID] inline",
  "claims": [
    {
      "claim_id": "CLAIM_01",
      "claim_text": "Discrete factual assertion",
      "evidence_ids": ["CHUNK_ID_001"]
    }
  ],
  "uncertainty": "Any missing information or ambiguity noted"
}
"""

    user_prompt = f"Question: {question}\n\nEvidence Passages:\n{context_str}"

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
            return SynthesizerOutput(**data)
        except Exception:
            pass

    # Deterministic local synthesizer
    # Extracts factual sentences from top chunks
    claims: List[FactualClaim] = []
    draft_parts = []
    claim_count = 1

    for c in evidence_chunks[:4]:
        c_id = c["chunk_id"]
        c_text = c.get("text", "")
        fn = c.get("filename", "")
        ver = c.get("version", "")
        # Look for sentences containing key numbers, leaves, days, or rules
        sentences = [s.strip() for s in re.split(r'(?<=\.)\s+', c_text) if s.strip()]
        for s in sentences:
            if any(term in s.lower() for term in ["entitled", "leave", "day", "policy", "amendment", "receive", "require", "rule"]):
                claim_id = f"CLAIM_{claim_count:02d}"
                claims.append(
                    FactualClaim(
                        claim_id=claim_id,
                        claim_text=s,
                        evidence_ids=[c_id]
                    )
                )
                draft_parts.append(f"{s} [{c_id}]")
                claim_count += 1
                if claim_count > 6:
                    break
        if claim_count > 6:
            break

    if not draft_parts:
        # Fallback to entire first chunk text
        c_first = evidence_chunks[0]
        claim_id = "CLAIM_01"
        claims.append(
            FactualClaim(
                claim_id=claim_id,
                claim_text=c_first.get("text", "")[:200],
                evidence_ids=[c_first["chunk_id"]]
            )
        )
        draft_parts.append(f"{c_first.get('text', '')[:200]} [{c_first['chunk_id']}]")

    draft_answer = " ".join(draft_parts)
    return SynthesizerOutput(
        draft_answer=draft_answer,
        claims=claims,
        uncertainty=None
    )
