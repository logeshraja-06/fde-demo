import re
from typing import List, Dict, Any, Optional
from app.config import settings
from app.schemas.documents import ChunkMetadata
from app.ingestion.parser import ExtractedSection


def get_token_count(text: str) -> int:
    """Calculates token count using tiktoken or reliable heuristic fallback."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        # Standard token heuristic: 1 token ~ 0.75 words (or len(text) / 4)
        words = text.split()
        return max(1, int(len(words) * 1.33))


def split_text_into_sentences(text: str) -> List[str]:
    """Splits text into sentences cleanly without breaking numbers like '12.0'."""
    pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+'
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if s.strip()]


def create_chunks_for_document(
    sections: List[ExtractedSection],
    doc_metadata: Dict[str, Any],
    target_tokens: Optional[int] = None,
    overlap_tokens: Optional[int] = None
) -> List[ChunkMetadata]:
    """
    Builds high-quality token-aware chunks adhering strictly to:
    - Split primarily by headings, sections, and paragraphs.
    - Use token-aware splitting when sections are too large.
    - Start with configurable target (~600 tokens, 100 overlap).
    - Keep short sections intact when practical.
    - Preserve document ID, chunk ID, page number, section heading, source filename, version, date.
    - Avoid splitting a sentence or important rule unnecessarily.
    - Do NOT combine unrelated sections just to reach target chunk size.
    """
    target_tokens = target_tokens or settings.TARGET_CHUNK_TOKENS
    overlap_tokens = overlap_tokens or settings.CHUNK_OVERLAP_TOKENS

    doc_id = doc_metadata.get("document_id", "DOC_UNKNOWN")
    filename = doc_metadata.get("filename", "unknown_file")
    version = doc_metadata.get("version")
    published_at = doc_metadata.get("published_at")
    effective_date = doc_metadata.get("effective_date")
    authority_level = doc_metadata.get("authority_level")

    chunks: List[ChunkMetadata] = []
    chunk_counter = 1

    for section in sections:
        section_text = section.text.strip()
        if not section_text:
            continue

        sec_tokens = get_token_count(section_text)

        # 1. If section is within target token limit (or slightly above, e.g. < 750 tokens), keep it intact!
        if sec_tokens <= int(target_tokens * 1.25):
            chunk_id = f"{doc_id}_CHUNK_{chunk_counter:03d}"
            chunks.append(
                ChunkMetadata(
                    document_id=doc_id,
                    chunk_id=chunk_id,
                    filename=filename,
                    page_number=section.page_number,
                    section=section.heading,
                    version=version,
                    published_at=published_at,
                    effective_date=effective_date,
                    authority_level=authority_level,
                    token_count=sec_tokens,
                    text=section_text
                )
            )
            chunk_counter += 1
            continue

        # 2. Section is oversized: split by paragraphs first
        paragraphs = [p.strip() for p in section_text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [p.strip() for p in section_text.splitlines() if p.strip()]

        current_paras: List[str] = []
        current_token_count = 0

        for para in paragraphs:
            p_tokens = get_token_count(para)

            # If a single paragraph is larger than target, split by sentences
            if p_tokens > target_tokens:
                # Flush existing buffer
                if current_paras:
                    c_text = "\n\n".join(current_paras)
                    chunk_id = f"{doc_id}_CHUNK_{chunk_counter:03d}"
                    chunks.append(
                        ChunkMetadata(
                            document_id=doc_id,
                            chunk_id=chunk_id,
                            filename=filename,
                            page_number=section.page_number,
                            section=section.heading,
                            version=version,
                            published_at=published_at,
                            effective_date=effective_date,
                            authority_level=authority_level,
                            token_count=current_token_count,
                            text=c_text
                        )
                    )
                    chunk_counter += 1
                    current_paras = []
                    current_token_count = 0

                sentences = split_text_into_sentences(para)
                s_buffer: List[str] = []
                s_tokens = 0

                for s in sentences:
                    st_len = get_token_count(s)
                    if s_tokens + st_len > target_tokens and s_buffer:
                        s_text = " ".join(s_buffer)
                        chunk_id = f"{doc_id}_CHUNK_{chunk_counter:03d}"
                        chunks.append(
                            ChunkMetadata(
                                document_id=doc_id,
                                chunk_id=chunk_id,
                                filename=filename,
                                page_number=section.page_number,
                                section=section.heading,
                                version=version,
                                published_at=published_at,
                                effective_date=effective_date,
                                authority_level=authority_level,
                                token_count=s_tokens,
                                text=s_text
                            )
                        )
                        chunk_counter += 1
                        # Retain overlap sentences
                        overlap_buffer: List[str] = []
                        overlap_count = 0
                        for prev_s in reversed(s_buffer):
                            p_len = get_token_count(prev_s)
                            if overlap_count + p_len <= overlap_tokens:
                                overlap_buffer.insert(0, prev_s)
                                overlap_count += p_len
                            else:
                                break
                        s_buffer = overlap_buffer + [s]
                        s_tokens = overlap_count + st_len
                    else:
                        s_buffer.append(s)
                        s_tokens += st_len

                if s_buffer:
                    s_text = " ".join(s_buffer)
                    chunk_id = f"{doc_id}_CHUNK_{chunk_counter:03d}"
                    chunks.append(
                        ChunkMetadata(
                            document_id=doc_id,
                            chunk_id=chunk_id,
                            filename=filename,
                            page_number=section.page_number,
                            section=section.heading,
                            version=version,
                            published_at=published_at,
                            effective_date=effective_date,
                            authority_level=authority_level,
                            token_count=s_tokens,
                            text=s_text
                        )
                    )
                    chunk_counter += 1

            elif current_token_count + p_tokens > target_tokens:
                # Chunk boundary reached within the section
                c_text = "\n\n".join(current_paras)
                chunk_id = f"{doc_id}_CHUNK_{chunk_counter:03d}"
                chunks.append(
                    ChunkMetadata(
                        document_id=doc_id,
                        chunk_id=chunk_id,
                        filename=filename,
                        page_number=section.page_number,
                        section=section.heading,
                        version=version,
                        published_at=published_at,
                        effective_date=effective_date,
                        authority_level=authority_level,
                        token_count=current_token_count,
                        text=c_text
                    )
                )
                chunk_counter += 1

                # Carry over last paragraph for overlap if within limit
                if current_paras and get_token_count(current_paras[-1]) <= overlap_tokens:
                    current_paras = [current_paras[-1], para]
                    current_token_count = get_token_count(current_paras[0]) + p_tokens
                else:
                    current_paras = [para]
                    current_token_count = p_tokens
            else:
                current_paras.append(para)
                current_token_count += p_tokens

        # Flush remaining paragraphs in section
        if current_paras:
            c_text = "\n\n".join(current_paras)
            chunk_id = f"{doc_id}_CHUNK_{chunk_counter:03d}"
            chunks.append(
                ChunkMetadata(
                    document_id=doc_id,
                    chunk_id=chunk_id,
                    filename=filename,
                    page_number=section.page_number,
                    section=section.heading,
                    version=version,
                    published_at=published_at,
                    effective_date=effective_date,
                    authority_level=authority_level,
                    token_count=current_token_count,
                    text=c_text
                )
            )
            chunk_counter += 1

    return chunks
