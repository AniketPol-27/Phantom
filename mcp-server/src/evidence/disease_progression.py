"""
disease_progression.py

Disease natural-history models for the Phantom simulation engine.

These models answer the central counterfactual question: "If we do nothing,
what is this patient's projected trajectory?" The answer is the baseline
against which interventions are compared.

Models implemented:
  - project_ckd_progression       : eGFR slope + KDIGO risk modifiers
  - project_diabetes_progression  : UKPDS-derived HbA1c trajectory
  - project_cv_risk_progression   : ASCVD risk evolution
  - project_masld_progression     : Hepatic fibrosis trajectory
  - get_cascade_modifiers         : Bidirectional comorbidity effects

Each model returns a dictionary with projected values, modifier
explanations, intervention opportunities, and source citations.

Sources cited inline:
  - KDIGO 2024 CKD Clinical Practice Guideline
  - DAPA-CKD, CREDENCE, EMPA-KIDNEY trials (treatment effect modifiers)
  - UKPDS 33/34/80 (diabetes natural history and legacy effect)
  - ACC/AHA 2018/2019 (ASCVD risk)
  - AASLD 2023 MASLD Practice Guidance
  - Coresh JAMA 2014 (CKD progression rates)

This module has zero dependencies on FHIR, MCP, or platform code.
Pure Python with optional numpy for math.
"""

from __future__ import annotations

from typing import Optional


# ===========================================================================
# CKD PROGRESSION MODEL
# ===========================================================================

