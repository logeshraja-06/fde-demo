"""
services/chunker.py
--------------------
The chunking service. Takes a long string of text and splits it into
smaller, overlapping pieces called "chunks".

WHY DO WE CHUNK?
----------------
Language models (LLMs) and embedding models have a maximum input size,
often around 512 or 8192 tokens (~words). A full company document might
be 50,000 characters long. We cannot feed the entire thing to an LLM at once.

Instead, we split it into manageable pieces. When a user asks a question,
we will (in Phase 3) search only the most relevant chunks instead of
sending the entire document.

WHY DOES OVERLAP EXIST?
-----------------------
Imagine this text:
  "... the employee must submit a claim within 30 days. Claims submitted
   after 30 days will not be reimbursed ..."

If we split right at "30 days.", the second chunk begins with
"Claims submitted after 30 days..." — which is grammatically complete.

But if the split happened mid-sentence, the second chunk would start
without context. Overlap solves this: the end of chunk 1 is repeated
at the start of chunk 2, so no sentence loses its context.

EXAMPLE:
  Text: "ABCDE FGHIJ KLMNO"
  chunk_size=10, overlap=3:
    Chunk 1: "ABCDE FGHI"
    Chunk 2: "GHI KLMNO"     ← "GHI" is repeated from chunk 1
"""

import re

# ── Configuration Constants ──────────────────────────────────────────────────
# Changing these two numbers changes the behaviour of the entire pipeline.
# We define them once here so there is a single place to tune them.

CHUNK_SIZE = 800      # Maximum characters per chunk
CHUNK_OVERLAP = 100   # Characters repeated at the boundary between chunks

# Minimum characters needed to create a chunk — prevents empty/trivial chunks
MIN_CHUNK_LENGTH = 50


def create_chunks(text: str, document_slug: str) -> list[dict]:
    """
    Split a long text string into overlapping chunks.

    Args:
        text:          The full cleaned text of the document.
        document_slug: A URL-safe version of the filename used to build chunk IDs
                       e.g. "leave-policy" → chunks get IDs "leave-policy-001", etc.

    Returns:
        A list of dicts, each with:
          { "id": "leave-policy-001", "text": "..." }

    Algorithm:
        We use a simple sliding-window approach:
        1. Start at position 0.
        2. Take CHUNK_SIZE characters → that is one chunk.
        3. Move forward by (CHUNK_SIZE - CHUNK_OVERLAP) characters.
        4. Repeat until we reach the end of the text.

        We try to break at sentence boundaries (". ") so chunks feel natural.
    """
    if not text or not text.strip():
        return []

    chunks = []
    start = 0
    chunk_number = 1

    while start < len(text):
        end = start + CHUNK_SIZE

        # If we're not at the very end of the document, try to find a
        # sentence boundary near the end of our window to cut cleanly.
        if end < len(text):
            # Look for a period followed by a space in the last 200 chars of the window
            boundary = text.rfind('. ', start + CHUNK_SIZE - 200, end)
            if boundary != -1:
                end = boundary + 1  # include the period

        chunk_text = text[start:end].strip()

        # Skip chunks that are too short to be meaningful
        if len(chunk_text) >= MIN_CHUNK_LENGTH:
            chunk_id = f"{document_slug}-{chunk_number:03d}"
            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
            })
            chunk_number += 1

        # Slide forward, but step back by CHUNK_OVERLAP so the next
        # chunk re-reads the last CHUNK_OVERLAP characters of this chunk.
        step = end - start - CHUNK_OVERLAP
        if step <= 0:
            # Safety: always advance at least 1 character to avoid infinite loop
            step = max(1, CHUNK_SIZE - CHUNK_OVERLAP)

        start += step

    return chunks


def make_document_slug(filename: str) -> str:
    """
    Convert a filename into a URL-safe slug used in chunk IDs.

    Examples:
        "Leave Policy 2024.pdf"  →  "leave-policy-2024"
        "employee_handbook.PDF"  →  "employee-handbook"
    """
    # Remove the file extension
    name = filename.rsplit('.', 1)[0]
    # Lowercase, replace spaces/underscores with hyphens
    slug = re.sub(r'[\s_]+', '-', name.lower())
    # Remove any characters that aren't alphanumeric or hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Collapse multiple hyphens
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug or "document"
