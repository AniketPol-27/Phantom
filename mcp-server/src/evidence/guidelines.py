"""
guidelines.py

Clinical guideline rules for the Phantom simulation engine.

Two rule categories:

  CARE GAP RULES — Things a patient SHOULD be receiving but is not.
    Examples: T2DM + CKD without SGLT2i, HbA1c above target, no annual
    eye exam in diabetes.

  DIAGNOSTIC GAP RULES — Patterns that suggest a diagnosis the patient
    likely has but is not yet documented.
    Examples: CKD + low hemoglobin without an anemia diagnosis, obesity
    + diabetes + persistent ALT elevation without a MASLD diagnosis.

Each rule is a structured dict with criteria, recommendation, evidence
grade, and citation. Two main evaluator functions take a patient's
clinical state and return all triggered rules.

Sources cited inline (KDIGO, ADA, ACC/AHA, USPSTF, AASLD, CDC).
This module has zero dependencies on FHIR, MCP, or platform code.
"""

from __future__ import annotations

from typing import Optional


# ===========================================================================
# CARE GAP RULES
# ===========================================================================
# Each rule defines structured criteria. The evaluator function checks
# the criteria against patient data and triggers if all clauses match.

CARE_GAP_RULES: list[dict] = [

    # -----------------------------------------------------------------------
    # Diabetes / CKD / Cardiometabolic
    # -----------------------------------------------------------------------

    {
        "id": "diabetes_sglt2i_ckd",
        "guideline": "KDIGO 2024",
        "category": "diabetes_ckd",
        "description": (
            "SGLT2 inhibitor recommended for T2DM with CKD (eGFR >= 20)"
        ),
        "criteria": {
            "conditions_present": ["type_2_diabetes", "chronic_kidney_disease"],
            "egfr_min": 20,
            "medication_class_absent": ["sglt2_inhibitor"],
        },
        "recommendation": (
            "Initiate SGLT2 inhibitor (empagliflozin or dapagliflozin) "
            "for renoprotection. Trial evidence: DAPA-CKD, EMPA-KIDNEY, "
            "CREDENCE."
        ),
        "evidence_grade": "1A",
        "priority": "high",
        "citation": "KDIGO 2024 CKD Clinical Practice Guideline",
    },

    {
        "id": "diabetes_glp1_ascvd",
        "guideline": "ADA Standards of Care 2024",
        "category": "diabetes_cv",
        "description": (
            "GLP-1 receptor agonist recommended for T2DM with established "
            "ASCVD or high CV risk"
        ),
        "criteria": {
            "conditions_present": ["type_2_diabetes"],
            "any_condition_present": [
                "ascvd", "coronary_artery_disease", "stroke",
                "peripheral_artery_disease", "myocardial_infarction",
            ],
            "medication_class_absent": ["glp_1_receptor_agonist"],
        },
        "recommendation": (
            "Add GLP-1 RA with proven CV benefit (semaglutide, liraglutide, "
            "or dulaglutide). Trial evidence: SUSTAIN-6, LEADER, REWIND."
        ),
        "evidence_grade": "1A",
        "priority": "high",
        "citation": "ADA Standards of Care 2024, Section 10",
    },

    {
        "id": "diabetes_hba1c_target",
        "guideline": "ADA Standards of Care 2024",
        "category": "diabetes_glycemic",
        "description": "HbA1c above individualized target",
        "criteria": {
            "conditions_present": ["type_2_diabetes"],
            "lab_above_threshold": {"test": "hba1c", "threshold": 7.0},
        },
        "recommendation": (
            "HbA1c above target of < 7%. Consider therapy intensification. "
            "Target may be individualized to < 8% in elderly, limited life "
            "expectancy, or high hypoglycemia risk."
        ),
        "evidence_grade": "1A",
        "priority": "high",
        "citation": "ADA Standards of Care 2024, Section 6",
    },

    {
        "id": "diabetes_metformin_first_line",
        "guideline": "ADA Standards of Care 2024",
        "category": "diabetes_glycemic",
        "description": (
            "Metformin recommended as first-line therapy if eGFR >= 30"
        ),
        "criteria": {
            "conditions_present": ["type_2_diabetes"],
            "egfr_min": 30,
            "medication_absent": ["metformin"],
            "contraindications_absent": ["metformin_intolerance"],
        },
        "recommendation": (
            "Initiate metformin as first-line glucose-lowering therapy "
            "unless contraindicated."
        ),
        "evidence_grade": "1A",
        "priority": "moderate",
        "citation": "ADA Standards of Care 2024, Section 9",
    },

    # -----------------------------------------------------------------------
    # Hypertension
    # -----------------------------------------------------------------------

    {
        "id": "hypertension_target_acc_aha",
        "guideline": "ACC/AHA 2017",
        "category": "hypertension",
        "description": "BP above ACC/AHA 2017 target of < 130/80",
        "criteria": {
            "conditions_present": ["hypertension"],
            "vital_above_threshold": {"vital": "systolic_bp", "threshold": 130},
        },
        "recommendation": (
            "Systolic BP above target of < 130 mmHg. Optimize "
            "antihypertensive therapy. SPRINT trial supports intensive "
            "control in high-CV-risk adults."
        ),
        "evidence_grade": "1A",
        "priority": "high",
        "citation": "ACC/AHA 2017 Hypertension Guideline",
    },

    {
        "id": "hypertension_acei_arb_diabetes",
        "guideline": "ADA / KDIGO 2024",
        "category": "hypertension",
        "description": (
            "ACEi or ARB recommended for hypertension with diabetes"
        ),
        "criteria": {
            "conditions_present": ["hypertension", "type_2_diabetes"],
            "medication_class_absent": ["ace_inhibitor", "arb"],
        },
        "recommendation": (
            "Initiate ACEi or ARB for renoprotection and BP control. "
            "Particularly important if albuminuria present."
        ),
        "evidence_grade": "1A",
        "priority": "high",
        "citation": "ADA Standards of Care 2024 / KDIGO 2024",
    },

    {
        "id": "ckd_acei_arb_albuminuria",
        "guideline": "KDIGO 2024",
        "category": "ckd",
        "description": (
            "ACEi or ARB recommended for CKD with albuminuria (UACR >= 30)"
        ),
        "criteria": {
            "conditions_present": ["chronic_kidney_disease"],
            "lab_above_threshold": {"test": "uacr", "threshold": 30},
            "medication_class_absent": ["ace_inhibitor", "arb"],
        },
        "recommendation": (
            "Initiate maximum-tolerated ACEi or ARB for slowing CKD "
            "progression and reducing albuminuria."
        ),
        "evidence_grade": "1A",
        "priority": "high",
        "citation": "KDIGO 2024 CKD Clinical Practice Guideline",
    },

    # -----------------------------------------------------------------------
    # Lipids / ASCVD
    # -----------------------------------------------------------------------

    {
        "id": "statin_ascvd_secondary",
        "guideline": "ACC/AHA 2018",
        "category": "lipids",
        "description": (
            "High-intensity statin recommended for established ASCVD "
            "(secondary prevention)"
        ),
        "criteria": {
            "any_condition_present": [
                "ascvd", "coronary_artery_disease", "myocardial_infarction",
                "stroke", "peripheral_artery_disease",
            ],
            "medication_class_absent": ["statin"],
        },
        "recommendation": (
            "Initiate high-intensity statin (atorvastatin 40-80 mg or "
            "rosuvastatin 20-40 mg) for secondary CV prevention."
        ),
        "evidence_grade": "1A",
        "priority": "high",
        "citation": "ACC/AHA 2018 Cholesterol Guideline",
    },

    {
        "id": "statin_diabetes_age_40_75",
        "guideline": "ACC/AHA 2018",
        "category": "lipids",
        "description": (
            "Moderate-intensity statin recommended for diabetes age 40-75"
        ),
        "criteria": {
            "conditions_present": ["type_2_diabetes"],
            "age_min": 40,
            "age_max": 75,
            "medication_class_absent": ["statin"],
        },
        "recommendation": (
            "Initiate at least moderate-intensity statin therapy. "
            "Consider high-intensity if multiple ASCVD risk factors."
        ),
        "evidence_grade": "1A",
        "priority": "high",
        "citation": "ACC/AHA 2018 Cholesterol Guideline",
    },

    {
        "id": "statin_high_ascvd_risk",
        "guideline": "ACC/AHA 2018",
        "category": "lipids",
        "description": (
            "Statin recommended if 10-year ASCVD risk >= 7.5% "
            "(intermediate or high risk)"
        ),
        "criteria": {
            "ascvd_risk_min": 7.5,
            "age_min": 40,
            "age_max": 75,
            "medication_class_absent": ["statin"],
        },
        "recommendation": (
            "Discuss moderate-to-high-intensity statin therapy. "
            "Risk-enhancing factors may shift recommendation."
        ),
        "evidence_grade": "1B",
        "priority": "moderate",
        "citation": "ACC/AHA 2019 Primary Prevention Guideline",
    },

    # -----------------------------------------------------------------------
    # Heart Failure
    # -----------------------------------------------------------------------

    {
        "id": "hfref_gdmt_quadruple",
        "guideline": "ACC/AHA/HFSA 2022",
        "category": "heart_failure",
        "description": (
            "Quadruple guideline-directed medical therapy for HFrEF: "
            "ACEi/ARB/ARNI + beta-blocker + MRA + SGLT2i"
        ),
        "criteria": {
            "conditions_present": ["heart_failure_reduced_ef"],
            "missing_medication_class_any_of": [
                "ace_inhibitor", "arb", "arni",
                "beta_blocker",
                "mineralocorticoid_receptor_antagonist",
                "sglt2_inhibitor",
            ],
        },
        "recommendation": (
            "Optimize quadruple GDMT for HFrEF: ACEi/ARB/ARNI + "
            "beta-blocker + MRA + SGLT2i (each Class I recommendation). "
            "Trial evidence: PARADIGM-HF, MERIT-HF, EMPHASIS-HF, DAPA-HF."
        ),
        "evidence_grade": "1A",
        "priority": "high",
        "citation": "ACC/AHA/HFSA 2022 Heart Failure Guideline",
    },

    # -----------------------------------------------------------------------
    # Diabetic complication screening
    # -----------------------------------------------------------------------

    {
        "id": "diabetes_annual_eye_exam",
        "guideline": "ADA Standards of Care 2024",
        "category": "diabetes_screening",
        "description": "Annual dilated eye exam for diabetic retinopathy",
        "criteria": {
            "conditions_present": ["type_2_diabetes"],
            "screening_overdue": {
                "test": "dilated_eye_exam",
                "max_months_since_last": 12,
            },
        },
        "recommendation": (
            "Annual dilated retinal exam (or every 1-2 years if no "
            "retinopathy and good glycemic control). Refer to ophthalmology."
        ),
        "evidence_grade": "1B",
        "priority": "moderate",
        "citation": "ADA Standards of Care 2024, Section 12",
    },

    {
        "id": "diabetes_annual_uacr",
        "guideline": "ADA / KDIGO 2024",
        "category": "diabetes_screening",
        "description": "Annual UACR for diabetic nephropathy screening",
        "criteria": {
            "conditions_present": ["type_2_diabetes"],
            "screening_overdue": {
                "test": "uacr",
                "max_months_since_last": 12,
            },
        },
        "recommendation": (
            "Annual urine albumin-to-creatinine ratio for early detection "
            "of diabetic kidney disease."
        ),
        "evidence_grade": "1B",
        "priority": "moderate",
        "citation": "ADA Standards of Care 2024, Section 11",
    },

    {
        "id": "diabetes_annual_foot_exam",
        "guideline": "ADA Standards of Care 2024",
        "category": "diabetes_screening",
        "description": "Annual comprehensive foot examination",
        "criteria": {
            "conditions_present": ["type_2_diabetes"],
            "screening_overdue": {
                "test": "foot_exam",
                "max_months_since_last": 12,
            },
        },
        "recommendation": (
            "Annual comprehensive foot exam including monofilament testing, "
            "vibration sense, ankle reflexes, pulse assessment."
        ),
        "evidence_grade": "1B",
        "priority": "moderate",
        "citation": "ADA Standards of Care 2024, Section 12",
    },

    # -----------------------------------------------------------------------
    # Cancer screening (USPSTF)
    # -----------------------------------------------------------------------

    {
        "id": "uspstf_colon_cancer_screening",
        "guideline": "USPSTF 2021",
        "category": "cancer_screening",
        "description": "Colorectal cancer screening, age 45-75",
        "criteria": {
            "age_min": 45,
            "age_max": 75,
            "screening_overdue": {
                "test": "colorectal_cancer_screening",
                "max_months_since_last": 120,  # colonoscopy interval
            },
        },
        "recommendation": (
            "Colorectal cancer screening recommended. Options: colonoscopy "
            "every 10 years, FIT annually, or stool DNA test every 1-3 years."
        ),
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF 2021 Recommendation Statement",
    },

    {
        "id": "uspstf_breast_cancer_screening",
        "guideline": "USPSTF 2024",
        "category": "cancer_screening",
        "description": "Biennial mammography for women age 40-74",
        "criteria": {
            "age_min": 40,
            "age_max": 74,
            "sex": "female",
            "screening_overdue": {
                "test": "mammography",
                "max_months_since_last": 24,
            },
        },
        "recommendation": (
            "Biennial screening mammography for average-risk women age 40-74."
        ),
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF 2024 Breast Cancer Screening",
    },

    {
        "id": "uspstf_lung_cancer_screening",
        "guideline": "USPSTF 2021",
        "category": "cancer_screening",
        "description": (
            "Annual low-dose CT for high-risk smokers, age 50-80"
        ),
        "criteria": {
            "age_min": 50,
            "age_max": 80,
            "smoking_history_pack_years_min": 20,
            "screening_overdue": {
                "test": "lung_cancer_screening",
                "max_months_since_last": 12,
            },
        },
        "recommendation": (
            "Annual low-dose CT screening if 20+ pack-year history and "
            "currently smoking or quit within 15 years."
        ),
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF 2021 Lung Cancer Screening",
    },

    {
        "id": "uspstf_hep_c_screening",
        "guideline": "USPSTF 2020",
        "category": "infectious_disease_screening",
        "description": "One-time hepatitis C screening, adults 18-79",
        "criteria": {
            "age_min": 18,
            "age_max": 79,
            "screening_ever_done": {
                "test": "hepatitis_c_antibody",
            },
        },
        "recommendation": "One-time hepatitis C antibody screening.",
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF 2020 Hepatitis C Screening",
    },

    # -----------------------------------------------------------------------
    # Bone health / osteoporosis
    # -----------------------------------------------------------------------

    {
        "id": "uspstf_osteoporosis_screening_women",
        "guideline": "USPSTF 2018",
        "category": "bone_health",
        "description": (
            "Osteoporosis screening (DEXA) for women age >= 65"
        ),
        "criteria": {
            "age_min": 65,
            "sex": "female",
            "screening_overdue": {
                "test": "dexa_scan",
                "max_months_since_last": 24,
            },
        },
        "recommendation": "Bone density screening with DEXA every 2 years.",
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF 2018 Osteoporosis Screening",
    },

    # -----------------------------------------------------------------------
    # Obesity / weight management
    # -----------------------------------------------------------------------

    {
        "id": "obesity_glp1_consideration",
        "guideline": "ADA / Obesity Society 2024",
        "category": "obesity",
        "description": (
            "Pharmacotherapy consideration for BMI >= 30 (or >= 27 with "
            "comorbidities)"
        ),
        "criteria": {
            "bmi_min": 30,
            "medication_class_absent": [
                "glp_1_receptor_agonist", "gip_glp1_agonist",
            ],
        },
        "recommendation": (
            "Consider GLP-1 RA (semaglutide) or GIP/GLP-1 (tirzepatide) for "
            "weight management. STEP and SURMOUNT trial evidence."
        ),
        "evidence_grade": "1B",
        "priority": "moderate",
        "citation": "ADA Standards of Care 2024 / Obesity Society 2023",
    },

    # -----------------------------------------------------------------------
    # Mental health
    # -----------------------------------------------------------------------

    {
        "id": "uspstf_depression_screening",
        "guideline": "USPSTF 2023",
        "category": "mental_health",
        "description": "Depression screening for all adults",
        "criteria": {
            "age_min": 18,
            "screening_overdue": {
                "test": "depression_screening_phq",
                "max_months_since_last": 12,
            },
        },
        "recommendation": (
            "Annual depression screening with PHQ-2 or PHQ-9. Particularly "
            "important in patients with chronic disease."
        ),
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF 2023 Depression Screening",
    },

    # -----------------------------------------------------------------------
    # Immunization (subset of CDC schedule)
    # -----------------------------------------------------------------------

    {
        "id": "cdc_pneumococcal_diabetes",
        "guideline": "CDC 2024",
        "category": "immunization",
        "description": "Pneumococcal vaccination in diabetes",
        "criteria": {
            "conditions_present": ["type_2_diabetes"],
            "age_min": 19,
            "screening_ever_done": {
                "test": "pneumococcal_vaccine",
            },
        },
        "recommendation": (
            "Pneumococcal vaccination (PCV20 or PCV15 + PPSV23) for adults "
            "with diabetes."
        ),
        "evidence_grade": "A",
        "priority": "moderate",
        "citation": "CDC ACIP Adult Immunization Schedule 2024",
    },

    {
        "id": "cdc_influenza_annual",
        "guideline": "CDC 2024",
        "category": "immunization",
        "description": "Annual influenza vaccination",
        "criteria": {
            "age_min": 6,  # months, but most adults
            "screening_overdue": {
                "test": "influenza_vaccine",
                "max_months_since_last": 12,
            },
        },
        "recommendation": "Annual influenza vaccination for all adults.",
        "evidence_grade": "A",
        "priority": "moderate",
        "citation": "CDC ACIP 2024",
    },

    # -----------------------------------------------------------------------
    # Drug-related monitoring gaps
    # -----------------------------------------------------------------------

    {
        "id": "metformin_b12_monitoring",
        "guideline": "ADA Standards of Care 2024",
        "category": "drug_monitoring",
        "description": (
            "B12 monitoring with long-term metformin use"
        ),
        "criteria": {
            "medications_present": ["metformin"],
            "screening_overdue": {
                "test": "vitamin_b12",
                "max_months_since_last": 12,
            },
        },
        "recommendation": (
            "Annual vitamin B12 level measurement after 4+ years of "
            "metformin use."
        ),
        "evidence_grade": "B",
        "priority": "low",
        "citation": "ADA Standards of Care 2024, Section 9",
    },

    {
        "id": "ace_arb_potassium_monitoring",
        "guideline": "ACC/AHA / KDIGO",
        "category": "drug_monitoring",
        "description": (
            "Potassium monitoring with ACEi/ARB therapy"
        ),
        "criteria": {
            "medications_class_present": ["ace_inhibitor", "arb"],
            "screening_overdue": {
                "test": "potassium",
                "max_months_since_last": 6,
            },
        },
        "recommendation": (
            "Periodic potassium and renal function monitoring (every 3-6 "
            "months) for patients on ACEi/ARB, more frequently if CKD."
        ),
        "evidence_grade": "1B",
        "priority": "moderate",
        "citation": "KDIGO 2024 / ACC/AHA",
    },

    # -----------------------------------------------------------------------
    # USPSTF Cancer Screening (added in Task 5C)
    # -----------------------------------------------------------------------

    {
        "id": "cervical_cancer_screening",
        "guideline": "USPSTF 2018",
        "category": "cancer_screening",
        "description": (
            "Cervical cancer screening recommended for women age 21-65"
        ),
        "criteria": {
            "sex": "female",
            "age_min": 21,
            "age_max": 65,
        },
        "recommendation": (
            "Pap smear every 3 years (age 21-29) or Pap + HPV co-testing "
            "every 5 years (age 30-65). Recommendation grade A."
        ),
        "evidence_grade": "A",
        "priority": "moderate",
        "citation": "USPSTF Cervical Cancer Screening 2018",
    },

    {
        "id": "aaa_screening_men",
        "guideline": "USPSTF 2019",
        "category": "cancer_screening",
        "description": (
            "One-time AAA screening with abdominal ultrasound for men "
            "age 65-75 who have ever smoked"
        ),
        "criteria": {
            "sex": "male",
            "age_min": 65,
            "age_max": 75,
            "smoking_history_present": True,
        },
        "recommendation": (
            "Order one-time abdominal ultrasound to screen for abdominal "
            "aortic aneurysm. Recommendation grade B."
        ),
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF AAA Screening 2019",
    },

    {
        "id": "osteoporosis_screening_postmenopausal",
        "guideline": "USPSTF 2018",
        "category": "bone_health",
        "description": (
            "Osteoporosis screening recommended for women age 65+ and "
            "men age 70+"
        ),
        "criteria": {
            "any_age_sex_combo": [
                {"sex": "female", "age_min": 65},
                {"sex": "male", "age_min": 70},
            ],
        },
        "recommendation": (
            "Order DEXA scan to assess bone mineral density. Repeat "
            "every 2 years if T-score is between -1.0 and -2.5."
        ),
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF Osteoporosis Screening 2018",
    },

    {
        "id": "hepatitis_c_screening_universal",
        "guideline": "USPSTF 2020",
        "category": "infectious_disease_screening",
        "description": (
            "One-time hepatitis C screening recommended for all adults "
            "age 18-79"
        ),
        "criteria": {
            "age_min": 18,
            "age_max": 79,
        },
        "recommendation": (
            "Order anti-HCV antibody test. If positive, confirm with "
            "HCV RNA. Refer for treatment if positive."
        ),
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF Hepatitis C Screening 2020",
    },

    {
        "id": "hepatitis_b_screening_high_risk",
        "guideline": "USPSTF 2020",
        "category": "infectious_disease_screening",
        "description": (
            "Hepatitis B screening recommended for high-risk adults "
            "(birth in endemic country, IV drug use, sexual exposure)"
        ),
        "criteria": {
            "any_condition_present": [
                "iv_drug_use_history",
                "born_in_hbv_endemic_country",
                "hiv_positive",
                "men_who_have_sex_with_men",
            ],
        },
        "recommendation": (
            "Order HBsAg, anti-HBs, and anti-HBc. Vaccinate if "
            "non-immune; refer if positive."
        ),
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF Hepatitis B Screening 2020",
    },

    {
        "id": "hiv_screening_universal",
        "guideline": "USPSTF 2019",
        "category": "infectious_disease_screening",
        "description": (
            "HIV screening recommended for all adolescents and adults "
            "age 15-65"
        ),
        "criteria": {
            "age_min": 15,
            "age_max": 65,
        },
        "recommendation": (
            "Order 4th-generation HIV antigen/antibody combination "
            "assay. Repeat at clinician discretion based on risk."
        ),
        "evidence_grade": "A",
        "priority": "moderate",
        "citation": "USPSTF HIV Screening 2019",
    },

    {
        "id": "lung_cancer_screening_high_risk",
        "guideline": "USPSTF 2021",
        "category": "cancer_screening",
        "description": (
            "Annual low-dose CT for lung cancer screening in adults "
            "age 50-80 with 20+ pack-years who currently smoke or quit "
            "within 15 years"
        ),
        "criteria": {
            "age_min": 50,
            "age_max": 80,
            "smoking_pack_years_min": 20,
            "smoking_status_any": ["current", "former_quit_within_15_years"],
        },
        "recommendation": (
            "Order annual low-dose chest CT. Counsel on smoking "
            "cessation if current smoker."
        ),
        "evidence_grade": "B",
        "priority": "high",
        "citation": "USPSTF Lung Cancer Screening 2021",
    },

    # -----------------------------------------------------------------------
    # Primary Prevention (Statin / Aspirin)
    # -----------------------------------------------------------------------

    {
        "id": "statin_primary_prevention_high_ascvd",
        "guideline": "ACC/AHA 2018 + USPSTF 2022",
        "category": "lipid_management",
        "description": (
            "Statin recommended for primary prevention if 10-year ASCVD "
            "risk >=10%"
        ),
        "criteria": {
            "age_min": 40,
            "age_max": 75,
            "ascvd_10yr_risk_min": 10,
            "medication_class_absent": ["statin"],
            "conditions_absent": ["pregnancy"],
        },
        "recommendation": (
            "Initiate moderate- or high-intensity statin therapy "
            "(atorvastatin 20-40 mg or rosuvastatin 10-20 mg)."
        ),
        "evidence_grade": "A",
        "priority": "high",
        "citation": "ACC/AHA 2018 Cholesterol Guidelines, USPSTF 2022",
    },

    {
        "id": "aspirin_primary_prevention_nuanced",
        "guideline": "USPSTF 2022",
        "category": "antiplatelet_therapy",
        "description": (
            "Low-dose aspirin for primary CV prevention has narrow benefit "
            "window; consider only if age 40-59 with 10-yr ASCVD >=10%"
        ),
        "criteria": {
            "age_min": 40,
            "age_max": 59,
            "ascvd_10yr_risk_min": 10,
            "medication_class_absent": ["antiplatelet"],
            "bleeding_risk_low": True,
            "conditions_absent": ["active_bleeding", "peptic_ulcer_disease"],
        },
        "recommendation": (
            "Discuss aspirin 81 mg daily with patient. Net benefit "
            "depends on patient bleeding risk and preferences."
        ),
        "evidence_grade": "C",
        "priority": "low",
        "citation": "USPSTF Aspirin for Primary CV Prevention 2022",
    },

    # -----------------------------------------------------------------------
    # Diabetes Screening (USPSTF + ADA)
    # -----------------------------------------------------------------------

    {
        "id": "prediabetes_diabetes_screening_uspstf",
        "guideline": "USPSTF 2021 + ADA 2024",
        "category": "diabetes_screening",
        "description": (
            "Screen for prediabetes and type 2 diabetes in adults age "
            "35-70 who are overweight or obese"
        ),
        "criteria": {
            "age_min": 35,
            "age_max": 70,
            "bmi_min": 25,
            "conditions_absent": ["type_2_diabetes", "type_1_diabetes"],
        },
        "recommendation": (
            "Order HbA1c or fasting plasma glucose. Repeat every 3 years "
            "if normal, or annually if prediabetes."
        ),
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF Diabetes Screening 2021, ADA Standards 2024",
    },

    # -----------------------------------------------------------------------
    # USPSTF Behavioral Counseling (added in Task 5C)
    # -----------------------------------------------------------------------

    {
        "id": "depression_screening_adults",
        "guideline": "USPSTF 2023",
        "category": "mental_health",
        "description": (
            "Depression screening recommended for all adults including "
            "older adults"
        ),
        "criteria": {
            "age_min": 18,
        },
        "recommendation": (
            "Administer PHQ-2 or PHQ-9. If positive, full evaluation and "
            "treatment per stepped care model."
        ),
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF Depression Screening 2023",
    },

    {
        "id": "falls_prevention_older_adults",
        "guideline": "USPSTF 2018",
        "category": "geriatrics",
        "description": (
            "Exercise interventions and multifactorial assessment to "
            "prevent falls in community-dwelling adults 65+"
        ),
        "criteria": {
            "age_min": 65,
        },
        "recommendation": (
            "Assess gait, balance, vision, medication review (Beers "
            "criteria). Refer to PT for exercise program if at risk."
        ),
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF Falls Prevention 2018",
    },

    {
        "id": "tobacco_cessation_counseling",
        "guideline": "USPSTF 2021",
        "category": "preventive_care",
        "description": (
            "Behavioral counseling and pharmacotherapy for all adults "
            "who use tobacco"
        ),
        "criteria": {
            "age_min": 18,
            "smoking_status_any": ["current"],
        },
        "recommendation": (
            "Brief counseling at every visit (5 A's: Ask, Advise, Assess, "
            "Assist, Arrange). Offer nicotine replacement, varenicline, "
            "or bupropion."
        ),
        "evidence_grade": "A",
        "priority": "high",
        "citation": "USPSTF Tobacco Cessation 2021",
    },

    {
        "id": "alcohol_use_screening",
        "guideline": "USPSTF 2018",
        "category": "preventive_care",
        "description": (
            "Screening and brief behavioral counseling for unhealthy "
            "alcohol use in primary care adults"
        ),
        "criteria": {
            "age_min": 18,
        },
        "recommendation": (
            "Use AUDIT-C or single-question screen. Provide brief "
            "intervention if positive; refer if alcohol use disorder."
        ),
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF Unhealthy Alcohol Use 2018",
    },

    {
        "id": "physical_activity_counseling_cv_risk",
        "guideline": "USPSTF 2020",
        "category": "preventive_care",
        "description": (
            "Behavioral counseling on healthy diet and physical activity "
            "for CV risk reduction in adults with CVD risk factors"
        ),
        "criteria": {
            "age_min": 35,
            "any_condition_present": [
                "hypertension", "dyslipidemia", "type_2_diabetes",
                "obesity", "metabolic_syndrome",
            ],
        },
        "recommendation": (
            "Refer to or provide intensive behavioral counseling on "
            "healthy diet and physical activity (>=150 min/week "
            "moderate-intensity). Recommendation grade B."
        ),
        "evidence_grade": "B",
        "priority": "moderate",
        "citation": "USPSTF Healthy Diet and Physical Activity 2020",
    },
]