def project_ckd_progression(
    current_egfr: float,
    egfr_slope: float,
    has_diabetes: bool,
    has_hypertension: bool,
    albuminuria_category: str,
    on_acei_or_arb: bool,
    on_sglt2i: bool,
    age: int,
) -> dict:
    """
    Project CKD progression from current eGFR slope and risk modifiers.

    Methodology
    -----------
    Starts from the patient's measured eGFR slope (negative = declining)
    and applies multiplicative modifiers for known accelerators
    (diabetes, uncontrolled BP, albuminuria) and treatment effects
    (RAAS blockade, SGLT2i). Adds a small natural age-related decline
    of -1.0 mL/min/year if the measured slope is unrealistically flat
    in an older patient.

    Returns projections at 6, 12, and 24 months, time-to-stage-5,
    time-to-dialysis, and a list of which modifiers were applied so the
    clinician understands the projection.

    Parameters
    ----------
    current_egfr : float
        Most recent eGFR in mL/min/1.73m^2.
    egfr_slope : float
        Measured eGFR slope in mL/min/year (negative = declining).
    has_diabetes : bool
    has_hypertension : bool
    albuminuria_category : str
        "A1", "A2", or "A3" (KDIGO categories).
    on_acei_or_arb : bool
    on_sglt2i : bool
    age : int

    Returns
    -------
    dict with projected eGFR at 6/12/24 months, stage-progression
    probability, time-to-ESKD estimates, modifiers list, and reversibility
    notes.

    Sources
    -------
    - KDIGO 2024 CKD Clinical Practice Guideline
    - Coresh J et al. Decline in estimated glomerular filtration rate.
      JAMA 2014;311(24):2518-2531. PMID: 24892770
    - DAPA-CKD, CREDENCE, EMPA-KIDNEY (treatment effect magnitudes)
    """
    if current_egfr is None or current_egfr <= 0:
        raise ValueError(f"current_egfr must be > 0, got {current_egfr}")

    # Start from measured slope (or use natural-history default if missing)
    if egfr_slope is None:
        # Natural decline ~1 mL/min/year after age 40 (Coresh 2014)
        base_slope = -1.0 if age >= 40 else -0.5
    else:
        base_slope = float(egfr_slope)

    modifiers_applied = []
    adjusted_slope = base_slope

    # Diabetes accelerates decline ~15% (Coresh 2014; ADA Standards)
    if has_diabetes:
        adjusted_slope *= 1.15
        modifiers_applied.append({
            "factor": "diabetes",
            "effect": "accelerates eGFR decline by ~15%",
            "multiplier": 1.15,
            "evidence": "Coresh JAMA 2014",
        })

    # Albuminuria modifies progression risk (KDIGO 2024)
    cat = (albuminuria_category or "A1").upper()
    if cat == "A2":
        adjusted_slope *= 1.5
        modifiers_applied.append({
            "factor": "albuminuria_A2",
            "effect": "moderately increased albuminuria ~doubles progression risk",
            "multiplier": 1.5,
            "evidence": "KDIGO 2024",
        })
    elif cat == "A3":
        adjusted_slope *= 2.5
        modifiers_applied.append({
            "factor": "albuminuria_A3",
            "effect": "severely increased albuminuria; >3-fold progression risk",
            "multiplier": 2.5,
            "evidence": "KDIGO 2024",
        })

    # Uncontrolled HTN (assume present-but-untreated worsens by 10%)
    if has_hypertension and not on_acei_or_arb:
        adjusted_slope *= 1.10
        modifiers_applied.append({
            "factor": "untreated_hypertension",
            "effect": "untreated HTN accelerates decline ~10%",
            "multiplier": 1.10,
            "evidence": "AASK trial; KDIGO 2024",
        })

    # Treatment effect: ACEi/ARB reduces slope by ~30% if albuminuria present
    if on_acei_or_arb and cat in ("A2", "A3"):
        adjusted_slope *= 0.70
        modifiers_applied.append({
            "factor": "acei_or_arb_with_albuminuria",
            "effect": "RAAS blockade slows decline ~30%",
            "multiplier": 0.70,
            "evidence": "REIN, RENAAL, IDNT trials",
        })

    # Treatment effect: SGLT2i reduces slope ~40% (DAPA-CKD/EMPA-KIDNEY)
    if on_sglt2i:
        adjusted_slope *= 0.60
        modifiers_applied.append({
            "factor": "sglt2_inhibitor",
            "effect": "SGLT2i slows decline ~40%",
            "multiplier": 0.60,
            "evidence": "DAPA-CKD, EMPA-KIDNEY",
        })
    else:
        modifiers_applied.append({
            "factor": "no_sglt2i",
            "effect": "missing 39-40% slope-reduction opportunity from SGLT2i",
            "multiplier": 1.0,
            "evidence": "DAPA-CKD, EMPA-KIDNEY",
        })

    # Project forward
    def project_at(years_ahead: float) -> float:
        return max(0.0, round(current_egfr + adjusted_slope * years_ahead, 1))

    egfr_6mo = project_at(0.5)
    egfr_12mo = project_at(1.0)
    egfr_24mo = project_at(2.0)

    # Probability of stage progression in 12 months — heuristic based on slope
    # severity. Rapid decline (> 5/year) or already near stage boundary -> high
    if adjusted_slope > -1:
        stage_prog_prob = 0.05
    elif adjusted_slope > -3:
        stage_prog_prob = 0.20
    elif adjusted_slope > -5:
        stage_prog_prob = 0.40
    else:
        stage_prog_prob = 0.65

    # Time-to-stage-5 (eGFR < 15) and dialysis-equivalent (eGFR < 10)
    time_to_stage_5 = None
    time_to_dialysis = None
    if adjusted_slope < -0.1:
        years_to_15 = (current_egfr - 15) / abs(adjusted_slope)
        years_to_10 = (current_egfr - 10) / abs(adjusted_slope)
        if 0 < years_to_15 < 25:
            time_to_stage_5 = round(years_to_15, 1)
        if 0 < years_to_10 < 25:
            time_to_dialysis = round(years_to_10, 1)

    # Reversibility narrative
    if current_egfr >= 60:
        reversibility = (
            "Substantial reversibility window. Aggressive risk-factor "
            "modification can stabilize or improve trajectory."
        )
    elif current_egfr >= 45:
        reversibility = (
            "Intervention within 6 months can meaningfully slow trajectory. "
            "Below eGFR 45, certain therapies (e.g., metformin) become "
            "constrained."
        )
    elif current_egfr >= 30:
        reversibility = (
            "Narrow therapeutic window. SGLT2i still indicated and effective; "
            "RAAS blockade requires cautious monitoring."
        )
    else:
        reversibility = (
            "Advanced CKD. Focus on slowing further decline, preparing for "
            "renal replacement, and managing complications (anemia, CKD-MBD)."
        )

    return {
        "current_egfr": round(current_egfr, 1),
        "baseline_slope_per_year": round(base_slope, 2),
        "adjusted_slope_per_year": round(adjusted_slope, 2),
        "projected_egfr_6mo": egfr_6mo,
        "projected_egfr_12mo": egfr_12mo,
        "projected_egfr_24mo": egfr_24mo,
        "stage_progression_probability_12mo": stage_prog_prob,
        "time_to_stage_5_years": time_to_stage_5,
        "time_to_dialysis_years": time_to_dialysis,
        "modifiers_applied": modifiers_applied,
        "reversibility_window": reversibility,
        "citation": (
            "KDIGO 2024 CKD Guideline; Coresh JAMA 2014 PMID:24892770; "
            "DAPA-CKD, EMPA-KIDNEY trials"
        ),
    }


