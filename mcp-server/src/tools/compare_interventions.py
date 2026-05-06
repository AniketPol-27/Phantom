"""
Tool: compare_interventions

Round 2.5: Stub. Real implementation in Round 5.
"""

import json
from typing import Annotated, Any

import structlog
from mcp.server.fastmcp import Context
from pydantic import Field

from src.sharp import SharpContextError, extract_sharp_context

logger = structlog.get_logger(__name__)


async def compare_interventions(
    ctx: Context,
    patient_model: Annotated[
        dict[str, Any],
        Field(description="The patient model from build_patient_model."),
    ],
    clinical_question: Annotated[
        str,
        Field(description="The clinical decision being evaluated."),
    ],
    interventions: Annotated[
        list[dict[str, Any]],
        Field(
            description="The interventions to compare (2-5 options).",
            min_length=2,
            max_length=5,
        ),
    ],
    prioritize_dimensions: Annotated[
        list[str] | None,
        Field(
            description=(
                "Which outcome dimensions matter most for this patient and "
                "decision. Affects composite scoring weights."
            ),
            default=None,
        ),
    ] = None,
) -> str:
    try:
        sharp = extract_sharp_context(ctx)
    except SharpContextError as e:
        return json.dumps({"error": "FHIR context required", "message": str(e)})

    logger.info(
        "compare_interventions.invoked",
        patient_id=sharp.patient_id_only,
        question=clinical_question,
        intervention_count=len(interventions),
    )

    stub_response = {
        "status": "stub",
        "message": "compare_interventions wired up. Real logic in Round 5.",
        "received": {
            "clinical_question": clinical_question,
            "intervention_count": len(interventions),
            "intervention_labels": [i.get("label", "?") for i in interventions],
        },
    }

    return json.dumps(stub_response, indent=2)