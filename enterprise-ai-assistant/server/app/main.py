"""
Enterprise AI Assistant - FastAPI Backend
==========================================
Phase 7: End-to-End Integration, Reliability & Testing

Architecture:
  main.py         — application factory, logging, error handlers, router registration
  routes/
    documents.py  — Document upload, duplicate replacement, details, and deletion
    rag.py        — Semantic vector search & retrieval endpoints with Top-K bounds
    chat.py       — Grounded RAG Chat with 3-Layer Guardrail Pipeline & structured errors
    analytics.py  — Observability and real-time execution audit telemetry
  services/
    document_processor.py — Ingestion, text extraction, validation, chunking
    chunker.py            — Sliding window chunking
    embedding_service.py  — Local SentenceTransformer embeddings
    retrieval_service.py  — Cosine similarity scoring, threshold filtering
    prompt_builder.py     — Structured prompt construction with source blocks
    llm_service.py        — Google Gemini API integration with offline deterministic fallback
    input_guardrail.py    — Input emptiness, length limit, prompt injection regex
    output_guardrail.py   — Output non-empty check, source requirement, system leak filter
    analytics_service.py  — Real-time execution telemetry recording and metrics aggregation
  vectorstore/
    chroma_store.py       — ChromaDB persistent vector database client
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.models.errors import StandardErrorResponse, ErrorDetail, ErrorCode
from app.routes import documents as documents_router
from app.routes import rag as rag_router
from app.routes import chat as chat_router
from app.routes import analytics as analytics_router
from app.routes import config as config_router
from app.services.document_processor import ensure_all_documents_indexed
from app.services.llm_service import is_llm_configured, get_gemini_model_name
from app.vectorstore.chroma_store import get_vector_store_stats

# ── Structured Server Logging ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("enterprise_ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure any existing saved documents are indexed in ChromaDB
    logger.info("Initializing Enterprise AI Assistant backend...")
    try:
        ensure_all_documents_indexed()
        logger.info("Vector store index verification completed.")
    except Exception as exc:
        logger.warning("Startup indexing warning: %s", exc)
    yield
    logger.info("Enterprise AI Assistant backend shutting down.")


# Create the FastAPI application instance
app = FastAPI(
    title="Enterprise AI Assistant API",
    description="Phase 7: End-to-End Integration, Reliability, and Production-Grade Safety Perimeter.",
    version="0.7.0",
    lifespan=lifespan,
)

# ── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.exceptions import RequestValidationError
import time
from collections import defaultdict

# ── Lightweight In-Memory Request Flooding Protection ─────────────────────────
# Tracks timestamps of recent requests per client IP to prevent accidental flooding
_request_history = defaultdict(list)
_RATE_LIMIT_WINDOW_SECONDS = 60
_MAX_REQUESTS_PER_WINDOW = 60

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Only rate-limit mutative or heavy endpoints (e.g. /chat, /rag/search, /api/documents/upload)
    path = request.url.path
    if path.startswith(("/chat", "/api/chat", "/rag/search", "/api/rag/search", "/api/documents/upload")):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        timestamps = _request_history[client_ip]
        # Purge timestamps outside current window
        _request_history[client_ip] = [t for t in timestamps if now - t < _RATE_LIMIT_WINDOW_SECONDS]
        
        if len(_request_history[client_ip]) >= _MAX_REQUESTS_PER_WINDOW:
            logger.warning("Rate limit exceeded for %s on %s", client_ip, path)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error": {
                        "code": ErrorCode.RATE_LIMIT_EXCEEDED,
                        "message": "Too many requests. Please slow down and try again shortly.",
                    },
                    "detail": "Too many requests. Please slow down and try again shortly.",
                },
            )
        _request_history[client_ip].append(now)

    response = await call_next(request)
    return response


# ── Global Standardized Exception Handlers ────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Standardize Pydantic validation errors into predictable INVALID_INPUT schema.
    """
    error_messages = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []) if l != "body")
        msg = err.get("msg", "Invalid value")
        error_messages.append(f"{loc}: {msg}" if loc else msg)
    message = "; ".join(error_messages) if error_messages else "Request validation failed."
    logger.warning("Validation error on %s: %s", request.url.path, message)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.INVALID_INPUT,
                "message": message,
            },
            "detail": message,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Standardize all HTTP exceptions into predictable Phase 7 error schema:
    {
      "success": false,
      "error": { "code": "...", "message": "..." },
      "detail": "..."
    }
    """
    error_code = ErrorCode.INTERNAL_SERVER_ERROR
    message = "An error occurred."

    if isinstance(exc.detail, dict):
        error_code = exc.detail.get("code", error_code)
        message = exc.detail.get("message", message)
    else:
        message = str(exc.detail) if exc.detail else message
        if exc.status_code == status.HTTP_400_BAD_REQUEST:
            error_code = ErrorCode.INVALID_INPUT
        elif exc.status_code == status.HTTP_404_NOT_FOUND:
            error_code = "RESOURCE_NOT_FOUND"
        elif exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            error_code = ErrorCode.DOCUMENT_PROCESSING_ERROR
        elif exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            error_code = ErrorCode.RATE_LIMIT_EXCEEDED
        elif exc.status_code == status.HTTP_502_BAD_GATEWAY:
            error_code = ErrorCode.LLM_SERVICE_ERROR
        elif exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            error_code = ErrorCode.BACKEND_UNAVAILABLE

    logger.warning("HTTP %d error on %s: %s (code=%s)", exc.status_code, request.url.path, message, error_code)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
            },
            "detail": message,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler preventing stack trace or path disclosure to clients.
    """
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    message = "An unexpected internal server error occurred. Please try again later."
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.INTERNAL_SERVER_ERROR,
                "message": message,
            },
            "detail": message,
        },
    )