# ===========================================================================
# DIAGNOSTIC GAP RULES
# ===========================================================================
# Patterns suggesting an undiagnosed condition.

DIAGNOSTIC_GAP_RULES: list[dict] = [

    # -----------------------------------------------------------------------
    # Anemia in CKD (very common missed diagnosis)
    # -----------------------------------------------------------------------

    {
        "id": "ckd_anemia_undiagnosed",
        "category": "hematology",
        "description": "Possible CKD-associated anemia not yet diagnosed",
        "pattern": {
            "conditions_present": ["chronic_kidney_disease"],
            "egfr_below": 60,
            "lab_below_threshold": {
                "test": "hemoglobin",
                "threshold_female": 12.0,
                "threshold_male": 13.0,
            },
            "diagnosis_absent": ["anemia", "anemia_of_ckd"],
        },
        "explanation": (
            "At eGFR < 60, reduced erythropoietin production can cause "
            "anemia. Hemoglobin is below normal but anemia is not on the "
            "problem list."
        ),
        "recommended_workup": [
            "reticulocyte_count", "iron_panel", "ferritin",
            "transferrin_saturation", "vitamin_b12", "folate",
            "epo_level_if_appropriate",
        ],
        "likely_diagnosis": (
            "CKD-associated anemia (reduced EPO production); "
            "rule out iron deficiency"
        ),
        "urgency": "moderate",
        "citation": "KDIGO 2012 Anemia in CKD Clinical Practice Guideline",
    },

    # -----------------------------------------------------------------------
    # MASLD / NAFLD
    # -----------------------------------------------------------------------

    {
        "id": "masld_undiagnosed",
        "category": "hepatology",
        "description": (
            "Possible MASLD (metabolic-associated steatotic liver disease)"
        ),
        "pattern": {
            "any_condition_present": [
                "obesity", "type_2_diabetes",
                "metabolic_syndrome", "dyslipidemia",
            ],
            "lab_above_threshold_persistent": {
                "test": "alt",
                "threshold": 40,
                "min_occurrences": 2,
            },
            "diagnosis_absent": [
                "masld", "nafld", "fatty_liver",
                "steatohepatitis", "nash",
            ],
        },
        "explanation": (
            "Persistent ALT elevation with metabolic risk factors strongly "
            "suggests undiagnosed MASLD. Up to 70% of T2DM patients have "
            "MASLD."
        ),
        "recommended_workup": [
            "fib4_calculation", "fibroscan_or_elastography",
            "rule_out_viral_hepatitis", "rule_out_alcohol",
            "consider_liver_mre",
        ],
        "likely_diagnosis": (
            "MASLD (metabolic-associated steatotic liver disease)"
        ),
        "urgency": "moderate",
        "citation": "AASLD 2023 Practice Guidance on MASLD",
    },

    # -----------------------------------------------------------------------
    # Sleep apnea
    # -----------------------------------------------------------------------

    {
        "id": "osa_undiagnosed",
        "category": "pulmonary",
        "description": "Possible obstructive sleep apnea (OSA)",
        "pattern": {
            "all_conditions_present": ["obesity"],
            "any_condition_present": [
                "hypertension", "atrial_fibrillation", "type_2_diabetes",
            ],
            "diagnosis_absent": [
                "sleep_apnea", "obstructive_sleep_apnea", "osa",
            ],
        },
        "explanation": (
            "Obesity plus hypertension/AFib/diabetes is a strong OSA "
            "phenotype. Untreated OSA worsens BP, glycemic control, and "
            "CV outcomes."
        ),
        "recommended_workup": [
            "stop_bang_questionnaire", "epworth_sleepiness_scale",
            "polysomnography_or_home_sleep_test",
        ],
        "likely_diagnosis": "Obstructive sleep apnea",
        "urgency": "moderate",
        "citation": "AASM 2017 Clinical Practice Guideline",
    },

    # -----------------------------------------------------------------------
    # Thyroid dysfunction
    # -----------------------------------------------------------------------

    {
        "id": "thyroid_dysfunction_unscreened",
        "category": "endocrinology",
        "description": (
            "Symptoms suggestive of thyroid dysfunction without recent TSH"
        ),
        "pattern": {
            "any_condition_present": ["fatigue", "weight_gain", "weight_loss"],
            "screening_overdue": {
                "test": "tsh",
                "max_months_since_last": 24,
            },
            "diagnosis_absent": ["hypothyroidism", "hyperthyroidism"],
        },
        "explanation": (
            "Common symptoms (fatigue, weight changes) without recent TSH "
            "evaluation. Thyroid dysfunction is common and easily screened."
        ),
        "recommended_workup": ["tsh", "free_t4_if_tsh_abnormal"],
        "likely_diagnosis": "Hypothyroidism or hyperthyroidism (rule out)",
        "urgency": "low",
        "citation": "ATA Guidelines on Thyroid Dysfunction Screening",
    },

    # -----------------------------------------------------------------------
    # Hyperkalemia risk
    # -----------------------------------------------------------------------

    {
        "id": "hyperkalemia_risk_combo",
        "category": "electrolytes",
        "description": (
            "High hyperkalemia risk: ACEi/ARB + MRA + CKD"
        ),
        "pattern": {
            "medications_class_present_any": [
                "ace_inhibitor", "arb",
            ],
            "medications_present_any": ["spironolactone", "eplerenone"],
            "egfr_below": 60,
        },
        "explanation": (
            "Combination of RAAS blockade + MRA + reduced eGFR substantially "
            "increases hyperkalemia risk. Frequent monitoring required."
        ),
        "recommended_workup": [
            "potassium_within_1_week",
            "more_frequent_potassium_monitoring",
            "review_dietary_potassium",
            "review_other_potassium_sparing_drugs",
        ],
        "likely_diagnosis": "Iatrogenic hyperkalemia risk",
        "urgency": "high",
        "citation": "KDIGO 2024 / ACC/AHA / KDOQI",
    },

    # -----------------------------------------------------------------------
    # Diabetic neuropathy
    # -----------------------------------------------------------------------

    {
        "id": "diabetic_neuropathy_unscreened",
        "category": "diabetes_complication",
        "description": (
            "Diabetic neuropathy not assessed in long-standing diabetes"
        ),
        "pattern": {
            "conditions_present": ["type_2_diabetes"],
            "diabetes_duration_years_min": 5,
            "screening_overdue": {
                "test": "neuropathy_assessment",
                "max_months_since_last": 12,
            },
            "diagnosis_absent": [
                "diabetic_neuropathy", "peripheral_neuropathy",
            ],
        },
        "explanation": (
            "Diabetic peripheral neuropathy affects ~50% of long-standing "
            "diabetics. Screening with monofilament and vibration testing "
            "is recommended annually."
        ),
        "recommended_workup": [
            "10g_monofilament_testing",
            "128hz_vibration_testing",
            "ankle_reflex_assessment",
            "consider_ncs_emg_if_atypical",
        ],
        "likely_diagnosis": "Diabetic peripheral neuropathy",
        "urgency": "low",
        "citation": "ADA Standards of Care 2024, Section 12",
    },

    # -----------------------------------------------------------------------
    # Peripheral artery disease
    # -----------------------------------------------------------------------

    {
        "id": "pad_undiagnosed",
        "category": "vascular",
        "description": "Possible peripheral artery disease",
        "pattern": {
            "any_condition_present": [
                "type_2_diabetes", "smoking", "hypertension",
            ],
            "age_min": 65,
            "any_symptom_present": [
                "claudication", "leg_pain", "non_healing_ulcer",
            ],
            "diagnosis_absent": [
                "peripheral_artery_disease", "pad",
            ],
        },
        "explanation": (
            "Vascular risk factors plus lower extremity symptoms suggest "
            "PAD. ABI is a simple non-invasive screen."
        ),
        "recommended_workup": [
            "ankle_brachial_index", "vascular_ultrasound_if_abi_abnormal",
        ],
        "likely_diagnosis": "Peripheral artery disease",
        "urgency": "moderate",
        "citation": "ACC/AHA 2016 PAD Guideline",
    },

    # -----------------------------------------------------------------------
    # Vitamin D deficiency in CKD
    # -----------------------------------------------------------------------

    {
        "id": "vitamin_d_deficiency_ckd",
        "category": "bone_mineral",
        "description": "Vitamin D not measured in CKD",
        "pattern": {
            "conditions_present": ["chronic_kidney_disease"],
            "egfr_below": 60,
            "screening_overdue": {
                "test": "25_hydroxy_vitamin_d",
                "max_months_since_last": 24,
            },
        },
        "explanation": (
            "CKD impairs vitamin D activation. Deficiency is common and "
            "contributes to CKD-MBD."
        ),
        "recommended_workup": [
            "25_hydroxy_vitamin_d", "calcium", "phosphate", "pth",
        ],
        "likely_diagnosis": "Vitamin D insufficiency / CKD-MBD",
        "urgency": "low",
        "citation": "KDIGO 2017 CKD-MBD Update",
    },

    # -----------------------------------------------------------------------
    # Nephrotoxin combo (the "triple whammy")
    # -----------------------------------------------------------------------

    {
        "id": "triple_whammy_nephrotoxicity",
        "category": "drug_safety",
        "description": (
            "ACEi/ARB + diuretic + NSAID = triple whammy AKI risk"
        ),
        "pattern": {
            "medications_class_present_all": [
                "ace_or_arb", "diuretic", "nsaid",
            ],
        },
        "explanation": (
            "Triple combination dramatically increases acute kidney injury "
            "risk, especially in elderly or volume-depleted patients."
        ),
        "recommended_workup": [
            "renal_function_within_1_week",
            "discontinue_nsaid_if_possible",
            "consider_alternative_analgesia",
        ],
        "likely_diagnosis": "Drug-induced AKI risk (triple whammy)",
        "urgency": "high",
        "citation": "BMJ 2013;346:e8525 (Lapi et al.)",
    },

    # -----------------------------------------------------------------------
    # Resistant hypertension / secondary causes
    # -----------------------------------------------------------------------

    {
        "id": "resistant_hypertension_secondary",
        "category": "hypertension",
        "description": (
            "Resistant hypertension warranting secondary cause workup"
        ),
        "pattern": {
            "conditions_present": ["hypertension"],
            "vital_above_threshold_persistent": {
                "vital": "systolic_bp",
                "threshold": 140,
                "min_occurrences": 3,
            },
            "medications_class_count_min": {
                "classes": ["ace_inhibitor", "arb", "diuretic", "ccb", "beta_blocker"],
                "min_count": 3,
            },
        },
        "explanation": (
            "BP above target despite >= 3 antihypertensive classes including "
            "a diuretic suggests resistant hypertension. Secondary causes "
            "warrant evaluation."
        ),
        "recommended_workup": [
            "aldosterone_renin_ratio",
            "plasma_metanephrines",
            "renal_artery_imaging",
            "polysomnography_for_osa",
            "tsh",
        ],
        "likely_diagnosis": (
            "Secondary hypertension (primary aldosteronism, renal artery "
            "stenosis, OSA, or pheochromocytoma)"
        ),
        "urgency": "moderate",
        "citation": "ACC/AHA 2017 Hypertension Guideline",
    },

    # -----------------------------------------------------------------------
    # Cognitive impairment
    # -----------------------------------------------------------------------

    {
        "id": "cognitive_impairment_unscreened",
        "category": "neurology",
        "description": "Cognitive screening overdue in elderly",
        "pattern": {
            "age_min": 65,
            "screening_overdue": {
                "test": "cognitive_assessment",
                "max_months_since_last": 24,
            },
            "diagnosis_absent": ["dementia", "mild_cognitive_impairment"],
        },
        "explanation": (
            "Annual or biennial cognitive screening in elderly enables "
            "early detection and intervention."
        ),
        "recommended_workup": [
            "mini_cog_or_moca", "history_from_caregiver",
        ],
        "likely_diagnosis": "Mild cognitive impairment or early dementia",
        "urgency": "low",
        "citation": "Medicare Annual Wellness Visit / AAN 2018",
    },
]


