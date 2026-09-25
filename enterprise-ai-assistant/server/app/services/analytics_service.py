"""
services/analytics_service.py
-----------------------------
Real-time Observability and Analytics Service for Phase 6.

WHAT THIS SERVICE DOES:
- Records actual query executions from the /chat endpoint.
- Captures real response times (ms), outcome status, scores, and sources count.
- Persists events to data/analytics.json so metrics survive server restarts.
- Queries ChromaDB and processed documents to return honest, non-fabricated metrics.
- Computes aggregations: total questions, success rate, blocked count, insufficient evidence count,
  and average response latency.
"""

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.vectorstore.chroma_store import get_vector_store_stats
from app.services.retrieval_service import DEFAULT_SIMILARITY_THRESHOLD

BASE_DIR = Path(__file__).resolve().parents[2]   # server/
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
ANALYTICS_FILE = DATA_DIR / "analytics.json"

_lock = threading.Lock()
_in_memory_events: List[Dict[str, Any]] = []


def _load_events() -> List[Dict[str, Any]]:
    """Load existing recorded events from disk."""
    if not ANALYTICS_FILE.exists():
        return []
    try:
        content = ANALYTICS_FILE.read_text(encoding="utf-8")
        if not content.strip():
            return []
        data = json.loads(content)
        if isinstance(data, list):
            return data
        return []
    except Exception as exc:
        print(f"Warning loading analytics events: {exc}")
        return []


def _save_events(events: List[Dict[str, Any]]) -> None:
    """Save events to disk safely."""
    try:
        ANALYTICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        # Keep last 500 events
        trimmed = events[-500:]
        ANALYTICS_FILE.write_text(json.dumps(trimmed, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as exc:
        print(f"Warning saving analytics events: {exc}")


# Initialize in-memory cache from disk on module import
with _lock:
    _in_memory_events = _load_events()


def record_chat_event(
    query: str,
    status: str,  # 'grounded', 'blocked_input', 'insufficient_evidence', 'blocked_output'
    response_time_ms: float,
    reason: Optional[str] = None,
    sources_count: int = 0,
    best_score: Optional[float] = None,
    model_used: Optional[str] = None,
    pipeline_status: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Record an actual chat pipeline execution event.
    """
    event = {
        "id": f"evt-{len(_in_memory_events) + 1:04d}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "status": status,
        "response_time_ms": round(response_time_ms, 2),
        "reason": reason,
        "sources_count": sources_count,
        "best_score": round(best_score, 4) if best_score is not None else None,
        "model_used": model_used,
        "pipeline_summary": pipeline_status or {},
    }

    with _lock:
        _in_memory_events.append(event)
        _save_events(_in_memory_events)

    return event


def get_real_analytics() -> Dict[str, Any]:
    """
    Aggregate real, non-fabricated metrics from ChromaDB, processed documents,
    and actual recorded chat executions.
    """
    with _lock:
        events = list(_in_memory_events)

    total_questions = len(events)
    successful = sum(1 for e in events if e.get("status") == "grounded")
    blocked_input = sum(1 for e in events if e.get("status") == "blocked_input")
    blocked_output = sum(1 for e in events if e.get("status") == "blocked_output")
    total_blocked = blocked_input + blocked_output
    insufficient = sum(1 for e in events if e.get("status") == "insufficient_evidence")

    # Real response time calculation from recorded events
    if events:
        avg_latency = round(sum(e.get("response_time_ms", 0.0) for e in events) / len(events), 2)
    else:
        avg_latency = None

    # Real sources count calculation for successful grounded questions
    grounded_events = [e for e in events if e.get("status") == "grounded"]
    if grounded_events:
        avg_sources = round(sum(e.get("sources_count", 0) for e in grounded_events) / len(grounded_events), 2)
    else:
        avg_sources = 0.0

    # Real knowledge base statistics
    try:
        vs_stats = get_vector_store_stats()
        total_chunks = vs_stats.get("total_chunks_indexed", 0)
    except Exception:
        total_chunks = 0

    try:
        doc_files = list(PROCESSED_DIR.glob("*.json"))
        # Count unique filenames from processed json documents
        unique_docs = set()
        for f in doc_files:
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                fn = d.get("filename")
                if fn:
                    unique_docs.add(fn)
            except Exception:
                pass
        total_documents = len(unique_docs) if unique_docs else len(doc_files)
    except Exception:
        total_documents = 0

    # Reverse recent activity so newest is first (top 25)
    recent = list(reversed(events[-25:]))

    return {
        "knowledge_base": {
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "vector_store": "ChromaDB",
            "embedding_model": "all-MiniLM-L6-v2",
            "relevance_threshold": float(os.getenv("RAG_RELEVANCE_THRESHOLD", str(DEFAULT_SIMILARITY_THRESHOLD))),
        },
        "requests": {
            "total_questions": total_questions,
            "successful_responses": successful,
            "blocked_requests": total_blocked,
            "blocked_input_count": blocked_input,
            "blocked_output_count": blocked_output,
            "insufficient_evidence": insufficient,
            "success_rate_pct": round((successful / total_questions * 100), 1) if total_questions > 0 else 0.0,
            "avg_response_time_ms": avg_latency,
            "avg_sources_retrieved": avg_sources,
        },
        "recent_activity": recent,
    }