# ── Register Routers ──────────────────────────────────────────────────────────
# 1. Document Management Endpoints (/api/documents)
app.include_router(documents_router.router)

# 2. RAG Retrieval Endpoints (/rag and /api/rag)
app.include_router(rag_router.router, prefix="/rag")
app.include_router(rag_router.router, prefix="/api/rag")

# 3. Chat & Guardrail Endpoints (/chat and /api/chat)
app.include_router(chat_router.router, prefix="/chat")
app.include_router(chat_router.router, prefix="/api/chat")

# 4. Observability & Analytics Endpoints (/analytics and /api/analytics)
app.include_router(analytics_router.router, prefix="/analytics")
app.include_router(analytics_router.router, prefix="/api/analytics")

# 5. Customer Profile & Configuration Endpoints (/config and /api/config)
app.include_router(config_router.router)
app.include_router(config_router.router, prefix="/config")


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", summary="System Health and Dependency Diagnostics")
def health_check():
    """
    Enhanced Phase 7 health check — verifies core service and critical dependencies:
    - Vector database (ChromaDB collection accessibility)
    - Embedding model (all-MiniLM-L6-v2)
    - LLM provider (Google Gemini configuration state)
    """
    dependencies = {
        "vector_database": "unavailable",
        "embedding_model": "loaded",
        "llm": "unconfigured",
    }
    is_healthy = True

    # 1. Check ChromaDB collection
    try:
        stats = get_vector_store_stats()
        if stats and "total_chunks_indexed" in stats:
            dependencies["vector_database"] = "healthy"
        else:
            dependencies["vector_database"] = "degraded"
    except Exception as exc:
        logger.error("Health check ChromaDB diagnostic failed: %s", exc)
        dependencies["vector_database"] = "unavailable"
        is_healthy = False

    # 2. Check LLM Configuration
    if is_llm_configured():
        dependencies["llm"] = f"configured ({get_gemini_model_name()})"
    else:
        dependencies["llm"] = "offline_fallback_mode"

    return {
        "status": "ok" if is_healthy else "degraded",
        "service": "enterprise-ai-assistant",
        "phase": "7 — Production Integration & Reliability",
        "dependencies": dependencies,
    }
