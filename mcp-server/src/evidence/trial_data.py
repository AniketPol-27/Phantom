"""
trial_data.py

Structured clinical trial outcome database for the Phantom simulation engine.

When the simulation engine projects a treatment effect (e.g., "adding
dapagliflozin slows eGFR decline by ~39%"), it pulls the underlying
numeric evidence from this module and cites the source trial.

Each trial entry encodes:
  - Trial identifiers (name, year, journal, PMID)
  - Population characteristics (size, demographics, inclusion criteria)
  - Primary outcome with hazard ratio, CI, p-value, NNT
  - Secondary outcomes
  - eGFR slope data where applicable
  - Safety outcomes
  - Subgroup analyses
  - Applicability notes for clinical reasoning

All data sourced directly from peer-reviewed publications.
This module has zero dependencies on FHIR, MCP, or platform code.
"""

from __future__ import annotations

from typing import Optional


# ===========================================================================
# CLINICAL TRIAL DATABASE
# ===========================================================================

_TRIALS: dict[str, dict] = {

    # -----------------------------------------------------------------------
    # DAPA-CKD: Dapagliflozin in CKD
    # -----------------------------------------------------------------------

    "DAPA-CKD": {
        "trial_name": "DAPA-CKD",
        "full_name": (
            "Dapagliflozin and Prevention of Adverse Outcomes in Chronic "
            "Kidney Disease"
        ),
        "drug_studied": "dapagliflozin",
        "drug_dose": "10 mg once daily",
        "comparator": "placebo",
        "year_published": 2020,
        "journal": "NEJM",
        "pmid": "32970396",
        "doi": "10.1056/NEJMoa2024816",

        "population": {
            "description": (
                "Adults with CKD (eGFR 25-75 mL/min/1.73m^2) and "
                "UACR 200-5000 mg/g, with or without type 2 diabetes"
            ),
            "n_enrolled": 4304,
            "mean_age": 61.8,
            "percent_female": 33.1,
            "percent_diabetes": 67.5,
            "mean_egfr": 43.1,
            "mean_uacr": 949,
            "key_inclusion": [
                "eGFR 25-75 mL/min/1.73m^2",
                "UACR 200-5000 mg/g",
                "stable ACEi or ARB at maximum tolerated dose for >=4 weeks",
            ],
            "key_exclusion": [
                "type_1_diabetes",
                "polycystic_kidney_disease",
                "lupus_nephritis",
                "ANCA-associated vasculitis",
                "immunosuppressive therapy within 6 months",
            ],
        },

        "primary_outcome": {
            "definition": (
                "Composite of sustained >=50% eGFR decline, end-stage "
                "kidney disease (ESKD), or death from renal or "
                "cardiovascular causes"
            ),
            "drug_group_rate_percent": 9.2,
            "placebo_group_rate_percent": 14.5,
            "hazard_ratio": 0.61,
            "ci_95": [0.51, 0.72],
            "p_value": "<0.001",
            "nnt": 19,
            "median_followup_years": 2.4,
        },

        "secondary_outcomes": [
            {
                "definition": (
                    "Composite renal outcome: sustained >=50% eGFR decline, "
                    "ESKD, or renal death"
                ),
                "hazard_ratio": 0.56,
                "ci_95": [0.45, 0.68],
                "p_value": "<0.001",
            },
            {
                "definition": "All-cause mortality",
                "hazard_ratio": 0.69,
                "ci_95": [0.53, 0.88],
                "p_value": "0.004",
            },
            {
                "definition": (
                    "Composite of cardiovascular death or hospitalization "
                    "for heart failure"
                ),
                "hazard_ratio": 0.71,
                "ci_95": [0.55, 0.92],
                "p_value": "0.009",
            },
        ],

        "egfr_slope_data": {
            "drug_slope_ml_per_min_per_year": -1.92,
            "placebo_slope_ml_per_min_per_year": -3.70,
            "difference": 1.78,
            "ci_95": [1.36, 2.20],
            "interpretation": (
                "39% slower eGFR decline with dapagliflozin vs placebo "
                "(chronic slope after first 2 weeks)"
            ),
        },

        "safety": {
            "serious_adverse_events_drug_percent": 29.5,
            "serious_adverse_events_placebo_percent": 33.9,
            "dka_drug_percent": 0.0,
            "dka_placebo_percent": 0.1,
            "discontinuation_drug_percent": 4.8,
            "discontinuation_placebo_percent": 5.2,
            "amputation_drug_percent": 1.6,
            "amputation_placebo_percent": 1.8,
        },

        "subgroups": [
            {
                "subgroup": "with_diabetes",
                "hazard_ratio": 0.64,
                "ci_95": [0.52, 0.79],
                "interaction_p": 0.24,
            },
            {
                "subgroup": "without_diabetes",
                "hazard_ratio": 0.50,
                "ci_95": [0.35, 0.72],
                "interaction_p": 0.24,
            },
            {
                "subgroup": "egfr_25_to_45",
                "hazard_ratio": 0.63,
                "ci_95": [0.51, 0.78],
            },
            {
                "subgroup": "egfr_45_to_75",
                "hazard_ratio": 0.49,
                "ci_95": [0.34, 0.69],
            },
            {
                "subgroup": "uacr_below_1000",
                "hazard_ratio": 0.54,
                "ci_95": [0.40, 0.74],
            },
            {
                "subgroup": "uacr_above_1000",
                "hazard_ratio": 0.62,
                "ci_95": [0.50, 0.76],
            },
        ],

        "applicability_notes": (
            "Benefit consistent across diabetes/non-diabetes subgroups. "
            "Trial stopped early for efficacy. Effect demonstrated even at "
            "low eGFR (25-30). Patients required to be on stable ACEi/ARB."
        ),

        "conditions": ["ckd", "diabetes", "diabetic_kidney_disease"],
    },

    # -----------------------------------------------------------------------
    # CREDENCE: Canagliflozin in Diabetic Kidney Disease
    # -----------------------------------------------------------------------

    "CREDENCE": {
        "trial_name": "CREDENCE",
        "full_name": (
            "Canagliflozin and Renal Events in Diabetes with Established "
            "Nephropathy Clinical Evaluation"
        ),
        "drug_studied": "canagliflozin",
        "drug_dose": "100 mg once daily",
        "comparator": "placebo",
        "year_published": 2019,
        "journal": "NEJM",
        "pmid": "30990260",
        "doi": "10.1056/NEJMoa1811744",

        "population": {
            "description": (
                "Adults with type 2 diabetes and albuminuric CKD "
                "(eGFR 30-90, UACR 300-5000) on ACEi or ARB"
            ),
            "n_enrolled": 4401,
            "mean_age": 63.0,
            "percent_female": 33.9,
            "percent_diabetes": 100.0,
            "mean_egfr": 56.2,
            "mean_uacr": 927,
            "key_inclusion": [
                "type_2_diabetes",
                "eGFR 30-90 mL/min/1.73m^2",
                "UACR 300-5000 mg/g",
                "stable ACEi or ARB",
            ],
            "key_exclusion": [
                "type_1_diabetes",
                "non-diabetic kidney disease",
                "history_of_dka",
                "dialysis",
            ],
        },

        "primary_outcome": {
            "definition": (
                "Composite of ESKD, doubling of serum creatinine, "
                "or renal/cardiovascular death"
            ),
            "drug_group_rate_percent": 11.1,
            "placebo_group_rate_percent": 15.5,
            "hazard_ratio": 0.70,
            "ci_95": [0.59, 0.82],
            "p_value": "0.00001",
            "nnt": 22,
            "median_followup_years": 2.62,
        },

        "secondary_outcomes": [
            {
                "definition": (
                    "Renal-specific composite: ESKD, doubling of creatinine, "
                    "or renal death"
                ),
                "hazard_ratio": 0.66,
                "ci_95": [0.53, 0.81],
                "p_value": "<0.001",
            },
            {
                "definition": "Hospitalization for heart failure",
                "hazard_ratio": 0.61,
                "ci_95": [0.47, 0.80],
                "p_value": "<0.001",
            },
            {
                "definition": (
                    "Composite of CV death, MI, or stroke (3-point MACE)"
                ),
                "hazard_ratio": 0.80,
                "ci_95": [0.67, 0.95],
                "p_value": "0.01",
            },
        ],

        "egfr_slope_data": {
            "drug_slope_ml_per_min_per_year": -1.85,
            "placebo_slope_ml_per_min_per_year": -4.59,
            "difference": 2.74,
            "ci_95": [2.37, 3.11],
            "interpretation": (
                "60% slower eGFR decline with canagliflozin vs placebo "
                "in diabetic kidney disease"
            ),
        },

        "safety": {
            "serious_adverse_events_drug_percent": 33.9,
            "serious_adverse_events_placebo_percent": 36.5,
            "dka_drug_percent": 0.2,
            "dka_placebo_percent": 0.1,
            "amputation_drug_percent": 1.2,
            "amputation_placebo_percent": 1.1,
            "discontinuation_drug_percent": 3.6,
            "discontinuation_placebo_percent": 4.0,
        },

        "subgroups": [
            {
                "subgroup": "egfr_30_to_45",
                "hazard_ratio": 0.75,
                "ci_95": [0.59, 0.95],
            },
            {
                "subgroup": "egfr_45_to_60",
                "hazard_ratio": 0.66,
                "ci_95": [0.51, 0.86],
            },
            {
                "subgroup": "egfr_60_to_90",
                "hazard_ratio": 0.69,
                "ci_95": [0.51, 0.94],
            },
        ],

        "applicability_notes": (
            "Trial stopped early for efficacy. First trial demonstrating "
            "renal benefit of SGLT2i in diabetic kidney disease. "
            "All patients on background RAAS blockade."
        ),

        "conditions": ["ckd", "diabetes", "diabetic_kidney_disease"],
    },

    # -----------------------------------------------------------------------
    # EMPA-REG OUTCOME: Empagliflozin CV Outcomes in T2DM
    # -----------------------------------------------------------------------

    "EMPA-REG OUTCOME": {
        "trial_name": "EMPA-REG OUTCOME",
        "full_name": (
            "Empagliflozin Cardiovascular Outcome Event Trial in Type 2 "
            "Diabetes Mellitus Patients"
        ),
        "drug_studied": "empagliflozin",
        "drug_dose": "10 mg or 25 mg once daily (pooled analysis)",
        "comparator": "placebo",
        "year_published": 2015,
        "journal": "NEJM",
        "pmid": "26378978",
        "doi": "10.1056/NEJMoa1504720",

        "population": {
            "description": (
                "Adults with type 2 diabetes and established CV disease"
            ),
            "n_enrolled": 7020,
            "mean_age": 63.1,
            "percent_female": 28.5,
            "percent_diabetes": 100.0,
            "mean_egfr": 74.0,
            "mean_uacr": None,  # not primary focus
            "key_inclusion": [
                "type_2_diabetes",
                "established_cardiovascular_disease",
                "BMI <= 45",
                "eGFR >= 30",
            ],
            "key_exclusion": [
                "type_1_diabetes",
                "egfr_below_30",
                "uncontrolled_hyperglycemia",
            ],
        },

        "primary_outcome": {
            "definition": (
                "Composite of cardiovascular death, nonfatal MI, "
                "or nonfatal stroke (3-point MACE)"
            ),
            "drug_group_rate_percent": 10.5,
            "placebo_group_rate_percent": 12.1,
            "hazard_ratio": 0.86,
            "ci_95": [0.74, 0.99],
            "p_value": "0.04 (superiority)",
            "nnt": 63,
            "median_followup_years": 3.1,
        },

        "secondary_outcomes": [
            {
                "definition": "Cardiovascular death",
                "hazard_ratio": 0.62,
                "ci_95": [0.49, 0.77],
                "p_value": "<0.001",
            },
            {
                "definition": "Hospitalization for heart failure",
                "hazard_ratio": 0.65,
                "ci_95": [0.50, 0.85],
                "p_value": "0.002",
            },
            {
                "definition": "All-cause mortality",
                "hazard_ratio": 0.68,
                "ci_95": [0.57, 0.82],
                "p_value": "<0.001",
            },
            {
                "definition": (
                    "Incident or worsening nephropathy "
                    "(progression to macroalbuminuria, doubling of "
                    "creatinine, ESKD, or renal death)"
                ),
                "hazard_ratio": 0.61,
                "ci_95": [0.53, 0.70],
                "p_value": "<0.001",
            },
        ],

        "egfr_slope_data": {
            "drug_slope_ml_per_min_per_year": -0.19,
            "placebo_slope_ml_per_min_per_year": -1.67,
            "difference": 1.48,
            "ci_95": [1.20, 1.76],
            "interpretation": (
                "Long-term eGFR preservation with empagliflozin after "
                "initial acute dip"
            ),
        },

        "safety": {
            "serious_adverse_events_drug_percent": 38.2,
            "serious_adverse_events_placebo_percent": 42.3,
            "dka_drug_percent": 0.1,
            "dka_placebo_percent": 0.0,
            "discontinuation_drug_percent": 17.3,
            "discontinuation_placebo_percent": 19.4,
            "genital_infection_drug_percent": 6.4,
            "genital_infection_placebo_percent": 1.8,
        },

        "subgroups": [
            {
                "subgroup": "with_ckd",
                "hazard_ratio": 0.85,
                "ci_95": [0.69, 1.05],
            },
            {
                "subgroup": "without_ckd",
                "hazard_ratio": 0.87,
                "ci_95": [0.72, 1.05],
            },
        ],

        "applicability_notes": (
            "First SGLT2i CV outcomes trial demonstrating mortality benefit. "
            "Population had established CVD; benefit may differ in primary "
            "prevention."
        ),

        "conditions": ["diabetes", "cardiovascular", "ckd"],
    },

    # -----------------------------------------------------------------------
    # EMPA-KIDNEY: Empagliflozin in CKD
    # -----------------------------------------------------------------------

    "EMPA-KIDNEY": {
        "trial_name": "EMPA-KIDNEY",
        "full_name": "Empagliflozin in Patients with Chronic Kidney Disease",
        "drug_studied": "empagliflozin",
        "drug_dose": "10 mg once daily",
        "comparator": "placebo",
        "year_published": 2023,
        "journal": "NEJM",
        "pmid": "36331190",
        "doi": "10.1056/NEJMoa2204233",

        "population": {
            "description": (
                "Adults with CKD at risk of progression "
                "(eGFR 20-45, or eGFR 45-90 with UACR >= 200), "
                "with or without diabetes"
            ),
            "n_enrolled": 6609,
            "mean_age": 63.8,
            "percent_female": 33.2,
            "percent_diabetes": 46.4,
            "mean_egfr": 37.3,
            "mean_uacr": 329,
            "key_inclusion": [
                "eGFR 20-45 OR (eGFR 45-90 AND UACR >= 200)",
                "stable RAAS blockade if indicated",
            ],
            "key_exclusion": [
                "polycystic_kidney_disease",
                "kidney_transplant",
                "type_1_diabetes",
            ],
        },

        "primary_outcome": {
            "definition": (
                "Composite of kidney disease progression or "
                "cardiovascular death"
            ),
            "drug_group_rate_percent": 13.1,
            "placebo_group_rate_percent": 16.9,
            "hazard_ratio": 0.72,
            "ci_95": [0.64, 0.82],
            "p_value": "<0.001",
            "nnt": 27,
            "median_followup_years": 2.0,
        },

        "secondary_outcomes": [
            {
                "definition": "Hospitalization for any cause",
                "hazard_ratio": 0.86,
                "ci_95": [0.78, 0.95],
                "p_value": "0.003",
            },
            {
                "definition": (
                    "Composite of cardiovascular death or "
                    "hospitalization for heart failure"
                ),
                "hazard_ratio": 0.84,
                "ci_95": [0.67, 1.07],
                "p_value": "0.15",
            },
            {
                "definition": "Death from any cause",
                "hazard_ratio": 0.87,
                "ci_95": [0.70, 1.08],
                "p_value": "NS",
            },
        ],

        "egfr_slope_data": {
            "drug_slope_ml_per_min_per_year": -2.10,
            "placebo_slope_ml_per_min_per_year": -3.41,
            "difference": 1.31,
            "ci_95": [1.04, 1.59],
            "interpretation": (
                "38% slower eGFR decline with empagliflozin "
                "(consistent across with/without diabetes subgroups)"
            ),
        },

        "safety": {
            "serious_adverse_events_drug_percent": 24.8,
            "serious_adverse_events_placebo_percent": 26.0,
            "dka_drug_percent": 0.1,
            "dka_placebo_percent": 0.0,
            "discontinuation_drug_percent": 16.5,
            "discontinuation_placebo_percent": 17.2,
            "ketoacidosis_drug_n": 6,
            "ketoacidosis_placebo_n": 1,
        },

        "subgroups": [
            {
                "subgroup": "with_diabetes",
                "hazard_ratio": 0.64,
                "ci_95": [0.54, 0.77],
                "interaction_p": 0.07,
            },
            {
                "subgroup": "without_diabetes",
                "hazard_ratio": 0.82,
                "ci_95": [0.68, 0.99],
                "interaction_p": 0.07,
            },
            {
                "subgroup": "egfr_below_30",
                "hazard_ratio": 0.73,
                "ci_95": [0.59, 0.89],
            },
            {
                "subgroup": "egfr_30_to_45",
                "hazard_ratio": 0.78,
                "ci_95": [0.66, 0.93],
            },
            {
                "subgroup": "egfr_above_45",
                "hazard_ratio": 0.64,
                "ci_95": [0.51, 0.81],
            },
        ],

        "applicability_notes": (
            "Largest SGLT2i kidney trial. Demonstrated benefit across "
            "wide eGFR range (20 to 90+) and in non-diabetic CKD. "
            "Established empagliflozin as broadly applicable in CKD."
        ),

        "conditions": ["ckd", "diabetes", "cardiovascular"],
    },

    # -----------------------------------------------------------------------
    # SUSTAIN-6: Semaglutide CV Outcomes
    # -----------------------------------------------------------------------

    "SUSTAIN-6": {
        "trial_name": "SUSTAIN-6",
        "full_name": (
            "Trial to Evaluate Cardiovascular and Other Long-term Outcomes "
            "with Semaglutide in Subjects with Type 2 Diabetes"
        ),
        "drug_studied": "semaglutide",
        "drug_dose": "0.5 mg or 1.0 mg SC weekly (pooled)",
        "comparator": "placebo",
        "year_published": 2016,
        "journal": "NEJM",
        "pmid": "27633186",
        "doi": "10.1056/NEJMoa1607141",

        "population": {
            "description": (
                "Adults with type 2 diabetes at high cardiovascular risk"
            ),
            "n_enrolled": 3297,
            "mean_age": 64.6,
            "percent_female": 39.3,
            "percent_diabetes": 100.0,
            "mean_egfr": 76.0,
            "mean_uacr": None,
            "key_inclusion": [
                "type_2_diabetes",
                "age >= 50 with established CVD/CKD OR age >= 60 with risk factors",
                "HbA1c >= 7.0%",
            ],
            "key_exclusion": [
                "type_1_diabetes",
                "MEN2",
                "history_medullary_thyroid_carcinoma",
                "egfr_below_30",
            ],
        },

        "primary_outcome": {
            "definition": (
                "Composite of cardiovascular death, nonfatal MI, "
                "or nonfatal stroke (3-point MACE)"
            ),
            "drug_group_rate_percent": 6.6,
            "placebo_group_rate_percent": 8.9,
            "hazard_ratio": 0.74,
            "ci_95": [0.58, 0.95],
            "p_value": "0.02 (superiority)",
            "nnt": 45,
            "median_followup_years": 2.1,
        },

        "secondary_outcomes": [
            {
                "definition": "Nonfatal stroke",
                "hazard_ratio": 0.61,
                "ci_95": [0.38, 0.99],
                "p_value": "0.04",
            },
            {
                "definition": "Nonfatal MI",
                "hazard_ratio": 0.74,
                "ci_95": [0.51, 1.08],
                "p_value": "0.12",
            },
            {
                "definition": "New or worsening nephropathy",
                "hazard_ratio": 0.64,
                "ci_95": [0.46, 0.88],
                "p_value": "0.005",
            },
            {
                "definition": "Retinopathy complications",
                "hazard_ratio": 1.76,
                "ci_95": [1.11, 2.78],
                "p_value": "0.02",
            },
        ],

        "egfr_slope_data": None,

        "safety": {
            "serious_adverse_events_drug_percent": 33.4,
            "serious_adverse_events_placebo_percent": 36.1,
            "discontinuation_drug_percent": 13.5,
            "discontinuation_placebo_percent": 11.4,
            "pancreatitis_drug_percent": 0.6,
            "pancreatitis_placebo_percent": 0.9,
            "retinopathy_complications_drug_percent": 3.0,
            "retinopathy_complications_placebo_percent": 1.8,
        },

        "subgroups": [
            {
                "subgroup": "with_established_cvd",
                "hazard_ratio": 0.72,
                "ci_95": [0.55, 0.93],
            },
            {
                "subgroup": "without_established_cvd",
                "hazard_ratio": 1.00,
                "ci_95": [0.41, 2.46],
            },
        ],

        "applicability_notes": (
            "First trial showing CV benefit of semaglutide. "
            "Retinopathy signal warrants caution in patients with "
            "advanced retinopathy and rapid HbA1c reduction."
        ),

        "conditions": ["diabetes", "cardiovascular"],
    },

    # -----------------------------------------------------------------------
    # LEADER: Liraglutide CV Outcomes
    # -----------------------------------------------------------------------

    "LEADER": {
        "trial_name": "LEADER",
        "full_name": (
            "Liraglutide Effect and Action in Diabetes: Evaluation of "
            "Cardiovascular Outcome Results"
        ),
        "drug_studied": "liraglutide",
        "drug_dose": "1.8 mg SC daily (or max tolerated)",
        "comparator": "placebo",
        "year_published": 2016,
        "journal": "NEJM",
        "pmid": "27295427",
        "doi": "10.1056/NEJMoa1603827",

        "population": {
            "description": (
                "Adults with type 2 diabetes and high cardiovascular risk"
            ),
            "n_enrolled": 9340,
            "mean_age": 64.3,
            "percent_female": 35.6,
            "percent_diabetes": 100.0,
            "mean_egfr": 80.0,
            "mean_uacr": None,
            "key_inclusion": [
                "type_2_diabetes",
                "age >= 50 with established CVD OR age >= 60 with risk factors",
                "HbA1c >= 7.0%",
            ],
            "key_exclusion": [
                "type_1_diabetes",
                "MEN2",
                "medullary_thyroid_carcinoma_history",
                "advanced_heart_failure",
            ],
        },

        "primary_outcome": {
            "definition": (
                "Composite of cardiovascular death, nonfatal MI, "
                "or nonfatal stroke (3-point MACE)"
            ),
            "drug_group_rate_percent": 13.0,
            "placebo_group_rate_percent": 14.9,
            "hazard_ratio": 0.87,
            "ci_95": [0.78, 0.97],
            "p_value": "0.01 (superiority)",
            "nnt": 53,
            "median_followup_years": 3.8,
        },

        "secondary_outcomes": [
            {
                "definition": "Cardiovascular death",
                "hazard_ratio": 0.78,
                "ci_95": [0.66, 0.93],
                "p_value": "0.007",
            },
            {
                "definition": "All-cause mortality",
                "hazard_ratio": 0.85,
                "ci_95": [0.74, 0.97],
                "p_value": "0.02",
            },
            {
                "definition": "Composite renal outcome",
                "hazard_ratio": 0.78,
                "ci_95": [0.67, 0.92],
                "p_value": "0.003",
            },
            {
                "definition": "New onset persistent macroalbuminuria",
                "hazard_ratio": 0.74,
                "ci_95": [0.60, 0.91],
                "p_value": "0.004",
            },
        ],

        "egfr_slope_data": None,

        "safety": {
            "serious_adverse_events_drug_percent": 49.7,
            "serious_adverse_events_placebo_percent": 50.4,
            "discontinuation_drug_percent": 9.5,
            "discontinuation_placebo_percent": 7.3,
            "pancreatitis_drug_percent": 0.4,
            "pancreatitis_placebo_percent": 0.5,
            "gallbladder_disease_drug_percent": 3.1,
            "gallbladder_disease_placebo_percent": 1.9,
        },

        "subgroups": [
            {
                "subgroup": "with_established_cvd",
                "hazard_ratio": 0.83,
                "ci_95": [0.74, 0.93],
            },
            {
                "subgroup": "primary_prevention",
                "hazard_ratio": 1.20,
                "ci_95": [0.86, 1.67],
            },
            {
                "subgroup": "egfr_below_60",
                "hazard_ratio": 0.69,
                "ci_95": [0.57, 0.85],
            },
            {
                "subgroup": "egfr_above_60",
                "hazard_ratio": 0.94,
                "ci_95": [0.83, 1.07],
            },
        ],

        "applicability_notes": (
            "First GLP-1 RA trial with positive primary CV outcome. "
            "Larger renal benefit in CKD subgroup. Effect concentrated "
            "in secondary prevention population."
        ),

        "conditions": ["diabetes", "cardiovascular", "ckd"],
    },

    # -----------------------------------------------------------------------
    # REWIND: Dulaglutide CV Outcomes
    # -----------------------------------------------------------------------

    "REWIND": {
        "trial_name": "REWIND",
        "full_name": (
            "Researching Cardiovascular Events with a Weekly Incretin in "
            "Diabetes"
        ),
        "drug_studied": "dulaglutide",
        "drug_dose": "1.5 mg SC weekly",
        "comparator": "placebo",
        "year_published": 2019,
        "journal": "Lancet",
        "pmid": "31189511",
        "doi": "10.1016/S0140-6736(19)31149-3",

        "population": {
            "description": (
                "Adults with type 2 diabetes and either established CVD "
                "or multiple CV risk factors (broad primary + secondary "
                "prevention population)"
            ),
            "n_enrolled": 9901,
            "mean_age": 66.2,
            "percent_female": 46.3,
            "percent_diabetes": 100.0,
            "mean_egfr": 76.9,
            "mean_uacr": None,
            "key_inclusion": [
                "type_2_diabetes",
                "age >= 50 with vascular disease OR age >= 55 with subclinical disease "
                "OR age >= 60 with risk factors",
                "HbA1c <= 9.5%",
            ],
            "key_exclusion": [
                "type_1_diabetes",
                "egfr_below_15",
                "severe_gastroparesis",
            ],
        },

        "primary_outcome": {
            "definition": (
                "Composite of cardiovascular death, nonfatal MI, "
                "or nonfatal stroke (3-point MACE)"
            ),
            "drug_group_rate_percent": 12.0,
            "placebo_group_rate_percent": 13.4,
            "hazard_ratio": 0.88,
            "ci_95": [0.79, 0.99],
            "p_value": "0.026 (superiority)",
            "nnt": 71,
            "median_followup_years": 5.4,
        },

        "secondary_outcomes": [
            {
                "definition": "Nonfatal stroke",
                "hazard_ratio": 0.76,
                "ci_95": [0.61, 0.95],
                "p_value": "0.017",
            },
            {
                "definition": (
                    "Composite renal outcome (new macroalbuminuria, "
                    "sustained 30% eGFR decline, or chronic renal "
                    "replacement therapy)"
                ),
                "hazard_ratio": 0.85,
                "ci_95": [0.77, 0.93],
                "p_value": "0.0004",
            },
            {
                "definition": "Cardiovascular death",
                "hazard_ratio": 0.91,
                "ci_95": [0.78, 1.06],
                "p_value": "0.21",
            },
        ],

        "egfr_slope_data": None,

        "safety": {
            "serious_adverse_events_drug_percent": 48.2,
            "serious_adverse_events_placebo_percent": 47.8,
            "discontinuation_drug_percent": 9.1,
            "discontinuation_placebo_percent": 6.0,
            "gi_adverse_events_drug_percent": 47.4,
            "gi_adverse_events_placebo_percent": 34.1,
            "pancreatitis_drug_percent": 0.4,
            "pancreatitis_placebo_percent": 0.4,
        },

        "subgroups": [
            {
                "subgroup": "with_established_cvd",
                "hazard_ratio": 0.87,
                "ci_95": [0.74, 1.02],
            },
            {
                "subgroup": "primary_prevention",
                "hazard_ratio": 0.87,
                "ci_95": [0.74, 1.02],
                "interaction_p": 0.97,
            },
        ],

        "applicability_notes": (
            "Notable for benefit in primary prevention population — broader "
            "applicability than other GLP-1 RA CV trials. Longest follow-up "
            "of any GLP-1 RA trial."
        ),

        "conditions": ["diabetes", "cardiovascular"],
    },

    # -----------------------------------------------------------------------
    # SURPASS-4: Tirzepatide vs Glargine
    # -----------------------------------------------------------------------

    "SURPASS-4": {
        "trial_name": "SURPASS-4",
        "full_name": (
            "Tirzepatide versus Insulin Glargine in Type 2 Diabetes and "
            "Increased Cardiovascular Risk"
        ),
        "drug_studied": "tirzepatide",
        "drug_dose": "5, 10, or 15 mg SC weekly",
        "comparator": "insulin_glargine",
        "year_published": 2021,
        "journal": "Lancet",
        "pmid": "34672967",
        "doi": "10.1016/S0140-6736(21)02188-7",

        "population": {
            "description": (
                "Adults with type 2 diabetes inadequately controlled on "
                "1-3 oral antidiabetic drugs and at high CV risk"
            ),
            "n_enrolled": 2002,
            "mean_age": 63.6,
            "percent_female": 36.6,
            "percent_diabetes": 100.0,
            "mean_egfr": 81.3,
            "mean_uacr": 14,
            "key_inclusion": [
                "type_2_diabetes",
                "HbA1c 7.5-10.5%",
                "high_cardiovascular_risk",
                "BMI >= 25",
            ],
            "key_exclusion": [
                "type_1_diabetes",
                "MEN2",
                "history_pancreatitis",
                "history_medullary_thyroid_carcinoma",
            ],
        },

        "primary_outcome": {
            "definition": (
                "HbA1c change from baseline at 52 weeks "
                "(non-inferiority then superiority)"
            ),
            "drug_group_rate_percent": None,  # continuous outcome
            "placebo_group_rate_percent": None,
            "hazard_ratio": None,
            "ci_95": None,
            "p_value": "<0.0001 (superiority for HbA1c reduction)",
            "drug_hba1c_change": -2.58,  # 15 mg dose
            "comparator_hba1c_change": -1.44,
            "difference": -1.14,
            "median_followup_years": 1.0,
        },

        "secondary_outcomes": [
            {
                "definition": (
                    "Major adverse cardiovascular events (MACE-4: CV death, "
                    "MI, stroke, hospitalization for unstable angina)"
                ),
                "hazard_ratio": 0.74,
                "ci_95": [0.51, 1.08],
                "p_value": "NS (safety endpoint, not powered for superiority)",
            },
            {
                "definition": "All-cause mortality",
                "hazard_ratio": 0.80,
                "ci_95": [0.51, 1.25],
                "p_value": "NS",
            },
            {
                "definition": "Body weight change at week 52 (15 mg dose)",
                "drug_change_kg": -10.9,
                "comparator_change_kg": 1.7,
                "difference": -12.6,
                "p_value": "<0.0001",
            },
            {
                "definition": (
                    "Composite renal outcome "
                    "(new macroalbuminuria, eGFR decline >= 40%, ESKD, renal death)"
                ),
                "hazard_ratio": 0.58,
                "ci_95": [0.43, 0.80],
                "p_value": "<0.001",
            },
        ],

        "egfr_slope_data": {
            "drug_slope_ml_per_min_per_year": -1.4,
            "comparator_slope_ml_per_min_per_year": -3.6,
            "difference": 2.2,
            "ci_95": [1.5, 2.9],
            "interpretation": (
                "Significantly slower eGFR decline with tirzepatide vs "
                "insulin glargine"
            ),
        },

        "safety": {
            "serious_adverse_events_drug_percent": 25.1,
            "serious_adverse_events_glargine_percent": 23.8,
            "discontinuation_drug_percent": 11.0,
            "discontinuation_glargine_percent": 2.7,
            "hypoglycemia_drug_percent": 6.0,
            "hypoglycemia_glargine_percent": 19.0,
            "pancreatitis_drug_percent": 0.4,
            "pancreatitis_glargine_percent": 0.0,
            "gi_adverse_events_drug_percent": 50.7,
            "gi_adverse_events_glargine_percent": 8.6,
        },

        "subgroups": [
            {
                "subgroup": "with_egfr_below_60",
                "hazard_ratio_renal": 0.57,
                "ci_95": [0.39, 0.83],
            },
            {
                "subgroup": "with_macroalbuminuria",
                "hazard_ratio_renal": 0.41,
                "ci_95": [0.26, 0.66],
            },
        ],

        "applicability_notes": (
            "Demonstrates HbA1c, weight, and renal benefit of tirzepatide "
            "vs insulin glargine. Active-controlled trial; CV safety "
            "endpoint not powered for superiority. Dedicated CVOT "
            "(SURPASS-CVOT) ongoing."
        ),

        "conditions": ["diabetes", "obesity", "cardiovascular"],
    },

    # -----------------------------------------------------------------------
    # UKPDS 33: Long-Term Diabetes Outcomes
    # -----------------------------------------------------------------------

    "UKPDS-33": {
        "trial_name": "UKPDS-33",
        "full_name": (
            "Intensive blood-glucose control with sulphonylureas or "
            "insulin compared with conventional treatment and risk of "
            "complications in patients with type 2 diabetes (UK Prospective "
            "Diabetes Study)"
        ),
        "drug_studied": "intensive_glycemic_control",
        "drug_dose": "Targeting fasting glucose < 6.0 mmol/L (108 mg/dL)",
        "comparator": "conventional_glycemic_control",
        "year_published": 1998,
        "journal": "Lancet",
        "pmid": "9742976",
        "doi": "10.1016/S0140-6736(98)07019-6",

        "population": {
            "description": (
                "Adults with newly diagnosed type 2 diabetes (3867 patients "
                "followed long-term in UKPDS 33)"
            ),
            "n_enrolled": 3867,
            "mean_age": 53.0,
            "percent_female": 39.0,
            "percent_diabetes": 100.0,
            "mean_egfr": None,
            "mean_uacr": None,
            "key_inclusion": [
                "newly_diagnosed_type_2_diabetes",
                "age 25-65",
                "fasting_glucose 6.1-15.0 mmol/L after 3-month diet run-in",
            ],
            "key_exclusion": [
                "ketonuria",
                "serum_creatinine_above_175",
                "MI_within_1_year",
                "advanced_retinopathy",
            ],
        },

        "primary_outcome": {
            "definition": (
                "Three aggregate endpoints: (1) any diabetes-related endpoint, "
                "(2) diabetes-related death, (3) all-cause mortality"
            ),
            "any_diabetes_endpoint_relative_risk": 0.88,
            "any_diabetes_endpoint_ci_95": [0.79, 0.99],
            "any_diabetes_endpoint_p": "0.029",
            "median_followup_years": 10.0,
            "hba1c_intensive_percent": 7.0,
            "hba1c_conventional_percent": 7.9,
            "hba1c_difference": -0.9,
        },

        "secondary_outcomes": [
            {
                "definition": "Microvascular endpoints",
                "relative_risk": 0.75,
                "ci_95": [0.60, 0.93],
                "p_value": "0.0099",
            },
            {
                "definition": "Myocardial infarction",
                "relative_risk": 0.84,
                "ci_95": [0.71, 1.00],
                "p_value": "0.052",
            },
            {
                "definition": "Diabetes-related death",
                "relative_risk": 0.90,
                "ci_95": [0.73, 1.11],
                "p_value": "0.34",
            },
            {
                "definition": "Photocoagulation requirement",
                "relative_risk": 0.71,
                "ci_95": [0.53, 0.96],
                "p_value": "0.0031",
            },
        ],

        "egfr_slope_data": None,

        "safety": {
            "major_hypoglycemia_intensive_percent_per_year": 1.8,
            "major_hypoglycemia_conventional_percent_per_year": 0.7,
            "weight_gain_intensive_kg": 3.1,
            "weight_gain_conventional_kg": 0.0,
        },

        "subgroups": [
            {
                "subgroup": "newly_diagnosed",
                "interpretation": (
                    "Benefit established in newly diagnosed patients; "
                    "extrapolation to long-standing diabetes uncertain"
                ),
            },
        ],

        "applicability_notes": (
            "Foundational study establishing benefit of glycemic control "
            "in T2DM. UKPDS-34 (metformin in overweight) and 10-year "
            "post-trial follow-up (UKPDS 80) demonstrated 'legacy effect' "
            "with sustained benefit."
        ),

        "conditions": ["diabetes"],
    },

    # -----------------------------------------------------------------------
    # SPRINT: Intensive BP Control
    # -----------------------------------------------------------------------

    "SPRINT": {
        "trial_name": "SPRINT",
        "full_name": "Systolic Blood Pressure Intervention Trial",
        "drug_studied": "intensive_bp_control",
        "drug_dose": "Target systolic BP < 120 mmHg (intensive arm)",
        "comparator": "standard_bp_control",  # Target < 140 mmHg
        "year_published": 2015,
        "journal": "NEJM",
        "pmid": "26551272",
        "doi": "10.1056/NEJMoa1511939",

        "population": {
            "description": (
                "Adults >= 50 years with systolic BP 130-180 mmHg and "
                "increased CV risk (CVD, CKD, ASCVD risk >= 15%, or age >= 75); "
                "diabetes was excluded"
            ),
            "n_enrolled": 9361,
            "mean_age": 67.9,
            "percent_female": 35.6,
            "percent_diabetes": 0.0,  # diabetes excluded
            "mean_egfr": 71.7,
            "mean_uacr": None,
            "key_inclusion": [
                "age >= 50",
                "systolic_bp 130-180 mmHg",
                "increased CV risk (CVD, CKD eGFR 20-60, ASCVD >= 15%, age >= 75)",
            ],
            "key_exclusion": [
                "diabetes",
                "history_of_stroke",
                "polycystic_kidney_disease",
                "egfr_below_20",
                "proteinuria > 1g/day",
            ],
        },

        "primary_outcome": {
            "definition": (
                "Composite of MI, other acute coronary syndrome, stroke, "
                "heart failure, or death from cardiovascular causes"
            ),
            "drug_group_rate_percent": 5.2,
            "placebo_group_rate_percent": 6.8,
            "hazard_ratio": 0.75,
            "ci_95": [0.64, 0.89],
            "p_value": "<0.001",
            "nnt": 61,
            "median_followup_years": 3.26,
        },

        "secondary_outcomes": [
            {
                "definition": "All-cause mortality",
                "hazard_ratio": 0.73,
                "ci_95": [0.60, 0.90],
                "p_value": "0.003",
            },
            {
                "definition": "Cardiovascular death",
                "hazard_ratio": 0.57,
                "ci_95": [0.38, 0.85],
                "p_value": "0.005",
            },
            {
                "definition": "Heart failure",
                "hazard_ratio": 0.62,
                "ci_95": [0.45, 0.84],
                "p_value": "0.002",
            },
            {
                "definition": (
                    "Composite renal outcome in CKD subgroup "
                    "(>= 50% reduction in eGFR or ESRD)"
                ),
                "hazard_ratio": 0.89,
                "ci_95": [0.42, 1.87],
                "p_value": "0.76 (NS)",
            },
        ],

        "egfr_slope_data": {
            "drug_slope_ml_per_min_per_year": -1.21,
            "placebo_slope_ml_per_min_per_year": -0.35,
            "difference": -0.86,
            "interpretation": (
                "Faster eGFR decline with intensive BP control "
                "(likely hemodynamic, mostly reversible)"
            ),
        },

        "safety": {
            "serious_adverse_events_drug_percent": 38.3,
            "serious_adverse_events_placebo_percent": 37.1,
            "hypotension_drug_percent": 3.4,
            "hypotension_placebo_percent": 2.0,
            "syncope_drug_percent": 3.5,
            "syncope_placebo_percent": 2.4,
            "aki_drug_percent": 4.4,
            "aki_placebo_percent": 2.6,
            "electrolyte_abnormality_drug_percent": 3.8,
            "electrolyte_abnormality_placebo_percent": 2.1,
        },

        "subgroups": [
            {
                "subgroup": "age_above_75",
                "hazard_ratio": 0.67,
                "ci_95": [0.51, 0.86],
            },
            {
                "subgroup": "with_ckd",
                "hazard_ratio": 0.81,
                "ci_95": [0.63, 1.05],
            },
            {
                "subgroup": "without_ckd",
                "hazard_ratio": 0.71,
                "ci_95": [0.57, 0.88],
            },
            {
                "subgroup": "with_prior_cvd",
                "hazard_ratio": 0.83,
                "ci_95": [0.62, 1.09],
            },
        ],

        "applicability_notes": (
            "Trial stopped early for benefit. Influenced 2017 ACC/AHA "
            "guideline recommending BP target < 130/80. Excluded diabetics "
            "(see ACCORD-BP for diabetic population). Risk of AKI, syncope, "
            "and electrolyte disturbances increased with intensive control."
        ),

        "conditions": ["hypertension", "cardiovascular", "ckd"],
    },
}


