from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    version: Optional[str] = None
    published_at: Optional[str] = None
    effective_date: Optional[str] = None
    status: Optional[str] = None  # e.g. "Approved Policy", "Draft", "FAQ"
    authority_level: Optional[str] = None  # e.g. "Policy", "Amendment", "Guideline", "Informational"
    extra_fields: Dict[str, Any] = Field(default_factory=dict)


class ChunkMetadata(BaseModel):
    document_id: str
    chunk_id: str
    filename: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    version: Optional[str] = None
    published_at: Optional[str] = None
    effective_date: Optional[str] = None
    authority_level: Optional[str] = None
    token_count: int
    text: str


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    status: str
    total_chunks: int
    extracted_preview: str
    detected_metadata: Dict[str, Any]
    created_at: str


class DocumentDetailResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    status: str
    chunk_count: int
    version: Optional[str] = None
    published_at: Optional[str] = None
    created_at: str


class ChunkDetailResponse(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page_number: Optional[int]
    section: Optional[str]
    version: Optional[str]
    published_at: Optional[str]
    token_count: int
    text: str
