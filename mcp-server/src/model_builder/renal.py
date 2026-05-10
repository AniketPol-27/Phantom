"""
Renal system model.

Computes:
- Current eGFR (uses CKD-EPI 2021 from teammate's risk_equations)
- CKD stage classification
- eGFR trajectory (uses teammate's compute_trajectory)
- Albuminuria category
- KDIGO composite risk
- Renoprotective medication coverage
- Nephrotoxic medication burden
- Projected eGFR at 6, 12, 24 months (uses teammate's project_ckd_progression)
"""

import structlog

from src.evidence.disease_progression import project_ckd_progression
from src.evidence.risk_equations import (
    calculate_egfr_ckd_epi_2021,
    classify_albuminuria,
    classify_ckd_stage,
    compute_trajectory,
    kdigo_risk_matrix,
)
from src.model_builder.confidence import compute_system_confidence
from src.model_builder.system_helpers import (
    get_active_drug_classes,
    get_lab_value_history,
    get_latest_lab_value,
    has_condition,
)

logger = structlog.get_logger(__name__)


# Nephrotoxic drug classes that contribute to burden score
NEPHROTOXIC_BURDEN = {
    "nsaid": 3,
    "aminoglycoside": 3,
    "loop_diuretic": 1,  # mild — only at high doses or volume depletion
}

# Renoprotective drug classes
RENOPROTECTIVE_CLASSES = ["sglt2_inhibitor", "ace_inhibitor", "arb"]