# ===========================================================================
# DRUG-TO-TRIALS LOOKUP (helper index, built at module load)
# ===========================================================================

_TRIALS_BY_DRUG: dict[str, list[str]] = {}
for _name, _data in _TRIALS.items():
    _drug = _data.get("drug_studied", "").lower()
    if _drug:
        _TRIALS_BY_DRUG.setdefault(_drug, []).append(_name)


# Drug name aliases (some trials list intervention names, not drug names)
_DRUG_ALIASES = {
    "intensive_glycemic_control": ["metformin", "sulfonylurea", "insulin"],
    "intensive_bp_control": ["lisinopril", "losartan", "hydrochlorothiazide"],
}


# ===========================================================================
# CONDITION-TO-TRIALS LOOKUP
# ===========================================================================

_TRIALS_BY_CONDITION: dict[str, list[str]] = {}
for _name, _data in _TRIALS.items():
    for _cond in _data.get("conditions", []):
        _TRIALS_BY_CONDITION.setdefault(_cond.lower(), []).append(_name)


# ===========================================================================
# PUBLIC API
# ===========================================================================

def get_trial(trial_name: str) -> Optional[dict]:
    """
    Retrieve a trial's full structured data by name.

    Lookup is case-insensitive and tolerates common name variations
    (e.g., "dapa-ckd", "DAPA CKD", "DAPA-CKD").

    Parameters
    ----------
    trial_name : str
        Trial name or canonical identifier.

    Returns
    -------
    dict or None
        Trial data dict, or None if not found.
    """
    if not trial_name:
        return None
    # Direct lookup first
    if trial_name in _TRIALS:
        return _TRIALS[trial_name]
    # Case-insensitive normalized lookup
    normalized = trial_name.strip().upper().replace(" ", "-").replace("_", "-")
    for key, value in _TRIALS.items():
        if key.upper().replace(" ", "-") == normalized:
            return value
    return None