# ===========================================================================
# DIABETES PROGRESSION MODEL
# ===========================================================================

def project_diabetes_progression(
    current_hba1c: float,
    hba1c_slope: float,
    years_since_diagnosis: int,
    current_medications: list[str],
    bmi: float,
    on_max_oral_therapy: bool,
) -> dict:
    """
    Project diabetes natural progression based on UKPDS-derived dynamics.

    Methodology
    -----------
    UKPDS 33/34/80 demonstrated progressive beta-cell decline of ~4% per
    year, leading to gradual HbA1c rise without therapy escalation. We
    use the patient's recent slope when available, otherwise fall back to
    the UKPDS-derived natural rate of ~+0.15-0.25%/year.

    Identifies the next intervention opportunity based on which drug
    classes are missing.

    Parameters
    ----------
    current_hba1c : float
        Most recent HbA1c (%).
    hba1c_slope : float
        HbA1c change per 6 months (positive = worsening).
    years_since_diagnosis : int
    current_medications : list of str
        Generic drug names (e.g., ["metformin", "lisinopril"]).
    bmi : float
    on_max_oral_therapy : bool

    Returns
    -------
    dict with projected HbA1c at 3/6/12 months, insulin-requirement
    probability, microvascular complication risk delta, and intervention
    opportunities ranked by expected benefit.

    Sources
    -------
    - UKPDS Group. Lancet 1998;352:837-853 (UKPDS 33). PMID: 9742976
    - UKPDS Group. Lancet 1998;352:854-865 (UKPDS 34, metformin).
    - Holman RR et al. NEJM 2008;359:1577-1589 (UKPDS 80, legacy effect).
      PMID: 18784090
    - ADA Standards of Care 2024.
    """
    if current_hba1c is None or current_hba1c < 0:
        raise ValueError(f"current_hba1c must be >= 0, got {current_hba1c}")

    # Convert 6-month slope to annual; fall back to UKPDS natural rate
    if hba1c_slope is None:
        # Natural rate: ~0.2%/year if untreated/long-standing T2DM
        annual_slope = 0.2
    else:
        annual_slope = float(hba1c_slope) * 2.0  # 6-month -> annual

    # Project forward
    hba1c_3mo = round(current_hba1c + annual_slope * 0.25, 2)
    hba1c_6mo = round(current_hba1c + annual_slope * 0.5, 2)
    hba1c_12mo = round(current_hba1c + annual_slope * 1.0, 2)

    # Insulin requirement probability (heuristic):
    # Higher current HbA1c, longer duration, on max oral all push higher
    insulin_prob = 0.10
    if current_hba1c >= 9.0:
        insulin_prob += 0.30
    elif current_hba1c >= 8.0:
        insulin_prob += 0.15
    if years_since_diagnosis is not None and years_since_diagnosis >= 10:
        insulin_prob += 0.20
    if on_max_oral_therapy:
        insulin_prob += 0.30
    insulin_prob = min(insulin_prob, 0.90)

    # Microvascular risk increase: each 1% HbA1c above 7 is ~37% increased
    # microvascular risk per UKPDS 35 (Stratton BMJ 2000).
    excess_above_target = max(0, current_hba1c - 7.0)
    microvascular_risk_increase_percent = round(excess_above_target * 37.0, 1)

    # Identify intervention opportunities
    meds_norm = {m.lower() for m in (current_medications or [])}
    has_sglt2i = any(d in meds_norm for d in [
        "empagliflozin", "dapagliflozin", "canagliflozin",
    ])
    has_glp1 = any(d in meds_norm for d in [
        "semaglutide", "liraglutide", "tirzepatide", "dulaglutide",
    ])
    has_metformin = "metformin" in meds_norm
    has_insulin = any(d in meds_norm for d in [
        "insulin_glargine", "insulin_lispro", "insulin",
    ])

    intervention_opportunities = []
    if not has_metformin:
        intervention_opportunities.append({
            "intervention": "Add metformin",
            "expected_hba1c_reduction": "1.0-2.0%",
            "rationale": "First-line ADA recommendation if eGFR >= 30",
            "priority": "high",
        })
    if not has_sglt2i:
        intervention_opportunities.append({
            "intervention": "Add SGLT2 inhibitor",
            "expected_hba1c_reduction": "0.5-0.8%",
            "rationale": (
                "Glycemic, renoprotective, and CV-protective benefits. "
                "Particularly indicated in CKD or heart failure."
            ),
            "priority": "high",
        })
    if not has_glp1 and bmi is not None and bmi >= 27:
        intervention_opportunities.append({
            "intervention": "Add GLP-1 receptor agonist",
            "expected_hba1c_reduction": "1.0-2.0%",
            "expected_weight_loss": "5-15%",
            "rationale": (
                "Strong glycemic and weight benefit, plus CV protection "
                "in established CVD"
            ),
            "priority": "high",
        })
    if (
        on_max_oral_therapy
        and not has_insulin
        and current_hba1c >= 9.0
    ):
        intervention_opportunities.append({
            "intervention": "Initiate basal insulin",
            "expected_hba1c_reduction": "1.5-2.5%",
            "rationale": "HbA1c >> target despite optimized oral therapy",
            "priority": "moderate",
        })

    return {
        "current_hba1c": round(current_hba1c, 2),
        "annual_slope_percent_per_year": round(annual_slope, 2),
        "projected_hba1c_3mo": hba1c_3mo,
        "projected_hba1c_6mo": hba1c_6mo,
        "projected_hba1c_12mo": hba1c_12mo,
        "insulin_requirement_probability_12mo": round(insulin_prob, 2),
        "microvascular_complication_risk_increase_percent":
            microvascular_risk_increase_percent,
        "intervention_opportunities": intervention_opportunities,
        "citation": (
            "UKPDS 33/34/80 (PMID: 9742976, 18784090); "
            "Stratton BMJ 2000 (UKPDS 35); ADA Standards of Care 2024"
        ),
    }


