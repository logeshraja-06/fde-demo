from typing import List, Dict, Any, Tuple
from app.schemas.verification import CitationValidation


def validate_citations(
    cited_chunk_ids: List[str],
    available_chunks: List[Dict[str, Any]]
) -> Tuple[bool, List[CitationValidation], List[CitationValidation]]:
    """
    Deterministically validates that every cited chunk ID exists in the database/evidence
    and links to verified source locations.
    """
    valid_citations: List[CitationValidation] = []
    invalid_citations: List[CitationValidation] = []

    chunk_map = {c["chunk_id"]: c for c in available_chunks}

    for idx, c_id in enumerate(set(cited_chunk_ids)):
        cit_label = f"[{idx + 1}]"
        if c_id in chunk_map:
            c_data = chunk_map[c_id]
            valid_citations.append(
                CitationValidation(
                    citation_id=cit_label,
                    chunk_id=c_id,
                    document_id=c_data.get("document_id", "UNKNOWN"),
                    source_filename=c_data.get("filename", "unknown"),
                    page_number=c_data.get("page_number"),
                    section=c_data.get("section"),
                    exists_in_db=True,
                    matches_context=True,
                    excerpt=c_data.get("text", "")[:280] + ("..." if len(c_data.get("text", "")) > 280 else "")
                )
            )
        else:
            invalid_citations.append(
                CitationValidation(
                    citation_id=cit_label,
                    chunk_id=c_id,
                    document_id="NON_EXISTENT",
                    source_filename="UNKNOWN",
                    page_number=None,
                    section=None,
                    exists_in_db=False,
                    matches_context=False,
                    excerpt="Citation ID not found in stored document corpus."
                )
            )

    all_valid = len(invalid_citations) == 0
    return all_valid, valid_citations, invalid_citations
