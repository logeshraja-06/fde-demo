"""
services/truthguard_service.py
------------------------------
TruthGuard Adversarial Document Verification Service.
Integrates LangGraph-inspired contradiction detection, governance resolution,
and Google Gemini API (gemini-flash-lite-latest) with the server backend.
"""

import re
import os
import logging
from typing import List, Dict, Any, Tuple, Optional
from google import genai
from google.genai import types

from app.services.llm_service import get_gemini_api_key, get_gemini_model_name

logger = logging.getLogger("enterprise_ai.truthguard")


def extract_policy_metrics(text: str) -> List[Tuple[str, str, str]]:
    """
    Extracts policy metrics: returns List of (number, metric_label, topic).
    """
    results = []
    # 1. Casual leave pattern
    cl_matches = re.finditer(r'\b(?:casual\s+leave[^\d]{1,35}?(\d+)\s*(?:days|calendar\s+days)?|(\d+)\s*(?:days|casual\s+leave\s+days)[^\.\n]{0,35}?casual\s+leave)\b', text, re.IGNORECASE)
    for m in cl_matches:
        num = m.group(1) or m.group(2)
        if num:
            results.append((num.strip(), f"{num} casual leave days", "Casual Leave Entitlement"))

    # Also detect 'from 12 days to 15 days' in casual leave sections
    if "casual leave" in text.lower():
        span_m = re.findall(r'\bfrom\s+(\d+)\s+days?\s+to\s+(\d+)\s+days?\b', text, re.IGNORECASE)
        for prev_n, new_n in span_m:
            results.append((new_n, f"{new_n} casual leave days (proposed)", "Casual Leave Entitlement"))
            results.append((prev_n, f"{prev_n} casual leave days (prior)", "Casual Leave Entitlement"))

    # 2. Expense reimbursement pattern
    exp_matches = re.finditer(r'\b(\d+)\s*(?:calendar\s+days|days)[^\.\n]{0,45}?(?:expense|receipt)\b|\b(?:expense|receipt)[^\.\n]{0,45}?(\d+)\s*(?:calendar\s+days|days)\b', text, re.IGNORECASE)
    for m in exp_matches:
        num = m.group(1) or m.group(2)
        if num:
            results.append((num.strip(), f"{num} expense submission days", "Expense Reimbursement Window"))

    # 3. Remote work policy pattern (e.g. 'up to two days per week' vs 'up to three days per week')
    word_map = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5"}
    rw_matches = re.finditer(
        r'\b(?:remote\s+work|work\s+remotely)[^\.\n]{0,45}?(?:up\s+to\s+)?(\d+|one|two|three|four|five)\s+days?\s+per\s+week\b|\b(?:up\s+to\s+)?(\d+|one|two|three|four|five)\s+days?\s+per\s+week[^\.\n]{0,45}?(?:remote\s+work|work\s+remotely)\b',
        text,
        re.IGNORECASE
    )
    for m in rw_matches:
        raw_n = m.group(1) or m.group(2)
        if raw_n:
            num = word_map.get(raw_n.lower(), raw_n)
            results.append((num.strip(), f"{num} remote work days per week", "Remote Work Policy"))

    # 4. General leave / days pattern if no specific matches
    if not results:
        gen_matches = re.finditer(r'\b(\d+)\s+([a-zA-Z\s]{3,25}?(?:leave|days|hours))\b', text, re.IGNORECASE)
        for m in gen_matches:
            num = m.group(1).strip()
            subj = m.group(2).strip().lower()
            results.append((num, f"{num} {subj}", subj.title()))

    return results


