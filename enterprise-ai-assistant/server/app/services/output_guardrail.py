"""
services/output_guardrail.py
-----------------------------
Output Guardrail Service for Phase 5: AI Safety & Defense.

WHAT IS AN OUTPUT GUARDRAIL?
----------------------------
Even when input passes and RAG retrieves valid chunks, the LLM output
must be verified before being presented to the user.

Output Guardrails check:
1. Non-empty response validation
2. Strict source evidence attachment (grounded answers must cite at least 1 source)
3. System instruction / internal prompt disclosure prevention
4. Safe fallback enforcement
"""

import re
from typing import List, Dict, Any, Optional

# Patterns indicating potential leakage of internal system instructions
SYSTEM_LEAK_PATTERNS = [
    r"you\s+are\s+an\s+enterprise\s+knowledge\s+assistant",
    r"answer\s+the\s+user['']?s\s+question\s+using\s+only\s+the\s+provided",
    r"rules:\s*1\.\s*ground\s+every\s+statement",
    r"do\s+not\s+mention\s+system\s+instructions",
    r"company\s+knowledge-base\s+context:\s*=====",
    r"grounded\s+answer:",
]

COMPILED_LEAK_REGEX = [
    re.compile(p, re.IGNORECASE) for p in SYSTEM_LEAK_PATTERNS
]


def validate_llm_output(
    generated_answer: str,
    sources: List[Dict[str, Any]],
    require_sources: bool = True
) -> Dict[str, Any]:
    """
    Evaluate the generated LLM response against all Layer 3 output guardrail checks.

    Args:
        generated_answer: The raw string response produced by the LLM.
        sources: List of source chunks retrieved by RAG.
        require_sources: Whether a grounded response strictly requires source evidence.

    Returns:
        Dict:
        {
            "passed": bool,
            "reason": Optional[str],
            "sanitized_answer": str,
            "checks": {
                "non_empty": "passed" | "failed",
                "source_attached": "passed" | "failed",
                "system_prompt_leak": "not_detected" | "detected"
            }
        }
    """
    raw_answer = (generated_answer or "").strip()

    # 1. Non-Empty Check
    if not raw_answer:
        return {
            "passed": False,
            "reason": "LLM returned an empty response.",
            "sanitized_answer": "I couldn't find enough information in the organization's knowledge base to answer that question.",
            "checks": {
                "non_empty": "failed",
                "source_attached": "not_run",
                "system_prompt_leak": "not_run",
            },
        }

    # 2. Source Evidence Requirement
    if require_sources and not sources:
        return {
            "passed": False,
            "reason": "Response lacks required source citations from the knowledge base.",
            "sanitized_answer": "I couldn't find enough information in the organization's knowledge base to answer that question.",
            "checks": {
                "non_empty": "passed",
                "source_attached": "failed",
                "system_prompt_leak": "not_run",
            },
        }

    # 3. System Prompt Disclosure Detection
    for pattern in COMPILED_LEAK_REGEX:
        if pattern.search(raw_answer):
            return {
                "passed": False,
                "reason": "Generated response contained potential system prompt or instruction disclosure.",
                "sanitized_answer": "I can only answer questions using verified company knowledge-base documentation.",
                "checks": {
                    "non_empty": "passed",
                    "source_attached": "passed",
                    "system_prompt_leak": "detected",
                },
            }

    # All Layer 3 checks passed
    return {
        "passed": True,
        "reason": None,
        "sanitized_answer": raw_answer,
        "checks": {
            "non_empty": "passed",
            "source_attached": "passed",
            "system_prompt_leak": "not_detected",
        },
    }
