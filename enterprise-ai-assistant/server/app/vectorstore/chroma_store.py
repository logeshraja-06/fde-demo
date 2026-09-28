"""
vectorstore/chroma_store.py
---------------------------
ChromaDB Vector Store interface for Phase 3.

WHAT IS A VECTOR DATABASE?
--------------------------
A standard database (like SQL) lets you search for exact words or numbers:
  SELECT * FROM documents WHERE text LIKE '%leave%'

A vector database stores high-dimensional vectors and lets you search
by MATHEMATICAL SIMILARITY rather than keyword matching:
  "Find the 3 chunks whose vectors are closest to the user's question vector"

HOW DOES SIMILARITY WORK?
-------------------------
We configure ChromaDB with `hnsw:space: "cosine"`.
ChromaDB computes the cosine distance $d$ between vectors.
Cosine distance ranges from 0.0 (identical vectors) to 2.0 (opposite).

We convert distance into a similarity score from 0.0 to 1.0:
  similarity = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
Or for normalized vectors:
  similarity = 1.0 - distance (clamped to 0.0 .. 1.0)
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import threading

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]   # server/
CHROMA_DATA_DIR = BASE_DIR / "data" / "chroma"
CHROMA_DATA_DIR.mkdir(parents=True, exist_ok=True)

COLLECTION_NAME = "enterprise_knowledge_base"

_client_instance = None
_client_lock = threading.Lock()


def get_chroma_client():
    """Return a persistent ChromaDB client singleton."""
    global _client_instance
    if _client_instance is None:
        with _client_lock:
            if _client_instance is None:
                import chromadb
                from chromadb.config import Settings
                _client_instance = chromadb.PersistentClient(
                    path=str(CHROMA_DATA_DIR),
                    settings=Settings(anonymized_telemetry=False)
                )
    return _client_instance


def get_collection():
    """
    Get or create the enterprise knowledge base collection.
    We configure cosine distance for vector comparison.
    """
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


def add_document_chunks(
    document_id: str,
    filename: str,
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    page_number: Optional[int] = None,
    domain: Optional[str] = "General"
) -> int:
    """
    Index a list of chunks into ChromaDB along with their embedding vectors and domain metadata.

    Args:
        document_id: UUID of the parent document.
        filename: Original file name (e.g. "leave-policy.pdf").
        chunks: List of chunk dicts (each with 'id' and 'text').
        embeddings: List of 384-dimensional float vectors matching the chunks.
        page_number: Optional page number if extracted from a specific page.
        domain: Knowledge domain (e.g. 'HR', 'Finance', 'IT', 'General').

    Returns:
        The number of chunks successfully indexed.
    """
    if not chunks or not embeddings:
        return 0

    if len(chunks) != len(embeddings):
        raise ValueError("Number of chunks and embeddings must match.")

    collection = get_collection()

    # ChromaDB requires lists of ids, embeddings, documents (texts), and metadatas
    ids = []
    documents = []
    metadatas = []

    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        chunk_id = chunk.get("id", f"{document_id}-{idx:03d}")
        text = chunk.get("text", "")
        # ChromaDB requires unique IDs per vector
        unique_id = f"{document_id}_{chunk_id}"

        metadata = {
            "document_id": document_id,
            "filename": filename,
            "chunk_id": chunk_id,
            "chunk_index": idx,
            "domain": domain or "General",
        }
        # Add page if available and valid
        if page_number is not None and page_number > 0:
            metadata["page"] = page_number

        ids.append(unique_id)
        documents.append(text)
        metadatas.append(metadata)

    # Upsert (insert or update) into ChromaDB
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    return len(ids)


def query_vector_store(
    query_embedding: List[float],
    top_k: int = 3,
    domain: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Query the vector store with a question embedding and return the top-K matches.
    Supports optional knowledge domain filtering (HR, Finance, IT).

    Args:
        query_embedding: The vector representation of the user question.
        top_k: Number of nearest neighbors to retrieve.
        domain: Optional domain filter ('HR', 'Finance', 'IT', or None/'ALL').

    Returns:
        List of dicts with score, distance, text, source, domain, chunk_id.
    """
    collection = get_collection()
    count = collection.count()

    if count == 0:
        return []

    # top_k cannot exceed the number of elements in the collection
    actual_k = min(top_k, count)
    # Query Chroma with broad candidate pool to allow deduplication of repeated document uploads
    candidate_k = min(count, max(actual_k * 10, 50))

    query_kwargs: Dict[str, Any] = {
        "query_embeddings": [query_embedding],
        "n_results": candidate_k,
        "include": ["documents", "metadatas", "distances"]
    }

    # Add metadata domain filter if requested and not "ALL"
    if domain and domain.strip().upper() not in ("ALL", ""):
        query_kwargs["where"] = {"domain": domain.strip()}

    try:
        results = collection.query(**query_kwargs)
    except Exception as exc:
        # If filtered query returns error (e.g. no docs with that domain), fall back safely
        logger_warn = logging.getLogger("enterprise_ai.chroma")
        logger_warn.warning("Filtered query error: %s. Falling back to unfiltered query.", exc)
        query_kwargs.pop("where", None)
        results = collection.query(**query_kwargs)

    formatted_results = []
    deferred_results = []
    seen_texts = set()
    doc_chunk_counts = {}

    if results and results.get("ids") and results["ids"][0]:
        ids = results["ids"][0]
        documents = results["documents"][0] if results.get("documents") else []
        metadatas = results["metadatas"][0] if results.get("metadatas") else []
        distances = results["distances"][0] if results.get("distances") else []

        for i in range(len(ids)):
            metadata = metadatas[i] if i < len(metadatas) else {}
            text = documents[i] if i < len(documents) else ""
            dist = distances[i] if i < len(distances) else 1.0

            clean_sample = text.strip()[:150]
            if clean_sample in seen_texts:
                continue
            seen_texts.add(clean_sample)

            # In Chroma cosine space: distance is 1 - cosine_similarity
            # Therefore similarity score = max(0.0, 1.0 - dist)
            similarity_score = max(0.0, min(1.0, 1.0 - dist))
            rounded_score = round(similarity_score, 4)

            entry = {
                "chunk_id": metadata.get("chunk_id", ids[i]),
                "source": metadata.get("filename", "Unknown document"),
                "document_id": metadata.get("document_id", ""),
                "page": metadata.get("page", None),
                "domain": metadata.get("domain", "General"),
                "score": rounded_score,
                "distance": round(dist, 4),
                "text": text
            }

            source_name = entry["source"]
            # To ensure multi-source diversity when top_k > 2, cap at 2 chunks per doc on first pass
            if actual_k > 2 and doc_chunk_counts.get(source_name, 0) >= 2:
                deferred_results.append(entry)
                continue

            doc_chunk_counts[source_name] = doc_chunk_counts.get(source_name, 0) + 1
            formatted_results.append(entry)

            if len(formatted_results) >= actual_k:
                break

        # If not enough unique docs to fill actual_k, pull from deferred results
        for entry in deferred_results:
            if len(formatted_results) >= actual_k:
                break
            formatted_results.append(entry)

    # Sort descending by similarity score
    formatted_results.sort(key=lambda x: x["score"], reverse=True)
    return formatted_results


def delete_document_vectors(document_id: str) -> bool:
    """
    Remove all chunk vectors belonging to a given document_id from ChromaDB.
    """
    try:
        collection = get_collection()
        collection.delete(where={"document_id": document_id})
        return True
    except Exception:
        return False


def get_vector_store_stats() -> Dict[str, Any]:
    """Return stats about the vector database."""
    try:
        collection = get_collection()
        return {
            "collection_name": COLLECTION_NAME,
            "total_chunks_indexed": collection.count(),
            "storage_path": str(CHROMA_DATA_DIR)
        }
    except Exception as exc:
        return {
            "collection_name": COLLECTION_NAME,
            "total_chunks_indexed": 0,
            "error": str(exc)
        }