# ===========================================================================
# INTERNAL HELPERS
# ===========================================================================

def _normalize(s: str) -> str:
    """Normalize a string for comparison: lowercase, strip whitespace."""
    return s.lower().strip() if s else ""


def _normalize_set(items: list[str]) -> set[str]:
    """Normalize a list to a lowercase set."""
    return {_normalize(s) for s in (items or [])}


def _has_any(target: set[str], candidates: list[str]) -> bool:
    """True if any candidate matches a target item (substring-tolerant)."""
    cand_norm = [_normalize(c) for c in candidates]
    for c in cand_norm:
        for t in target:
            if c == t or c in t or t in c:
                return True
    return False


def _has_all(target: set[str], required: list[str]) -> bool:
    """True if every required item matches some target item."""
    for r in required:
        rn = _normalize(r)
        if not any(rn == t or rn in t or t in rn for t in target):
            return False
    return True


def _med_class_present(
    medication_classes: list[str], required_classes: list[str]
) -> bool:
    """True if any required drug class is present in patient's classes."""
    present = _normalize_set(medication_classes)
    return _has_any(present, required_classes)


def _med_class_absent(
    medication_classes: list[str], required_classes: list[str]
) -> bool:
    """True if NO required drug class is in patient's classes."""
    return not _med_class_present(medication_classes, required_classes)


