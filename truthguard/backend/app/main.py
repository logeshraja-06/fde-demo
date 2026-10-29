import os
import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.db import init_db, is_pg_active
from app.database import repository
from app.ingestion.parser import parse_document
from app.ingestion.metadata_extractor import extract_document_metadata_from_text
from app.ingestion.chunker import create_chunks_for_document
from app.retrieval.embeddings import generate_embeddings
from app.graph.workflow import execute_truthguard_workflow
from app.schemas.documents import (
    DocumentUploadResponse,
    DocumentDetailResponse,
    ChunkDetailResponse
)
from app.schemas.api import QuestionRequest, QuestionResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("truthguard.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing TruthGuard Document Verification Backend...")
    try:
        init_db()
        logger.info(f"Database initialized. Active engine: {'PostgreSQL+pgvector' if is_pg_active() else 'Local SQLite Vector Store'}")
    except Exception as exc:
        logger.error(f"Database initialization error: {exc}")
    yield
    logger.info("TruthGuard Backend shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="TruthGuard — Adversarial Document Verification Prototype with LangGraph, pgvector, and Guardrails",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "db_mode": "PostgreSQL+pgvector" if is_pg_active() else "Local SQLite Fallback",
        "openai_configured": bool(settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY.strip()) > 10)
    }


@app.post("/documents/upload", response_model=DocumentUploadResponse, tags=["Documents"])
async def upload_document(
    file: UploadFile = File(...),
    custom_version: Optional[str] = Form(None)
):
    """
    Step 1: Upload, validate, extract, chunk, embed, and index document evidence.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file missing filename.")

    ext = file.filename.split(".")[-1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '.{ext}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}."
        )

    file_bytes = await file.read()
    if len(file_bytes) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size limit of {settings.MAX_FILE_SIZE_BYTES / (1024*1024):.1f} MB."
        )

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")

    # Save to upload folder
    saved_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(saved_path, "wb") as f:
        f.write(file_bytes)

    # 1. Parse document into sections and full text
    sections, full_text = parse_document(file_bytes, file.filename)

    # 2. Extract metadata (version, publication date, authority, supersession)
    doc_metadata = extract_document_metadata_from_text(full_text, file.filename)
    if custom_version:
        doc_metadata["version"] = custom_version

    doc_metadata["file_type"] = ext.upper()
    doc_metadata["file_size_bytes"] = len(file_bytes)

    # 3. Create high-quality token-aware chunks preserving metadata
    chunks = create_chunks_for_document(
        sections=sections,
        doc_metadata=doc_metadata
    )

    if not chunks:
        raise HTTPException(status_code=400, detail="Document could not be partitioned into any text chunks.")

    # 4. Generate embeddings for all chunks
    chunk_texts = [c.text for c in chunks]
    embeddings = generate_embeddings(chunk_texts)

    chunks_data = []
    for c, emb in zip(chunks, embeddings):
        c_dict = c.model_dump()
        c_dict["embedding"] = emb
        chunks_data.append(c_dict)

    # 5. Persist document and chunks (de-duplicates prior chunks on re-upload)
    repository.upsert_document(doc_metadata)
    repository.upsert_chunks(doc_metadata["document_id"], chunks_data)

    preview_text = full_text[:400] + ("..." if len(full_text) > 400 else "")

    return DocumentUploadResponse(
        document_id=doc_metadata["document_id"],
        filename=file.filename,
        file_type=ext.upper(),
        file_size_bytes=len(file_bytes),
        status="Indexed",
        total_chunks=len(chunks),
        extracted_preview=preview_text,
        detected_metadata=doc_metadata,
        created_at=doc_metadata.get("published_at") or "Recently"
    )


@app.get("/documents", response_model=List[DocumentDetailResponse], tags=["Documents"])
def get_documents():
    """Returns list of uploaded documents and processing status."""
    docs = repository.list_documents()
    return [
        DocumentDetailResponse(
            document_id=d["document_id"],
            filename=d["filename"],
            file_type=d["file_type"],
            file_size_bytes=d["file_size_bytes"],
            status=d.get("status") or "Indexed",
            chunk_count=d.get("chunk_count", 0),
            version=d.get("version"),
            published_at=d.get("published_at"),
            created_at=str(d.get("created_at"))
        )
        for d in docs
    ]


@app.get("/documents/{document_id}/chunks", response_model=List[ChunkDetailResponse], tags=["Documents"])
def get_document_chunks(document_id: str):
    """Returns all extracted chunks for a document with page and section metadata."""
    chunks = repository.get_document_chunks(document_id)
    if not chunks:
        raise HTTPException(status_code=404, detail=f"No chunks found for document '{document_id}'.")
    return [
        ChunkDetailResponse(
            chunk_id=c["chunk_id"],
            document_id=c["document_id"],
            filename=c.get("filename", ""),
            page_number=c.get("page_number"),
            section=c.get("section"),
            version=c.get("version"),
            published_at=c.get("published_at"),
            token_count=c.get("token_count", 0),
            text=c.get("text", "")
        )
        for c in chunks
    ]


@app.get("/documents/{document_id}/status", tags=["Documents"])
def get_document_status(document_id: str):
    """Returns the ingestion status and metadata of a document."""
    doc = repository.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")
    chunks = repository.get_document_chunks(document_id)
    return {
        "document_id": document_id,
        "filename": doc.get("filename"),
        "status": "Indexed" if chunks else "No Chunks",
        "chunk_count": len(chunks),
        "metadata": doc
    }


@app.post("/questions", response_model=QuestionResponse, tags=["Verification"])
def ask_question(req: QuestionRequest):
    """
    Step 4: Executes the 9-node LangGraph adversarial verification workflow
    and returns verified answer, conflict explanation, and citation breakdown.
    """
    try:
        report = execute_truthguard_workflow(
            question=req.question,
            user_id=req.user_id,
            permissions=req.permissions,
            document_ids=req.document_ids,
            version_filter=req.version_filter
        )
        return QuestionResponse(**report.model_dump())
    except Exception as exc:
        logger.error(f"Error during question verification workflow: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Verification workflow failure: {str(exc)}")


@app.get("/questions/{query_id}/report", response_model=QuestionResponse, tags=["Verification"])
def get_verification_report(query_id: str):
    """Retrieves an existing verification audit report by query ID."""
    rep_dict = repository.get_report(query_id)
    if not rep_dict:
        raise HTTPException(status_code=404, detail=f"Verification report '{query_id}' not found.")
    return QuestionResponse(**rep_dict)
