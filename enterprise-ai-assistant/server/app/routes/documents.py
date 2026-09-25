"""
routes/documents.py
-------------------
All API endpoints for document management.

This file defines an APIRouter — a mini FastAPI app that handles
a group of related routes. The main app (main.py) mounts this router
under the /api/documents prefix.

ENDPOINTS:
  POST   /api/documents/upload              → Upload & process a document
  GET    /api/documents                     → List all processed documents
  GET    /api/documents/{document_id}       → Get one document with chunks
  DELETE /api/documents/{document_id}       → Delete a document

HTTP Status Codes used:
  200 OK            — Success
  201 Created       — Resource created (upload)
  400 Bad Request   — Client sent invalid input
  404 Not Found     — Resource doesn't exist
  422 Unprocessable — Validation error
  500 Server Error  — Unexpected backend failure
"""

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.models.errors import ErrorCode
from app.services import document_processor

# Create a router — this is FastAPI's way of grouping related endpoints
router = APIRouter(
    prefix="/api/documents",
    tags=["documents"],
)


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/documents/upload
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/upload", status_code=201)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF or TXT document, process it, and return the result.

    WHAT IS multipart/form-data?
    ----------------------------
    When a browser uploads a file, it cannot send raw bytes in JSON.
    Instead it uses a special encoding called "multipart/form-data".
    The request body is split into "parts" — one part per field/file.
    FastAPI's UploadFile automatically handles this encoding for us.

    The 'file: UploadFile' parameter tells FastAPI to expect a file
    in the request body. The 'File(...)' marker makes it required.
    """
    # Read the raw bytes from the upload
    file_bytes = await file.read()

    try:
        processed = document_processor.process_document(
            filename     = file.filename or "unnamed",
            file_bytes   = file_bytes,
            content_type = file.content_type or "",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": ErrorCode.DOCUMENT_UPLOAD_ERROR, "message": str(exc)}
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": ErrorCode.DOCUMENT_PROCESSING_ERROR, "message": str(exc)}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"code": ErrorCode.INTERNAL_SERVER_ERROR, "message": "An unexpected error occurred during processing."}
        )

    # Return the processed document data (without the full chunk list — just metadata)
    return {
        "success": True,
        "document_id": processed["document_id"],
        "filename":    processed["filename"],
        "file_type":   processed["file_type"],
        "chunk_count": processed["chunk_count"],
        "status":      processed["status"],
        "uploaded_at": processed["uploaded_at"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/documents
# ─────────────────────────────────────────────────────────────────────────────

@router.get("")
def get_all_documents():
    """
    Return a list of all processed documents (metadata only, no chunks).
    The frontend uses this to populate the document list.
    """
    documents = document_processor.list_documents()
    return {"documents": documents, "count": len(documents)}


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/documents/{document_id}
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{document_id}")
def get_document(document_id: str):
    """
    Return the full detail of one document, including all its chunks.
    This is used by the Document Detail view in the frontend.

    The {document_id} is a path parameter — FastAPI extracts it from the URL.
    For example: GET /api/documents/abc123 → document_id = "abc123"
    """
    doc = document_processor.get_document(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")
    return doc


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /api/documents/{document_id}
# ─────────────────────────────────────────────────────────────────────────────

@router.delete("/{document_id}", status_code=200)
def delete_document(document_id: str):
    """
    Delete a document — removes both the processed JSON and the uploaded file.
    Returns 404 if the document does not exist.
    """
    deleted = document_processor.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")
    return {"message": f"Document '{document_id}' deleted successfully."}
