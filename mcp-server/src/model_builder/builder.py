"""
Unified computational patient model orchestration layer.

Aggregates all physiological system builders into a single
simulation-ready computational patient model.

Round 4:
- System aggregation
- Medication profile integration
- Comorbidity cascade integration
- Global confidence synthesis
- Clinical priority synthesis
"""

from datetime import datetime

import structlog

from src.model_builder.cardiovascular import build_cardiovascular_system
from src.model_builder.comorbidity_map import build_comorbidity_map
from src.model_builder.hepatic import build_hepatic_system
from src.model_builder.medication_profile import build_medication_profile
from src.model_builder.metabolic import build_metabolic_system
from src.model_builder.renal import build_renal_system

logger = structlog.get_logger(__name__)


def assemble_patient_model(
    patient: dict,
    lab_observations: list[dict],
    vital_observations: list[dict],
    active_conditions: list[dict],
    active_medications: list[dict],
) -> dict:
    """
    Assemble the unified computational patient model.
    """

    logger.info(
        "builder.assemble_patient_model.start",
        patient_id=patient.get("id"),
    )

    # ============================================================
    # Physiological Systems
    # ============================================================

    renal_model = build_renal_system(
        patient=patient,
        lab_observations=lab_observations,
        active_conditions=active_conditions,
        active_medications=active_medications,
    )

    metabolic_model = build_metabolic_system(
        patient=patient,
        lab_observations=lab_observations,
        vital_observations=vital_observations,
        active_conditions=active_conditions,
        active_medications=active_medications,
    )

    cardiovascular_model = build_cardiovascular_system(
        patient=patient,
        lab_observations=lab_observations,
        vital_observations=vital_observations,
        active_conditions=active_conditions,
        active_medications=active_medications,
    )

    hepatic_model = build_hepatic_system(
        patient=patient,
        lab_observations=lab_observations,
        active_conditions=active_conditions,
        active_medications=active_medications,
    )

    system_models = {
        "renal": renal_model,
        "metabolic": metabolic_model,
        "cardiovascular": cardiovascular_model,
        "hepatic": hepatic_model,
    }

    # ============================================================
    # Cross-System Analysis
    # ============================================================

    medication_profile = build_medication_profile(
        medications=active_medications,
        active_conditions=active_conditions,
        current_egfr=renal_model.get("current_egfr"),
    )

    comorbidity_map = build_comorbidity_map(
        active_conditions=active_conditions,
    )

    # ============================================================
    # Aggregate Confidence
    # ============================================================

    subsystem_confidences = {
        system_name: model.get("confidence", {})
        for system_name, model in system_models.items()
    }

    confidence_levels = [
        conf.get("overall")
        for conf in subsystem_confidences.values()
        if conf.get("overall")
    ]

    if confidence_levels:
        if all(level == "high" for level in confidence_levels):
            overall_confidence = "high"
        elif any(level == "low" for level in confidence_levels):
            overall_confidence = "low"
        else:
            overall_confidence = "moderate"
    else:
        overall_confidence = "unknown"

    model_confidence = {
        "overall": overall_confidence,
        "systems": subsystem_confidences,
    }

    # ============================================================
    # Clinical Priority Synthesis
    # ============================================================

    clinical_priorities = []

    # ---- CKD progression ----
    kdigo = renal_model.get("kdigo_risk")
    renal_projection = renal_model.get("projection")
    reno_coverage = renal_model.get("renoprotective_coverage", {})
    nephro_burden = renal_model.get("nephrotoxic_burden", {})

    if kdigo and kdigo.get("risk_category") in ("high", "very_high"):
        clinical_priorities.append({
            "id": "ckd_progression_risk",
            "system": "renal",
            "priority_score": 92,
            "severity": "high",
            "progression_risk": "high",
            "intervention_leverage": "high",
            "title": "High risk CKD progression",
            "summary": (
                "Kidney disease progression risk is elevated based on "
                "KDIGO risk stratification and longitudinal trajectory."
            ),
            "drivers": [
                kdigo.get("risk_category"),
                reno_coverage.get("coverage_score"),
            ],
            "suggested_actions": [
                "Optimize renoprotective therapy",
                "Review nephrotoxic medications",
                "Monitor renal function closely",
            ],
            "monitoring_recommendations": [
                "Repeat BMP and UACR within 3 months",
            ],
            "evidence_basis": [
                "KDIGO risk classification",
                "eGFR trajectory analysis",
            ],
        })

    # ---- Missing SGLT2i ----
    if reno_coverage.get("coverage_score") == "missing_sglt2i_gap":
        clinical_priorities.append({
            "id": "sglt2_gap",
            "system": "renal",
            "priority_score": 88,
            "severity": "high",
            "progression_risk": "moderate",
            "intervention_leverage": "high",
            "title": "Missing SGLT2 inhibitor therapy",
            "summary": (
                "Patient may benefit from SGLT2 inhibitor therapy for "
                "renal and cardiovascular protection."
            ),
            "drivers": [
                "CKD",
                "Diabetes",
                "No active SGLT2 inhibitor",
            ],
            "suggested_actions": [
                "Evaluate SGLT2 inhibitor eligibility",
            ],
            "monitoring_recommendations": [
                "Monitor renal function after initiation",
            ],
            "evidence_basis": [
                "KDIGO 2024",
                "Renoprotective therapy assessment",
            ],
        })

    # ---- Nephrotoxic burden ----
    if nephro_burden.get("level") in ("moderate", "high"):
        clinical_priorities.append({
            "id": "nephrotoxic_burden",
            "system": "renal",
            "priority_score": 75,
            "severity": nephro_burden.get("level"),
            "progression_risk": "moderate",
            "intervention_leverage": "moderate",
            "title": "Elevated nephrotoxic medication burden",
            "summary": (
                "Current medication regimen includes nephrotoxic exposure "
                "which may accelerate renal decline."
            ),
            "drivers": [
                med.get("name")
                for med in nephro_burden.get("contributing_medications", [])
            ],
            "suggested_actions": [
                "Review medication safety profile",
                "Reduce nephrotoxic exposure if possible",
            ],
            "monitoring_recommendations": [
                "Monitor creatinine and potassium",
            ],
            "evidence_basis": [
                "Medication burden analysis",
            ],
        })

    # ---- Diabetes control ----
    glycemic = metabolic_model.get("glycemic_control")

    if glycemic in ("above_target", "well_above_target"):
        clinical_priorities.append({
            "id": "glycemic_control",
            "system": "metabolic",
            "priority_score": 82,
            "severity": "moderate",
            "progression_risk": "moderate",
            "intervention_leverage": "high",
            "title": "Suboptimal glycemic control",
            "summary": (
                "HbA1c remains above individualized target range."
            ),
            "drivers": [
                glycemic,
            ],
            "suggested_actions": [
                "Escalate diabetes therapy",
                "Review adherence and lifestyle factors",
            ],
            "monitoring_recommendations": [
                "Repeat HbA1c within 3 months",
            ],
            "evidence_basis": [
                "HbA1c trajectory analysis",
            ],
        })

    # ---- ASCVD risk ----
    ascvd = cardiovascular_model.get("ascvd_10yr_risk")

    if ascvd and ascvd.get("risk_category") in ("high", "very_high"):
        clinical_priorities.append({
            "id": "ascvd_risk",
            "system": "cardiovascular",
            "priority_score": 84,
            "severity": "high",
            "progression_risk": "moderate",
            "intervention_leverage": "high",
            "title": "Elevated cardiovascular risk",
            "summary": (
                "ASCVD risk estimation suggests elevated cardiovascular risk."
            ),
            "drivers": [
                ascvd.get("risk_category"),
            ],
            "suggested_actions": [
                "Optimize lipid management",
                "Optimize blood pressure control",
            ],
            "monitoring_recommendations": [
                "Repeat lipid panel within 6-12 months",
            ],
            "evidence_basis": [
                "ASCVD 10-year risk estimation",
            ],
        })

    # ---- MASLD / hepatic risk ----
    fib4 = hepatic_model.get("fib4")

    if fib4 and fib4.get("risk_category") in ("intermediate", "high"):
        clinical_priorities.append({
            "id": "hepatic_fibrosis_risk",
            "system": "hepatic",
            "priority_score": 70,
            "severity": fib4.get("risk_category"),
            "progression_risk": "moderate",
            "intervention_leverage": "moderate",
            "title": "Elevated hepatic fibrosis risk",
            "summary": (
                "Fibrosis risk assessment suggests possible progressive "
                "metabolic liver disease."
            ),
            "drivers": [
                fib4.get("risk_category"),
            ],
            "suggested_actions": [
                "Consider hepatic fibrosis workup",
                "Optimize metabolic risk factors",
            ],
            "monitoring_recommendations": [
                "Trend liver enzymes and fibrosis markers",
            ],
            "evidence_basis": [
                "FIB-4 risk assessment",
            ],
        })

    # Sort descending
    clinical_priorities = sorted(
        clinical_priorities,
        key=lambda x: x.get("priority_score", 0),
        reverse=True,
    )

    # ============================================================
    # Longitudinal Risk Summary
    # ============================================================

    longitudinal_risk_summary = {
        "renal_progression": renal_model.get("projection"),
        "diabetes_progression": metabolic_model.get("projection"),
        "cardiovascular_progression": cardiovascular_model.get("projection"),
        "hepatic_progression": hepatic_model.get("projection"),
    }

    # ============================================================
    # Intervention Opportunities
    # ============================================================

    intervention_opportunities = []

    for priority in clinical_priorities:
        intervention_opportunities.append({
            "priority_id": priority["id"],
            "system": priority["system"],
            "opportunity": priority["title"],
            "recommended_actions": priority["suggested_actions"],
            "priority_score": priority["priority_score"],
        })

    # ============================================================
    # Metadata
    # ============================================================

    model_metadata = {
        "generated_at": datetime.utcnow().isoformat(),
        "model_version": "4.1",
        "model_type": "computational_patient_model",
        "stateless": True,
    }

    logger.info(
        "builder.assemble_patient_model.complete",
        patient_id=patient.get("id"),
        priority_count=len(clinical_priorities),
        overall_confidence=overall_confidence,
    )

    return {
        "system_models": system_models,
        "medication_profile": medication_profile,
        "comorbidity_map": comorbidity_map,
        "clinical_priorities": clinical_priorities,
        "longitudinal_risk_summary": longitudinal_risk_summary,
        "intervention_opportunities": intervention_opportunities,
        "model_confidence": model_confidence,
        "model_metadata": model_metadata,
    }