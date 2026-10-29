import re
from typing import Dict, Any


def extract_document_metadata_from_text(text: str, filename: str) -> Dict[str, Any]:
    """
    Extracts version, publication date, effective date, status, authority, and supersession notes.
    Adheres strictly to the requirement:
    'Metadata that cannot be reliably extracted must remain unknown instead of being invented.'
    """
    first_few_lines = "\n".join(text.splitlines()[:25])
    
    # 1. Version extraction (e.g. 'v1', 'v2', 'v1.0', 'VERSION 2.0')
    version = None
    v_match = re.search(r'\b(?:version|ver\.?|v)\s*([0-9]+(?:\.[0-9]+)?)\b', first_few_lines, re.IGNORECASE)
    if not v_match:
        v_match = re.search(r'\bv([0-9]+(?:\.[0-9]+)?)\b', filename, re.IGNORECASE)
    if v_match:
        version = f"v{v_match.group(1)}"

    # 2. Published date extraction (e.g. 'Published: January 15, 2024', 'January 2024', '2024-01-01')
    published_at = None
    date_patterns = [
        r'(?:Published|Date|Issued|Created|Dated)\s*:\s*([A-Za-z]+ \d{1,2}, \d{4})',
        r'(?:Published|Date|Issued|Created|Dated)\s*:\s*([A-Za-z]+ \d{4})',
        r'(?:Published|Date|Issued|Created|Dated)\s*:\s*(\d{4}-\d{2}-\d{2})',
        r'\b([A-Za-z]+ \d{1,2}, \d{4})\b',
        r'\b([A-Za-z]+ \d{4})\b',
        r'\b(\d{4}-\d{2}-\d{2})\b'
    ]
    for pattern in date_patterns:
        d_match = re.search(pattern, first_few_lines, re.IGNORECASE)
        if d_match:
            published_at = d_match.group(1).strip()
            break

    # 3. Effective date
    effective_date = None
    eff_match = re.search(r'(?:Effective(?:\s+Date)?|Commencing)\s*:\s*([A-Za-z]+ \d{1,2}, \d{4}|\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
    if eff_match:
        effective_date = eff_match.group(1).strip()

    # 4. Status (Approved Policy, Draft, Pending, FAQ)
    status = None
    if re.search(r'\bApproved Policy\b', first_few_lines, re.IGNORECASE):
        status = "Approved Policy"
    elif re.search(r'\bPending\b|\bDraft\b|\bUnder Review\b', first_few_lines, re.IGNORECASE):
        status = "Pending Board Ratification / Draft"
    elif re.search(r'\bFAQ\b|\bFrequently Asked Questions\b', first_few_lines, re.IGNORECASE):
        status = "Informational FAQ"

    # 5. Authority level
    authority_level = "Unknown"
    lower_fn = filename.lower()
    if "amendment" in lower_fn or "amendment" in first_few_lines.lower():
        authority_level = "Amendment"
    elif "policy" in lower_fn or "policy" in first_few_lines.lower():
        authority_level = "Policy"
    elif "faq" in lower_fn or "frequently asked questions" in first_few_lines.lower():
        authority_level = "FAQ"
    elif "guideline" in lower_fn or "guidelines" in first_few_lines.lower():
        authority_level = "Guideline"

    # 6. Supersession clause detection
    supersedes_note = None
    sup_match = re.search(r'([^\.\n]*supersede[^\.\n]*\.)', text, re.IGNORECASE)
    if sup_match:
        supersedes_note = sup_match.group(1).strip()

    # 7. Document ID creation
    clean_fn = re.sub(r'[^a-zA-Z0-9]', '_', filename).upper()
    doc_id = f"DOC_{clean_fn}"

    return {
        "document_id": doc_id,
        "filename": filename,
        "version": version,
        "published_at": published_at,
        "effective_date": effective_date,
        "status": status,
        "authority_level": authority_level,
        "supersedes_note": supersedes_note
    }
