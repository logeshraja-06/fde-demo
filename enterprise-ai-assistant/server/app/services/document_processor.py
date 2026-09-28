"""
services/document_processor.py
--------------------------------
The document processing & indexing pipeline for Phase 2 & Phase 3.

Pipeline steps:
  1. File validation  (type, size)
  2. Text extraction  (PDF via pypdf with page tracking, TXT via UTF-8)
  3. Text cleaning    (whitespace, blank lines)
  4. Chunking         (via chunker.py)
  5. JSON storage     (saved to data/processed/)
  6. Embedding        (via embedding_service.py)
  7. Vector Indexing  (via chroma_store.py)
  8. Status: "indexed"

WHAT IS pypdf?
--------------
pypdf is a Python library that parses the binary internal structures of PDF files
and extracts the clean textual content across all pages.
"""

import re
import json
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from pypdf import PdfReader

from app.services.chunker import create_chunks, make_document_slug
from app.services.embedding_service import get_embeddings
from app.vectorstore.chroma_store import add_document_chunks, delete_document_vectors

logger = logging.getLogger("enterprise_ai.documents")

# ── File constraints ──────────────────────────────────────────────────────────
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024   # 10 MB
ALLOWED_EXTENSIONS  = {".pdf", ".txt"}
ALLOWED_MIME_TYPES  = {"application/pdf", "text/plain"}

# ── Storage paths ─────────────────────────────────────────────────────────────
BASE_DIR       = Path(__file__).resolve().parents[2]   # server/
UPLOADS_DIR    = BASE_DIR / "data" / "uploads"
PROCESSED_DIR  = BASE_DIR / "data" / "processed"

# Ensure the directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ── Public interface ──────────────────────────────────────────────────────────

def process_document(filename: str, file_bytes: bytes, content_type: str, domain: Optional[str] = None) -> dict:
    """
    Full pipeline: validate -> duplicate check -> save -> extract -> clean -> chunk -> store -> embed -> index.

    Args:
        filename:     Original filename from user upload.
        file_bytes:   Raw bytes of the file.
        content_type: MIME type sent by browser.
        domain:       Optional knowledge domain ('HR', 'Finance', 'IT', etc.).

    Returns:
        A dict representing the processed and indexed document with domain metadata.
    """
    # 1. Validate
    _validate_file(filename, file_bytes, content_type)

    # 2. Duplicate Document Replacement Policy
    # If a document with the same filename was previously uploaded, replace it
    # to prevent duplicate knowledge and conflicting context.
    existing_docs = list_documents()
    replaced_id = None
    for doc in existing_docs:
        if doc.get("filename") == filename:
            replaced_id = doc.get("document_id")
            delete_document(replaced_id)
            logger.info("Replaced existing document '%s' (previous ID: %s)", filename, replaced_id)
            break

    # 3. Domain classification with smart inference fallback
    assigned_domain = domain.strip() if domain and domain.strip() else ""
    if not assigned_domain or assigned_domain.lower() in ("general", "all"):
        fname = filename.lower()
        if any(k in fname for k in ("leave", "handbook", "hr", "conduct", "employee")):
            assigned_domain = "HR"
        elif any(k in fname for k in ("expense", "travel", "finance", "receipt", "reimbursement")):
            assigned_domain = "Finance"
        elif any(k in fname for k in ("security", "password", "it-", "device", "it_")):
            assigned_domain = "IT"
        else:
            assigned_domain = "General"

    # 4. Assign unique ID and metadata
    document_id = str(uuid.uuid4())
    extension   = Path(filename).suffix.lower()          # ".pdf" or ".txt"
    file_type   = extension.lstrip(".")                  # "pdf" or "txt"
    uploaded_at = datetime.now(timezone.utc).isoformat()

    # 5. Save original file
    safe_filename = f"{document_id}{extension}"
    upload_path   = UPLOADS_DIR / safe_filename
    upload_path.write_bytes(file_bytes)

    # 6. Extract raw text
    try:
        raw_text, page_count = _extract_text_and_meta(upload_path, file_type, file_bytes)
    except ValueError:
        upload_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        upload_path.unlink(missing_ok=True)
        if file_type == "pdf":
            raise RuntimeError("Unable to process this PDF.") from exc
        raise RuntimeError(f"Text extraction failed: {exc}") from exc

    # 7. Clean text
    cleaned_text = _clean_text(raw_text)

    if not cleaned_text.strip():
        upload_path.unlink(missing_ok=True)
        raise ValueError("The document does not contain usable text.")

    # 8. Chunk text
    document_slug = make_document_slug(filename)
    chunks        = create_chunks(cleaned_text, document_slug)

    if not chunks:
        upload_path.unlink(missing_ok=True)
        raise ValueError("The document was too short to produce any chunks.")

    # 9. Generate Embeddings & Index in Vector DB with Domain (Phase 3 & Phase 8)
    chunk_texts = [c["text"] for c in chunks]
    try:
        embeddings = get_embeddings(chunk_texts)
        add_document_chunks(
            document_id=document_id,
            filename=filename,
            chunks=chunks,
            embeddings=embeddings,
            page_number=1 if file_type == "pdf" else None,
            domain=assigned_domain
        )
        status_value = "indexed"
    except Exception as exc:
        logger.warning("Indexing error for %s: %s", filename, exc)
        status_value = "processed"

    indexed_at = datetime.now(timezone.utc).isoformat() if status_value == "indexed" else None

    # 10. Build full processed document record
    processed = {
        "document_id": document_id,
        "filename":    filename,
        "file_type":   file_type,
        "domain":      assigned_domain,
        "chunk_count": len(chunks),
        "status":      status_value,
        "uploaded_at": uploaded_at,
        "indexed_at":  indexed_at,
        "page_count":  page_count,
        "chunks":      chunks,
    }

    # 11. Save to data/processed/<document_id>.json
    processed_path = PROCESSED_DIR / f"{document_id}.json"
    processed_path.write_text(json.dumps(processed, indent=2, ensure_ascii=False), encoding="utf-8")

    return processed


