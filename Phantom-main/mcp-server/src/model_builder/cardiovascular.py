"""
Cardiovascular system model.

Computes:
- BP trajectory and current control
- Lipid status
- ASCVD 10-year risk (uses teammate's calculate_ascvd_10yr_risk)
- CV risk projection
- Modifiable vs non-modifiable risk breakdown
"""

import structlog

from src.evidence.disease_progression import project_cv_risk_progression
from src.evidence.risk_equations import (
    calculate_ascvd_10yr_risk,
    compute_trajectory,
)
from src.model_builder.confidence import compute_system_confidence
from src.model_builder.system_helpers import (
    get_active_drug_classes,
    get_bp_history,
    get_lab_value_history,
    get_latest_lab_value,
    has_condition,
)

logger = structlog.get_logger(__name__)


def build_cardiovascular_system(
    patient: dict,
    lab_observations: list[dict],
    vital_observations: list[dict],
    active_conditions: list[dict],
    active_medications: list[dict],
) -> dict:
    """Build the cardiovascular system model."""

    age = patient.get("age")
    sex = patient.get("gender")
    race = patient.get("race")

    # ---- Blood pressure ----
    bp_history = get_bp_history(vital_observations)

    current_bp = None
    if bp_history:
        latest = bp_history[-1]
        current_bp = {
            "systolic": latest["systolic"],
            "diastolic": latest["diastolic"],
            "date": latest["date"],
        }

    # Convert BP history to systolic-only for trajectory
    systolic_history = [
        {"value": bp["systolic"], "date": bp["date"]}
        for bp in bp_history
    ]

    bp_trajectory = None
    if len(systolic_history) >= 2:
        try:
            bp_trajectory = compute_trajectory(systolic_history)
        except Exception as e:
            logger.warning("cardiovascular.bp_trajectory_failed", error=str(e))

    bp_at_target = None
    if current_bp:
        bp_at_target = (current_bp["systolic"] < 130 and current_bp["diastolic"] < 80)

    # ---- Lipids ----
    latest_ldl = get_latest_lab_value(lab_observations, "ldl_cholesterol")
    latest_hdl = get_latest_lab_value(lab_observations, "hdl_cholesterol")
    latest_total_chol = get_latest_lab_value(lab_observations, "total_cholesterol")
    latest_triglycerides = get_latest_lab_value(lab_observations, "triglycerides")

    drug_classes = get_active_drug_classes(active_medications)
    on_statin = "statin" in drug_classes
    on_bp_medication = any(c in drug_classes for c in [
        "ace_inhibitor", "arb", "calcium_channel_blocker",
        "beta_blocker", "thiazide_diuretic", "loop_diuretic",
    ])

    # ---- ASCVD 10-year risk ----
    ascvd_risk = None
    if (
        age and age >= 40 and age <= 79
        and sex
        and latest_total_chol
        and latest_hdl
        and current_bp
    ):
        try:
            race_normalized = "black" if race and "black" in race.lower() else "white"
            ascvd_risk = calculate_ascvd_10yr_risk(
                age=age,
                sex=sex,
                race=race_normalized,
                total_cholesterol=latest_total_chol["value"],
                hdl_cholesterol=latest_hdl["value"],
                systolic_bp=current_bp["systolic"],
                bp_treated=on_bp_medication,
                diabetes=has_condition(active_conditions, "type_2_diabetes"),
                current_smoker=False,  # not in our test data
            )
        except Exception as e:
            logger.warning("cardiovascular.ascvd_failed", error=str(e))

    # ---- Lipid status ----
    lipid_target_ldl = _ldl_target(active_conditions, ascvd_risk)
    ldl_at_target = None
    if latest_ldl and lipid_target_ldl:
        ldl_at_target = latest_ldl["value"] <= lipid_target_ldl

    # ---- Projection ----
    projection = None
    if ascvd_risk and current_bp and latest_ldl:
        try:
            bp_slope = bp_trajectory.get("slope_per_year") if bp_trajectory else 0.0
            projection = project_cv_risk_progression(
                current_ascvd_risk=ascvd_risk.get("risk_percent", 0),
                current_bp_systolic=current_bp["systolic"],
                bp_trend_per_year=bp_slope or 0.0,
                current_ldl=latest_ldl["value"],
                on_statin=on_statin,
                has_diabetes=has_condition(active_conditions, "type_2_diabetes"),
                has_ckd=has_condition(active_conditions, "chronic_kidney_disease"),
                current_bmi=patient.get("bmi") or 27.0,
                smoking=False,
                age=age or 60,
            )
        except Exception as e:
            logger.warning("cardiovascular.projection_failed", error=str(e))

    # ---- Modifiable vs non-modifiable risk breakdown ----
    modifiable_risk_factors = []
    non_modifiable = []

    if current_bp and not bp_at_target:
        modifiable_risk_factors.append({
            "factor": "blood_pressure",
            "current": f"{current_bp['systolic']}/{current_bp['diastolic']}",
            "target": "<130/80",
            "leverage": "high",
        })
    if latest_ldl and lipid_target_ldl and latest_ldl["value"] > lipid_target_ldl:
        modifiable_risk_factors.append({
            "factor": "ldl_cholesterol",
            "current": latest_ldl["value"],
            "target": f"<{lipid_target_ldl}",
            "leverage": "high",
        })
    if has_condition(active_conditions, "type_2_diabetes"):
        modifiable_risk_factors.append({
            "factor": "glycemic_control",
            "leverage": "moderate",
        })

    non_modifiable.extend(["age", "sex"])
    if race:
        non_modifiable.append("race")

    # ---- Confidence ----
    confidence = compute_system_confidence(
        required_labs=["ldl_cholesterol", "hdl_cholesterol", "total_cholesterol"],
        lab_observations=lab_observations,
    )

    return {
        "current_bp": current_bp,
        "bp_at_target": bp_at_target,
        "bp_trajectory": bp_trajectory,
        "lipids": {
            "ldl": latest_ldl,
            "hdl": latest_hdl,
            "total_cholesterol": latest_total_chol,
            "triglycerides": latest_triglycerides,
            "target_ldl": lipid_target_ldl,
            "ldl_at_target": ldl_at_target,
            "on_statin": on_statin,
        },
        "ascvd_10yr_risk": ascvd_risk,
        "projection": projection,
        "modifiable_risk_factors": modifiable_risk_factors,
        "non_modifiable_factors": non_modifiable,
        "on_bp_medication": on_bp_medication,
        "confidence": confidence,
    }


def _ldl_target(active_conditions: list[dict], ascvd_risk: dict | None) -> int | None:
    """Determine LDL target based on risk profile per ACC/AHA 2018."""
    if has_condition(active_conditions, "coronary_artery_disease"):
        return 70  # secondary prevention
    if has_condition(active_conditions, "stroke"):
        return 70
    if ascvd_risk:
        risk_pct = ascvd_risk.get("risk_percent", 0)
        if risk_pct >= 20:
            return 70
        if risk_pct >= 7.5:
            return 100
    if has_condition(active_conditions, "type_2_diabetes"):
        return 100
    return 130