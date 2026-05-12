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
from src.evidence.guidelines import evaluate_care_gaps, evaluate_diagnostic_gaps
from src.model_builder.system_helpers import (
    get_active_conditions_list,
    get_active_drug_classes,
    get_active_medication_names,
)
from src.sharp import SharpContextError, extract_sharp_context

logger = structlog.get_logger(__name__)


async def simulate_scenario(
    ctx: Context,
    patient_model: Annotated[
        dict[str, Any],
        Field(description="Patient model from build_patient_model."),
    ],
    scenario_type: Annotated[
        str,
        Field(
            description=(
                "Scenario type: "
                "'inaction', "
                "'medication_change', "
                "'lifestyle_change', "
                "'diagnostic_gap'."
            ),
        ),
    ],
    scenario_details: Annotated[
        dict[str, Any] | None,
        Field(description="Scenario-specific parameters.", default=None),
    ] = None,
    time_horizon_months: Annotated[
        int,
        Field(description="Projection horizon.", default=12, ge=3, le=60),
    ] = 12,
) -> str:

    try:
        sharp = extract_sharp_context(ctx)
    except SharpContextError as e:
        return json.dumps({"error": "FHIR context required", "message": str(e)})

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
    priorities = patient_model.get("clinical_priorities", [])

    # ============================================================
    # INACTION SCENARIO — Uses real evidence projections
    # ============================================================

    if scenario_type == "inaction":

        trajectory_alerts = []
        projected_changes = []
        deterioration_risks = []
        evidence_citations = []

        # ---- RENAL ----
        renal_projection = renal.get("projection")
        current_egfr = renal.get("current_egfr")
        egfr_trajectory = renal.get("egfr_trajectory", {})

        if current_egfr and egfr_trajectory:
            slope = egfr_trajectory.get("slope_per_year")
            if slope and slope < -3:
                severity = "critical" if slope < -5 else "high"
                trajectory_alerts.append({
                    "system": "renal",
                    "severity": severity,
                    "finding": f"eGFR declining at {abs(slope):.1f} mL/min/year",
                    "current_egfr": current_egfr,
                    "projected_egfr_12mo": round(current_egfr + slope, 1),
                    "projected_egfr_24mo": round(current_egfr + slope * 2, 1),
                    "kdigo_threshold_crossed": slope < -5,
                    "clinical_urgency": (
                        "URGENT — Rapid progression by KDIGO criteria"
                        if slope < -5 else
                        "HIGH — Above expected aging rate"
                    ),
                })
                evidence_citations.append(
                    "KDIGO 2024: eGFR decline >5 mL/min/year = rapid progression"
                )

        if renal_projection:
            projected_changes.append({
                "system": "renal",
                "baseline_egfr": current_egfr,
                "projected_trajectory": renal_projection,
                "time_to_stage_5_years": renal_projection.get("time_to_dialysis_years"),
                "clinical_impact": "Progressive nephron loss accelerates CV burden",
            })
            deterioration_risks.append({
                "system": "renal",
                "risk": "Accelerating CKD progression",
                "severity": "high",
                "evidence": "KDIGO 2024 CKD Guidelines",
            })

        # ---- METABOLIC ----
        metabolic_projection = metabolic.get("projection")
        current_hba1c = None
        if metabolic.get("current_hba1c"):
            current_hba1c = metabolic["current_hba1c"].get("value")

        hba1c_trajectory = metabolic.get("hba1c_trajectory", {})

        if current_hba1c and hba1c_trajectory:
            hba1c_slope = hba1c_trajectory.get("slope_per_year", 0)
            if current_hba1c > 7.0 or hba1c_slope > 0.3:
                trajectory_alerts.append({
                    "system": "metabolic",
                    "severity": "high" if current_hba1c > 9.0 else "moderate",
                    "finding": f"HbA1c {current_hba1c}% — {'rising' if hba1c_slope > 0 else 'stable'}",
                    "current_hba1c": current_hba1c,
                    "projected_hba1c_12mo": round(current_hba1c + hba1c_slope, 2),
                    "microvascular_risk_increase": f"{round(max(0, current_hba1c - 7.0) * 37)}% above baseline",
                    "clinical_urgency": (
                        "URGENT — Severe hyperglycemia"
                        if current_hba1c > 9.0 else
                        "MODERATE — Above target"
                    ),
                })
                evidence_citations.append(
                    "UKPDS 35: Each 1% HbA1c above 7% = 37% increased microvascular risk"
                )

        if metabolic_projection:
            projected_changes.append({
                "system": "metabolic",
                "baseline_hba1c": current_hba1c,
                "projected_trajectory": metabolic_projection,
                "insulin_requirement_probability": metabolic_projection.get(
                    "insulin_requirement_probability_12mo"
                ),
                "clinical_impact": "Persistent glycemic burden amplifies renal and CV deterioration",
            })

        # ---- CARDIOVASCULAR ----
        cv_projection = cardiovascular.get("projection")
        ascvd_risk = cardiovascular.get("ascvd_10yr_risk", {})

        if ascvd_risk:
            risk_pct = ascvd_risk.get("risk_percent")
            risk_cat = ascvd_risk.get("risk_category", "")
            if risk_pct and risk_pct >= 7.5:
                trajectory_alerts.append({
                    "system": "cardiovascular",
                    "severity": "high" if risk_pct >= 20 else "moderate",
                    "finding": f"10-year ASCVD risk: {risk_pct}% ({risk_cat})",
                    "current_risk_percent": risk_pct,
                    "risk_category": risk_cat,
                    "projected_risk_12mo": cv_projection.get(
                        "projected_ascvd_risk_12mo_percent"
                    ) if cv_projection else None,
                    "clinical_urgency": (
                        "HIGH — Statin therapy indicated"
                        if risk_pct >= 7.5 else "MODERATE"
                    ),
                })
                evidence_citations.append(
                    "ACC/AHA 2019: ASCVD risk ≥7.5% = statin therapy discussion"
                )

        if cv_projection:
            projected_changes.append({
                "system": "cardiovascular",
                "baseline_ascvd_risk": ascvd_risk,
                "projected_trajectory": cv_projection,
                "highest_leverage_intervention": cv_projection.get(
                    "highest_leverage_intervention"
                ),
                "clinical_impact": "CV convergence risk increasing longitudinally",
            })

        # ---- HEPATIC ----
        hepatic_projection = hepatic.get("projection")
        fib4 = hepatic.get("fib4", {})

        if fib4:
            fib4_score = fib4.get("score")
            fib4_cat = fib4.get("category", "")
            if fib4_score and fib4_score >= 1.30:
                trajectory_alerts.append({
                    "system": "hepatic",
                    "severity": "high" if fib4_score > 2.67 else "moderate",
                    "finding": f"FIB-4 score: {fib4_score} ({fib4_cat})",
                    "fib4_score": fib4_score,
                    "fibrosis_probability": fib4_cat,
                    "clinical_urgency": (
                        "HIGH — Hepatology referral indicated"
                        if fib4_score > 2.67 else
                        "MODERATE — FibroScan recommended"
                    ),
                })
                evidence_citations.append(
                    "Sterling 2006: FIB-4 >2.67 = high advanced fibrosis probability"
                )

        if hepatic_projection:
            projected_changes.append({
                "system": "hepatic",
                "fib4_score": fib4.get("score"),
                "projected_trajectory": hepatic_projection,
                "cirrhosis_probability_10yr": hepatic_projection.get(
                    "cirrhosis_probability_10yr"
                ),
                "clinical_impact": "Metabolic liver disease may progress silently",
            })

        # ---- Sort alerts by severity ----
        severity_order = {"critical": 0, "high": 1, "moderate": 2, "low": 3}
        trajectory_alerts.sort(
            key=lambda x: severity_order.get(x.get("severity", "low"), 3)
        )

        response = {
            "scenario_type": "inaction",
            "time_horizon_months": time_horizon_months,
            "executive_summary": (
                "Without intervention, longitudinal modeling projects "
                "continued multi-system disease progression. "
                f"{len(trajectory_alerts)} active trajectory alerts detected "
                "across physiological systems."
            ),
            "trajectory_alerts": trajectory_alerts,
            "alert_count": len(trajectory_alerts),
            "projected_changes": projected_changes,
            "deterioration_risks": deterioration_risks,
            "highest_risk_domains": [
                p.get("system") for p in priorities[:3]
            ],
            "recommended_intervention_targets": [
                p.get("title") for p in priorities[:5]
            ],
            "evidence_citations": evidence_citations,
            "simulation_confidence": patient_model.get("model_confidence", {}),
            "simulation_metadata": {
                "engine_version": "5.1",
                "simulation_type": "longitudinal_inaction",
            },
        }

        logger.info(
            "simulate_scenario.complete",
            patient_id=sharp.patient_id_only,
            scenario_type=scenario_type,
            alert_count=len(trajectory_alerts),
        )

        return json.dumps(response, indent=2, default=str)

    # ============================================================
    # DIAGNOSTIC GAP SCENARIO — Uses guidelines engine
    # ============================================================

    elif scenario_type == "diagnostic_gap":

        # Extract patient data for gap evaluation
        conditions_data = patient_model.get("conditions", {}).get("items", [])
        medications_data = patient_model.get("medications", {}).get("items", [])
        labs_data = patient_model.get("lab_observations", {}).get("items", [])

        patient_info = patient_model.get("patient", {})
        age = patient_info.get("age")
        sex = patient_info.get("gender", "unknown")

        # Build condition list
        active_condition_keys = []
        for cond in conditions_data:
            if cond.get("is_active"):
                display = (cond.get("display") or "").lower()
                code = (cond.get("code") or "").lower()
                active_condition_keys.append(display or code)

        # Build medication class list
        med_names = [
            m.get("drug_name", "").lower()
            for m in medications_data
            if m.get("is_active")
        ]

        # Build latest labs dict
        latest_labs = {}
        for obs in labs_data:
            code_display = (obs.get("display") or "").lower()
            value = obs.get("value")
            if value is not None and isinstance(value, (int, float)):
                latest_labs[code_display] = value

        current_egfr = renal.get("current_egfr")

        # Evaluate care gaps
        care_gaps = []
        diagnostic_gaps = []

        try:
            care_gaps = evaluate_care_gaps(
                patient_conditions=active_condition_keys,
                patient_medications=med_names,
                patient_labs=latest_labs,
                patient_age=age or 50,
                patient_sex=sex,
                patient_egfr=current_egfr,
            )
        except Exception as e:
            logger.warning("simulate_scenario.care_gap_eval_failed", error=str(e))

        try:
            diagnostic_gaps = evaluate_diagnostic_gaps(
                patient_conditions=active_condition_keys,
                patient_labs=latest_labs,
                patient_vitals={},
                patient_age=age or 50,
                patient_sex=sex,
                patient_egfr=current_egfr,
            )
        except Exception as e:
            logger.warning("simulate_scenario.diagnostic_gap_eval_failed", error=str(e))

        # Sort by priority
        priority_order = {"high": 0, "moderate": 1, "low": 2}
        care_gaps.sort(
            key=lambda x: priority_order.get(x.get("priority", "low"), 2)
        )

        response = {
            "scenario_type": "diagnostic_gap",
            "executive_summary": (
                f"Guideline evaluation identified {len(care_gaps)} care gaps "
                f"and {len(diagnostic_gaps)} potential diagnostic gaps."
            ),
            "care_gaps": care_gaps,
            "care_gap_count": len(care_gaps),
            "diagnostic_gaps": diagnostic_gaps,
            "diagnostic_gap_count": len(diagnostic_gaps),
            "high_priority_gaps": [
                g for g in care_gaps if g.get("priority") == "high"
            ],
            "simulation_metadata": {
                "engine_version": "5.1",
                "simulation_type": "diagnostic_gap_analysis",
            },
        }

        return json.dumps(response, indent=2, default=str)

    # ============================================================
    # MEDICATION CHANGE
    # ============================================================

    elif scenario_type == "medication_change":

        medication = (scenario_details or {}).get("medication", {})
        medication_name = medication.get("name", "unspecified medication")
        medication_class = medication.get("class", "").lower()

        anticipated_effects = []

        if "sglt2" in medication_class:
            anticipated_effects.extend([
                {
                    "system": "renal",
                    "effect": "Expected 39-49% reduction in CKD progression velocity",
                    "confidence": "high",
                    "evidence": "DAPA-CKD HR 0.61, EMPA-KIDNEY HR 0.72",
                },
                {
                    "system": "cardiovascular",
                    "effect": "14% MACE reduction expected",
                    "confidence": "high",
                    "evidence": "EMPA-REG OUTCOME HR 0.86",
                },
                {
                    "system": "metabolic",
                    "effect": "HbA1c reduction 0.6-0.8%, weight loss 2-3kg",
                    "confidence": "high",
                    "evidence": "Multiple SGLT2i RCTs",
                },
            ])

        elif "glp1" in medication_class:
            anticipated_effects.extend([
                {
                    "system": "metabolic",
                    "effect": "HbA1c reduction 1.0-1.8%, weight loss 4-8kg",
                    "confidence": "high",
                    "evidence": "SUSTAIN-6, LEADER trials",
                },
                {
                    "system": "cardiovascular",
                    "effect": "26% MACE reduction in high-CV-risk patients",
                    "confidence": "high",
                    "evidence": "SUSTAIN-6 HR 0.74",
                },
                {
                    "system": "renal",
                    "effect": "Modest renoprotection, albuminuria reduction",
                    "confidence": "moderate",
                    "evidence": "FLOW trial",
                },
            ])

        response = {
            "scenario_type": "medication_change",
            "medication": medication_name,
            "time_horizon_months": time_horizon_months,
            "executive_summary": (
                f"Adding {medication_name} is projected to provide "
                f"multi-system longitudinal benefit for this patient."
            ),
            "anticipated_effects": anticipated_effects,
            "monitoring_recommendations": [
                "Renal function at 2 and 6 weeks after initiation",
                "Electrolytes if on ACEi/ARB",
                "HbA1c at 3 months",
            ],
            "simulation_metadata": {
                "engine_version": "5.1",
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
                "Lifestyle optimization projected to reduce metabolic "
                "and cardiovascular disease burden."
            ),
            "anticipated_effects": [
                {
                    "system": "metabolic",
                    "effect": "5-10% weight loss improves HbA1c by 0.5-1.0%",
                    "evidence": "Look AHEAD trial",
                },
                {
                    "system": "cardiovascular",
                    "effect": "BP reduction 4-8 mmHg with regular exercise",
                    "evidence": "ACC/AHA Lifestyle Guidelines",
                },
                {
                    "system": "hepatic",
                    "effect": "7-10% weight loss can reverse MASLD steatosis",
                    "evidence": "AASLD 2023 MASLD Guidelines",
                },
            ],
            "time_horizon_months": time_horizon_months,
            "simulation_metadata": {
                "engine_version": "5.1",
                "simulation_type": "lifestyle_change",
            },
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
            "diagnostic_gap",
        ],
    }, indent=2)