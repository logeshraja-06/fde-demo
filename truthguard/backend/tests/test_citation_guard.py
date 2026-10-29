import pytest
from app.guards.citation_guard import validate_citations


def test_citation_guard_passes_for_existing_chunks():
    available_chunks = [
        {"chunk_id": "CHUNK_001", "document_id": "DOC_01", "filename": "leave_v1.txt", "page_number": 2, "section": "Casual", "text": "12 casual leaves"},
        {"chunk_id": "CHUNK_002", "document_id": "DOC_02", "filename": "leave_v2.docx", "page_number": 1, "section": "Casual", "text": "15 casual leaves"}
    ]
    cited_ids = ["CHUNK_001", "CHUNK_002"]

    all_valid, valid_cits, invalid_cits = validate_citations(cited_ids, available_chunks)

    assert all_valid is True
    assert len(valid_cits) == 2
    assert len(invalid_cits) == 0
    assert valid_cits[0].exists_in_db is True
    assert valid_cits[0].source_filename in ["leave_v1.txt", "leave_v2.docx"]


def test_citation_guard_detects_hallucinated_chunk_ids():
    available_chunks = [
        {"chunk_id": "CHUNK_001", "document_id": "DOC_01", "filename": "leave_v1.txt", "page_number": 2, "section": "Casual", "text": "12 casual leaves"}
    ]
    # CHUNK_999 does not exist!
    cited_ids = ["CHUNK_001", "CHUNK_999_HALLUCINATED"]

    all_valid, valid_cits, invalid_cits = validate_citations(cited_ids, available_chunks)

    assert all_valid is False
    assert len(valid_cits) == 1
    assert len(invalid_cits) == 1
    assert invalid_cits[0].chunk_id == "CHUNK_999_HALLUCINATED"
    assert invalid_cits[0].exists_in_db is False
