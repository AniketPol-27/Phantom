"""
Tool: compare_interventions

Advanced comparative longitudinal intervention engine.
Uses real drug knowledge and trial evidence.
"""

import json
from typing import Annotated, Any

import structlog
from mcp.server.fastmcp import Context
from pydantic import Field

from src.evidence.drug_knowledge import (
    check_contraindications,
    get_drug,
    get_drug_effects,
    get_monitoring_requirements,
)
from src.evidence.trial_data import get_trials_for_drug
from src.model_builder.system_helpers import get_active_conditions_list
from src.sharp import SharpContextError, extract_sharp_context

logger = structlog.get_logger(__name__)


def _extract_scores_from_drug_knowledge(
    drug_name: str,
    patient_conditions: list[str],
    current_egfr: float | None,
) -> dict:
    """
    Extract real scores from drug knowledge base.
    Returns normalized 0-100 scores per dimension.
    """
    drug = get_drug(drug_name.lower().replace(" ", "_"))
    if not drug:
        # Try common name variations
        for name_variant in [
            drug_name.lower(),
            drug_name.lower().split()[0],
        ]:
            drug = get_drug(name_variant)
            if drug:
                break

    if not drug:
        return None

    effects = drug.get("effects", {})
    renal = effects.get("renal", {})
    cv = effects.get("cardiovascular", {})
    metabolic = effects.get("metabolic", {})
    weight = effects.get("weight", {})

    # Renal score — based on slope modifier and renoprotection
    slope_mod = renal.get("egfr_slope_modifier", 1.0)
    renoprotective = renal.get("renoprotective", False)
    if renoprotective and slope_mod < 0.7:
        renal_score = 95
    elif renoprotective and slope_mod < 0.85:
        renal_score = 82
    elif renoprotective:
        renal_score = 70
    elif slope_mod > 1.2:
        renal_score = 30  # nephrotoxic
    else:
        renal_score = 50

    # Metabolic score — based on HbA1c reduction
    hba1c_reduction = abs(metabolic.get("hba1c_reduction_percent", 0))
    if hba1c_reduction >= 1.5:
        metabolic_score = 95
    elif hba1c_reduction >= 1.0:
        metabolic_score = 80
    elif hba1c_reduction >= 0.5:
        metabolic_score = 65
    else:
        metabolic_score = 40

    # Cardiovascular score — based on MACE RR
    mace_rr = cv.get("mace_relative_risk", 1.0)
    if mace_rr < 0.80:
        cv_score = 95
    elif mace_rr < 0.90:
        cv_score = 82
    elif mace_rr <= 1.0:
        cv_score = 65
    else:
        cv_score = 35

    # Safety score — based on hypoglycemia and side effects
    hypo_risk = metabolic.get("hypoglycemia_risk", "low")
    hypo_map = {"very_low": 95, "low": 85, "moderate": 60, "high": 40}
    safety_score = hypo_map.get(hypo_risk, 70)

    # Adherence score — based on route and frequency
    route = drug.get("route", "oral")
    frequency = drug.get("frequency", "once_daily")
    adherence_factors = drug.get("adherence_factors", {})
    injection = adherence_factors.get("injection", False)
    titration = adherence_factors.get("titration_required", False)

    adherence_score = 90
    if injection:
        adherence_score -= 15
    if titration:
        adherence_score -= 5
    if "twice" in frequency:
        adherence_score -= 5

    # Check contraindications
    contraindications = check_contraindications(
        name=drug_name.lower(),
        patient_conditions=patient_conditions,
        patient_egfr=current_egfr,
    )

    # Get trial citations
    trials = get_trials_for_drug(drug_name.lower())
    trial_citations = [
        f"{t.get('trial_name')} ({t.get('journal')} {t.get('year_published')})"
        for t in trials[:3]
    ]

    # Weight effect
    weight_direction = weight.get("direction", "neutral")
    weight_kg = weight.get("expected_kg", 0)

    return {
        "renal_score": max(0, min(100, renal_score)),
        "metabolic_score": max(0, min(100, metabolic_score)),
        "cv_score": max(0, min(100, cv_score)),
        "safety_score": max(0, min(100, adherence_score)),
        "adherence_score": max(0, min(100, adherence_score)),
        "contraindications": contraindications,
        "trial_citations": trial_citations,
        "weight_direction": weight_direction,
        "weight_kg": weight_kg,
        "hba1c_reduction": hba1c_reduction,
        "mace_rr": mace_rr,
        "renoprotective": renoprotective,
        "drug_class": drug.get("drug_class", "unknown"),
        "cost_tier": drug.get("cost_tier", "$$"),
        "monitoring": get_monitoring_requirements(drug_name.lower()),
    }