def list_documents() -> list[dict]:
    """
    Return a list of all processed/indexed documents (metadata only).
    """
    documents = []
    for json_file in sorted(PROCESSED_DIR.glob("*.json")):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            documents.append({
                "document_id": data["document_id"],
                "filename":    data["filename"],
                "file_type":   data["file_type"],
                "domain":      data.get("domain", "General"),
                "chunk_count": data["chunk_count"],
                "status":      data.get("status", "indexed"),
                "uploaded_at": data.get("uploaded_at", ""),
                "indexed_at":  data.get("indexed_at", None),
                "page_count":  data.get("page_count", None),
            })
        except Exception:
            continue
    return documents


def get_document(document_id: str) -> dict | None:
    """Return the full processed document with all chunks by ID."""
    json_file = PROCESSED_DIR / f"{document_id}.json"
    if not json_file.exists():
        return None
    return json.loads(json_file.read_text())


def delete_document(document_id: str) -> bool:
    """
    Delete processed JSON, source upload file, AND vector embeddings from ChromaDB.
    """
    json_file = PROCESSED_DIR / f"{document_id}.json"
    if not json_file.exists():
        return False

    try:
        data      = json.loads(json_file.read_text())
        file_type = data.get("file_type", "")
        extension = f".{file_type}" if file_type else ""
    except Exception:
        extension = ""

    # 1. Delete ChromaDB vector embeddings
    delete_document_vectors(document_id)

    # 2. Remove processed JSON
    json_file.unlink(missing_ok=True)

    # 3. Remove original uploaded file
    upload_path = UPLOADS_DIR / f"{document_id}{extension}"
    upload_path.unlink(missing_ok=True)

    return True


def ensure_all_documents_indexed():
    """
    Helper to check all saved processed documents and index any unindexed ones into ChromaDB.
    """
    for json_file in sorted(PROCESSED_DIR.glob("*.json")):
        try:
            data = json.loads(json_file.read_text())
            doc_id = data.get("document_id")
            filename = data.get("filename", "")
            chunks = data.get("chunks", [])
            if chunks and (data.get("status") != "indexed"):
                chunk_texts = [c["text"] for c in chunks]
                embeddings = get_embeddings(chunk_texts)
                add_document_chunks(
                    document_id=doc_id,
                    filename=filename,
                    chunks=chunks,
                    embeddings=embeddings
                )
                data["status"] = "indexed"
                data["indexed_at"] = datetime.now(timezone.utc).isoformat()
                json_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception:
            continue


# ── Private helpers ───────────────────────────────────────────────────────────

def _validate_file(filename: str, file_bytes: bytes, content_type: str) -> None:
    """Validate file extension, mime type, and file size."""
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported document type. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    if content_type and content_type not in ALLOWED_MIME_TYPES:
        if content_type != "application/octet-stream":
            raise ValueError(
                f"Unsupported document type: unexpected content type '{content_type}' for a {extension} file."
            )

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        raise ValueError(f"File exceeds maximum size of {mb} MB.")

    if len(file_bytes) == 0:
        raise ValueError("The document does not contain usable text.")


def _extract_text_and_meta(file_path: Path, file_type: str, file_bytes: bytes) -> tuple[str, Optional[int]]:
    """Extract text and page count metadata from PDF or TXT."""
    if file_type == "pdf":
        try:
            reader = PdfReader(str(file_path))
            num_pages = len(reader.pages)
        except Exception as exc:
            raise RuntimeError("Unable to process this PDF.") from exc

        if num_pages == 0:
            raise ValueError("The document does not contain usable text.")

        page_texts = []
        for page in reader.pages:
            try:
                t = page.extract_text()
                if t:
                    page_texts.append(t)
            except Exception:
                continue

        if not page_texts:
            raise ValueError("The document does not contain usable text.")

        return "\n\n".join(page_texts), num_pages
    elif file_type == "txt":
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = file_bytes.decode("latin-1")
            except Exception:
                raise ValueError("The document does not contain usable text.")
        if not text.strip():
            raise ValueError("The document does not contain usable text.")
        return text, None
    else:
        raise ValueError(f"Unsupported document type: {file_type}")


def _clean_text(text: str) -> str:
    """Normalize extracted text whitespace and formatting."""
    # Collapse multiple inline spaces
    text = re.sub(r'[^\S\n]+', ' ', text)
    # Collapse 3+ newlines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip trailing whitespace on each line
    lines = [line.rstrip() for line in text.splitlines()]
    text  = '\n'.join(lines)
    return text.strip()