def _med_present(
    medications: list[str], required_meds: list[str]
) -> bool:
    """True if any required medication name is in patient's med list."""
    present = _normalize_set(medications)
    return _has_any(present, required_meds)


def _condition_present_all(
    patient_conditions: list[str], required: list[str]
) -> bool:
    """True if ALL required conditions are present (substring-tolerant)."""
    present = _normalize_set(patient_conditions)
    return _has_all(present, required)


def _condition_present_any(
    patient_conditions: list[str], required: list[str]
) -> bool:
    """True if ANY required condition is present."""
    present = _normalize_set(patient_conditions)
    return _has_any(present, required)


def _condition_absent_all(
    patient_conditions: list[str], excluded: list[str]
) -> bool:
    """True if NONE of the excluded conditions are present."""
    present = _normalize_set(patient_conditions)
    for e in excluded:
        en = _normalize(e)
        if any(en == p or en in p or p in en for p in present):
            return False
    return True


def _evaluate_care_gap_rule(
    rule: dict,
    patient_conditions: list[str],
    patient_medications: list[str],
    patient_medication_classes: list[str],
    patient_labs: dict,
    patient_vitals: dict,
    patient_age: Optional[int],
    patient_sex: Optional[str],
    patient_bmi: Optional[float],
    patient_egfr: Optional[float],
    ascvd_risk_percent: Optional[float],
    smoking_pack_years: Optional[float],
    last_screening_dates: dict,
) -> bool:
    """Return True if the care-gap rule's criteria are all satisfied."""
    crit = rule.get("criteria", {})

    # Age bounds
    if "age_min" in crit:
        if patient_age is None or patient_age < crit["age_min"]:
            return False
    if "age_max" in crit:
        if patient_age is None or patient_age > crit["age_max"]:
            return False

    # Sex
    if "sex" in crit:
        if not patient_sex or _normalize(patient_sex) != _normalize(crit["sex"]):
            return False

    # eGFR thresholds
    if "egfr_min" in crit:
        if patient_egfr is None or patient_egfr < crit["egfr_min"]:
            return False
    if "egfr_max" in crit:
        if patient_egfr is None or patient_egfr > crit["egfr_max"]:
            return False

    # BMI threshold
    if "bmi_min" in crit:
        if patient_bmi is None or patient_bmi < crit["bmi_min"]:
            return False

    # ASCVD risk
    if "ascvd_risk_min" in crit:
        if ascvd_risk_percent is None or ascvd_risk_percent < crit["ascvd_risk_min"]:
            return False

    # Smoking
    if "smoking_history_pack_years_min" in crit:
        if (
            smoking_pack_years is None
            or smoking_pack_years < crit["smoking_history_pack_years_min"]
        ):
            return False

    # Conditions
    if "conditions_present" in crit:
        if not _condition_present_all(
            patient_conditions, crit["conditions_present"]
        ):
            return False
    if "any_condition_present" in crit:
        if not _condition_present_any(
            patient_conditions, crit["any_condition_present"]
        ):
            return False
    if "conditions_absent" in crit:
        if not _condition_absent_all(
            patient_conditions, crit["conditions_absent"]
        ):
            return False

    # Medication checks
    if "medication_absent" in crit:
        if _med_present(patient_medications, crit["medication_absent"]):
            return False
    if "medications_present" in crit:
        if not _med_present(patient_medications, crit["medications_present"]):
            return False
    if "medication_class_absent" in crit:
        if _med_class_present(
            patient_medication_classes, crit["medication_class_absent"]
        ):
            return False
    if "medications_class_present" in crit:
        if not _med_class_present(
            patient_medication_classes, crit["medications_class_present"]
        ):
            return False
    if "missing_medication_class_any_of" in crit:
        # Triggers if ANY of these classes is absent
        any_missing = False
        for cls in crit["missing_medication_class_any_of"]:
            if _med_class_absent(patient_medication_classes, [cls]):
                any_missing = True
                break
        if not any_missing:
            return False

    # Lab thresholds
    if "lab_above_threshold" in crit:
        spec = crit["lab_above_threshold"]
        test = spec["test"]
        threshold = spec["threshold"]
        val = patient_labs.get(test)
        if val is None or val <= threshold:
            return False
    if "lab_below_threshold" in crit:
        spec = crit["lab_below_threshold"]
        test = spec["test"]
        threshold = spec["threshold"]
        val = patient_labs.get(test)
        if val is None or val >= threshold:
            return False

    # Vital thresholds
    if "vital_above_threshold" in crit:
        spec = crit["vital_above_threshold"]
        vital = spec["vital"]
        threshold = spec["threshold"]
        val = patient_vitals.get(vital)
        if val is None or val <= threshold:
            return False

    # Screening overdue
    if "screening_overdue" in crit:
        spec = crit["screening_overdue"]
        test = spec["test"]
        max_months = spec["max_months_since_last"]
        months_since = last_screening_dates.get(test)
        # If never screened, always overdue
        if months_since is None:
            pass  # triggers
        elif months_since <= max_months:
            return False

    if "screening_ever_done" in crit:
        spec = crit["screening_ever_done"]
        test = spec["test"]
        if test in last_screening_dates and last_screening_dates[test] is not None:
            return False

    return True


