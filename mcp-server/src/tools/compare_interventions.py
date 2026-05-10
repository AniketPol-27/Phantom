"""
Tool: compare_interventions

Compares multiple interventions against the computational
patient model and ranks likely clinical benefit.
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
        Field(
            description="The computational patient model.",
        ),
    ],
    clinical_question: Annotated[
        str,
        Field(
            description="The clinical decision being evaluated.",
        ),
    ],
    interventions: Annotated[
        list[dict[str, Any]],
        Field(
            description="Interventions to compare.",
            min_length=2,
            max_length=5,
        ),
    ],
    prioritize_dimensions: Annotated[
        list[str] | None,
        Field(
            description="Preferred outcome dimensions.",
            default=None,
        ),
    ] = None,
) -> str:

    try:
        sharp = extract_sharp_context(ctx)
    except SharpContextError as e:
        return json.dumps({
            "error": "FHIR context required",
            "message": str(e),
        })

    logger.info(
        "compare_interventions.invoked",
        patient_id=sharp.patient_id_only,
        intervention_count=len(interventions),
    )

    renal = (
        patient_model.get("system_models", {})
        .get("renal", {})
    )

    metabolic = (
        patient_model.get("system_models", {})
        .get("metabolic", {})
    )

    priorities = patient_model.get(
        "clinical_priorities",
        [],
    )

    comparisons = []

    for intervention in interventions:

        label = intervention.get("label", "Unnamed intervention")
        drug_class = intervention.get("drug_class", "").lower()

        renal_score = 50
        metabolic_score = 50
        cardiovascular_score = 50
        safety_score = 50
        adherence_score = 50

        rationale = []

        # ========================================================
        # SGLT2 Inhibitors
        # ========================================================

        if drug_class == "sglt2_inhibitor":

            renal_score = 95
            cardiovascular_score = 88
            metabolic_score = 72
            safety_score = 80
            adherence_score = 85

            rationale.extend([
                "Strong renal protection benefit",
                "Reduces CKD progression risk",
                "Cardiovascular protection supported",
            ])

            reno_coverage = renal.get(
                "renoprotective_coverage",
                {},
            )

            if reno_coverage.get(
                "coverage_score"
            ) == "missing_sglt2i_gap":
                renal_score += 5
                rationale.append(
                    "Addresses current renoprotective therapy gap"
                )

        # ========================================================
        # GLP1 Agonists
        # ========================================================

        elif drug_class == "glp1_agonist":

            metabolic_score = 94
            cardiovascular_score = 82
            renal_score = 68
            safety_score = 75
            adherence_score = 70

            rationale.extend([
                "Strong HbA1c reduction potential",
                "Supports weight reduction",
                "Cardiovascular benefit potential",
            ])

        # ========================================================
        # Insulin
        # ========================================================

        elif drug_class == "insulin":

            metabolic_score = 92
            cardiovascular_score = 55
            renal_score = 50
            safety_score = 60
            adherence_score = 45

            rationale.extend([
                "Strong glycemic reduction",
                "Higher adherence burden",
                "Hypoglycemia monitoring required",
            ])

        # ========================================================
        # Generic fallback
        # ========================================================

        else:
            rationale.append(
                "Limited evidence model available for this intervention"
            )

        composite_score = round(
            (
                renal_score
                + metabolic_score
                + cardiovascular_score
                + safety_score
                + adherence_score
            ) / 5
        )

        comparisons.append({
            "label": label,
            "drug_class": drug_class,

            "scores": {
                "renal_protection": renal_score,
                "metabolic_benefit": metabolic_score,
                "cardiovascular_benefit": cardiovascular_score,
                "safety": safety_score,
                "adherence": adherence_score,
                "composite": composite_score,
            },

            "rationale": rationale,
        })

    # ============================================================
    # Sort Best First
    # ============================================================

    comparisons = sorted(
        comparisons,
        key=lambda x: x["scores"]["composite"],
        reverse=True,
    )

    # ============================================================
    # Recommendation
    # ============================================================

    top_choice = comparisons[0] if comparisons else None

    response = {
        "clinical_question": clinical_question,

        "patient_context": {
            "priority_count": len(priorities),
            "renal_risk": renal.get("kdigo_risk"),
            "glycemic_control": metabolic.get(
                "glycemic_control"
            ),
        },

        "comparisons": comparisons,

        "recommended_intervention": top_choice,

        "methodology": (
            "Deterministic multi-system intervention scoring "
            "using the Phantom computational patient model."
        ),
    }

    return json.dumps(response, indent=2, default=str)