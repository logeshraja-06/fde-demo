import pytest
from app.ingestion.parser import ExtractedSection
from app.ingestion.chunker import create_chunks_for_document, get_token_count


def test_chunking_preserves_short_sections():
    sections = [
        ExtractedSection(heading="Section 1: Casual Leave", text="Employees are entitled to 12 casual leave days per year.", page_number=1),
        ExtractedSection(heading="Section 2: Sick Leave", text="Employees receive 10 paid sick leave days per year.", page_number=1)
    ]
    doc_metadata = {
        "document_id": "DOC_TEST_001",
        "filename": "leave_policy.txt",
        "version": "v1.0",
        "published_at": "2024-01-01"
    }

    chunks = create_chunks_for_document(sections, doc_metadata, target_tokens=600, overlap_tokens=100)

    # Each short section must be kept intact as its own chunk
    assert len(chunks) == 2
    assert chunks[0].section == "Section 1: Casual Leave"
    assert chunks[0].page_number == 1
    assert chunks[0].version == "v1.0"
    assert "12 casual leave days" in chunks[0].text

    assert chunks[1].section == "Section 2: Sick Leave"
    assert "10 paid sick leave days" in chunks[1].text


def test_chunking_splits_large_sections_without_splitting_sentences():
    # Long paragraph containing multiple full sentences
    sentences = [f"This is sentence number {i} regarding company regulatory standards." for i in range(1, 45)]
    long_text = " ".join(sentences)

    sections = [
        ExtractedSection(heading="Long Section", text=long_text, page_number=2)
    ]
    doc_metadata = {
        "document_id": "DOC_TEST_LARGE",
        "filename": "large_policy.pdf",
        "version": "v2.0"
    }

    chunks = create_chunks_for_document(sections, doc_metadata, target_tokens=100, overlap_tokens=20)

    assert len(chunks) > 1
    for c in chunks:
        assert c.document_id == "DOC_TEST_LARGE"
        assert c.page_number == 2
        # Ensure chunks end cleanly with a period or sentence boundary, not truncated words
        assert c.text.strip().endswith(".")