def _evaluate_diagnostic_gap_rule(
    rule: dict,
    patient_conditions: list[str],
    patient_medications: list[str],
    patient_medication_classes: list[str],
    patient_labs: dict,
    patient_vitals: dict,
    patient_age: Optional[int],
    patient_sex: Optional[str],
    patient_egfr: Optional[float],
    persistent_lab_history: dict,
    persistent_vital_history: dict,
    diabetes_duration_years: Optional[float],
    last_screening_dates: dict,
    patient_symptoms: Optional[list[str]] = None,
) -> bool:
    """Return True if the diagnostic-gap pattern's criteria are met."""
    pat = rule.get("pattern", {})

    # Demographics
    if "age_min" in pat:
        if patient_age is None or patient_age < pat["age_min"]:
            return False
    if "age_max" in pat:
        if patient_age is None or patient_age > pat["age_max"]:
            return False
    if "sex" in pat:
        if not patient_sex or _normalize(patient_sex) != _normalize(pat["sex"]):
            return False

    # Conditions present (any/all)
    if "conditions_present" in pat:
        if not _condition_present_all(patient_conditions, pat["conditions_present"]):
            return False
    if "all_conditions_present" in pat:
        if not _condition_present_all(patient_conditions, pat["all_conditions_present"]):
            return False
    if "any_condition_present" in pat:
        if not _condition_present_any(patient_conditions, pat["any_condition_present"]):
            return False

    # Diagnoses absent
    if "diagnosis_absent" in pat:
        if not _condition_absent_all(patient_conditions, pat["diagnosis_absent"]):
            return False

    # eGFR threshold
    if "egfr_below" in pat:
        if patient_egfr is None or patient_egfr >= pat["egfr_below"]:
            return False
    if "egfr_above" in pat:
        if patient_egfr is None or patient_egfr <= pat["egfr_above"]:
            return False

    # Sex-specific lab threshold
    if "lab_below_threshold" in pat:
        spec = pat["lab_below_threshold"]
        test = spec["test"]
        sex_norm = _normalize(patient_sex) if patient_sex else "unknown"
        if sex_norm == "female" and "threshold_female" in spec:
            threshold = spec["threshold_female"]
        elif sex_norm == "male" and "threshold_male" in spec:
            threshold = spec["threshold_male"]
        else:
            threshold = spec.get("threshold")
        val = patient_labs.get(test)
        if val is None or threshold is None or val >= threshold:
            return False

    # Persistent lab elevation
    if "lab_above_threshold_persistent" in pat:
        spec = pat["lab_above_threshold_persistent"]
        test = spec["test"]
        threshold = spec["threshold"]
        min_occ = spec["min_occurrences"]
        history = persistent_lab_history.get(test, [])
        elevated = [v for v in history if v is not None and v > threshold]
        if len(elevated) < min_occ:
            return False

    # Persistent vital elevation
    if "vital_above_threshold_persistent" in pat:
        spec = pat["vital_above_threshold_persistent"]
        vital = spec["vital"]
        threshold = spec["threshold"]
        min_occ = spec["min_occurrences"]
        history = persistent_vital_history.get(vital, [])
        elevated = [v for v in history if v is not None and v > threshold]
        if len(elevated) < min_occ:
            return False

    # Medications
    if "medications_class_present_any" in pat:
        if not _med_class_present(
            patient_medication_classes, pat["medications_class_present_any"]
        ):
            return False
    if "medications_present_any" in pat:
        if not _med_present(patient_medications, pat["medications_present_any"]):
            return False
    if "medications_class_present_all" in pat:
        for cls in pat["medications_class_present_all"]:
            if not _med_class_present(patient_medication_classes, [cls]):
                return False
    if "medications_class_count_min" in pat:
        spec = pat["medications_class_count_min"]
        present_count = sum(
            1 for cls in spec["classes"]
            if _med_class_present(patient_medication_classes, [cls])
        )
        if present_count < spec["min_count"]:
            return False

    # Diabetes duration
    if "diabetes_duration_years_min" in pat:
        if (
            diabetes_duration_years is None
            or diabetes_duration_years < pat["diabetes_duration_years_min"]
        ):
            return False

    # Screening overdue
    if "screening_overdue" in pat:
        spec = pat["screening_overdue"]
        test = spec["test"]
        max_months = spec["max_months_since_last"]
        months_since = last_screening_dates.get(test)
        if months_since is not None and months_since <= max_months:
            return False

    # Symptoms
    if "any_symptom_present" in pat:
        if not patient_symptoms:
            return False
        if not _condition_present_any(patient_symptoms, pat["any_symptom_present"]):
            return False

    return True


