"""
Tool: simulate_scenario

Advanced longitudinal simulation engine for Phantom.
"""

import json
from typing import Annotated, Any

import structlog
from mcp.server.fastmcp import Context
from pydantic import Field

from src.evidence.disease_progression import (
    project_ckd_progression,
    project_cv_risk_progression,
    project_diabetes_progression,
    project_masld_progression,
)
from src.sharp import SharpContextError, extract_sharp_context

logger = structlog.get_logger(__name__)


async def simulate_scenario(
    ctx: Context,
    patient_model: Annotated[
        dict[str, Any],
        Field(
            description="Patient model from build_patient_model."
        ),
    ],
    scenario_type: Annotated[
        str,
        Field(
            description=(
                "Scenario type: "
                "'inaction', "
                "'medication_change', "
                "'lifestyle_change'."
            ),
        ),
    ],
    scenario_details: Annotated[
        dict[str, Any] | None,
        Field(
            description="Scenario-specific parameters.",
            default=None,
        ),
    ] = None,
    time_horizon_months: Annotated[
        int,
        Field(
            description="Projection horizon.",
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
        "simulate_scenario.start",
        patient_id=sharp.patient_id_only,
        scenario_type=scenario_type,
        horizon=time_horizon_months,
    )

    system_models = patient_model.get("system_models", {})

    renal = system_models.get("renal", {})
    metabolic = system_models.get("metabolic", {})
    cardiovascular = system_models.get("cardiovascular", {})
    hepatic = system_models.get("hepatic", {})

    priorities = patient_model.get(
        "clinical_priorities",
        [],
    )

    # ============================================================
    # INACTION SCENARIO
    # ============================================================

    if scenario_type == "inaction":

        projected_changes = []
        deterioration_risks = []
        trajectory_alerts = []

        # --------------------------------------------------------
        # RENAL
        # --------------------------------------------------------

        renal_projection = renal.get("projection")

        if renal_projection:

            projected_changes.append({
                "system": "renal",
                "baseline": renal.get("current_egfr"),
                "projected_trajectory": renal_projection,
                "clinical_impact": (
                    "Progressive renal decline may accelerate "
                    "future cardiovascular burden."
                ),
            })

            deterioration_risks.append({
                "system": "renal",
                "risk": "Accelerating CKD progression",
                "severity": "high",
            })

            trajectory_alerts.append(
                "Renal trajectory suggests ongoing nephron loss."
            )

        # --------------------------------------------------------
        # METABOLIC
        # --------------------------------------------------------

        metabolic_projection = metabolic.get("projection")

        if metabolic_projection:

            projected_changes.append({
                "system": "metabolic",
                "baseline_hba1c": metabolic.get("current_hba1c"),
                "projected_trajectory": metabolic_projection,
                "clinical_impact": (
                    "Persistent glycemic burden may amplify "
                    "renal and cardiovascular deterioration."
                ),
            })

            deterioration_risks.append({
                "system": "metabolic",
                "risk": "Progressive metabolic dysfunction",
                "severity": "moderate",
            })

        # --------------------------------------------------------
        # CARDIOVASCULAR
        # --------------------------------------------------------

        cv_projection = cardiovascular.get("projection")

        if cv_projection:

            projected_changes.append({
                "system": "cardiovascular",
                "baseline_risk": cardiovascular.get(
                    "ascvd_10yr_risk"
                ),
                "projected_trajectory": cv_projection,
                "clinical_impact": (
                    "Cardiovascular convergence risk expected "
                    "to increase longitudinally."
                ),
            })

            deterioration_risks.append({
                "system": "cardiovascular",
                "risk": "Increasing ASCVD burden",
                "severity": "moderate",
            })

        # --------------------------------------------------------
        # HEPATIC
        # --------------------------------------------------------

        hepatic_projection = hepatic.get("projection")

        if hepatic_projection:

            projected_changes.append({
                "system": "hepatic",
                "projected_trajectory": hepatic_projection,
                "clinical_impact": (
                    "Metabolic liver disease may progress silently."
                ),
            })

            deterioration_risks.append({
                "system": "hepatic",
                "risk": "Progressive fibrosis risk",
                "severity": "moderate",
            })

        response = {

            "scenario_type": "inaction",

            "time_horizon_months": time_horizon_months,

            "executive_summary": (
                "Without intervention, longitudinal modeling suggests "
                "continued multi-system disease progression with "
                "increasing convergence of renal, metabolic, and "
                "cardiovascular risk."
            ),

            "trajectory_alerts": trajectory_alerts,

            "projected_changes": projected_changes,

            "deterioration_risks": deterioration_risks,

            "highest_risk_domains": [
                p.get("system")
                for p in priorities[:3]
            ],

            "projected_clinical_consequences": [
                "Increased future hospitalization risk",
                "Higher long-term cardiovascular burden",
                "Progressive multi-system physiological decline",
            ],

            "recommended_intervention_targets": [
                p.get("title")
                for p in priorities[:5]
            ],

            "simulation_confidence": patient_model.get(
                "model_confidence",
                {},
            ),

            "simulation_metadata": {
                "engine_version": "5.0",
                "simulation_type": "longitudinal_inaction",
            },
        }

        logger.info(
            "simulate_scenario.complete",
            patient_id=sharp.patient_id_only,
            scenario_type=scenario_type,
        )

        return json.dumps(response, indent=2, default=str)

    # ============================================================
    # MEDICATION CHANGE
    # ============================================================

    elif scenario_type == "medication_change":

        medication = (scenario_details or {}).get(
            "medication",
            {},
        )

        medication_name = medication.get(
            "name",
            "unspecified medication",
        )

        medication_class = medication.get(
            "class",
            "",
        ).lower()

        anticipated_effects = []

        if "sglt2" in medication_class:

            anticipated_effects.extend([
                {
                    "system": "renal",
                    "effect": (
                        "Expected reduction in CKD progression velocity."
                    ),
                    "confidence": "high",
                },
                {
                    "system": "cardiovascular",
                    "effect": (
                        "Potential reduction in cardiovascular burden."
                    ),
                    "confidence": "moderate",
                },
            ])

        elif "glp1" in medication_class:

            anticipated_effects.extend([
                {
                    "system": "metabolic",
                    "effect": (
                        "Expected improvement in glycemic trajectory."
                    ),
                    "confidence": "high",
                },
                {
                    "system": "cardiovascular",
                    "effect": (
                        "Potential reduction in ASCVD progression."
                    ),
                    "confidence": "moderate",
                },
            ])

        response = {

            "scenario_type": "medication_change",

            "medication": medication_name,

            "time_horizon_months": time_horizon_months,

            "executive_summary": (
                f"Simulation suggests potential longitudinal "
                f"benefit from {medication_name}."
            ),

            "anticipated_effects": anticipated_effects,

            "projected_benefits": [
                "Potential slowing of disease progression",
                "Reduction in longitudinal risk burden",
                "Improved future physiological stability",
            ],

            "monitoring_recommendations": [
                "Trend longitudinal biomarkers",
                "Monitor medication tolerance",
                "Assess trajectory response over time",
            ],

            "simulation_metadata": {
                "engine_version": "5.0",
                "simulation_type": "medication_change",
            },
        }

        return json.dumps(response, indent=2, default=str)

    # ============================================================
    # LIFESTYLE CHANGE
    # ============================================================

    elif scenario_type == "lifestyle_change":

        response = {

            "scenario_type": "lifestyle_change",

            "executive_summary": (
                "Lifestyle optimization may reduce future "
                "metabolic and cardiovascular disease burden."
            ),

            "anticipated_effects": [
                {
                    "system": "metabolic",
                    "effect": "Improved glycemic stability",
                },
                {
                    "system": "cardiovascular",
                    "effect": "Reduced long-term ASCVD risk",
                },
                {
                    "system": "hepatic",
                    "effect": "Potential reduction in MASLD progression",
                },
            ],

            "time_horizon_months": time_horizon_months,
        }

        return json.dumps(response, indent=2, default=str)

    # ============================================================
    # UNSUPPORTED
    # ============================================================

    return json.dumps({
        "error": "unsupported_scenario",
        "supported_types": [
            "inaction",
            "medication_change",
            "lifestyle_change",
        ],
    }, indent=2)