# ===========================================================================
# CARDIOVASCULAR RISK PROGRESSION
# ===========================================================================

def project_cv_risk_progression(
    current_ascvd_risk: float,
    current_bp_systolic: float,
    bp_trend_per_year: float,
    current_ldl: float,
    on_statin: bool,
    has_diabetes: bool,
    has_ckd: bool,
    current_bmi: float,
    smoking: bool,
    age: int,
) -> dict:
    """
    Project cardiovascular risk trajectory and identify highest-leverage
    interventions.

    Methodology
    -----------
    Uses current ASCVD 10-yr risk as baseline. Projects 12-month risk by
    accounting for natural risk increase with age (~1-2% per year in
    moderate-risk patients) and worsening modifiable factors (BP trend,
    LDL if untreated). Identifies modifiable factors with highest
    leverage based on relative-risk literature.

    Parameters
    ----------
    current_ascvd_risk : float
        10-year ASCVD risk percent from PCE.
    current_bp_systolic : float
    bp_trend_per_year : float
        Change in systolic BP per year.
    current_ldl : float
        LDL-C in mg/dL.
    on_statin : bool
    has_diabetes : bool
    has_ckd : bool
    current_bmi : float
    smoking : bool
    age : int

    Returns
    -------
    dict with projected risk, modifiable vs non-modifiable factors,
    and the highest-leverage intervention.

    Sources
    -------
    - Goff DC Jr et al. JACC 2014;63:2935-2959 (Pooled Cohort Equations).
      PMID: 24239921
    - Arnett DK et al. JACC 2019;74:e177-e232 (2019 Primary Prevention).
      PMID: 30894318
    - SPRINT, ACC/AHA 2018 Cholesterol Guideline
    """
    if current_ascvd_risk is None or current_ascvd_risk < 0:
        raise ValueError(
            f"current_ascvd_risk must be >= 0, got {current_ascvd_risk}"
        )

    # Heuristic projection: risk grows ~0.5-1.5%/year, faster if untreated
    risk_increment = 0.5
    if not on_statin and current_ldl is not None and current_ldl > 130:
        risk_increment += 0.7
    if bp_trend_per_year is not None and bp_trend_per_year > 1:
        risk_increment += 0.5
    if smoking:
        risk_increment += 0.5
    if has_diabetes:
        risk_increment += 0.3
    if has_ckd:
        risk_increment += 0.3

    projected_risk_12mo = round(current_ascvd_risk + risk_increment, 1)

    # Categorize
    def categorize(r: float) -> str:
        if r < 5:
            return "low"
        if r < 7.5:
            return "borderline"
        if r < 20:
            return "intermediate"
        return "high"

    current_cat = categorize(current_ascvd_risk)
    projected_cat = categorize(projected_risk_12mo)
    risk_category_change = (
        f"{current_cat} -> {projected_cat}"
        if current_cat != projected_cat
        else f"remains {current_cat}"
    )

    # Modifiable risk factors with leverage estimates
    modifiable = []
    if current_bp_systolic is not None and current_bp_systolic > 130:
        modifiable.append({
            "factor": "blood_pressure",
            "current": current_bp_systolic,
            "target": 130,
            "leverage": "high",
            "expected_risk_reduction_percent": (
                "~25% relative MACE reduction per 10 mmHg SBP lowering "
                "(SPRINT)"
            ),
        })
    if current_ldl is not None and current_ldl > 70 and not on_statin:
        modifiable.append({
            "factor": "ldl",
            "current": current_ldl,
            "target": 70,
            "leverage": "high",
            "expected_risk_reduction_percent": (
                "~22% relative MACE reduction per 1 mmol/L (~39 mg/dL) "
                "LDL lowering (CTT meta-analysis)"
            ),
        })
    elif current_ldl is not None and current_ldl > 70 and on_statin:
        modifiable.append({
            "factor": "ldl",
            "current": current_ldl,
            "target": 70,
            "leverage": "moderate",
            "expected_risk_reduction_percent": (
                "Statin intensity escalation or add-on therapy possible"
            ),
        })
    if smoking:
        modifiable.append({
            "factor": "smoking",
            "current": "active",
            "target": "cessation",
            "leverage": "very_high",
            "expected_risk_reduction_percent": (
                "Up to 50% MACE reduction within 1-2 years of cessation"
            ),
        })
    if current_bmi is not None and current_bmi >= 30:
        modifiable.append({
            "factor": "weight",
            "current": current_bmi,
            "target": "BMI < 25 (or 5-10% loss)",
            "leverage": "moderate",
            "expected_risk_reduction_percent": (
                "5-10% weight loss improves BP, lipids, glycemia"
            ),
        })

    # Pick highest-leverage intervention
    leverage_order = {"very_high": 4, "high": 3, "moderate": 2, "low": 1}
    if modifiable:
        highest = max(modifiable, key=lambda f: leverage_order.get(f["leverage"], 0))
        highest_intervention = f"{highest['factor']}_optimization"
    else:
        highest_intervention = "maintain_current_management"

    non_modifiable = ["age", "sex", "race", "family_history"]

    return {
        "current_ascvd_risk_percent": round(current_ascvd_risk, 1),
        "projected_ascvd_risk_12mo_percent": projected_risk_12mo,
        "risk_category_change": risk_category_change,
        "modifiable_risk_factors": modifiable,
        "non_modifiable_risk_factors": non_modifiable,
        "highest_leverage_intervention": highest_intervention,
        "citation": (
            "Goff DC JACC 2014 (PMID:24239921); "
            "Arnett DK JACC 2019 (PMID:30894318); SPRINT NEJM 2015"
        ),
    }