# ===========================================================================
# PUBLIC API
# ===========================================================================

def get_all_care_gap_rules() -> list[dict]:
    """Return all care gap rules in the knowledge base."""
    return list(CARE_GAP_RULES)


def get_care_gap_rules_for_condition(condition: str) -> list[dict]:
    """
    Return care gap rules whose criteria reference a given condition.

    Useful for showing condition-relevant rules to clinicians.

    Parameters
    ----------
    condition : str
        Condition keyword (e.g., "diabetes", "ckd", "hypertension").

    Returns
    -------
    list of dict
        Matching care gap rules.
    """
    if not condition:
        return []
    cond = _normalize(condition)
    matching = []
    for rule in CARE_GAP_RULES:
        crit = rule.get("criteria", {})
        # Search across condition fields and category
        candidates: list[str] = []
        candidates.extend(crit.get("conditions_present", []))
        candidates.extend(crit.get("any_condition_present", []))
        candidates.append(rule.get("category", ""))
        candidates_norm = _normalize_set(candidates)
        if any(cond == c or cond in c or c in cond for c in candidates_norm):
            matching.append(rule)
    return matching


def get_all_diagnostic_gap_rules() -> list[dict]:
    """Return all diagnostic gap rules."""
    return list(DIAGNOSTIC_GAP_RULES)