def get_trials_for_drug(drug_name: str) -> list[dict]:
    """
    Retrieve all trials studying a specific drug.

    Includes trials where the drug is part of an intervention group
    (e.g., metformin will return UKPDS-33 because it was part of the
    intensive glycemic control arm).

    Parameters
    ----------
    drug_name : str
        Generic drug name.

    Returns
    -------
    list of dict
        All trials studying this drug.
    """
    if not drug_name:
        return []
    drug_norm = drug_name.lower().strip()
    trials = list(_TRIALS_BY_DRUG.get(drug_norm, []))

    # Also check aliases
    for alias_key, drug_list in _DRUG_ALIASES.items():
        if drug_norm in [d.lower() for d in drug_list]:
            trials.extend(_TRIALS_BY_DRUG.get(alias_key, []))

    # De-duplicate while preserving order
    seen = set()
    unique_trials = []
    for t in trials:
        if t not in seen:
            seen.add(t)
            unique_trials.append(t)

    return [_TRIALS[t] for t in unique_trials]


def get_trials_for_condition(condition: str) -> list[dict]:
    """
    Retrieve all trials relevant to a condition.

    Parameters
    ----------
    condition : str
        Condition keyword (e.g., "ckd", "diabetes", "cardiovascular",
        "hypertension").

    Returns
    -------
    list of dict
        All trials tagged with this condition.
    """
    if not condition:
        return []
    cond_norm = condition.lower().strip()
    trial_names = _TRIALS_BY_CONDITION.get(cond_norm, [])
    return [_TRIALS[t] for t in trial_names]


