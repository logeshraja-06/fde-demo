"""
services/input_guardrail.py
----------------------------
Input Guardrail Service for Phase 5: AI Safety & Defense.

WHAT IS AN INPUT GUARDRAIL?
---------------------------
An input guardrail is the first defensive perimeter in an AI application.
Before spending computation on RAG retrieval or sending tokens to an LLM,
the input guardrail inspects the user's prompt for:
1. Empty or whitespace-only queries
2. Excessively large payloads (preventing DoS / buffer issues)
3. Obvious adversarial Prompt Injections & Jailbreak attempts

WHY DETERMINISTIC CHECKS FIRST?
-------------------------------
Deterministic regex / pattern checks run in microseconds (<1ms) locally on CPU
with zero API cost. If an attack is caught at Layer 1, RAG and LLM are NEVER called.

IMPORTANT NOTE:
Keyword matching is a practical first-layer demo defense. It reduces common
injection risks, but enterprise security combines this with multi-layered defenses.
"""

import os
import re
from typing import Dict, Any

# ── Configurable Constants ───────────────────────────────────────────────────
# Can be overridden via environment variables
DEFAULT_MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "2000"))
DEFAULT_MIN_INPUT_LENGTH = 1

# Common prompt injection, jailbreak, and system instruction override patterns
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+|your\s+|the\s+|previous\s+|prior\s+|above\s+)*(instructions|rules|prompts)",
    r"disregard\s+(all\s+|your\s+|the\s+|previous\s+|prior\s+|above\s+)*(instructions|rules|prompts|filters|guardrails)",
    r"reveal\s+(your\s+|the\s+)?((hidden|system|developer|internal)\s+)+(prompt|instructions|rules|message)",
    r"show\s+(me\s+)?(your\s+|the\s+)?((hidden|system|developer|internal)\s+)+(prompt|instructions|rules|message)",
    r"tell\s+(me\s+)?(your\s+|the\s+)?((hidden|system|developer|internal)\s+)+(prompt|instructions|rules|message)",
    r"reveal\s+hidden\s+instructions",
    r"disregard\s+your\s+rules",
    r"disregard\s+your\s+instructions",
    r"developer\s+(message|mode)",
    r"(override|bypass|disregard|ignore)\s+.*?(assistant['']?s\s+)?(operating|system)\s+instructions",
    r"what\s+are\s+your\s+(system|hidden|developer|internal)\s+(instructions|prompts)",
    r"developer\s+mode\s+(enabled|on|activate)",
    r"bypass\s+(safety|guardrails|filters|rules)",
    r"override\s+(system|operating)\s+instructions",
    r"print\s+(the\s+)?(system\s+prompt|hidden\s+instructions)",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"repeat\s+the\s+words\s+above",
]

# Compile patterns for fast sub-millisecond evaluation
COMPILED_INJECTION_REGEX = [
    re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS
]


def validate_user_input(
    user_input: str,
    max_length: int = DEFAULT_MAX_INPUT_LENGTH
) -> Dict[str, Any]:
    """
    Evaluate user input against all Layer 1 input guardrail checks.

    Args:
        user_input: Raw string received from the user / client.
        max_length: Maximum allowed character length.

    Returns:
        Dict:
        {
            "passed": bool,
            "reason": Optional[str],
            "checks": {
                "empty_check": "passed" | "failed",
                "length_check": "passed" | "failed",
                "prompt_injection": "not_detected" | "detected"
            },
            "matched_pattern": Optional[str]
        }
    """
    raw_text = user_input if user_input is not None else ""
    cleaned = raw_text.strip()

    # 1. Empty / Whitespace Check
    if not cleaned:
        return {
            "passed": False,
            "reason": "Input message cannot be empty or whitespace only.",
            "checks": {
                "empty_check": "failed",
                "length_check": "not_run",
                "prompt_injection": "not_run",
            },
            "matched_pattern": None,
        }

    # 2. Length Validation
    if len(cleaned) > max_length:
        return {
            "passed": False,
            "reason": f"Input exceeds maximum allowed length of {max_length} characters (received {len(cleaned)}).",
            "checks": {
                "empty_check": "passed",
                "length_check": "failed",
                "prompt_injection": "not_run",
            },
            "matched_pattern": None,
        }

    # 3. Prompt Injection & Jailbreak Detection
    for pattern in COMPILED_INJECTION_REGEX:
        match = pattern.search(cleaned)
        if match:
            return {
                "passed": False,
                "reason": "Potential prompt injection detected",
                "checks": {
                    "empty_check": "passed",
                    "length_check": "passed",
                    "prompt_injection": "detected",
                },
                "matched_pattern": match.group(0),
            }

    # All Layer 1 checks passed
    return {
        "passed": True,
        "reason": None,
        "checks": {
            "empty_check": "passed",
            "length_check": "passed",
            "prompt_injection": "not_detected",
        },
        "matched_pattern": None,
    }