def get_diagnostic_gap_rules_for_condition(condition: str) -> list[dict]:
    """
    Return diagnostic gap rules whose pattern references a given condition.

    Parameters
    ----------
    condition : str
        Condition keyword.

    Returns
    -------
    list of dict
        Matching diagnostic gap rules.
    """
    if not condition:
        return []
    cond = _normalize(condition)
    matching = []
    for rule in DIAGNOSTIC_GAP_RULES:
        pat = rule.get("pattern", {})
        candidates: list[str] = []
        candidates.extend(pat.get("conditions_present", []))
        candidates.extend(pat.get("all_conditions_present", []))
        candidates.extend(pat.get("any_condition_present", []))
        candidates.extend(pat.get("diagnosis_absent", []))
        candidates.append(rule.get("category", ""))
        candidates_norm = _normalize_set(candidates)
        if any(cond == c or cond in c or c in cond for c in candidates_norm):
            matching.append(rule)
    return matching


def evaluate_care_gaps(
    patient_conditions: list[str],
    patient_medications: list[str],
    patient_labs: dict,
    patient_age: int,
    patient_sex: str,
    patient_medication_classes: Optional[list[str]] = None,
    patient_vitals: Optional[dict] = None,
    patient_bmi: Optional[float] = None,
    patient_egfr: Optional[float] = None,
    ascvd_risk_percent: Optional[float] = None,
    smoking_pack_years: Optional[float] = None,
    last_screening_dates: Optional[dict] = None,
) -> list[dict]:
    """
    Evaluate all care gap rules against a patient and return triggered gaps.

    Each returned entry includes the original rule plus an 'evidence_summary'
    field summarizing which criteria triggered.

    Parameters
    ----------
    patient_conditions : list of str
        Active diagnoses (e.g., "type_2_diabetes", "chronic_kidney_disease").
    patient_medications : list of str
        Generic names of current medications.
    patient_labs : dict
        Latest lab values keyed by test name (e.g., {"hba1c": 8.2}).
    patient_age : int
    patient_sex : str
        "male" or "female".
    patient_medication_classes : list of str, optional
        Drug classes patient is on. Inferred or supplied by caller.
    patient_vitals : dict, optional
        Latest vital signs (e.g., {"systolic_bp": 145}).
    patient_bmi : float, optional
    patient_egfr : float, optional
    ascvd_risk_percent : float, optional
        Computed 10-year ASCVD risk.
    smoking_pack_years : float, optional
    last_screening_dates : dict, optional
        Months since last screening, keyed by test name. Missing keys
        treated as never screened.

    Returns
    -------
    list of dict
        Triggered care gaps with full rule data plus evaluation context.
    """
    classes = patient_medication_classes or []
    vitals = patient_vitals or {}
    screenings = last_screening_dates or {}
    triggered = []

    for rule in CARE_GAP_RULES:
        if _evaluate_care_gap_rule(
            rule=rule,
            patient_conditions=patient_conditions,
            patient_medications=patient_medications,
            patient_medication_classes=classes,
            patient_labs=patient_labs,
            patient_vitals=vitals,
            patient_age=patient_age,
            patient_sex=patient_sex,
            patient_bmi=patient_bmi,
            patient_egfr=patient_egfr,
            ascvd_risk_percent=ascvd_risk_percent,
            smoking_pack_years=smoking_pack_years,
            last_screening_dates=screenings,
        ):
            triggered.append({
                "rule_id": rule["id"],
                "guideline": rule.get("guideline"),
                "category": rule.get("category"),
                "description": rule.get("description"),
                "recommendation": rule.get("recommendation"),
                "evidence_grade": rule.get("evidence_grade"),
                "priority": rule.get("priority"),
                "citation": rule.get("citation"),
            })
    return triggered


