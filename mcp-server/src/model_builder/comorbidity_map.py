"""
Comorbidity interaction mapping.

Identifies active disease cascades using teammate's get_cascade_modifiers.
"""

import structlog

from src.evidence.disease_progression import get_cascade_modifiers
from src.model_builder.system_helpers import get_active_conditions_list

logger = structlog.get_logger(__name__)


def build_comorbidity_map(active_conditions: list[dict]) -> dict:
    """
    Build the comorbidity interaction map.
    Returns active disease cascades.
    """

    condition_keys = get_active_conditions_list(active_conditions)

    cascades = []
    try:
        cascades = get_cascade_modifiers(condition_keys)
    except Exception as e:
        logger.warning("comorbidity_map.cascade_lookup_failed", error=str(e))

    return {
        "active_conditions": condition_keys,
        "active_cascades": cascades,
        "cascade_count": len(cascades),
    }