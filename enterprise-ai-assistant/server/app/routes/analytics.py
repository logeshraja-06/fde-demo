"""
routes/analytics.py
-------------------
API endpoints for Phase 6 Observability and Dashboard Metrics.

Provides:
  GET /analytics  (and /api/analytics)  - Aggregated real-time metrics and recent activity log
"""

from fastapi import APIRouter
from app.services.analytics_service import get_real_analytics

router = APIRouter(tags=["Observability & Analytics"])


@router.get(
    "",
    summary="Get honest, aggregated AI pipeline analytics and recent activity log",
    description="Returns real document counts, chunk counts, query volumes, guardrail breakdown, and recent execution events."
)
def analytics_endpoint():
    """
    Return real application metrics and observability data.
    """
    return get_real_analytics()