def evaluate_diagnostic_gaps(
    patient_conditions: list[str],
    patient_labs: dict,
    patient_vitals: dict,
    patient_age: int,
    patient_sex: str,
    patient_medications: Optional[list[str]] = None,
    patient_medication_classes: Optional[list[str]] = None,
    patient_egfr: Optional[float] = None,
    persistent_lab_history: Optional[dict] = None,
    persistent_vital_history: Optional[dict] = None,
    diabetes_duration_years: Optional[float] = None,
    last_screening_dates: Optional[dict] = None,
    patient_symptoms: Optional[list[str]] = None,
) -> list[dict]:
    """
    Evaluate all diagnostic gap rules and return matching patterns.

    Parameters
    ----------
    patient_conditions, patient_labs, patient_vitals, patient_age, patient_sex
        Same as for evaluate_care_gaps.
    patient_medications : list of str, optional
    patient_medication_classes : list of str, optional
    patient_egfr : float, optional
    persistent_lab_history : dict, optional
        For each lab test, list of historical values
        (e.g., {"alt": [42, 58, 51]}).
    persistent_vital_history : dict, optional
        Same structure for vitals (e.g., {"systolic_bp": [148, 152, 145]}).
    diabetes_duration_years : float, optional
    last_screening_dates : dict, optional
        Months since last screening, keyed by test name.
    patient_symptoms : list of str, optional
        Reported symptoms (for symptom-pattern rules).

    Returns
    -------
    list of dict
        Triggered diagnostic gap patterns with workup recommendations.
    """
    meds = patient_medications or []
    classes = patient_medication_classes or []
    lab_history = persistent_lab_history or {}
    vital_history = persistent_vital_history or {}
    screenings = last_screening_dates or {}
    triggered = []

    for rule in DIAGNOSTIC_GAP_RULES:
        if _evaluate_diagnostic_gap_rule(
            rule=rule,
            patient_conditions=patient_conditions,
            patient_medications=meds,
            patient_medication_classes=classes,
            patient_labs=patient_labs,
            patient_vitals=patient_vitals,
            patient_age=patient_age,
            patient_sex=patient_sex,
            patient_egfr=patient_egfr,
            persistent_lab_history=lab_history,
            persistent_vital_history=vital_history,
            diabetes_duration_years=diabetes_duration_years,
            last_screening_dates=screenings,
            patient_symptoms=patient_symptoms,
        ):
            triggered.append({
                "rule_id": rule["id"],
                "category": rule.get("category"),
                "description": rule.get("description"),
                "explanation": rule.get("explanation"),
                "recommended_workup": rule.get("recommended_workup"),
                "likely_diagnosis": rule.get("likely_diagnosis"),
                "urgency": rule.get("urgency"),
                "citation": rule.get("citation"),
            })
    return triggered


# ===========================================================================
# Module-level metadata
# ===========================================================================

__all__ = [
    "CARE_GAP_RULES",
    "DIAGNOSTIC_GAP_RULES",
    "get_all_care_gap_rules",
    "get_care_gap_rules_for_condition",
    "get_all_diagnostic_gap_rules",
    "get_diagnostic_gap_rules_for_condition",
    "evaluate_care_gaps",
    "evaluate_diagnostic_gaps",
]