async def compare_interventions(
    ctx: Context,
    patient_model: Annotated[
        dict[str, Any],
        Field(description="Computational patient model."),
    ],
    clinical_question: Annotated[
        str,
        Field(description="Clinical decision under evaluation."),
    ],
    interventions: Annotated[
        list[dict[str, Any]],
        Field(description="Interventions to compare.", min_length=2, max_length=5),
    ],
    prioritize_dimensions: Annotated[
        list[str] | None,
        Field(description="Preferred optimization dimensions.", default=None),
    ] = None,
) -> str:

    try:
        sharp = extract_sharp_context(ctx)
    except SharpContextError as e:
        return json.dumps({"error": "FHIR context required", "message": str(e)})

    logger.info(
        "compare_interventions.start",
        patient_id=sharp.patient_id_only,
        intervention_count=len(interventions),
    )

    system_models = patient_model.get("system_models", {})
    renal = system_models.get("renal", {})
    metabolic = system_models.get("metabolic", {})
    cardiovascular = system_models.get("cardiovascular", {})
    priorities = patient_model.get("clinical_priorities", [])

    # ---- Patient context for scoring ----
    current_egfr = renal.get("current_egfr")
    conditions_items = patient_model.get("conditions", {}).get("items", [])
    patient_condition_keys = [
        (c.get("display") or "").lower()
        for c in conditions_items
        if c.get("is_active")
    ]

    # ---- Dynamic weights based on patient priorities ----
    renal_weight = 1.0
    metabolic_weight = 1.0
    cv_weight = 1.0

    for priority in priorities:
        system = priority.get("system")
        score = priority.get("priority_score", 50)
        if system == "renal":
            renal_weight += score / 100
        elif system == "metabolic":
            metabolic_weight += score / 100
        elif system == "cardiovascular":
            cv_weight += score / 100

    comparisons = []

    # ============================================================
    # Evaluate Each Intervention
    # ============================================================

    for intervention in interventions:
        label = intervention.get("label", "Unnamed")
        drug_name = intervention.get("drug_name", label)
        drug_class = intervention.get("drug_class", "").lower()

        rationale = []
        longitudinal_benefits = []
        tradeoffs = []
        contraindication_warnings = []

        # Try to get real drug data
        drug_data = _extract_scores_from_drug_knowledge(
            drug_name=drug_name,
            patient_conditions=patient_condition_keys,
            current_egfr=current_egfr,
        )

        if drug_data:
            # Use real evidence-based scores
            renal_score = drug_data["renal_score"]
            metabolic_score = drug_data["metabolic_score"]
            cv_score = drug_data["cv_score"]
            safety_score = drug_data["safety_score"]
            adherence_score = drug_data["adherence_score"]
            trial_citations = drug_data["trial_citations"]
            drug_class = drug_data["drug_class"].lower()

            # Build rationale from real data
            if drug_data["renoprotective"]:
                rationale.append(
                    f"Renoprotective — eGFR slope modifier "
                    f"{drug_data.get('mace_rr', 'N/A')}"
                )
                longitudinal_benefits.append(
                    "Slows CKD progression with trial-level evidence"
                )

            if drug_data["hba1c_reduction"] > 0:
                rationale.append(
                    f"HbA1c reduction: -{drug_data['hba1c_reduction']}%"
                )

            if drug_data["mace_rr"] < 0.95:
                rationale.append(
                    f"CV benefit: MACE RR {drug_data['mace_rr']} "
                    f"({', '.join(trial_citations[:1])})"
                )
                longitudinal_benefits.append(
                    "Reduces major adverse cardiovascular events"
                )

            if drug_data["weight_direction"] == "loss":
                longitudinal_benefits.append(
                    f"Expected weight loss: {abs(drug_data['weight_kg'])} kg"
                )
            elif drug_data["weight_direction"] == "gain":
                tradeoffs.append(
                    f"Expected weight gain: +{abs(drug_data['weight_kg'])} kg"
                )

            # Contraindications
            for ci in drug_data["contraindications"]:
                severity = ci.get("severity", "relative")
                contraindication_warnings.append({
                    "condition": ci.get("condition"),
                    "severity": severity,
                    "warning": f"{'ABSOLUTE' if severity == 'absolute' else 'RELATIVE'} contraindication: {ci.get('condition')}",
                })
                if severity == "absolute":
                    renal_score = 0
                    metabolic_score = 0
                    cv_score = 0
                    tradeoffs.append(f"CONTRAINDICATED: {ci.get('condition')}")

        else:
            # Fallback to class-based scoring
            trial_citations = []
            if "sglt2" in drug_class:
                renal_score, metabolic_score, cv_score = 95, 72, 88
                safety_score, adherence_score = 82, 85
                trial_citations = ["DAPA-CKD (NEJM 2020)", "EMPA-KIDNEY (NEJM 2023)"]
                rationale.append("SGLT2i — strong renal and CV evidence")
                longitudinal_benefits.append("39-49% reduction in CKD progression")

            elif "glp1" in drug_class:
                renal_score, metabolic_score, cv_score = 68, 95, 84
                safety_score, adherence_score = 75, 72
                trial_citations = ["SUSTAIN-6 (NEJM 2016)", "LEADER (NEJM 2016)"]
                rationale.append("GLP-1 RA — strong glycemic and CV evidence")
                longitudinal_benefits.append("26% MACE reduction in high-risk patients")

            elif "insulin" in drug_class:
                renal_score, metabolic_score, cv_score = 52, 92, 55
                safety_score, adherence_score = 55, 45
                rationale.append("Insulin — strong glycemic lowering")
                tradeoffs.append("Hypoglycemia risk + weight gain")

            elif any(x in drug_class for x in ["ace", "arb"]):
                renal_score, metabolic_score, cv_score = 88, 52, 82
                safety_score, adherence_score = 80, 88
                trial_citations = ["REIN trial", "RENAAL (NEJM 2001)"]
                rationale.append("RAAS blockade — renal and CV protection")

            else:
                renal_score, metabolic_score, cv_score = 50, 50, 50
                safety_score, adherence_score = 60, 70
                rationale.append("Limited evidence profile in knowledge base")

        # ---- Weighted composite score ----
        total_weight = renal_weight + metabolic_weight + cv_weight + 2
        weighted_score = round(
            (
                renal_score * renal_weight
                + metabolic_score * metabolic_weight
                + cv_score * cv_weight
                + safety_score
                + adherence_score
            )
            / total_weight
        )

        comparisons.append({
            "label": label,
            "drug_name": drug_name,
            "drug_class": drug_class,
            "scores": {
                "renal_protection": renal_score,
                "metabolic_benefit": metabolic_score,
                "cardiovascular_benefit": cv_score,
                "safety": safety_score,
                "adherence": adherence_score,
                "weighted_composite": weighted_score,
            },
            "confidence": "high" if drug_data else "moderate",
            "evidence_based": bool(drug_data),
            "trial_citations": trial_citations,
            "rationale": rationale,
            "longitudinal_benefits": longitudinal_benefits,
            "tradeoffs": tradeoffs,
            "contraindication_warnings": contraindication_warnings,
            "absolute_contraindication": any(
                c.get("severity") == "absolute"
                for c in contraindication_warnings
            ),
        })

    # ---- Rank by weighted composite ----
    comparisons.sort(
        key=lambda x: x["scores"]["weighted_composite"],
        reverse=True,
    )

    # Filter out absolute contraindications from recommendation
    eligible = [c for c in comparisons if not c.get("absolute_contraindication")]
    top_choice = eligible[0] if eligible else comparisons[0]

    # ---- Strategic summary ----
    strategic_summary = (
        f"{top_choice['label']} provides the strongest projected "
        f"longitudinal benefit (composite score: "
        f"{top_choice['scores']['weighted_composite']}/100) "
        f"given this patient's dominant risk profile."
    )

    comparative_insights = []
    if len(comparisons) >= 2:
        best = comparisons[0]
        second = comparisons[1]
        score_diff = (
            best["scores"]["weighted_composite"]
            - second["scores"]["weighted_composite"]
        )
        comparative_insights.append(
            f"{best['label']} scores {score_diff} points above "
            f"{second['label']} on the patient-weighted composite."
        )

    response = {
        "clinical_question": clinical_question,
        "patient_context": {
            "priority_count": len(priorities),
            "current_egfr": current_egfr,
            "renal_risk": renal.get("kdigo_risk"),
            "glycemic_control": metabolic.get("glycemic_control"),
            "cardiovascular_risk": cardiovascular.get("ascvd_10yr_risk"),
            "scoring_weights": {
                "renal_weight": round(renal_weight, 2),
                "metabolic_weight": round(metabolic_weight, 2),
                "cardiovascular_weight": round(cv_weight, 2),
            },
        },
        "strategy_summary": strategic_summary,
        "comparative_insights": comparative_insights,
        "comparisons": comparisons,
        "recommended_intervention": top_choice,
        "methodology": (
            "Evidence-based longitudinal comparison using Phantom drug "
            "knowledge base, trial evidence, and patient-specific "
            "weighted scoring."
        ),
        "comparison_metadata": {
            "engine_version": "6.1",
            "comparison_type": "evidence_based_longitudinal_analysis",
            "evidence_sourced": sum(1 for c in comparisons if c.get("evidence_based")),
        },
    }

    logger.info(
        "compare_interventions.complete",
        patient_id=sharp.patient_id_only,
        recommended=top_choice["label"],
        top_score=top_choice["scores"]["weighted_composite"],
    )

    return json.dumps(response, indent=2, default=str)