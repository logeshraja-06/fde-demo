import pytest
from app.ingestion.metadata_extractor import extract_document_metadata_from_text


def test_metadata_extraction_known_document():
    text = """ACME CORPORATION
POLICY MANUAL: LEAVE POLICY (VERSION 1.0)
Published: January 15, 2024
Status: Approved Policy
Category: Human Resources Regulations

Section 1: Casual Leave Entitlement
Employees are entitled to 12 casual leave days per year.
"""
    metadata = extract_document_metadata_from_text(text, "leave_policy_v1.txt")

    assert metadata["version"] == "v1.0" or metadata["version"] == "v1"
    assert "January 15, 2024" in metadata["published_at"]
    assert metadata["status"] == "Approved Policy"
    assert metadata["authority_level"] == "Policy"


def test_metadata_extraction_remains_none_when_absent():
    text = """GENERAL NOTICE TO EMPLOYEES
All employees must wear their badges at all times.
Visitors must sign in at the front desk.
"""
    metadata = extract_document_metadata_from_text(text, "general_notice.txt")

    # Metadata that cannot be reliably extracted must remain unknown (None), not invented
    assert metadata["version"] is None
    assert metadata["published_at"] is None
    assert metadata["effective_date"] is None
    assert metadata["status"] is None
