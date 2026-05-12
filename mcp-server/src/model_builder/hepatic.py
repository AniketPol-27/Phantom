"""
Hepatic system model.

Computes:
- FIB-4 score (uses teammate's calculate_fib4)
- MASLD risk markers
- Liver enzyme trajectory
- Hepatotoxic medication burden
- Drug metabolism capacity estimate
"""

import structlog

from src.evidence.disease_progression import project_masld_progression
from src.evidence.risk_equations import calculate_fib4, compute_trajectory
from src.model_builder.confidence import compute_system_confidence
from src.model_builder.system_helpers import (
    detect_drug_class,
    get_lab_value_history,
    get_latest_lab_value,
    has_condition,
)

logger = structlog.get_logger(__name__)


HEPATOTOXIC_BURDEN = {
    "statin": 1,  # mild — usually monitored
    "nsaid": 1,
}


def build_hepatic_system(
    patient: dict,
    lab_observations: list[dict],
    active_conditions: list[dict],
    active_medications: list[dict],
) -> dict:
    """Build the hepatic system model."""

    age = patient.get("age")

    # ---- Liver enzymes ----
    latest_ast = get_latest_lab_value(lab_observations, "ast")
    latest_alt = get_latest_lab_value(lab_observations, "alt")
    latest_platelets = get_latest_lab_value(lab_observations, "platelets")
    latest_albumin = get_latest_lab_value(lab_observations, "albumin")
    latest_bilirubin = get_latest_lab_value(lab_observations, "total_bilirubin")

    # ---- ALT trajectory ----
    alt_history = get_lab_value_history(lab_observations, "alt")
    alt_trajectory = None
    if len(alt_history) >= 2:
        try:
            alt_trajectory = compute_trajectory(alt_history)
        except Exception as e:
            logger.warning("hepatic.alt_trajectory_failed", error=str(e))

    # Persistently elevated ALT (≥2 readings >40)
    persistent_alt_elevation = (
        sum(1 for entry in alt_history if entry["value"] > 40) >= 2
    )

    # ---- FIB-4 ----
    fib4_info = None
    if age and latest_ast and latest_alt and latest_platelets:
        try:
            fib4_info = calculate_fib4(
                age=age,
                ast=latest_ast["value"],
                alt=latest_alt["value"],
                platelet_count=latest_platelets["value"],
            )
        except Exception as e:
            logger.warning("hepatic.fib4_failed", error=str(e))

    # ---- MASLD risk assessment ----
    metabolic_risk_factors = []
    if has_condition(active_conditions, "type_2_diabetes"):
        metabolic_risk_factors.append("type_2_diabetes")
    if has_condition(active_conditions, "obesity"):
        metabolic_risk_factors.append("obesity")
    if has_condition(active_conditions, "dyslipidemia"):
        metabolic_risk_factors.append("dyslipidemia")
    if has_condition(active_conditions, "hypertension"):
        metabolic_risk_factors.append("hypertension")

    masld_risk_level = "low"
    if persistent_alt_elevation and len(metabolic_risk_factors) >= 2:
        masld_risk_level = "high"
    elif persistent_alt_elevation or len(metabolic_risk_factors) >= 2:
        masld_risk_level = "moderate"

    # ---- Hepatotoxic burden ----
    hepatotoxic_score = 0
    hepatotoxic_meds = []
    for med in active_medications:
        if not med.get("is_active"):
            continue
        drug_class = detect_drug_class(med.get("drug_name"))
        if drug_class in HEPATOTOXIC_BURDEN:
            hepatotoxic_score += HEPATOTOXIC_BURDEN[drug_class]
            hepatotoxic_meds.append({
                "name": med.get("drug_name"),
                "class": drug_class,
                "burden_points": HEPATOTOXIC_BURDEN[drug_class],
            })

    # ---- MASLD projection ----
    projection = None
    if fib4_info and metabolic_risk_factors:
        try:
            alt_trend_str = "stable"
            if alt_trajectory:
                slope = alt_trajectory.get("slope_per_year", 0)
                if slope > 5:
                    alt_trend_str = "rising"
                elif slope < -5:
                    alt_trend_str = "falling"

            projection = project_masld_progression(
                fib4_score=fib4_info.get("score", 0),
                has_diabetes=has_condition(active_conditions, "type_2_diabetes"),
                bmi=patient.get("bmi") or 30.0,
                alt_trend=alt_trend_str,
                alcohol_use="none",
            )
        except Exception as e:
            logger.warning("hepatic.projection_failed", error=str(e))

    # ---- Confidence ----
    confidence = compute_system_confidence(
        required_labs=["ast", "alt", "platelets"],
        lab_observations=lab_observations,
    )

    return {
        "ast": latest_ast,
        "alt": latest_alt,
        "platelets": latest_platelets,
        "albumin": latest_albumin,
        "bilirubin": latest_bilirubin,
        "alt_trajectory": alt_trajectory,
        "persistent_alt_elevation": persistent_alt_elevation,
        "fib4": fib4_info,
        "masld_risk": {
            "level": masld_risk_level,
            "metabolic_risk_factors": metabolic_risk_factors,
            "persistent_alt_elevation": persistent_alt_elevation,
        },
        "hepatotoxic_burden": {
            "score": hepatotoxic_score,
            "level": _classify_burden(hepatotoxic_score),
            "contributing_medications": hepatotoxic_meds,
        },
        "projection": projection,
        "confidence": confidence,
    }


def _classify_burden(score: int) -> str:
    if score == 0:
        return "none"
    if score <= 2:
        return "low"
    if score <= 5:
        return "moderate"
    return "high"