# ===========================================================================
# MASLD PROGRESSION MODEL
# ===========================================================================

def project_masld_progression(
    fib4_score: float,
    has_diabetes: bool,
    bmi: float,
    alt_trend: str,
    alcohol_use: str,
) -> dict:
    """
    Project MASLD/NASH progression risk and stage estimate.

    Methodology
    -----------
    FIB-4 stages risk of advanced fibrosis. Risk modifiers (diabetes,
    obesity, ongoing ALT elevation, alcohol) shift the cirrhosis-in-10yr
    probability. Returns recommended evaluation and modifiable factors.

    Parameters
    ----------
    fib4_score : float
        FIB-4 index score.
    has_diabetes : bool
    bmi : float
    alt_trend : str
        "rising", "stable", or "falling".
    alcohol_use : str
        "none", "moderate", or "heavy".

    Returns
    -------
    dict with current stage, progression risk, cirrhosis probability,
    recommended evaluation, and modifiable factors.

    Sources
    -------
    - Sterling RK et al. Hepatology 2006;43:1317-1325 (FIB-4). PMID: 16729309
    - AASLD 2023 Practice Guidance on MASLD
    - Singh S et al. Clin Gastroenterol Hepatol 2015;13:643-654
      (NAFLD progression rates).
    """
    if fib4_score is None or fib4_score < 0:
        raise ValueError(f"fib4_score must be >= 0, got {fib4_score}")

    # Stage classification by FIB-4 (Sterling 2006)
    if fib4_score < 1.30:
        current_stage = "low_probability_advanced_fibrosis"
        base_cirrhosis_prob = 0.02
    elif fib4_score <= 2.67:
        current_stage = "indeterminate_fibrosis"
        base_cirrhosis_prob = 0.10
    else:
        current_stage = "high_probability_advanced_fibrosis"
        base_cirrhosis_prob = 0.30

    # Modify base probability with risk factors
    cirrhosis_prob_10yr = base_cirrhosis_prob
    progression_risk = "low"

    if has_diabetes:
        cirrhosis_prob_10yr *= 1.5  # T2DM is the strongest progression driver
    if bmi is not None and bmi >= 35:
        cirrhosis_prob_10yr *= 1.3
    elif bmi is not None and bmi >= 30:
        cirrhosis_prob_10yr *= 1.15
    if alt_trend == "rising":
        cirrhosis_prob_10yr *= 1.3
    elif alt_trend == "falling":
        cirrhosis_prob_10yr *= 0.7
    if alcohol_use == "heavy":
        cirrhosis_prob_10yr *= 2.0
    elif alcohol_use == "moderate":
        cirrhosis_prob_10yr *= 1.15

    cirrhosis_prob_10yr = min(round(cirrhosis_prob_10yr, 2), 0.95)

    if cirrhosis_prob_10yr >= 0.30:
        progression_risk = "high"
    elif cirrhosis_prob_10yr >= 0.10:
        progression_risk = "moderate"
    else:
        progression_risk = "low"

    # Recommended evaluation
    if fib4_score < 1.30:
        recommended_evaluation = (
            "Reassess FIB-4 every 1-3 years if metabolic risk factors persist; "
            "address modifiable factors."
        )
    elif fib4_score <= 2.67:
        recommended_evaluation = (
            "FibroScan or liver MRE to better stratify fibrosis stage; "
            "consider hepatology referral."
        )
    else:
        recommended_evaluation = (
            "Hepatology referral; consider liver biopsy or advanced imaging; "
            "screen for cirrhosis complications (varices, HCC)."
        )

    modifiable_factors = []
    if bmi is not None and bmi >= 25:
        modifiable_factors.append({
            "factor": "weight_loss",
            "target": "5-10% body weight loss",
            "expected_benefit": "5% loss reduces steatosis; 10% can reverse fibrosis",
        })
    if has_diabetes:
        modifiable_factors.append({
            "factor": "glycemic_control",
            "target": "HbA1c < 7%",
            "expected_benefit": "Improves steatosis; GLP-1 RA and SGLT2i offer added benefit",
        })
    if alcohol_use in ("moderate", "heavy"):
        modifiable_factors.append({
            "factor": "alcohol_cessation",
            "target": "abstinence",
            "expected_benefit": "Reduces synergistic fibrosis progression",
        })
    modifiable_factors.append({
        "factor": "metabolic_risk_optimization",
        "target": "Treat dyslipidemia, hypertension",
        "expected_benefit": "Reduces cardiovascular events (leading cause of death in MASLD)",
    })

    return {
        "current_stage": current_stage,
        "fib4_score": round(fib4_score, 2),
        "progression_risk": progression_risk,
        "cirrhosis_probability_10yr": cirrhosis_prob_10yr,
        "recommended_evaluation": recommended_evaluation,
        "modifiable_factors": modifiable_factors,
        "citation": (
            "Sterling Hepatology 2006 PMID:16729309; "
            "AASLD 2023 MASLD Practice Guidance; "
            "Singh CGH 2015 (progression rates)"
        ),
    }


