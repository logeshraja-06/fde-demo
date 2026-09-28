"""
services/config_service.py
--------------------------
Customer Profile and Runtime Configuration Service for Phase 8:
Forward Deployed Engineering Customer Implementation Simulation.

Supports dynamic customer configuration without rewriting code:
- Organization Name
- Assistant Branding Name
- Knowledge Domains (e.g. HR, Finance, IT)
- Max Input Length
- RAG Top K
- Grounding Threshold
- Allow Unknown Answers
- Show Sources
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("enterprise_ai.config")

BASE_DIR = Path(__file__).resolve().parents[2]   # server/
CONFIG_FILE = BASE_DIR / "data" / "customer_config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "customer": "Acme Corporation",
    "organization": "Acme Corporation",
    "assistant_name": "Acme Knowledge Assistant",
    "project": "Internal Knowledge Assistant",
    "business_goal": "Help employees quickly find answers from approved company documentation.",
    "domains": ["HR", "Finance", "IT"],
    "max_input_length": 2000,
    "rag_top_k": 3,
    "grounding_threshold": 0.35,
    "allow_unknown_answers": True,
    "show_sources": True,
    "mode": "engineering",  # 'customer' or 'engineering' demo role simulation
    "version": "1.5.0",
}


def get_customer_config() -> Dict[str, Any]:
    """Retrieve current customer configuration, creating default file if not yet saved."""
    if not CONFIG_FILE.exists():
        try:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as exc:
            logger.warning("Could not write initial config file: %s", exc)
        return DEFAULT_CONFIG.copy()

    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        merged = DEFAULT_CONFIG.copy()
        merged.update(data)
        return merged
    except Exception as exc:
        logger.error("Failed to read customer configuration: %s. Using defaults.", exc)
        return DEFAULT_CONFIG.copy()


def save_customer_config(new_config: Dict[str, Any]) -> Dict[str, Any]:
    """Persist updated customer configuration to server/data/customer_config.json."""
    if CONFIG_FILE.exists():
        try:
            current = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            current = DEFAULT_CONFIG.copy()
    else:
        current = DEFAULT_CONFIG.copy()

    current.update(new_config)

    # Validate types & bounds safely
    if "rag_top_k" in current:
        current["rag_top_k"] = max(1, min(10, int(current["rag_top_k"])))
    if "grounding_threshold" in current:
        current["grounding_threshold"] = max(0.0, min(1.0, float(current["grounding_threshold"])))
    if "max_input_length" in current:
        current["max_input_length"] = max(10, min(10000, int(current["max_input_length"])))

    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(current, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Saved customer configuration for organization '%s'", current.get("organization"))
    return current
