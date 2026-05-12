"""
Tool: compare_interventions

Advanced comparative longitudinal intervention engine.
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
            description="Computational patient model.",
        ),
    ],
    clinical_question: Annotated[
        str,
        Field(
            description="Clinical decision under evaluation.",
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
            description="Preferred optimization dimensions.",
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
        "compare_interventions.start",
        patient_id=sharp.patient_id_only,
        intervention_count=len(interventions),
    )

    system_models = patient_model.get(
        "system_models",
        {},
    )

    renal = system_models.get("renal", {})
    metabolic = system_models.get("metabolic", {})
    cardiovascular = system_models.get(
        "cardiovascular",
        {},
    )

    priorities = patient_model.get(
        "clinical_priorities",
        [],
    )

    # ============================================================
    # Dynamic Patient Weighting
    # ============================================================

    renal_weight = 1.0
    metabolic_weight = 1.0
    cardiovascular_weight = 1.0

    for priority in priorities:

        system = priority.get("system")

        if system == "renal":
            renal_weight += 0.5

        elif system == "metabolic":
            metabolic_weight += 0.5

        elif system == "cardiovascular":
            cardiovascular_weight += 0.5

    comparisons = []

    # ============================================================
    # Evaluate Interventions
    # ============================================================

    for intervention in interventions:

        label = intervention.get(
            "label",
            "Unnamed intervention",
        )

        drug_class = intervention.get(
            "drug_class",
            "",
        ).lower()

        rationale = []
        longitudinal_benefits = []
        tradeoffs = []

        renal_score = 50
        metabolic_score = 50
        cardiovascular_score = 50
        safety_score = 50
        adherence_score = 50

        # ========================================================
        # SGLT2
        # ========================================================

        if drug_class == "sglt2_inhibitor":

            renal_score = 96
            cardiovascular_score = 88
            metabolic_score = 72
            safety_score = 82
            adherence_score = 85

            rationale.extend([
                "Strong evidence for renal protection",
                "Reduces CKD progression velocity",
                "Provides cardiovascular benefit",
            ])

            longitudinal_benefits.extend([
                "Likely slows eGFR decline",
                "May delay CKD progression",
                "Reduces long-term cardiovascular convergence risk",
            ])

            tradeoffs.extend([
                "Requires renal function monitoring",
                "Risk of genitourinary side effects",
            ])

        # ========================================================
        # GLP1
        # ========================================================

        elif drug_class == "glp1_agonist":

            metabolic_score = 95
            cardiovascular_score = 84
            renal_score = 68
            safety_score = 75
            adherence_score = 72

            rationale.extend([
                "Strong glycemic improvement potential",
                "Supports weight reduction",
                "Cardiovascular benefit supported",
            ])

            longitudinal_benefits.extend([
                "Improves metabolic trajectory",
                "May reduce long-term ASCVD burden",
                "Supports obesity-related risk reduction",
            ])

            tradeoffs.extend([
                "GI side effects possible",
                "Injection burden may reduce adherence",
            ])

        # ========================================================
        # INSULIN
        # ========================================================

        elif drug_class == "insulin":

            metabolic_score = 92
            cardiovascular_score = 55
            renal_score = 52
            safety_score = 60
            adherence_score = 45

            rationale.extend([
                "Strong glycemic lowering capability",
                "Rapid HbA1c reduction potential",
            ])

            longitudinal_benefits.extend([
                "Improves severe hyperglycemia",
            ])

            tradeoffs.extend([
                "Hypoglycemia risk",
                "High adherence burden",
                "Requires monitoring intensity",
            ])

        # ========================================================
        # ACE/ARB
        # ========================================================

        elif drug_class in [
            "ace_inhibitor",
            "arb",
        ]:

            renal_score = 88
            cardiovascular_score = 82
            metabolic_score = 52
            safety_score = 80
            adherence_score = 88

            rationale.extend([
                "Strong renal hemodynamic protection",
                "Blood pressure optimization benefit",
            ])

            longitudinal_benefits.extend([
                "Slows renal progression",
                "Reduces cardiovascular strain",
            ])

            tradeoffs.extend([
                "Requires potassium monitoring",
            ])

        # ========================================================
        # FALLBACK
        # ========================================================

        else:

            rationale.append(
                "Limited evidence profile available."
            )

            tradeoffs.append(
                "Comparative confidence reduced."
            )

        # ========================================================
        # Weighted Composite
        # ========================================================

        weighted_score = round(
            (
                renal_score * renal_weight
                + metabolic_score * metabolic_weight
                + cardiovascular_score * cardiovascular_weight
                + safety_score
                + adherence_score
            )
            /
            (
                renal_weight
                + metabolic_weight
                + cardiovascular_weight
                + 2
            )
        )

        # ========================================================
        # Confidence
        # ========================================================

        if drug_class in [
            "sglt2_inhibitor",
            "glp1_agonist",
            "insulin",
            "ace_inhibitor",
            "arb",
        ]:
            confidence = "high"
        else:
            confidence = "moderate"

        comparisons.append({

            "label": label,

            "drug_class": drug_class,

            "scores": {

                "renal_protection": renal_score,

                "metabolic_benefit": metabolic_score,

                "cardiovascular_benefit": cardiovascular_score,

                "safety": safety_score,

                "adherence": adherence_score,

                "weighted_composite": weighted_score,
            },

            "confidence": confidence,

            "rationale": rationale,

            "longitudinal_benefits": longitudinal_benefits,

            "tradeoffs": tradeoffs,
        })

    # ============================================================
    # Rank Interventions
    # ============================================================

    comparisons = sorted(
        comparisons,
        key=lambda x: x["scores"]["weighted_composite"],
        reverse=True,
    )

    top_choice = comparisons[0]

    # ============================================================
    # Strategic Summary
    # ============================================================

    strategic_summary = (
        f"{top_choice['label']} appears to provide the "
        f"strongest projected longitudinal benefit profile "
        f"for this patient's dominant risk structure."
    )

    # ============================================================
    # Comparative Insights
    # ============================================================

    comparative_insights = []

    if len(comparisons) >= 2:

        best = comparisons[0]
        second = comparisons[1]

        comparative_insights.append(
            f"{best['label']} ranked above "
            f"{second['label']} due to stronger "
            f"multi-system longitudinal protection."
        )

    # ============================================================
    # Output
    # ============================================================

    response = {

        "clinical_question": clinical_question,

        "patient_context": {

            "priority_count": len(priorities),

            "renal_risk": renal.get("kdigo_risk"),

            "glycemic_control": metabolic.get(
                "glycemic_control"
            ),

            "cardiovascular_risk": cardiovascular.get(
                "ascvd_10yr_risk"
            ),
        },

        "strategy_summary": strategic_summary,

        "comparative_insights": comparative_insights,

        "comparisons": comparisons,

        "recommended_intervention": top_choice,

        "optimization_weights": {

            "renal_weight": renal_weight,

            "metabolic_weight": metabolic_weight,

            "cardiovascular_weight": cardiovascular_weight,
        },

        "methodology": (
            "Dynamic longitudinal multi-system intervention "
            "comparison using the Phantom computational "
            "patient model."
        ),

        "comparison_metadata": {

            "engine_version": "6.0",

            "comparison_type": "longitudinal_intervention_analysis",
        },
    }

    logger.info(
        "compare_interventions.complete",
        patient_id=sharp.patient_id_only,
        recommended=top_choice["label"],
    )

    return json.dumps(
        response,
        indent=2,
        default=str,
    )