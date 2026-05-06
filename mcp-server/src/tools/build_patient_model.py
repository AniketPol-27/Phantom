"""
Tool: build_patient_model

Constructs a computational patient model from FHIR data.
This is the foundation tool that simulate_scenario and compare_interventions
operate on.

Round 2.5: Stub implementation that proves SHARP context extraction works.
Round 3: Real FHIR data fetching and basic patient model construction.
Round 4: Full system models with trajectories and risk scores.
"""

import json
from typing import Annotated

import structlog
from mcp.server.fastmcp import Context
from pydantic import Field

from src.sharp import SharpContextError, extract_sharp_context

logger = structlog.get_logger(__name__)


async def build_patient_model(
    ctx: Context,
    model_depth: Annotated[
        str,
        Field(
            description=(
                "'comprehensive' builds all physiological systems. "
                "'focused' builds only systems specified in focus_systems."
            ),
            default="comprehensive",
        ),
    ] = "comprehensive",
    lookback_months: Annotated[
        int,
        Field(
            description=(
                "How many months of historical data to pull for "
                "trajectory computation. Default 24 months."
            ),
            default=24,
            ge=6,
            le=60,
        ),
    ] = 24,
) -> str:
    """
    Build a computational patient model from the patient currently in SHARP context.

    Returns:
        JSON string containing the patient model (or stub response in Round 2.5)
    """
    try:
        sharp = extract_sharp_context(ctx)
    except SharpContextError as e:
        logger.error("build_patient_model.no_context", error=str(e))
        return json.dumps({
            "error": "FHIR context required",
            "message": str(e),
            "hint": (
                "This tool requires FHIR context. Make sure the user has "
                "authorized FHIR access for this MCP server in Prompt Opinion."
            ),
        })

    if not sharp.patient_id:
        return json.dumps({
            "error": "No patient in context",
            "message": (
                "A patient must be loaded in the workspace before calling "
                "this tool. The X-Patient-ID header was not provided and "
                "no patient claim was found in the FHIR access token."
            ),
        })

    logger.info(
        "build_patient_model.invoked",
        patient_id=sharp.patient_id_only,
        model_depth=model_depth,
        lookback_months=lookback_months,
    )

    # Round 2.5 stub response.
    # Round 3 will fetch real FHIR data and return an actual patient model.
    stub_response = {
        "status": "stub",
        "message": (
            "build_patient_model is wired up correctly. SHARP context "
            "extracted successfully. Real FHIR fetching coming in Round 3."
        ),
        "context_received": {
            "patient_id": sharp.patient_id_only,
            "fhir_url": sharp.fhir_url,
            "has_token": bool(sharp.fhir_token),
            "has_refresh_token": bool(sharp.refresh_token),
        },
        "parameters_received": {
            "model_depth": model_depth,
            "lookback_months": lookback_months,
        },
    }

    return json.dumps(stub_response, indent=2)