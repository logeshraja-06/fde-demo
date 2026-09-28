"""
routes/config.py
----------------
Customer Profile & Configuration Endpoints for Phase 8.

ENDPOINTS:
  GET  /api/config   → Retrieve current customer profile & runtime settings
  POST /api/config   → Update customer configuration
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

from app.services.config_service import get_customer_config, save_customer_config

router = APIRouter(
    prefix="/api/config",
    tags=["Customer Configuration & Profile"],
)


class CustomerConfigUpdate(BaseModel):
    organization: Optional[str] = Field(None, description="Customer organization name")
    assistant_name: Optional[str] = Field(None, description="Branded assistant name")
    project: Optional[str] = Field(None, description="Project title")
    business_goal: Optional[str] = Field(None, description="High-level customer business goal")
    domains: Optional[List[str]] = Field(None, description="Supported knowledge domains")
    max_input_length: Optional[int] = Field(None, ge=10, le=10000)
    rag_top_k: Optional[int] = Field(None, ge=1, le=10)
    grounding_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    allow_unknown_answers: Optional[bool] = None
    show_sources: Optional[bool] = None
    mode: Optional[str] = Field(None, description="'customer' or 'engineering' demo role simulation")


@router.get("", summary="Get Current Customer Configuration")
def get_config():
    """Returns the active customer profile, branding, and runtime controls."""
    return get_customer_config()


@router.post("", summary="Update Customer Configuration")
def update_config(payload: CustomerConfigUpdate):
    """Updates runtime configuration without modifying source code."""
    data = payload.dict(exclude_unset=True)
    updated = save_customer_config(data)
    return {"success": True, "config": updated}