def build_renal_system(
    patient: dict,
    lab_observations: list[dict],
    active_conditions: list[dict],
    active_medications: list[dict],
) -> dict:
    """
    Build the renal system model from parsed FHIR data.

    Args:
        patient: Parsed Patient dict (must have age, gender)
        lab_observations: All parsed lab observations
        active_conditions: All parsed active conditions
        active_medications: All parsed active medications

    Returns:
        Renal system dict with current state, trajectory, risk, projections.
    """
    age = patient.get("age")
    sex = patient.get("gender")

    # ---- Current eGFR ----
    # Try to use stored eGFR if available, otherwise compute from creatinine
    latest_egfr_obs = get_latest_lab_value(lab_observations, "egfr")
    latest_creatinine_obs = get_latest_lab_value(lab_observations, "creatinine")

    current_egfr = None
    egfr_source = None
    creatinine_value = None
    creatinine_date = None

    if latest_creatinine_obs:
        creatinine_value = latest_creatinine_obs["value"]
        creatinine_date = latest_creatinine_obs["date"]

    if latest_egfr_obs:
        current_egfr = latest_egfr_obs["value"]
        egfr_source = "observation"
    elif latest_creatinine_obs and age and sex:
        try:
            current_egfr = calculate_egfr_ckd_epi_2021(
                serum_creatinine=latest_creatinine_obs["value"],
                age=age,
                sex=sex,
            )
            egfr_source = "computed_from_creatinine"
        except Exception as e:
            logger.warning("renal.egfr_computation_failed", error=str(e))

    # ---- CKD stage ----
    ckd_stage_info = None
    if current_egfr is not None:
        try:
            ckd_stage_info = classify_ckd_stage(current_egfr)
        except Exception as e:
            logger.warning("renal.ckd_stage_classification_failed", error=str(e))

    # ---- eGFR trajectory ----
    # Prefer stored eGFR history, fallback to computing from creatinine history
    egfr_history = get_lab_value_history(lab_observations, "egfr")
    if not egfr_history and age and sex:
        creatinine_history = get_lab_value_history(lab_observations, "creatinine")
        if creatinine_history:
            egfr_history = []
            for entry in creatinine_history:
                try:
                    computed = calculate_egfr_ckd_epi_2021(
                        serum_creatinine=entry["value"],
                        age=age,
                        sex=sex,
                    )
                    egfr_history.append({
                        "value": computed,
                        "unit": "mL/min/1.73m^2",
                        "date": entry["date"],
                    })
                except Exception:
                    continue

    trajectory = None
    if len(egfr_history) >= 2:
        try:
            trajectory = compute_trajectory(egfr_history)
        except Exception as e:
            logger.warning("renal.trajectory_failed", error=str(e))

    # ---- Albuminuria ----
    latest_uacr = get_latest_lab_value(lab_observations, "uacr")
    albuminuria_info = None
    if latest_uacr:
        try:
            albuminuria_info = classify_albuminuria(latest_uacr["value"])
        except Exception as e:
            logger.warning("renal.albuminuria_classification_failed", error=str(e))

    # ---- KDIGO risk ----
    kdigo_risk = None
    if ckd_stage_info and albuminuria_info:
        try:
            kdigo_risk = kdigo_risk_matrix(
                ckd_stage=ckd_stage_info.get("stage"),
                albuminuria_category=albuminuria_info.get("category"),
            )
        except Exception as e:
            logger.warning("renal.kdigo_failed", error=str(e))

    # ---- Renoprotective coverage ----
    active_classes = get_active_drug_classes(active_medications)
    has_acei_arb = "ace_inhibitor" in active_classes or "arb" in active_classes
    has_sglt2i = "sglt2_inhibitor" in active_classes

    renoprotective_coverage = {
        "ace_inhibitor_or_arb": has_acei_arb,
        "sglt2_inhibitor": has_sglt2i,
        "coverage_score": _renoprotective_coverage_score(
            has_acei_arb=has_acei_arb,
            has_sglt2i=has_sglt2i,
            has_diabetes=has_condition(active_conditions, "type_2_diabetes"),
            has_ckd=has_condition(active_conditions, "chronic_kidney_disease"),
            albuminuria_category=albuminuria_info.get("category") if albuminuria_info else None,
        ),
    }

    # ---- Nephrotoxic burden ----
    nephrotoxic_score = 0
    nephrotoxic_meds = []
    for med in active_medications:
        if not med.get("is_active"):
            continue
        from src.model_builder.system_helpers import detect_drug_class
        drug_class = detect_drug_class(med.get("drug_name"))
        if drug_class in NEPHROTOXIC_BURDEN:
            nephrotoxic_score += NEPHROTOXIC_BURDEN[drug_class]
            nephrotoxic_meds.append({
                "name": med.get("drug_name"),
                "class": drug_class,
                "burden_points": NEPHROTOXIC_BURDEN[drug_class],
            })

    nephrotoxic_burden = {
        "score": nephrotoxic_score,
        "level": _classify_burden(nephrotoxic_score),
        "contributing_medications": nephrotoxic_meds,
    }

    # ---- Forward projection ----
    projection = None
    if (
        current_egfr is not None
        and trajectory
        and trajectory.get("slope_per_year") is not None
    ):
        try:
            projection = project_ckd_progression(
                current_egfr=current_egfr,
                egfr_slope=trajectory["slope_per_year"],
                has_diabetes=has_condition(active_conditions, "type_2_diabetes"),
                has_hypertension=has_condition(active_conditions, "hypertension"),
                albuminuria_category=albuminuria_info.get("category") if albuminuria_info else "A1",
                on_acei_or_arb=has_acei_arb,
                on_sglt2i=has_sglt2i,
                age=age or 60,
            )
        except Exception as e:
            logger.warning("renal.projection_failed", error=str(e))

    # ---- Confidence ----
    confidence = compute_system_confidence(
        required_labs=["creatinine", "uacr", "potassium"],
        lab_observations=lab_observations,
    )

    return {
        "current_egfr": current_egfr,
        "egfr_source": egfr_source,
        "egfr_unit": "mL/min/1.73m^2",
        "creatinine": {
            "value": creatinine_value,
            "unit": latest_creatinine_obs.get("unit") if latest_creatinine_obs else None,
            "date": creatinine_date,
        } if creatinine_value else None,
        "ckd_stage": ckd_stage_info,
        "egfr_trajectory": trajectory,
        "albuminuria": albuminuria_info,
        "kdigo_risk": kdigo_risk,
        "renoprotective_coverage": renoprotective_coverage,
        "nephrotoxic_burden": nephrotoxic_burden,
        "projection": projection,
        "confidence": confidence,
    }


def _renoprotective_coverage_score(
    has_acei_arb: bool,
    has_sglt2i: bool,
    has_diabetes: bool,
    has_ckd: bool,
    albuminuria_category: str | None,
) -> str:
    """Classify how well-covered the patient is for renoprotection."""
    if not has_ckd and not has_diabetes:
        return "not_indicated"

    coverage_count = sum([has_acei_arb, has_sglt2i])

    # SGLT2i is 1A indication for T2DM + CKD per KDIGO 2024
    if has_diabetes and has_ckd and not has_sglt2i:
        return "missing_sglt2i_gap"

    # ACEi/ARB indicated for any albuminuria
    if albuminuria_category in ("A2", "A3") and not has_acei_arb:
        return "missing_acei_arb_gap"

    if coverage_count >= 2:
        return "full"
    if coverage_count == 1:
        return "partial"
    return "none"


def _classify_burden(score: int) -> str:
    """Classify cumulative organ burden score."""
    if score == 0:
        return "none"
    if score <= 2:
        return "low"
    if score <= 5:
        return "moderate"
    return "high"