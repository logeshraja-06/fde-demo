"""
models/errors.py
----------------
Standardized API error models and error codes for Phase 7.

Ensures all error responses across endpoints follow a predictable schema:
{
  "success": false,
  "error": {
    "code": "LLM_SERVICE_ERROR",
    "message": "The AI service is temporarily unavailable."
  },
  "detail": "The AI service is temporarily unavailable."
}
"""

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class ErrorCode:
    INVALID_INPUT = "INVALID_INPUT"
    DOCUMENT_UPLOAD_ERROR = "DOCUMENT_UPLOAD_ERROR"
    DOCUMENT_PROCESSING_ERROR = "DOCUMENT_PROCESSING_ERROR"
    RAG_SEARCH_ERROR = "RAG_SEARCH_ERROR"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    LLM_SERVICE_ERROR = "LLM_SERVICE_ERROR"
    OUTPUT_VALIDATION_ERROR = "OUTPUT_VALIDATION_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    BACKEND_UNAVAILABLE = "BACKEND_UNAVAILABLE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable safe error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Optional extra diagnostic details")


class StandardErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    detail: Optional[str] = None  # Preserved for backward compatibility with standard FastAPI consumers
