"""
Metabolic system model.

Computes:
- Current HbA1c and trajectory
- Glycemic control assessment
- Weight/BMI trajectory
- Adherence signal from medication refill patterns
- Projected HbA1c at 3, 6, 12 months
"""

import structlog

from src.evidence.disease_progression import project_diabetes_progression
from src.evidence.risk_equations import compute_trajectory
from src.model_builder.confidence import compute_system_confidence
from src.model_builder.system_helpers import (
    get_active_drug_classes,
    get_lab_value_history,
    get_latest_lab_value,
    has_condition,
)

logger = structlog.get_logger(__name__)


def build_metabolic_system(
    patient: dict,
    lab_observations: list[dict],
    vital_observations: list[dict],
    active_conditions: list[dict],
    active_medications: list[dict],
) -> dict:
    """Build the metabolic system model."""

    has_diabetes = has_condition(active_conditions, "type_2_diabetes")
    age = patient.get("age")

    # ---- HbA1c ----
    latest_hba1c = get_latest_lab_value(lab_observations, "hba1c")
    hba1c_history = get_lab_value_history(lab_observations, "hba1c")

    hba1c_trajectory = None
    if len(hba1c_history) >= 2:
        try:
            hba1c_trajectory = compute_trajectory(hba1c_history)
        except Exception as e:
            logger.warning("metabolic.hba1c_trajectory_failed", error=str(e))

    # ---- Glycemic control assessment ----
    target_hba1c = _hba1c_target(patient, active_conditions)
    glycemic_control = None
    if latest_hba1c:
        if latest_hba1c["value"] <= target_hba1c:
            glycemic_control = "at_target"
        elif latest_hba1c["value"] <= target_hba1c + 1.0:
            glycemic_control = "above_target"
        else:
            glycemic_control = "well_above_target"

    # ---- BMI / Weight trajectory ----
    bmi_history = get_lab_value_history(vital_observations, "bmi")
    weight_history = get_lab_value_history(vital_observations, "weight_kg")

    bmi_trajectory = None
    if len(bmi_history) >= 2:
        try:
            bmi_trajectory = compute_trajectory(bmi_history)
        except Exception as e:
            logger.warning("metabolic.bmi_trajectory_failed", error=str(e))

    weight_trajectory = None
    if len(weight_history) >= 2:
        try:
            weight_trajectory = compute_trajectory(weight_history)
        except Exception as e:
            logger.warning("metabolic.weight_trajectory_failed", error=str(e))

    # ---- Adherence signal from medication refills ----
    adherence_signal = _compute_adherence_signal(active_medications)

    # ---- Active diabetes drug classes ----
    drug_classes = get_active_drug_classes(active_medications)
    diabetes_drug_classes = [
        c for c in drug_classes
        if c in ("biguanide", "sulfonylurea", "sglt2_inhibitor", "glp1_agonist", "dpp4_inhibitor", "insulin")
    ]

    on_max_oral = (
        "biguanide" in drug_classes
        and (
            "sulfonylurea" in drug_classes
            or "dpp4_inhibitor" in drug_classes
            or "sglt2_inhibitor" in drug_classes
            or "glp1_agonist" in drug_classes
        )
    )

    # ---- Forward projection ----
    projection = None
    if (
        has_diabetes
        and latest_hba1c
        and hba1c_trajectory
        and hba1c_trajectory.get("slope_per_year") is not None
    ):
        try:
            current_bmi = bmi_history[-1]["value"] if bmi_history else None
            # Convert slope_per_year to slope_per_6_months
            slope_per_6mo = hba1c_trajectory["slope_per_year"] / 2.0
            projection = project_diabetes_progression(
                current_hba1c=latest_hba1c["value"],
                hba1c_slope=slope_per_6mo,
                years_since_diagnosis=_years_since_diagnosis(active_conditions, "type_2_diabetes"),
                current_medications=diabetes_drug_classes,
                bmi=current_bmi or 30.0,
                on_max_oral_therapy=on_max_oral,
            )
        except Exception as e:
            logger.warning("metabolic.projection_failed", error=str(e))

    # ---- Confidence ----
    confidence = compute_system_confidence(
        required_labs=["hba1c", "fasting_glucose"],
        lab_observations=lab_observations,
    )

    return {
        "has_diabetes": has_diabetes,
        "current_hba1c": {
            "value": latest_hba1c["value"] if latest_hba1c else None,
            "unit": latest_hba1c.get("unit") if latest_hba1c else "%",
            "date": latest_hba1c["date"] if latest_hba1c else None,
        } if latest_hba1c else None,
        "target_hba1c": target_hba1c,
        "glycemic_control": glycemic_control,
        "hba1c_trajectory": hba1c_trajectory,
        "bmi_trajectory": bmi_trajectory,
        "current_bmi": bmi_history[-1]["value"] if bmi_history else None,
        "weight_trajectory": weight_trajectory,
        "current_weight_kg": weight_history[-1]["value"] if weight_history else None,
        "active_diabetes_classes": diabetes_drug_classes,
        "on_max_oral_therapy": on_max_oral,
        "adherence_signal": adherence_signal,
        "projection": projection,
        "confidence": confidence,
    }


def _hba1c_target(patient: dict, active_conditions: list[dict]) -> float:
    """
    Determine individualized HbA1c target.

    Per ADA 2024:
    - <7.0% for most adults
    - <8.0% for elderly, multiple comorbidities, limited life expectancy
    - <6.5% if achievable without significant hypoglycemia
    """
    age = patient.get("age", 60)
    has_ckd = has_condition(active_conditions, "chronic_kidney_disease")

    if age >= 75 or has_ckd:
        return 8.0
    return 7.0


def _years_since_diagnosis(active_conditions: list[dict], condition_key: str) -> int:
    """Calculate years since condition was diagnosed."""
    from datetime import datetime
    from src.model_builder.system_helpers import CONDITION_KEYWORDS

    keywords = CONDITION_KEYWORDS.get(condition_key, [])
    for cond in active_conditions:
        code = (cond.get("code") or "").lower()
        display = (cond.get("display") or "").lower()
        for keyword in keywords:
            kw = keyword.lower()
            if kw in code or kw in display:
                onset = cond.get("onset_date")
                if onset:
                    try:
                        date = datetime.fromisoformat(onset.split("T")[0])
                        return max(0, datetime.utcnow().year - date.year)
                    except Exception:
                        pass
    return 5  # default assumption


def _compute_adherence_signal(medications: list[dict]) -> dict:
    """
    Estimate adherence based on medication refill patterns.

    Note: Without dispense history, this is a rough proxy. Returns a
    qualitative score per medication.
    """
    return {
        "method": "refill_gap_proxy",
        "note": "Adherence estimation requires MedicationDispense data which is not available.",
        "category": "unknown",
    }