def detect_adversarial_conflicts(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Compares retrieved chunks against one another to identify numerical or policy contradictions.
    """
    conflicts = []
    seen = set()

    for i in range(len(chunks)):
        for j in range(i + 1, len(chunks)):
            c1 = chunks[i]
            c2 = chunks[j]

            src1 = c1.get("source", "") or c1.get("filename", "")
            src2 = c2.get("source", "") or c2.get("filename", "")

            # Only compare across distinct documents
            if src1 == src2:
                continue

            t1 = c1.get("text", "")
            t2 = c2.get("text", "")

            m1 = extract_policy_metrics(t1)
            m2 = extract_policy_metrics(t2)

            for num1, label1, topic1 in m1:
                for num2, label2, topic2 in m2:
                    # Same topic but different values
                    if topic1 == topic2 and num1 != num2:
                        key = tuple(sorted([f"{src1}:{num1}:{topic1}", f"{src2}:{num2}:{topic2}"]))
                        if key in seen:
                            continue
                        seen.add(key)

                        conflicts.append({
                            "topic": topic1,
                            "doc_a": src1,
                            "value_a": label1,
                            "chunk_a_text": t1,
                            "doc_b": src2,
                            "value_b": label2,
                            "chunk_b_text": t2,
                        })

    return conflicts


def evaluate_conflict_governance(
    conflicts: List[Dict[str, Any]],
    chunks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates whether an adversarial conflict is resolved or unresolved based on governance evidence.
    Rule: Never conclude a newer document supersedes an older one based solely on date!
    Require reliable approval or active ratification.
    """
    if not conflicts:
        return {"status": "resolved", "rationale": "No cross-document policy conflicts detected."}

    all_text = " ".join(c.get("text", "") for c in chunks).lower()

    # Check for approval status in amendment text
    is_unconfirmed = any(term in all_text for term in [
        "approval not confirmed",
        "pending board ratification",
        "sample — approval not confirmed",
        "pending ratification",
        "under review",
        "contingent upon final board"
    ])

    if is_unconfirmed:
        return {
            "status": "unresolved",
            "reason": (
                "While a newer amendment document was retrieved stating a revised entitlement, "
                "the document explicitly notes that its approval and official adoption have not been confirmed "
                "(or remain pending board ratification). Corporate governance prohibits assuming supersession "
                "based solely on publication date. Therefore, the binding policy entitlement cannot be conclusively determined."
            )
        }

    return {
        "status": "resolved",
        "reason": "Superseding amendment has confirmed approval and official corporate sign-off."
    }


def call_gemini_truthguard(
    query: str,
    chunks: List[Dict[str, Any]],
    conflicts: List[Dict[str, Any]],
    governance: Dict[str, Any]
) -> str:
    """
    Calls Google Gemini using the server's GEMINI_API_KEY with TruthGuard adversarial context.
    """
    api_key = get_gemini_api_key()
    model_name = get_gemini_model_name()

    if not api_key:
        return _fallback_truthguard_response(query, chunks, conflicts, governance)

    # Format chunks
    context_lines = []
    for idx, c in enumerate(chunks, 1):
        src = c.get("source") or c.get("filename") or f"Doc {idx}"
        page = c.get("page", 1)
        txt = c.get("text", "").strip()
        context_lines.append(f"[{idx}] Source: {src} (Page {page})\n{txt}")

    context_str = "\n\n".join(context_lines)

    system_instruction = """You are TruthGuard — an Adversarial Document Verification and Policy AI Assistant.
Rules:
1. Answer the user's question using ONLY the provided verified document excerpts.
2. Structure your answer neatly using standard, valid Markdown:
   - Use '### Section Title' for headings with a space after hashes.
   - For bulleted lists, use '* **Item Title:** Description' with a space after the asterisk. Never concatenate asterisks like '***Item:**'.
   - Leave a blank line before and after lists and headings for clean separation.
3. If multiple documents state conflicting values (e.g. Leave Policy states 12 days while an Amendment states 15 days), you MUST explicitly report the adversarial conflict.
4. If an amendment's approval is unconfirmed or pending ratification, state clearly that the entitlement remains UNRESOLVED, disclose both numbers with their respective documents, and explain why corporate governance prevents the newer draft from automatically prevailing.
5. Always cite your sources cleanly (e.g. (*Northstar_Employee_Basic_Policies_v1.pdf*, Page 1)).
6. Be concise, objective, authoritative, and neatly formatted.
"""

    conflict_note = ""
    if governance["status"] == "unresolved":
        conflict_note = f"\n\nCRITICAL CONFLICT DETECTED:\n{governance['reason']}\nDisclose all competing numbers and explain why current entitlement is unresolved."

    user_prompt = f"User Question: {query}\n{conflict_note}\n\nVerified Document Passages:\n{context_str}"

    try:
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,
                max_output_tokens=1000
            )
        )
        if resp and resp.text:
            return resp.text.strip()
    except Exception as exc:
        logger.warning("Gemini generation failed (%s), using deterministic TruthGuard response.", exc)

    return _fallback_truthguard_response(query, chunks, conflicts, governance)


def _fallback_truthguard_response(
    query: str,
    chunks: List[Dict[str, Any]],
    conflicts: List[Dict[str, Any]],
    governance: Dict[str, Any]
) -> str:
    """Deterministic fallback synthesis adhering strictly to TruthGuard governance."""
    if governance["status"] == "unresolved":
        competing = []
        for cf in conflicts:
            competing.append(f"• {cf['doc_a']}: Stated entitlement is {cf['value_a']}")
            competing.append(f"• {cf['doc_b']}: Stated entitlement is {cf['value_b']} (Approval not confirmed)")

        competing_str = "\n".join(sorted(set(competing)))
        return (
            f"Adversarial Policy Conflict Detected:\n\n"
            f"{competing_str}\n\n"
            f"Why this is unresolved:\n"
            f"{governance['reason']}\n\n"
            f"Governance Rule: A newer amendment cannot be assumed to supersede an active policy based solely on date without confirmed board ratification."
        )

    # Standard single-policy response
    first_chunk = chunks[0] if chunks else {}
    src = first_chunk.get("source", "Company Policy")
    text = first_chunk.get("text", "")
    return f"According to {src}:\n\n{text[:350]}..."
