"""
Tool: simulate_scenario

Round 2.5: Stub. Real implementation in Round 4.
"""

import json
from typing import Annotated, Any

import structlog
from mcp.server.fastmcp import Context
from pydantic import Field

from src.sharp import SharpContextError, extract_sharp_context

logger = structlog.get_logger(__name__)


async def simulate_scenario(
    ctx: Context,
    patient_model: Annotated[
        dict[str, Any],
        Field(
            description=(
                "The patient model object returned by build_patient_model, "
                "or a model_id string referencing a cached model."
            ),
        ),
    ],
    scenario_type: Annotated[
        str,
        Field(
            description=(
                "The type of scenario to simulate. One of: "
                "'medication_change', 'inaction', 'diagnostic_gap', 'lifestyle_change'."
            ),
        ),
    ],
    scenario_details: Annotated[
        dict[str, Any] | None,
        Field(
            description=(
                "Scenario-specific parameters. For medication_change: "
                "{action, medication: {name, dose, frequency}}. "
                "For lifestyle_change: {changes: [{type, magnitude}]}. "
                "Not required for inaction or diagnostic_gap."
            ),
            default=None,
        ),
    ] = None,
    time_horizon_months: Annotated[
        int,
        Field(
            description="How far forward to project, in months.",
            default=12,
            ge=3,
            le=60,
        ),
    ] = 12,
) -> str:
    try:
        sharp = extract_sharp_context(ctx)
    except SharpContextError as e:
        return json.dumps({"error": "FHIR context required", "message": str(e)})

    logger.info(
        "simulate_scenario.invoked",
        patient_id=sharp.patient_id_only,
        scenario_type=scenario_type,
        time_horizon=time_horizon_months,
    )

    stub_response = {
        "status": "stub",
        "message": "simulate_scenario wired up. Real logic in Round 4.",
        "received": {
            "scenario_type": scenario_type,
            "time_horizon_months": time_horizon_months,
            "has_scenario_details": scenario_details is not None,
        },
    }

    return json.dumps(stub_response, indent=2)