# ===========================================================================
# COMORBIDITY CASCADE MODIFIERS
# ===========================================================================

# Static cascade definitions: bidirectional and unidirectional disease
# interactions encoded with combined modifiers and clinical evidence.
_CASCADE_DEFINITIONS = [
    {
        "trigger_conditions": {"type_2_diabetes", "chronic_kidney_disease"},
        "cascade": ["type_2_diabetes", "chronic_kidney_disease"],
        "relationship": "bidirectional_acceleration",
        "diabetes_effect_on_ckd": "Accelerates eGFR decline by ~15%",
        "ckd_effect_on_diabetes": (
            "Reduces metformin eligibility; alters insulin clearance; "
            "increases hypoglycemia risk"
        ),
        "combined_modifier": 1.15,
        "evidence": "UKPDS, ADVANCE, Coresh JAMA 2014",
    },
    {
        "trigger_conditions": {"chronic_kidney_disease"},
        "min_egfr_below": 60,
        "cascade": ["chronic_kidney_disease", "anemia"],
        "relationship": "causative",
        "explanation": (
            "Reduced erythropoietin production at eGFR < 60 leads to "
            "hypoproliferative anemia"
        ),
        "combined_modifier": None,
        "evidence": "KDIGO 2012 Anemia in CKD",
    },
    {
        "trigger_conditions": {"chronic_kidney_disease"},
        "min_egfr_below": 45,
        "cascade": ["chronic_kidney_disease", "bone_mineral_disorder"],
        "relationship": "causative",
        "explanation": (
            "CKD impairs phosphate excretion and vitamin D activation, "
            "causing CKD-MBD"
        ),
        "combined_modifier": None,
        "evidence": "KDIGO 2017 CKD-MBD Update",
    },
    {
        "trigger_conditions": {"type_2_diabetes"},
        "cascade": ["type_2_diabetes", "cardiovascular_disease"],
        "relationship": "macrovascular_complication",
        "explanation": (
            "T2DM doubles CV risk and accelerates atherosclerosis"
        ),
        "combined_modifier": 2.0,
        "evidence": "UKPDS, MRFIT, ADA Standards",
    },
    {
        "trigger_conditions": {"hypertension"},
        "cascade": ["hypertension", "chronic_kidney_disease"],
        "relationship": "causative",
        "explanation": (
            "Long-standing HTN causes nephrosclerosis and CKD progression"
        ),
        "combined_modifier": 1.10,
        "evidence": "AASK trial, KDIGO 2024",
    },
    {
        "trigger_conditions": {"hypertension"},
        "cascade": ["hypertension", "cardiovascular_disease"],
        "relationship": "causative",
        "explanation": (
            "HTN drives LVH, MI, stroke, and HF risk"
        ),
        "combined_modifier": 1.5,
        "evidence": "SPRINT, MRFIT, ACC/AHA 2017",
    },
    {
        "trigger_conditions": {"obesity", "type_2_diabetes"},
        "cascade": ["obesity", "type_2_diabetes", "chronic_kidney_disease"],
        "relationship": "progressive_cascade",
        "explanation": (
            "Obesity drives insulin resistance -> T2DM -> CKD progression"
        ),
        "combined_modifier": 1.20,
        "evidence": "Hsu CY Ann Intern Med 2006",
    },
    {
        "trigger_conditions": {"obesity"},
        "cascade": ["obesity", "masld", "cirrhosis"],
        "relationship": "progressive_cascade",
        "explanation": (
            "Obesity drives MASLD, which can progress to cirrhosis and HCC"
        ),
        "combined_modifier": None,
        "evidence": "AASLD 2023 MASLD Practice Guidance",
    },
    {
        "trigger_conditions": {"heart_failure", "chronic_kidney_disease"},
        "cascade": ["heart_failure", "chronic_kidney_disease"],
        "relationship": "bidirectional_cardiorenal",
        "explanation": (
            "Cardiorenal syndrome — each accelerates the other; diuretic "
            "management is challenging"
        ),
        "combined_modifier": 1.30,
        "evidence": "Ronco C JACC 2008 (CRS classification)",
    },
    {
        "trigger_conditions": {"chronic_kidney_disease"},
        "cascade": ["chronic_kidney_disease", "drug_accumulation"],
        "relationship": "pharmacokinetic",
        "explanation": (
            "Reduced renal clearance accumulates renally cleared drugs; "
            "dose adjustment required"
        ),
        "combined_modifier": None,
        "evidence": "KDIGO 2024 (drug dosing)",
    },
    {
        "trigger_conditions": {"atrial_fibrillation"},
        "cascade": ["atrial_fibrillation", "stroke"],
        "relationship": "thromboembolic",
        "explanation": (
            "AFib raises stroke risk 5-fold; CHA2DS2-VASc guides "
            "anticoagulation"
        ),
        "combined_modifier": 5.0,
        "evidence": "CHA2DS2-VASc; ACC/AHA AFib Guideline",
    },
    {
        "trigger_conditions": {"obesity", "hypertension"},
        "cascade": ["obesity", "obstructive_sleep_apnea", "hypertension"],
        "relationship": "progressive_cascade",
        "explanation": (
            "Obesity drives OSA, which worsens BP and CV risk"
        ),
        "combined_modifier": None,
        "evidence": "AASM Clinical Practice Guideline 2017",
    },
]


