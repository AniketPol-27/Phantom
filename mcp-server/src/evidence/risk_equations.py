"""
risk_equations.py

Validated clinical risk equations for the Phantom simulation engine.

All formulas are implemented exactly as published in peer-reviewed sources.
Every function returns a dictionary with both raw numeric values AND
clinical interpretation, so the simulation engine can directly serialize
to JSON and present meaningful results to clinicians.

Dependencies: Python standard library + numpy + scipy (linregress only)
No FHIR, MCP, SHARP, or platform-specific dependencies.

Sources cited inline for every coefficient and threshold.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Optional

import numpy as np
from scipy import stats


# ---------------------------------------------------------------------------
# 1. eGFR — CKD-EPI 2021 (race-free)
# ---------------------------------------------------------------------------

def calculate_egfr_ckd_epi_2021(
    serum_creatinine: float,
    age: int,
    sex: str,
) -> dict:
    """
    Calculate estimated Glomerular Filtration Rate (eGFR) using the
    CKD-EPI 2021 race-free equation.

    Formula:
        eGFR = 142
             × min(Scr/κ, 1)^α
             × max(Scr/κ, 1)^(-1.200)
             × 0.9938^Age
             × (1.012 if female else 1)

    Where:
        κ = 0.7 (female) or 0.9 (male)
        α = -0.241 (female) or -0.302 (male)
        Scr = serum creatinine in mg/dL

    Source:
        Inker LA, Eneanya ND, Coresh J, et al.
        New Creatinine- and Cystatin C-Based Equations to Estimate GFR
        without Race. NEJM 2021;385(19):1737-1749.
        PMID: 34554658
        DOI: 10.1056/NEJMoa2102953

    Parameters
    ----------
    serum_creatinine : float
        Serum creatinine in mg/dL (must be > 0)
    age : int
        Age in years (must be >= 18 — equation validated in adults only)
    sex : str
        "male" or "female" (case-insensitive)

    Returns
    -------
    dict with keys:
        - egfr (float): eGFR in mL/min/1.73m²
        - units (str): "mL/min/1.73m²"
        - equation (str): "CKD-EPI 2021"
        - inputs (dict): the values used
    """
    # --- Input validation ---
    if serum_creatinine is None or serum_creatinine <= 0:
        raise ValueError(
            f"serum_creatinine must be > 0, got {serum_creatinine}"
        )
    if age is None or age < 18:
        raise ValueError(
            f"CKD-EPI 2021 is validated for adults >= 18 years, got age={age}"
        )
    if sex is None or sex.lower() not in ("male", "female"):
        raise ValueError(f"sex must be 'male' or 'female', got {sex!r}")

    sex_norm = sex.lower()

    # --- Sex-specific constants from Inker 2021 ---
    if sex_norm == "female":
        kappa = 0.7        # mg/dL
        alpha = -0.241
        sex_multiplier = 1.012
    else:  # male
        kappa = 0.9        # mg/dL
        alpha = -0.302
        sex_multiplier = 1.0

    scr_over_kappa = serum_creatinine / kappa

    egfr = (
        142.0
        * (min(scr_over_kappa, 1.0) ** alpha)
        * (max(scr_over_kappa, 1.0) ** -1.200)
        * (0.9938 ** age)
        * sex_multiplier
    )

    return {
        "egfr": round(egfr, 1),
        "units": "mL/min/1.73m^2",
        "equation": "CKD-EPI 2021 (race-free)",
        "citation": "Inker LA et al. NEJM 2021;385:1737-1749. PMID:34554658",
        "inputs": {
            "serum_creatinine_mg_dl": serum_creatinine,
            "age_years": age,
            "sex": sex_norm,
        },
    }


# ---------------------------------------------------------------------------
# 2. CKD Stage Classification (KDIGO 2024)
# ---------------------------------------------------------------------------

def classify_ckd_stage(egfr: float) -> dict:
    """
    Classify CKD stage based on eGFR per KDIGO 2024 guideline.

    Stages:
        G1  : eGFR >= 90    (Normal or high)
        G2  : eGFR 60-89    (Mildly decreased)
        G3a : eGFR 45-59    (Mildly to moderately decreased)
        G3b : eGFR 30-44    (Moderately to severely decreased)
        G4  : eGFR 15-29    (Severely decreased)
        G5  : eGFR < 15     (Kidney failure)

    Source:
        KDIGO 2024 Clinical Practice Guideline for the Evaluation and
        Management of Chronic Kidney Disease.
        Kidney International (2024) 105, S117-S314.

    Parameters
    ----------
    egfr : float
        eGFR in mL/min/1.73m² (must be >= 0)

    Returns
    -------
    dict with stage, description, range, and risk level.
    """
    if egfr is None or egfr < 0:
        raise ValueError(f"egfr must be >= 0, got {egfr}")

    if egfr >= 90:
        stage, desc, rng, risk = "G1", "Normal or high", ">=90", "low"
    elif egfr >= 60:
        stage, desc, rng, risk = "G2", "Mildly decreased", "60-89", "low"
    elif egfr >= 45:
        stage, desc, rng, risk = (
            "G3a",
            "Mildly to moderately decreased",
            "45-59",
            "moderate",
        )
    elif egfr >= 30:
        stage, desc, rng, risk = (
            "G3b",
            "Moderately to severely decreased",
            "30-44",
            "high",
        )
    elif egfr >= 15:
        stage, desc, rng, risk = "G4", "Severely decreased", "15-29", "very_high"
    else:
        stage, desc, rng, risk = "G5", "Kidney failure", "<15", "critical"

    return {
        "stage": stage,
        "description": desc,
        "egfr_range": rng,
        "risk_level": risk,
        "egfr_value": round(egfr, 1),
        "citation": "KDIGO 2024 CKD Clinical Practice Guideline",
    }


# ---------------------------------------------------------------------------
# 3. Albuminuria Classification (KDIGO 2024)
# ---------------------------------------------------------------------------

def classify_albuminuria(uacr: float) -> dict:
    """
    Classify albuminuria category by urine albumin-to-creatinine ratio (UACR).

    Categories:
        A1 : UACR < 30 mg/g       (Normal to mildly increased)
        A2 : UACR 30-300 mg/g     (Moderately increased)
        A3 : UACR > 300 mg/g      (Severely increased)

    Source:
        KDIGO 2024 Clinical Practice Guideline for CKD.

    Parameters
    ----------
    uacr : float
        Urine albumin-to-creatinine ratio in mg/g (must be >= 0)

    Returns
    -------
    dict with category, description, range, clinical significance.
    """
    if uacr is None or uacr < 0:
        raise ValueError(f"uacr must be >= 0, got {uacr}")

    if uacr < 30:
        category, desc, rng, sig = (
            "A1",
            "Normal to mildly increased",
            "<30",
            "low_risk",
        )
    elif uacr <= 300:
        category, desc, rng, sig = (
            "A2",
            "Moderately increased (microalbuminuria)",
            "30-300",
            "elevated_risk",
        )
    else:
        category, desc, rng, sig = (
            "A3",
            "Severely increased (macroalbuminuria)",
            ">300",
            "high_risk",
        )

    return {
        "category": category,
        "description": desc,
        "uacr_range_mg_per_g": rng,
        "uacr_value": round(uacr, 1),
        "clinical_significance": sig,
        "citation": "KDIGO 2024 CKD Clinical Practice Guideline",
    }


# ---------------------------------------------------------------------------
# 4. KDIGO Risk Matrix (CKD heat map)
# ---------------------------------------------------------------------------

def kdigo_risk_matrix(ckd_stage: str, albuminuria_category: str) -> dict:
    """
    Determine KDIGO composite risk using the CKD risk heat map (Figure 5
    in KDIGO 2024 guideline).

    The heat map combines GFR category (G1-G5) and albuminuria category
    (A1-A3) into a 5x3 risk matrix:

                        A1          A2          A3
        G1 (>=90)      low         moderate    high
        G2 (60-89)     low         moderate    high
        G3a (45-59)    moderate    high        very_high
        G3b (30-44)    high        very_high   very_high
        G4 (15-29)     very_high   very_high   very_high
        G5 (<15)       very_high   very_high   very_high

    Source:
        KDIGO 2024 CKD Clinical Practice Guideline, Figure 5
        (CGA staging and prognosis heat map).

    Parameters
    ----------
    ckd_stage : str
        One of: "G1", "G2", "G3a", "G3b", "G4", "G5"
    albuminuria_category : str
        One of: "A1", "A2", "A3"

    Returns
    -------
    dict with risk level, color coding, monitoring frequency,
    and referral recommendation.
    """
    valid_stages = {"G1", "G2", "G3a", "G3b", "G4", "G5"}
    valid_albuminuria = {"A1", "A2", "A3"}

    if ckd_stage not in valid_stages:
        raise ValueError(
            f"ckd_stage must be one of {valid_stages}, got {ckd_stage!r}"
        )
    if albuminuria_category not in valid_albuminuria:
        raise ValueError(
            f"albuminuria_category must be one of {valid_albuminuria}, "
            f"got {albuminuria_category!r}"
        )

    # KDIGO 2024 heat map encoded as a lookup table
    matrix = {
        ("G1", "A1"): "low",
        ("G1", "A2"): "moderate",
        ("G1", "A3"): "high",
        ("G2", "A1"): "low",
        ("G2", "A2"): "moderate",
        ("G2", "A3"): "high",
        ("G3a", "A1"): "moderate",
        ("G3a", "A2"): "high",
        ("G3a", "A3"): "very_high",
        ("G3b", "A1"): "high",
        ("G3b", "A2"): "very_high",
        ("G3b", "A3"): "very_high",
        ("G4", "A1"): "very_high",
        ("G4", "A2"): "very_high",
        ("G4", "A3"): "very_high",
        ("G5", "A1"): "very_high",
        ("G5", "A2"): "very_high",
        ("G5", "A3"): "very_high",
    }

    risk = matrix[(ckd_stage, albuminuria_category)]

    # Risk-level metadata per KDIGO 2024
    risk_metadata = {
        "low": {
            "color": "green",
            "monitoring_frequency": "annually",
            "referral_recommended": False,
            "interpretation": "No CKD if no other markers; routine follow-up.",
        },
        "moderate": {
            "color": "yellow",
            "monitoring_frequency": "annually",
            "referral_recommended": False,
            "interpretation": "Monitor; address modifiable risk factors.",
        },
        "high": {
            "color": "orange",
            "monitoring_frequency": "every 6 months",
            "referral_recommended": True,
            "interpretation": "Nephrology referral recommended.",
        },
        "very_high": {
            "color": "red",
            "monitoring_frequency": "every 1-3 months",
            "referral_recommended": True,
            "interpretation": (
                "Urgent nephrology referral; "
                "consider preparation for renal replacement therapy."
            ),
        },
    }

    meta = risk_metadata[risk]

    return {
        "risk": risk,
        "color": meta["color"],
        "monitoring_frequency": meta["monitoring_frequency"],
        "referral_recommended": meta["referral_recommended"],
        "interpretation": meta["interpretation"],
        "ckd_stage": ckd_stage,
        "albuminuria_category": albuminuria_category,
        "citation": "KDIGO 2024 CKD Guideline, Figure 5 (CGA heat map)",
    }


# ---------------------------------------------------------------------------
# 5. ASCVD 10-Year Risk (Pooled Cohort Equations, Goff 2013)
# ---------------------------------------------------------------------------

# Pooled Cohort Equation coefficients
# Source: Goff DC Jr, Lloyd-Jones DM, Bennett G, et al.
# 2013 ACC/AHA Guideline on the Assessment of Cardiovascular Risk.
# JACC 2014;63(25 Pt B):2935-2959. PMID: 24239921
# Coefficients from Appendix 7 of the guideline.
_PCE_COEFFICIENTS = {
    "white_female": {
        "ln_age": -29.799,
        "ln_age_sq": 4.884,
        "ln_tc": 13.540,
        "ln_age_x_ln_tc": -3.114,
        "ln_hdl": -13.578,
        "ln_age_x_ln_hdl": 3.149,
        "ln_treated_sbp": 2.019,
        "ln_age_x_ln_treated_sbp": 0.0,
        "ln_untreated_sbp": 1.957,
        "ln_age_x_ln_untreated_sbp": 0.0,
        "smoker": 7.574,
        "ln_age_x_smoker": -1.665,
        "diabetes": 0.661,
        "mean_terms": -29.18,
        "baseline_survival": 0.9665,
    },
    "white_male": {
        "ln_age": 12.344,
        "ln_age_sq": 0.0,
        "ln_tc": 11.853,
        "ln_age_x_ln_tc": -2.664,
        "ln_hdl": -7.990,
        "ln_age_x_ln_hdl": 1.769,
        "ln_treated_sbp": 1.797,
        "ln_age_x_ln_treated_sbp": 0.0,
        "ln_untreated_sbp": 1.764,
        "ln_age_x_ln_untreated_sbp": 0.0,
        "smoker": 7.837,
        "ln_age_x_smoker": -1.795,
        "diabetes": 0.658,
        "mean_terms": 61.18,
        "baseline_survival": 0.9144,
    },
    "black_female": {
        "ln_age": 17.114,
        "ln_age_sq": 0.0,
        "ln_tc": 0.940,
        "ln_age_x_ln_tc": 0.0,
        "ln_hdl": -18.920,
        "ln_age_x_ln_hdl": 4.475,
        "ln_treated_sbp": 29.291,
        "ln_age_x_ln_treated_sbp": -6.432,
        "ln_untreated_sbp": 27.820,
        "ln_age_x_ln_untreated_sbp": -6.087,
        "smoker": 0.691,
        "ln_age_x_smoker": 0.0,
        "diabetes": 0.874,
        "mean_terms": 86.61,
        "baseline_survival": 0.9533,
    },
    "black_male": {
        "ln_age": 2.469,
        "ln_age_sq": 0.0,
        "ln_tc": 0.302,
        "ln_age_x_ln_tc": 0.0,
        "ln_hdl": -0.307,
        "ln_age_x_ln_hdl": 0.0,
        "ln_treated_sbp": 1.916,
        "ln_age_x_ln_treated_sbp": 0.0,
        "ln_untreated_sbp": 1.809,
        "ln_age_x_ln_untreated_sbp": 0.0,
        "smoker": 0.549,
        "ln_age_x_smoker": 0.0,
        "diabetes": 0.645,
        "mean_terms": 19.54,
        "baseline_survival": 0.8954,
    },
}


def calculate_ascvd_10yr_risk(
    age: int,
    sex: str,
    race: str,
    total_cholesterol: float,
    hdl_cholesterol: float,
    systolic_bp: float,
    bp_treated: bool,
    diabetes: bool,
    current_smoker: bool,
) -> dict:
    """
    Calculate 10-year ASCVD risk using the ACC/AHA Pooled Cohort Equations
    (Goff 2013).

    Formula:
        Individual sum = Σ (coefficient × value)
        10-yr risk = 1 - S₀^exp(Individual sum - mean terms)

    Source:
        Goff DC Jr et al. 2013 ACC/AHA Guideline on the Assessment of
        Cardiovascular Risk. JACC 2014;63(25 Pt B):2935-2959.
        PMID: 24239921

        Risk thresholds from:
        Arnett DK et al. 2019 ACC/AHA Guideline on the Primary Prevention
        of Cardiovascular Disease. JACC 2019;74(10):e177-e232.
        PMID: 30894318

    Risk categories (2019 thresholds):
        Low          : < 5%
        Borderline   : 5% to < 7.5%
        Intermediate : 7.5% to < 20%
        High         : >= 20%

    Parameters
    ----------
    age : int
        Age in years (validated for 40-79)
    sex : str
        "male" or "female"
    race : str
        "white", "black", or "other"
        ("other" uses white coefficients per ACC/AHA recommendation)
    total_cholesterol : float
        mg/dL (range 130-320)
    hdl_cholesterol : float
        mg/dL (range 20-100)
    systolic_bp : float
        mmHg (range 90-200)
    bp_treated : bool
        Currently on antihypertensive medication
    diabetes : bool
        Type 1 or Type 2 diabetes
    current_smoker : bool
        Currently smokes tobacco

    Returns
    -------
    dict with risk_percent, risk_category, recommendation, and inputs.
    """
    # --- Validation ---
    if age < 40 or age > 79:
        # Equations validated only for 40-79; return informational result
        return {
            "risk_percent": None,
            "risk_category": "out_of_range",
            "recommendation": (
                f"Pooled Cohort Equations validated for ages 40-79; "
                f"age {age} is outside this range."
            ),
            "citation": "Goff DC Jr et al. JACC 2014;63:2935-2959.",
            "inputs": {"age": age},
        }

    sex_norm = sex.lower()
    race_norm = race.lower()
    if sex_norm not in ("male", "female"):
        raise ValueError(f"sex must be 'male' or 'female', got {sex!r}")
    if race_norm not in ("white", "black", "other"):
        raise ValueError(
            f"race must be 'white', 'black', or 'other', got {race!r}"
        )

    # Per ACC/AHA, "other" races use white coefficients
    race_for_coef = "white" if race_norm == "other" else race_norm
    key = f"{race_for_coef}_{sex_norm}"
    coef = _PCE_COEFFICIENTS[key]

    # --- Compute log-transformed predictors ---
    ln_age = math.log(age)
    ln_age_sq = ln_age ** 2
    ln_tc = math.log(total_cholesterol)
    ln_hdl = math.log(hdl_cholesterol)
    ln_sbp = math.log(systolic_bp)

    smoker_int = 1 if current_smoker else 0
    diabetes_int = 1 if diabetes else 0

    # --- Build the individual sum ---
    if bp_treated:
        sbp_term = coef["ln_treated_sbp"] * ln_sbp
        sbp_age_term = coef["ln_age_x_ln_treated_sbp"] * (ln_age * ln_sbp)
    else:
        sbp_term = coef["ln_untreated_sbp"] * ln_sbp
        sbp_age_term = coef["ln_age_x_ln_untreated_sbp"] * (ln_age * ln_sbp)

    individual_sum = (
        coef["ln_age"] * ln_age
        + coef["ln_age_sq"] * ln_age_sq
        + coef["ln_tc"] * ln_tc
        + coef["ln_age_x_ln_tc"] * (ln_age * ln_tc)
        + coef["ln_hdl"] * ln_hdl
        + coef["ln_age_x_ln_hdl"] * (ln_age * ln_hdl)
        + sbp_term
        + sbp_age_term
        + coef["smoker"] * smoker_int
        + coef["ln_age_x_smoker"] * (ln_age * smoker_int)
        + coef["diabetes"] * diabetes_int
    )

    # --- Compute 10-year risk ---
    risk = 1.0 - (
        coef["baseline_survival"] ** math.exp(individual_sum - coef["mean_terms"])
    )
    risk_percent = round(risk * 100, 1)

    # --- Categorize per 2019 ACC/AHA Primary Prevention Guideline ---
    if risk_percent < 5:
        category = "low"
        recommendation = (
            "Emphasize lifestyle to reduce CV risk; statin not routinely indicated."
        )
    elif risk_percent < 7.5:
        category = "borderline"
        recommendation = (
            "Consider risk-enhancing factors; "
            "moderate-intensity statin may be considered if present."
        )
    elif risk_percent < 20:
        category = "intermediate"
        recommendation = (
            "Initiate moderate-intensity statin; consider high-intensity if "
            "risk-enhancing factors present."
        )
    else:
        category = "high"
        recommendation = "Initiate high-intensity statin therapy."

    return {
        "risk_percent": risk_percent,
        "risk_category": category,
        "recommendation": recommendation,
        "equation": "ACC/AHA Pooled Cohort Equations (Goff 2013)",
        "citation": (
            "Goff DC Jr et al. JACC 2014;63:2935-2959. PMID:24239921; "
            "Arnett DK et al. JACC 2019;74:e177-e232. PMID:30894318"
        ),
        "inputs": {
            "age": age,
            "sex": sex_norm,
            "race": race_norm,
            "total_cholesterol_mg_dl": total_cholesterol,
            "hdl_cholesterol_mg_dl": hdl_cholesterol,
            "systolic_bp_mmhg": systolic_bp,
            "bp_treated": bp_treated,
            "diabetes": diabetes,
            "current_smoker": current_smoker,
        },
    }


# ---------------------------------------------------------------------------
# 6. FIB-4 Index (Hepatic Fibrosis)
# ---------------------------------------------------------------------------

def calculate_fib4(
    age: int,
    ast: float,
    alt: float,
    platelet_count: float,
) -> dict:
    """
    Calculate FIB-4 index, a non-invasive estimate of hepatic fibrosis.

    Formula:
        FIB-4 = (Age × AST) / (Platelet count × √ALT)

    Where:
        Age         : years
        AST, ALT    : U/L
        Platelets   : × 10^9/L  (equivalent to × 10^3/μL)

    Interpretation (in chronic liver disease):
        < 1.30        : Low risk of advanced fibrosis (NPV ~95%)
        1.30 - 2.67   : Indeterminate; further evaluation needed
        > 2.67        : High risk of advanced fibrosis (PPV ~65%)

    Source:
        Sterling RK et al. Development of a simple noninvasive index to
        predict significant fibrosis in patients with HIV/HCV coinfection.
        Hepatology 2006;43(6):1317-1325.
        PMID: 16729309

        Validated in MASLD/NAFLD: Shah AG et al. Clin Gastroenterol
        Hepatol 2009;7(10):1104-1112. PMID: 19523535

    Parameters
    ----------
    age : int
        Age in years (must be > 0)
    ast : float
        Aspartate aminotransferase (U/L)
    alt : float
        Alanine aminotransferase (U/L)
    platelet_count : float
        Platelets in × 10^9/L

    Returns
    -------
    dict with score, category, interpretation, and recommendation.
    """
    if age <= 0 or ast <= 0 or alt <= 0 or platelet_count <= 0:
        raise ValueError(
            "All FIB-4 inputs (age, AST, ALT, platelets) must be > 0; "
            f"got age={age}, ast={ast}, alt={alt}, plt={platelet_count}"
        )

    score = (age * ast) / (platelet_count * math.sqrt(alt))

    if score < 1.30:
        category = "low"
        interpretation = "Low probability of advanced fibrosis (F3-F4)."
        probability = "low"
        recommendation = (
            "Routine follow-up; reassess FIB-4 in 1-3 years if risk factors persist."
        )
    elif score <= 2.67:
        category = "indeterminate"
        interpretation = (
            "Indeterminate; cannot rule in or rule out advanced fibrosis."
        )
        probability = "moderate"
        recommendation = (
            "Further evaluation recommended (FibroScan, liver MRE, or "
            "specialist referral)."
        )
    else:
        category = "high"
        interpretation = "High probability of advanced fibrosis (F3-F4)."
        probability = "high"
        recommendation = (
            "Hepatology referral; consider liver biopsy or advanced imaging."
        )

    return {
        "score": round(score, 2),
        "category": category,
        "interpretation": interpretation,
        "advanced_fibrosis_probability": probability,
        "recommendation": recommendation,
        "citation": "Sterling RK et al. Hepatology 2006;43:1317-1325. PMID:16729309",
        "inputs": {
            "age_years": age,
            "ast_u_per_l": ast,
            "alt_u_per_l": alt,
            "platelet_count_10e9_per_l": platelet_count,
        },
    }


# ---------------------------------------------------------------------------
# 7. qSOFA Score (Sepsis Screening)
# ---------------------------------------------------------------------------

def calculate_qsofa(
    respiratory_rate: int,
    systolic_bp: int,
    altered_mentation: bool,
) -> dict:
    """
    Calculate quick Sequential Organ Failure Assessment (qSOFA) score.

    1 point each for:
        - Respiratory rate >= 22 breaths/min
        - Systolic blood pressure <= 100 mmHg
        - Altered mentation (Glasgow Coma Scale < 15)

    Total score 0-3.

    Interpretation:
        0-1 : Low risk of poor outcome
        >=2 : High risk; consider sepsis workup and ICU-level care

    Source:
        Seymour CW, Liu VX, Iwashyna TJ, et al.
        Assessment of Clinical Criteria for Sepsis: For the Third
        International Consensus Definitions for Sepsis and Septic Shock
        (Sepsis-3). JAMA 2016;315(8):762-774.
        PMID: 26903335
        DOI: 10.1001/jama.2016.0288

    Parameters
    ----------
    respiratory_rate : int
        Breaths per minute
    systolic_bp : int
        mmHg
    altered_mentation : bool
        True if GCS < 15 or new altered mental status

    Returns
    -------
    dict with score, components, interpretation, mortality risk.
    """
    if respiratory_rate < 0 or systolic_bp < 0:
        raise ValueError(
            "Vital signs must be non-negative; "
            f"got rr={respiratory_rate}, sbp={systolic_bp}"
        )

    rr_point = 1 if respiratory_rate >= 22 else 0
    bp_point = 1 if systolic_bp <= 100 else 0
    mentation_point = 1 if altered_mentation else 0

    score = rr_point + bp_point + mentation_point

    if score >= 2:
        interpretation = (
            "High risk of poor outcome (in-hospital mortality, ICU admission); "
            "consider full sepsis workup and escalation of care."
        )
        mortality_risk = "elevated"
    else:
        interpretation = (
            "Low risk by qSOFA; continue standard assessment. "
            "Note: qSOFA has limited sensitivity; clinical judgment required."
        )
        mortality_risk = "low_to_moderate"

    return {
        "score": score,
        "components": {
            "respiratory_rate_>=22": bool(rr_point),
            "systolic_bp_<=100": bool(bp_point),
            "altered_mentation": bool(mentation_point),
        },
        "interpretation": interpretation,
        "mortality_risk": mortality_risk,
        "citation": "Seymour CW et al. JAMA 2016;315:762-774. PMID:26903335",
        "inputs": {
            "respiratory_rate": respiratory_rate,
            "systolic_bp_mmhg": systolic_bp,
            "altered_mentation": altered_mentation,
        },
    }


# ---------------------------------------------------------------------------
# 8. Linear Trajectory Computation (longitudinal lab trends)
# ---------------------------------------------------------------------------

def _parse_date(d) -> datetime:
    """Accept either a datetime or an ISO-format string."""
    if isinstance(d, datetime):
        return d
    if isinstance(d, str):
        # Accept "YYYY-MM-DD" or full ISO 8601
        try:
            return datetime.fromisoformat(d.replace("Z", "+00:00"))
        except ValueError:
            return datetime.strptime(d, "%Y-%m-%d")
    raise ValueError(f"Cannot parse date: {d!r}")


def compute_trajectory(
    data_points: list[dict],
    rate_thresholds: Optional[dict] = None,
) -> dict:
    """
    Compute a linear-regression trajectory from longitudinal observations.

    Used to characterize lab trends (eGFR decline, HbA1c trend, weight loss
    trajectory, etc.) and project future values with prediction intervals.

    Parameters
    ----------
    data_points : list of dict
        Each dict: {"date": ISO date string or datetime, "value": float}
        Minimum 2 points required for regression.
    rate_thresholds : dict, optional
        Override default rate classification thresholds. Format:
        {"normal": float, "moderate": float, "rapid": float}
        where values are absolute slope-per-year cutoffs.
        Default thresholds are appropriate for eGFR (mL/min/year).

    Returns
    -------
    dict with slope, intercept, r², direction, projections at
    6, 12, and 24 months, and confidence label.

    Notes
    -----
    Uses scipy.stats.linregress for regression (least-squares fit).
    95% prediction intervals computed from residual standard error.
    """
    if not data_points or len(data_points) < 2:
        return {
            "slope_per_year": None,
            "slope_per_month": None,
            "intercept": None,
            "r_squared": None,
            "direction": "insufficient_data",
            "rate_classification": "unknown",
            "data_points_used": len(data_points) if data_points else 0,
            "confidence": "insufficient_data",
            "projections": None,
            "note": "At least 2 data points are required for trajectory.",
        }

    # --- Parse and sort by date ---
    parsed = sorted(
        (
            {"date": _parse_date(p["date"]), "value": float(p["value"])}
            for p in data_points
        ),
        key=lambda p: p["date"],
    )

    # Convert dates to "years since first observation" for regression
    t0 = parsed[0]["date"]
    x_years = np.array(
        [(p["date"] - t0).total_seconds() / (365.25 * 86400.0) for p in parsed]
    )
    y_values = np.array([p["value"] for p in parsed])

    # --- Linear regression ---
    result = stats.linregress(x_years, y_values)
    slope = float(result.slope)            # units: y per year
    intercept = float(result.intercept)
    r_value = float(result.rvalue)
    r_squared = r_value ** 2

    # --- Direction ---
    # Use small dead-band to avoid calling near-zero "declining"
    if abs(slope) < 0.05 * (abs(np.mean(y_values)) if np.mean(y_values) else 1):
        direction = "stable"
    elif slope < 0:
        direction = "declining"
    else:
        direction = "improving"

    # --- Rate classification ---
    thresholds = rate_thresholds or {
        "normal": 1.0,    # |slope| < 1 per year   -> normal
        "moderate": 3.0,  # 1 <= |slope| < 3       -> moderate
        # |slope| >= 3                              -> rapid
    }
    abs_slope = abs(slope)
    if abs_slope < thresholds["normal"]:
        rate_class = "normal"
    elif abs_slope < thresholds["moderate"]:
        rate_class = "moderate"
    else:
        rate_class = "rapid"

    # --- Confidence based on N points ---
    n = len(parsed)
    if n < 3:
        confidence = "low"
    elif n <= 5:
        confidence = "moderate"
    else:
        confidence = "high"

    # --- Projections with 95% prediction intervals ---
    # Last observation date is reference for "now"
    t_now = x_years[-1]
    last_value = y_values[-1]

    # Residual standard error
    y_pred_train = intercept + slope * x_years
    residuals = y_values - y_pred_train
    if n > 2:
        se_resid = math.sqrt(np.sum(residuals ** 2) / (n - 2))
    else:
        se_resid = 0.0

    # t-value for 95% PI (use 1.96 as a reasonable approximation;
    # strictly should use t-distribution with n-2 df)
    t_crit = stats.t.ppf(0.975, df=max(n - 2, 1))

    def project(months_ahead: float) -> dict:
        t_target = t_now + (months_ahead / 12.0)
        point = intercept + slope * t_target
        # Simple PI ignoring leverage (acceptable for short horizons)
        margin = t_crit * se_resid * math.sqrt(1 + 1 / max(n, 1))
        return {
            "value": round(point, 2),
            "ci_low": round(point - margin, 2),
            "ci_high": round(point + margin, 2),
            "months_from_last_observation": months_ahead,
        }

    projections = {
        "6_months": project(6),
        "12_months": project(12),
        "24_months": project(24),
    }

    return {
        "slope_per_year": round(slope, 3),
        "slope_per_month": round(slope / 12.0, 4),
        "intercept": round(intercept, 3),
        "r_squared": round(r_squared, 3),
        "direction": direction,
        "rate_classification": rate_class,
        "data_points_used": n,
        "confidence": confidence,
        "last_observed_value": round(float(last_value), 2),
        "projections": projections,
        "method": "Ordinary least-squares linear regression (scipy.stats.linregress)",
    }


# ---------------------------------------------------------------------------
# Module-level metadata
# ---------------------------------------------------------------------------

__all__ = [
    "calculate_egfr_ckd_epi_2021",
    "classify_ckd_stage",
    "classify_albuminuria",
    "kdigo_risk_matrix",
    "calculate_ascvd_10yr_risk",
    "calculate_fib4",
    "calculate_qsofa",
    "compute_trajectory",
]