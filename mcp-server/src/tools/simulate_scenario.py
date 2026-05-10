"""
Tool: simulate_scenario

Simulates longitudinal clinical scenarios against the
computational patient model.
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
                "The patient model object returned by build_patient_model."
            ),
        ),
    ],
    scenario_type: Annotated[
        str,
        Field(
            description=(
                "Scenario type: "
                "'medication_change', 'inaction', "
                "'diagnostic_gap', 'lifestyle_change'."
            ),
        ),
    ],
    scenario_details: Annotated[
        dict[str, Any] | None,
        Field(
            description="Scenario-specific details.",
            default=None,
        ),
    ] = None,
    time_horizon_months: Annotated[
        int,
        Field(
            description="Projection horizon in months.",
            default=12,
            ge=3,
            le=60,
        ),
    ] = 12,
) -> str:

    try:
        sharp = extract_sharp_context(ctx)
    except SharpContextError as e:
        return json.dumps({
            "error": "FHIR context required",
            "message": str(e),
        })

    logger.info(
        "simulate_scenario.invoked",
        patient_id=sharp.patient_id_only,
        scenario_type=scenario_type,
        horizon=time_horizon_months,
    )

    system_models = patient_model.get("system_models", {})

    renal = system_models.get("renal", {})
    metabolic = system_models.get("metabolic", {})
    cardiovascular = system_models.get("cardiovascular", {})
    hepatic = system_models.get("hepatic", {})

    # ============================================================
    # INACTION SCENARIO
    # ============================================================

    if scenario_type == "inaction":

        key_changes = []

        renal_projection = renal.get("projection")
        if renal_projection:
            key_changes.append({
                "system": "renal",
                "finding": "Projected renal decline without intervention",
                "projection": renal_projection,
            })

        diabetes_projection = metabolic.get("projection")
        if diabetes_projection:
            key_changes.append({
                "system": "metabolic",
                "finding": "Glycemic burden expected to worsen",
                "projection": diabetes_projection,
            })

        cv_projection = cardiovascular.get("projection")
        if cv_projection:
            key_changes.append({
                "system": "cardiovascular",
                "finding": "Cardiovascular risk progression expected",
                "projection": cv_projection,
            })

        hepatic_projection = hepatic.get("projection")
        if hepatic_projection:
            key_changes.append({
                "system": "hepatic",
                "finding": "Metabolic liver disease progression risk",
                "projection": hepatic_projection,
            })

        response = {
            "scenario_type": "inaction",

            "summary": (
                "Without intervention, current longitudinal trends suggest "
                "continued multi-system disease progression."
            ),

            "time_horizon_months": time_horizon_months,

            "baseline_priorities": patient_model.get(
                "clinical_priorities",
                [],
            ),

            "projected_outcomes": {
                "renal": renal_projection,
                "metabolic": diabetes_projection,
                "cardiovascular": cv_projection,
                "hepatic": hepatic_projection,
            },

            "key_changes": key_changes,

            "monitoring_recommendations": [
                "Close longitudinal follow-up recommended",
                "Monitor trajectory acceleration",
                "Reassess intervention opportunities",
            ],

            "confidence": patient_model.get(
                "model_confidence",
                {},
            ),
        }

        return json.dumps(response, indent=2, default=str)

    # ============================================================
    # MEDICATION CHANGE
    # ============================================================

    elif scenario_type == "medication_change":

        medication = (scenario_details or {}).get("medication", {})
        medication_name = medication.get("name")

        response = {
            "scenario_type": "medication_change",

            "summary": (
                f"Simulation prepared for medication change involving "
                f"{medication_name or 'unspecified medication'}."
            ),

            "note": (
                "Round 4 implementation includes preliminary medication "
                "change scaffolding. Advanced physiological response "
                "simulation will be expanded in future rounds."
            ),

            "time_horizon_months": time_horizon_months,

            "anticipated_system_effects": [
                {
                    "system": "renal",
                    "possible_effect": (
                        "Renal trajectory may improve depending on "
                        "medication class and CKD status."
                    ),
                },
                {
                    "system": "metabolic",
                    "possible_effect": (
                        "HbA1c trajectory and metabolic burden may change."
                    ),
                },
                {
                    "system": "cardiovascular",
                    "possible_effect": (
                        "Cardiovascular risk profile may shift."
                    ),
                },
            ],

            "confidence": "moderate",
        }

        return json.dumps(response, indent=2, default=str)

    # ============================================================
    # Unsupported Scenario
    # ============================================================

    return json.dumps({
        "error": "unsupported_scenario",
        "supported_types": [
            "inaction",
            "medication_change",
        ],
    }, indent=2)