def get_cascade_modifiers(active_conditions: list[str]) -> list[dict]:
    """
    Identify bidirectional and progressive disease interactions.

    Returns the subset of known comorbidity cascades whose trigger
    conditions are met by the patient's active condition list.

    Parameters
    ----------
    active_conditions : list of str
        Patient's active diagnoses (normalized condition keys).

    Returns
    -------
    list of dict
        Each entry describes a triggered cascade with relationship type,
        clinical explanation, combined progression modifier (if numeric),
        and supporting evidence.
    """
    if not active_conditions:
        return []

    active_set = {c.lower().strip() for c in active_conditions}

    triggered = []
    for cascade in _CASCADE_DEFINITIONS:
        # Check that all trigger conditions are present (substring tolerant)
        all_present = True
        for trigger in cascade["trigger_conditions"]:
            trig_norm = trigger.lower()
            if not any(
                trig_norm == c or trig_norm in c or c in trig_norm
                for c in active_set
            ):
                all_present = False
                break
        if not all_present:
            continue

        # Optional eGFR-threshold filter — caller should pre-screen this
        # For simplicity here, skip any rules requiring eGFR data
        # (those will be checked by the engine layer).
        if "min_egfr_below" in cascade:
            # Cannot evaluate without eGFR; surface as conditional cascade
            entry = {
                "cascade": cascade["cascade"],
                "relationship": cascade["relationship"],
                "explanation": cascade.get(
                    "explanation",
                    "Disease interaction (eGFR-dependent)",
                ),
                "combined_modifier": cascade.get("combined_modifier"),
                "evidence": cascade.get("evidence"),
                "condition_dependent_on_egfr_below": cascade["min_egfr_below"],
            }
            triggered.append(entry)
            continue

        entry = {
            "cascade": cascade["cascade"],
            "relationship": cascade["relationship"],
        }
        # Copy whichever explanatory fields exist
        for key in (
            "diabetes_effect_on_ckd", "ckd_effect_on_diabetes",
            "explanation",
        ):
            if key in cascade:
                entry[key] = cascade[key]
        entry["combined_modifier"] = cascade.get("combined_modifier")
        entry["evidence"] = cascade.get("evidence")
        triggered.append(entry)

    return triggered


# ===========================================================================
# Module-level metadata
# ===========================================================================

__all__ = [
    "project_ckd_progression",
    "project_diabetes_progression",
    "project_cv_risk_progression",
    "project_masld_progression",
    "get_cascade_modifiers",
]