def get_outcome_data(trial_name: str, outcome: str) -> Optional[dict]:
    """
    Retrieve specific outcome data from a trial by keyword search.

    Searches both the primary outcome and all secondary outcomes for a
    match against the outcome keyword (case-insensitive substring match).

    Parameters
    ----------
    trial_name : str
        Trial name.
    outcome : str
        Outcome keyword (e.g., "mortality", "MACE", "renal", "stroke").

    Returns
    -------
    dict or None
        First matching outcome dict, or None if no match.
    """
    trial = get_trial(trial_name)
    if not trial or not outcome:
        return None

    outcome_lower = outcome.lower()

    # Check primary outcome
    primary = trial.get("primary_outcome", {})
    if outcome_lower in primary.get("definition", "").lower():
        return {"type": "primary", **primary}

    # Check secondary outcomes
    for sec in trial.get("secondary_outcomes", []):
        if outcome_lower in sec.get("definition", "").lower():
            return {"type": "secondary", **sec}

    return None


def get_egfr_slope_data(trial_name: str) -> Optional[dict]:
    """
    Retrieve eGFR slope data from a trial, if available.

    Parameters
    ----------
    trial_name : str

    Returns
    -------
    dict or None
        eGFR slope dict, or None if trial does not have slope data.
    """
    trial = get_trial(trial_name)
    if not trial:
        return None
    return trial.get("egfr_slope_data")


def get_subgroup_data(
    trial_name: str,
    subgroup: str,
) -> Optional[dict]:
    """
    Retrieve subgroup analysis data from a trial.

    Parameters
    ----------
    trial_name : str
        Trial name.
    subgroup : str
        Subgroup keyword (e.g., "with_diabetes", "egfr_below_30").

    Returns
    -------
    dict or None
        First matching subgroup, or None if no match.
    """
    trial = get_trial(trial_name)
    if not trial or not subgroup:
        return None

    sg_lower = subgroup.lower()
    for sg in trial.get("subgroups", []):
        if sg_lower in sg.get("subgroup", "").lower():
            return sg
    return None


def get_all_trial_names() -> list[str]:
    """
    Return all trial names in the database.

    Returns
    -------
    list of str
        Sorted list of trial names.
    """
    return sorted(_TRIALS.keys())


# ===========================================================================
# Module-level metadata
# ===========================================================================

__all__ = [
    "get_trial",
    "get_trials_for_drug",
    "get_trials_for_condition",
    "get_outcome_data",
    "get_egfr_slope_data",
    "get_subgroup_data",
    "get_all_trial_names",
]