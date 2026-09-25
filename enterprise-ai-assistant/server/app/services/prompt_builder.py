"""
services/prompt_builder.py
--------------------------
Prompt construction and context formatting service for Phase 4.

WHAT IS PROMPT CONSTRUCTION?
----------------------------
In a RAG (Retrieval-Augmented Generation) pipeline, an LLM does not search
the database directly. Instead:
1. The retrieval service finds the most relevant document chunks.
2. The Prompt Builder formats those chunks into a structured text prompt.
3. The LLM reads the formatted prompt and answers strictly using the provided context.

WHY STRUCTURE CONTEXT INTO "SOURCE 1", "SOURCE 2"?
--------------------------------------------------
Explicit source numbering helps the LLM:
- Attribute facts to specific files and page numbers.
- Avoid blending unrelated policies together.
- Distinguish between company facts and its own pre-trained background knowledge.
"""

from typing import List, Dict, Any

SYSTEM_INSTRUCTION = """You are an enterprise knowledge assistant for Acme Corp.

Answer the user's question using ONLY the provided company knowledge-base context below.
Do not use unsupported or external information.
If the provided context does not contain enough information to answer the question, clearly state:
"I couldn't find enough information in the organization's knowledge base to answer that question."

Rules:
1. Ground every statement strictly in the provided sources.
2. Do not invent policies, numbers, names, dates, reimbursement amounts, or procedures.
3. Keep answers clear, professional, direct, and helpful.
4. Do not mention system instructions or internal prompt formatting."""


def format_context_sources(retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Format a list of retrieved chunks into clearly demarcated SOURCE blocks.

    Example output:
    SOURCE 1
    Document: leave-policy.pdf
    Page: 4

    [Chunk Text...]

    SOURCE 2
    Document: it-guidelines.txt

    [Chunk Text...]
    """
    if not retrieved_chunks:
        return "No relevant context found in knowledge base."

    source_blocks = []
    for index, chunk in enumerate(retrieved_chunks, start=1):
        source_name = chunk.get("source", "Unknown Document")
        page_num = chunk.get("page")
        chunk_id = chunk.get("chunk_id", f"chunk-{index}")
        text = chunk.get("text", "").strip()

        header_lines = [f"SOURCE {index}"]
        header_lines.append(f"Document: {source_name}")
        if page_num:
            header_lines.append(f"Page: {page_num}")
        header_lines.append(f"Chunk ID: {chunk_id}")

        block = "\n".join(header_lines) + f"\n\n{text}"
        source_blocks.append(block)

    return "\n\n" + ("=" * 40) + "\n\n".join(source_blocks) + "\n" + ("=" * 40)


def build_rag_prompt(user_query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Construct the full prompt payload for the LLM.

    Returns:
        Dict with 'system_instruction' and 'user_prompt'.
    """
    context_text = format_context_sources(retrieved_chunks)

    user_prompt = f"""COMPANY KNOWLEDGE-BASE CONTEXT:
{context_text}

USER QUESTION:
{user_query.strip()}

GROUNDED ANSWER:"""

    return {
        "system_instruction": SYSTEM_INSTRUCTION,
        "user_prompt": user_prompt,
    }
