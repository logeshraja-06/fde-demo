import os
from pathlib import Path
import pytest
from app.database.db import init_db
from app.database import repository
from app.ingestion.parser import parse_document
from app.ingestion.metadata_extractor import extract_document_metadata_from_text
from app.ingestion.chunker import create_chunks_for_document
from app.retrieval.embeddings import generate_embeddings
from app.graph.workflow import execute_truthguard_workflow
from app.schemas.verification import ConflictStatus

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"


@pytest.fixture(scope="module", autouse=True)
def setup_three_document_corpus():
    """Initializes DB and indexes the three conflict test documents."""
    init_db()

    fixture_files = [
        ("leave_policy_v1.txt", "v1.0"),
        ("leave_amendment_v2.docx", "v2.0"),
        ("employee_faq.pdf", None)
    ]

    for fn, custom_ver in fixture_files:
        f_path = FIXTURES_DIR / fn
        if not f_path.exists():
            continue
        with open(f_path, "rb") as f:
            file_bytes = f.read()

        sections, full_text = parse_document(file_bytes, fn)
        doc_metadata = extract_document_metadata_from_text(full_text, fn)
        if custom_ver:
            doc_metadata["version"] = custom_ver
        doc_metadata["file_type"] = fn.split(".")[-1].upper()
        doc_metadata["file_size_bytes"] = len(file_bytes)

        chunks = create_chunks_for_document(sections, doc_metadata)
        embeddings = generate_embeddings([c.text for c in chunks])

        chunks_data = []
        for c, emb in zip(chunks, embeddings):
            c_dict = c.model_dump()
            c_dict["embedding"] = emb
            chunks_data.append(c_dict)

        repository.upsert_document(doc_metadata)
        repository.upsert_chunks(doc_metadata["document_id"], chunks_data)


def test_three_document_conflict_scenario():
    """
    Step 6/7 Scenario:
    Document A: 12 casual leave days (v1, Approved)
    Document B: 15 casual leave days (v2, Contingent on April 1 sign-off)
    Document C: 12 casual leave days (FAQ)

    Query: "What is the current casual leave entitlement?"

    TruthGuard MUST:
    1. Retrieve all three relevant passages.
    2. Detect conflicting values of 12 and 15 days.
    3. Identify FAQ's agreement with v1 and disagreement with v2.
    4. Check whether amendment officially supersedes old policy (it's contingent!).
    5. Conclude conflict is UNRESOLVED and explain why both positions exist.
    """
    question = "What is the current casual leave entitlement?"
    report = execute_truthguard_workflow(question=question)

    # 1. Verification status must be UNRESOLVED due to pending ratification
    assert report.conflict_status == ConflictStatus.UNRESOLVED

    # 2. Contradictions must be detected
    assert len(report.contradictions) > 0
    contra = report.contradictions[0]
    assert "12" in (contra.value_a + contra.value_b)
    assert "15" in (contra.value_a + contra.value_b)

    # 3. Competing positions must list both values and sources
    assert len(report.competing_positions) >= 2
    stated_values = [p.stated_value for p in report.competing_positions]
    assert any("12" in v for v in stated_values)
    assert any("15" in v for v in stated_values)

    # 4. Citations must be valid and non-hallucinated
    assert len(report.citations) > 0
    for cit in report.citations:
        assert cit.exists_in_db is True

    # 5. Final answer must disclose conflict and explain why 15 cannot be claimed conclusively
    assert "Adversarial Policy Conflict Detected" in report.final_answer or "unresolved" in report.final_answer.lower()
    assert "12" in report.final_answer
    assert "15" in report.final_answer
