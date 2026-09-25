"""
models/document.py
------------------
Data models for Phase 2 document processing.

We use Python dataclasses here — they are simple containers for data.
Think of a dataclass as a struct: it holds fields and their types.

In a later phase we might switch to Pydantic models or a database ORM,
but for now dataclasses are perfectly readable and lightweight.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Chunk:
    """
    Represents a single piece of a larger document.

    After a document is extracted and cleaned, the text is split into
    many smaller Chunks. Each Chunk has:
      - id:   a unique identifier like "leave-policy-001"
      - text: the actual content of this piece
    """
    id: str
    text: str


@dataclass
class ProcessedDocument:
    """
    Represents a document after it has been fully processed.

    Fields:
      - document_id:  a unique UUID assigned when the file is uploaded
      - filename:     original filename (e.g. "leave-policy.pdf")
      - file_type:    "pdf" or "txt"
      - chunk_count:  how many chunks were created
      - chunks:       the list of Chunk objects
      - status:       "processed" or "error"
      - uploaded_at:  ISO timestamp string
    """
    document_id: str
    filename: str
    file_type: str
    chunk_count: int
    chunks: List[Chunk] = field(default_factory=list)
    status: str = "processed"
    uploaded_at: str = ""
