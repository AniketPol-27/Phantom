"""
drug_knowledge.py

Structured drug profiles for the Phantom clinical simulation engine.

Each drug entry encodes:
  - Identifiers (RxNorm, ATC, brand names)
  - Mechanism of action
  - Multi-system effects (metabolic, renal, CV, hepatic, weight)
  - Contraindications with severity
  - Side-effect profile with frequencies
  - Drug-drug interactions with clinical recommendations
  - Monitoring requirements
  - Dosing and adherence factors

All numeric estimates are sourced from FDA prescribing information,
peer-reviewed clinical trials, and major society guidelines (ADA,
KDIGO, ACC/AHA). Citations are included inline.

This module has zero dependencies on FHIR, MCP, or platform code.
"""

from __future__ import annotations

from typing import Optional


# ===========================================================================
# DRUG DATABASE
# ===========================================================================
# Keyed by lowercase generic name. Values are dicts following a uniform
# schema. See module docstring for field descriptions.

_DRUGS: dict[str, dict] = {

    # -----------------------------------------------------------------------
    # SGLT2 INHIBITORS
    # -----------------------------------------------------------------------

    "empagliflozin": {
        "name": "empagliflozin",
        "brand_names": ["Jardiance"],
        "rxcui": "1545653",
        "drug_class": "SGLT2 inhibitor",
        "atc_code": "A10BK03",
        "mechanism": (
            "Selectively inhibits sodium-glucose co-transporter 2 (SGLT2) "
            "in the proximal renal tubule, reducing glucose reabsorption and "
            "promoting urinary glucose excretion (glucosuria)."
        ),
        "indications": ["type_2_diabetes", "heart_failure", "ckd"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": -0.7,
                "hba1c_range": [-0.5, -0.8],
                "weight_change_kg": -2.5,
                "weight_range_kg": [-1.5, -3.5],
                "hypoglycemia_risk": "very_low",
                "mechanism_of_glycemic_effect": "insulin-independent glucosuria",
                "evidence": "EMPA-REG OUTCOME, EMPEROR trials",
            },
            "renal": {
                "egfr_acute_effect": -3,
                "egfr_acute_reversible": True,
                "egfr_slope_modifier": 0.61,  # 39% slowing of decline
                "albuminuria_reduction_percent": -30,
                "evidence_trial": "EMPA-KIDNEY",
                "renoprotective": True,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.86,
                "mace_evidence": "EMPA-REG OUTCOME (NEJM 2015)",
                "hf_hospitalization_rr": 0.65,
                "bp_systolic_change_mmhg": -4,
                "bp_diastolic_change_mmhg": -1.5,
            },
            "hepatic": {
                "alt_effect": "decrease",
                "hepatotoxicity_risk": "none",
                "masld_benefit": "possible",
            },
            "weight": {
                "direction": "loss",
                "expected_kg": -2.5,
                "mechanism": "caloric loss via glucosuria + mild osmotic diuresis",
            },
        },

        "contraindications": [
            {"condition": "type_1_diabetes", "severity": "absolute"},
            {"condition": "egfr_below_20", "severity": "absolute"},
            {"condition": "dialysis", "severity": "absolute"},
            {"condition": "dka_history", "severity": "relative"},
            {"condition": "recurrent_genital_infections", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "genital_mycotic_infection", "frequency": "common", "percent": 6.4},
            {"effect": "urinary_tract_infection", "frequency": "common", "percent": 7.6},
            {"effect": "volume_depletion", "frequency": "uncommon", "percent": 1.4},
            {"effect": "diabetic_ketoacidosis", "frequency": "rare", "percent": 0.1},
            {"effect": "fournier_gangrene", "frequency": "very_rare", "percent": 0.01},
        ],

        "monitoring": [
            {"test": "renal_function", "timing": "before_initiation_and_periodically"},
            {"test": "potassium", "timing": "if_on_ace_or_arb"},
            {"test": "volume_status", "timing": "if_on_diuretics"},
            {"test": "ketones", "timing": "if_dka_symptoms"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "loop_diuretics",
                "severity": "moderate",
                "effect": "Additive volume depletion and hypotension risk",
                "recommendation": "Consider reducing diuretic dose; monitor volume status",
            },
            {
                "interacting_drug_class": "insulin",
                "severity": "moderate",
                "effect": "Increased hypoglycemia risk",
                "recommendation": "Consider reducing insulin dose by 20%",
            },
            {
                "interacting_drug_class": "sulfonylurea",
                "severity": "moderate",
                "effect": "Increased hypoglycemia risk",
                "recommendation": "Consider reducing sulfonylurea dose",
            },
        ],

        "dosing": {
            "starting_dose": "10 mg once daily",
            "max_dose": "25 mg once daily",
            "renal_adjustment": "No adjustment for eGFR >= 20; do not initiate if eGFR < 20",
            "hepatic_adjustment": "No adjustment needed",
        },

        "cost_tier": "$$$$",
        "generic_available": False,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": False,
            "food_requirements": "none",
        },
    },

    "dapagliflozin": {
        "name": "dapagliflozin",
        "brand_names": ["Farxiga", "Forxiga"],
        "rxcui": "1488564",
        "drug_class": "SGLT2 inhibitor",
        "atc_code": "A10BK01",
        "mechanism": (
            "Selectively inhibits SGLT2 in the proximal renal tubule, "
            "reducing glucose reabsorption and producing glucosuria."
        ),
        "indications": ["type_2_diabetes", "heart_failure", "ckd"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": -0.6,
                "hba1c_range": [-0.5, -0.8],
                "weight_change_kg": -2.2,
                "weight_range_kg": [-1.5, -3.0],
                "hypoglycemia_risk": "very_low",
                "mechanism_of_glycemic_effect": "insulin-independent glucosuria",
                "evidence": "DAPA-CKD, DAPA-HF",
            },
            "renal": {
                "egfr_acute_effect": -3,
                "egfr_acute_reversible": True,
                "egfr_slope_modifier": 0.51,  # ~49% slowing in DAPA-CKD
                "albuminuria_reduction_percent": -29,
                "evidence_trial": "DAPA-CKD (NEJM 2020)",
                "renoprotective": True,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.93,
                "mace_evidence": "DECLARE-TIMI 58",
                "hf_hospitalization_rr": 0.73,
                "bp_systolic_change_mmhg": -3.5,
                "bp_diastolic_change_mmhg": -1.5,
            },
            "hepatic": {
                "alt_effect": "decrease",
                "hepatotoxicity_risk": "none",
                "masld_benefit": "possible",
            },
            "weight": {
                "direction": "loss",
                "expected_kg": -2.2,
                "mechanism": "caloric loss via glucosuria",
            },
        },

        "contraindications": [
            {"condition": "type_1_diabetes", "severity": "absolute"},
            {"condition": "egfr_below_25", "severity": "absolute"},
            {"condition": "dialysis", "severity": "absolute"},
            {"condition": "dka_history", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "genital_mycotic_infection", "frequency": "common", "percent": 6.9},
            {"effect": "urinary_tract_infection", "frequency": "common", "percent": 5.7},
            {"effect": "volume_depletion", "frequency": "uncommon", "percent": 1.2},
            {"effect": "diabetic_ketoacidosis", "frequency": "rare", "percent": 0.1},
        ],

        "monitoring": [
            {"test": "renal_function", "timing": "before_initiation_and_periodically"},
            {"test": "volume_status", "timing": "if_on_diuretics"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "loop_diuretics",
                "severity": "moderate",
                "effect": "Additive volume depletion",
                "recommendation": "Reduce diuretic dose; monitor",
            },
            {
                "interacting_drug_class": "insulin",
                "severity": "moderate",
                "effect": "Increased hypoglycemia risk",
                "recommendation": "Consider reducing insulin by 20%",
            },
        ],

        "dosing": {
            "starting_dose": "10 mg once daily",
            "max_dose": "10 mg once daily",
            "renal_adjustment": "No adjustment for eGFR >= 25; do not initiate if eGFR < 25",
            "hepatic_adjustment": "Use with caution in severe hepatic impairment",
        },

        "cost_tier": "$$$$",
        "generic_available": False,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": False,
            "food_requirements": "none",
        },
    },

    "canagliflozin": {
        "name": "canagliflozin",
        "brand_names": ["Invokana"],
        "rxcui": "1373458",
        "drug_class": "SGLT2 inhibitor",
        "atc_code": "A10BK02",
        "mechanism": (
            "Inhibits SGLT2 (and weakly SGLT1) in the proximal tubule, "
            "reducing glucose reabsorption."
        ),
        "indications": ["type_2_diabetes", "diabetic_kidney_disease"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": -0.8,
                "hba1c_range": [-0.6, -1.0],
                "weight_change_kg": -2.5,
                "weight_range_kg": [-1.5, -3.5],
                "hypoglycemia_risk": "very_low",
                "mechanism_of_glycemic_effect": "insulin-independent glucosuria",
                "evidence": "CREDENCE, CANVAS",
            },
            "renal": {
                "egfr_acute_effect": -3.5,
                "egfr_acute_reversible": True,
                "egfr_slope_modifier": 0.66,  # ~34% slowing in CREDENCE
                "albuminuria_reduction_percent": -27,
                "evidence_trial": "CREDENCE (NEJM 2019)",
                "renoprotective": True,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.86,
                "mace_evidence": "CANVAS (NEJM 2017)",
                "hf_hospitalization_rr": 0.67,
                "bp_systolic_change_mmhg": -4,
                "bp_diastolic_change_mmhg": -2,
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "none",
                "masld_benefit": "possible",
            },
            "weight": {
                "direction": "loss",
                "expected_kg": -2.5,
                "mechanism": "caloric loss via glucosuria",
            },
        },

        "contraindications": [
            {"condition": "type_1_diabetes", "severity": "absolute"},
            {"condition": "egfr_below_30", "severity": "absolute"},
            {"condition": "dialysis", "severity": "absolute"},
            {"condition": "history_of_amputation", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "genital_mycotic_infection", "frequency": "common", "percent": 7.5},
            {"effect": "urinary_tract_infection", "frequency": "common", "percent": 5.9},
            {"effect": "lower_limb_amputation", "frequency": "uncommon", "percent": 0.6},
            {"effect": "fracture", "frequency": "uncommon", "percent": 1.5},
            {"effect": "diabetic_ketoacidosis", "frequency": "rare", "percent": 0.1},
        ],

        "monitoring": [
            {"test": "renal_function", "timing": "before_initiation_and_periodically"},
            {"test": "foot_exam", "timing": "regular_assessment_for_amputation_risk"},
            {"test": "volume_status", "timing": "if_on_diuretics"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "loop_diuretics",
                "severity": "moderate",
                "effect": "Additive volume depletion",
                "recommendation": "Adjust diuretic dose",
            },
            {
                "interacting_drug_class": "ace_inhibitor",
                "severity": "moderate",
                "effect": "Hyperkalemia risk in CKD",
                "recommendation": "Monitor potassium",
            },
        ],

        "dosing": {
            "starting_dose": "100 mg once daily",
            "max_dose": "300 mg once daily",
            "renal_adjustment": "Limit to 100 mg if eGFR 30-60; do not initiate if eGFR < 30",
            "hepatic_adjustment": "Avoid in severe hepatic impairment",
        },

        "cost_tier": "$$$$",
        "generic_available": False,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": True,
            "food_requirements": "before_first_meal",
        },
    },

    # -----------------------------------------------------------------------
    # GLP-1 RECEPTOR AGONISTS
    # -----------------------------------------------------------------------

    "semaglutide": {
        "name": "semaglutide",
        "brand_names": ["Ozempic", "Wegovy", "Rybelsus"],
        "rxcui": "1991302",
        "drug_class": "GLP-1 receptor agonist",
        "atc_code": "A10BJ06",
        "mechanism": (
            "Long-acting GLP-1 receptor agonist. Stimulates glucose-dependent "
            "insulin release, suppresses glucagon, slows gastric emptying, "
            "and promotes satiety via central appetite regulation."
        ),
        "indications": ["type_2_diabetes", "obesity", "cardiovascular_risk_reduction"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": -1.5,
                "hba1c_range": [-1.0, -1.8],
                "weight_change_kg": -6.0,
                "weight_range_kg": [-4.0, -15.0],  # higher with Wegovy 2.4mg
                "hypoglycemia_risk": "low",
                "mechanism_of_glycemic_effect": "glucose-dependent insulin secretion",
                "evidence": "SUSTAIN, STEP, SELECT trials",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_acute_reversible": False,
                "egfr_slope_modifier": 0.76,  # FLOW trial 24% reduction in renal events
                "albuminuria_reduction_percent": -22,
                "evidence_trial": "FLOW (NEJM 2024)",
                "renoprotective": True,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.74,
                "mace_evidence": "SUSTAIN-6 (NEJM 2016), SELECT (NEJM 2023)",
                "hf_hospitalization_rr": 0.93,
                "bp_systolic_change_mmhg": -4,
                "bp_diastolic_change_mmhg": -1,
            },
            "hepatic": {
                "alt_effect": "decrease",
                "hepatotoxicity_risk": "very_low",
                "masld_benefit": "demonstrated",
            },
            "weight": {
                "direction": "loss",
                "expected_kg": -6.0,
                "mechanism": "appetite suppression + delayed gastric emptying",
            },
        },

        "contraindications": [
            {"condition": "personal_history_medullary_thyroid_carcinoma", "severity": "absolute"},
            {"condition": "men2_syndrome", "severity": "absolute"},
            {"condition": "history_of_pancreatitis", "severity": "relative"},
            {"condition": "severe_gastroparesis", "severity": "relative"},
            {"condition": "type_1_diabetes", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "nausea", "frequency": "very_common", "percent": 20.0},
            {"effect": "diarrhea", "frequency": "common", "percent": 8.5},
            {"effect": "vomiting", "frequency": "common", "percent": 9.2},
            {"effect": "constipation", "frequency": "common", "percent": 6.5},
            {"effect": "abdominal_pain", "frequency": "common", "percent": 7.3},
            {"effect": "pancreatitis", "frequency": "rare", "percent": 0.3},
            {"effect": "gallbladder_disease", "frequency": "uncommon", "percent": 1.5},
        ],

        "monitoring": [
            {"test": "thyroid_symptoms", "timing": "ongoing"},
            {"test": "amylase_lipase", "timing": "if_pancreatitis_suspected"},
            {"test": "renal_function", "timing": "if_severe_GI_symptoms_with_volume_loss"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "insulin",
                "severity": "moderate",
                "effect": "Increased hypoglycemia risk",
                "recommendation": "Reduce insulin dose by 20% on initiation",
            },
            {
                "interacting_drug_class": "sulfonylurea",
                "severity": "moderate",
                "effect": "Increased hypoglycemia risk",
                "recommendation": "Consider reducing sulfonylurea dose",
            },
            {
                "interacting_drug_class": "oral_medications",
                "severity": "low",
                "effect": "Delayed gastric emptying may affect absorption",
                "recommendation": "Generally not clinically significant",
            },
        ],

        "dosing": {
            "starting_dose": "0.25 mg SC weekly x 4 weeks (titrate up)",
            "max_dose": "2.0 mg SC weekly (T2DM); 2.4 mg SC weekly (obesity)",
            "renal_adjustment": "No adjustment needed",
            "hepatic_adjustment": "No adjustment needed",
        },

        "cost_tier": "$$$$",
        "generic_available": False,
        "route": "subcutaneous",
        "frequency": "once_weekly",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": True,
            "titration_required": True,
            "food_requirements": "none",
        },
    },

    "liraglutide": {
        "name": "liraglutide",
        "brand_names": ["Victoza", "Saxenda"],
        "rxcui": "475968",
        "drug_class": "GLP-1 receptor agonist",
        "atc_code": "A10BJ02",
        "mechanism": (
            "GLP-1 receptor agonist with 97% homology to native GLP-1. "
            "Stimulates glucose-dependent insulin release, suppresses glucagon, "
            "slows gastric emptying, increases satiety."
        ),
        "indications": ["type_2_diabetes", "obesity", "cardiovascular_risk_reduction"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": -1.1,
                "hba1c_range": [-0.8, -1.5],
                "weight_change_kg": -3.0,
                "weight_range_kg": [-2.0, -8.0],  # higher with Saxenda 3.0mg
                "hypoglycemia_risk": "low",
                "mechanism_of_glycemic_effect": "glucose-dependent insulin secretion",
                "evidence": "LEAD, LEADER, SCALE trials",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_acute_reversible": False,
                "egfr_slope_modifier": 0.78,
                "albuminuria_reduction_percent": -17,
                "evidence_trial": "LEADER (NEJM 2016)",
                "renoprotective": True,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.87,
                "mace_evidence": "LEADER (NEJM 2016)",
                "hf_hospitalization_rr": 0.87,
                "bp_systolic_change_mmhg": -2.7,
                "bp_diastolic_change_mmhg": -0.6,
            },
            "hepatic": {
                "alt_effect": "decrease",
                "hepatotoxicity_risk": "very_low",
                "masld_benefit": "possible",
            },
            "weight": {
                "direction": "loss",
                "expected_kg": -3.0,
                "mechanism": "appetite suppression + delayed gastric emptying",
            },
        },

        "contraindications": [
            {"condition": "personal_history_medullary_thyroid_carcinoma", "severity": "absolute"},
            {"condition": "men2_syndrome", "severity": "absolute"},
            {"condition": "history_of_pancreatitis", "severity": "relative"},
            {"condition": "type_1_diabetes", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "nausea", "frequency": "very_common", "percent": 28.4},
            {"effect": "diarrhea", "frequency": "common", "percent": 17.1},
            {"effect": "vomiting", "frequency": "common", "percent": 10.9},
            {"effect": "headache", "frequency": "common", "percent": 13.6},
            {"effect": "pancreatitis", "frequency": "rare", "percent": 0.3},
        ],

        "monitoring": [
            {"test": "thyroid_symptoms", "timing": "ongoing"},
            {"test": "amylase_lipase", "timing": "if_pancreatitis_suspected"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "insulin",
                "severity": "moderate",
                "effect": "Increased hypoglycemia risk",
                "recommendation": "Reduce insulin dose on initiation",
            },
            {
                "interacting_drug_class": "sulfonylurea",
                "severity": "moderate",
                "effect": "Increased hypoglycemia risk",
                "recommendation": "Consider reducing sulfonylurea dose",
            },
        ],

        "dosing": {
            "starting_dose": "0.6 mg SC daily x 1 week (titrate up)",
            "max_dose": "1.8 mg SC daily (T2DM); 3.0 mg SC daily (obesity)",
            "renal_adjustment": "No adjustment needed",
            "hepatic_adjustment": "Use with caution in severe hepatic impairment",
        },

        "cost_tier": "$$$$",
        "generic_available": False,
        "route": "subcutaneous",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": True,
            "titration_required": True,
            "food_requirements": "none",
        },
    },

    "tirzepatide": {
        "name": "tirzepatide",
        "brand_names": ["Mounjaro", "Zepbound"],
        "rxcui": "2601723",
        "drug_class": "GIP/GLP-1 receptor co-agonist",
        "atc_code": "A10BX16",
        "mechanism": (
            "Dual agonist at glucose-dependent insulinotropic polypeptide (GIP) "
            "and GLP-1 receptors. Enhances insulin secretion, suppresses glucagon, "
            "slows gastric emptying, and induces robust weight loss via appetite "
            "regulation."
        ),
        "indications": ["type_2_diabetes", "obesity"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": -2.1,
                "hba1c_range": [-1.7, -2.4],
                "weight_change_kg": -10.5,
                "weight_range_kg": [-7.0, -22.0],  # dose-dependent up to 15mg
                "hypoglycemia_risk": "low",
                "mechanism_of_glycemic_effect": "GIP + GLP-1 mediated insulin secretion",
                "evidence": "SURPASS, SURMOUNT trials",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_acute_reversible": False,
                "egfr_slope_modifier": 0.85,
                "albuminuria_reduction_percent": -25,
                "evidence_trial": "SURPASS-4 (Lancet 2021)",
                "renoprotective": True,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.80,
                "mace_evidence": "SURPASS-CVOT (ongoing); SURPASS-4 cardiac safety",
                "hf_hospitalization_rr": 0.80,
                "bp_systolic_change_mmhg": -6,
                "bp_diastolic_change_mmhg": -2,
            },
            "hepatic": {
                "alt_effect": "decrease",
                "hepatotoxicity_risk": "very_low",
                "masld_benefit": "demonstrated",
            },
            "weight": {
                "direction": "loss",
                "expected_kg": -10.5,
                "mechanism": "robust appetite suppression + delayed gastric emptying",
            },
        },

        "contraindications": [
            {"condition": "personal_history_medullary_thyroid_carcinoma", "severity": "absolute"},
            {"condition": "men2_syndrome", "severity": "absolute"},
            {"condition": "history_of_pancreatitis", "severity": "relative"},
            {"condition": "severe_gastroparesis", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "nausea", "frequency": "very_common", "percent": 22.0},
            {"effect": "diarrhea", "frequency": "very_common", "percent": 17.0},
            {"effect": "vomiting", "frequency": "common", "percent": 9.0},
            {"effect": "constipation", "frequency": "common", "percent": 6.7},
            {"effect": "decreased_appetite", "frequency": "common", "percent": 9.0},
            {"effect": "pancreatitis", "frequency": "rare", "percent": 0.2},
        ],

        "monitoring": [
            {"test": "thyroid_symptoms", "timing": "ongoing"},
            {"test": "amylase_lipase", "timing": "if_pancreatitis_suspected"},
            {"test": "gallbladder_symptoms", "timing": "ongoing"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "insulin",
                "severity": "moderate",
                "effect": "Increased hypoglycemia risk",
                "recommendation": "Reduce insulin dose by 20-30% on initiation",
            },
            {
                "interacting_drug_class": "sulfonylurea",
                "severity": "moderate",
                "effect": "Increased hypoglycemia risk",
                "recommendation": "Reduce sulfonylurea dose",
            },
            {
                "interacting_drug_class": "oral_contraceptives",
                "severity": "moderate",
                "effect": "Reduced contraceptive efficacy after initial dose",
                "recommendation": "Use barrier method for 4 weeks after initiation/dose change",
            },
        ],

        "dosing": {
            "starting_dose": "2.5 mg SC weekly x 4 weeks (titrate up)",
            "max_dose": "15 mg SC weekly",
            "renal_adjustment": "No adjustment needed",
            "hepatic_adjustment": "No adjustment needed",
        },

        "cost_tier": "$$$$",
        "generic_available": False,
        "route": "subcutaneous",
        "frequency": "once_weekly",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": True,
            "titration_required": True,
            "food_requirements": "none",
        },
    },

    "dulaglutide": {
        "name": "dulaglutide",
        "brand_names": ["Trulicity"],
        "rxcui": "1551291",
        "drug_class": "GLP-1 receptor agonist",
        "atc_code": "A10BJ05",
        "mechanism": (
            "Long-acting GLP-1 receptor agonist (Fc-fusion protein). "
            "Stimulates insulin secretion, suppresses glucagon, slows gastric "
            "emptying, promotes satiety."
        ),
        "indications": ["type_2_diabetes", "cardiovascular_risk_reduction"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": -1.2,
                "hba1c_range": [-0.8, -1.5],
                "weight_change_kg": -3.0,
                "weight_range_kg": [-2.0, -4.5],
                "hypoglycemia_risk": "low",
                "mechanism_of_glycemic_effect": "glucose-dependent insulin secretion",
                "evidence": "AWARD, REWIND trials",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_acute_reversible": False,
                "egfr_slope_modifier": 0.85,
                "albuminuria_reduction_percent": -20,
                "evidence_trial": "REWIND (Lancet 2019)",
                "renoprotective": True,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.88,
                "mace_evidence": "REWIND (Lancet 2019)",
                "hf_hospitalization_rr": 0.93,
                "bp_systolic_change_mmhg": -2.5,
                "bp_diastolic_change_mmhg": -1,
            },
            "hepatic": {
                "alt_effect": "decrease",
                "hepatotoxicity_risk": "very_low",
                "masld_benefit": "possible",
            },
            "weight": {
                "direction": "loss",
                "expected_kg": -3.0,
                "mechanism": "appetite suppression",
            },
        },

        "contraindications": [
            {"condition": "personal_history_medullary_thyroid_carcinoma", "severity": "absolute"},
            {"condition": "men2_syndrome", "severity": "absolute"},
            {"condition": "history_of_pancreatitis", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "nausea", "frequency": "very_common", "percent": 21.1},
            {"effect": "diarrhea", "frequency": "common", "percent": 12.6},
            {"effect": "vomiting", "frequency": "common", "percent": 12.7},
            {"effect": "abdominal_pain", "frequency": "common", "percent": 9.4},
            {"effect": "decreased_appetite", "frequency": "common", "percent": 8.6},
        ],

        "monitoring": [
            {"test": "thyroid_symptoms", "timing": "ongoing"},
            {"test": "amylase_lipase", "timing": "if_pancreatitis_suspected"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "insulin",
                "severity": "moderate",
                "effect": "Increased hypoglycemia risk",
                "recommendation": "Reduce insulin dose on initiation",
            },
            {
                "interacting_drug_class": "sulfonylurea",
                "severity": "moderate",
                "effect": "Increased hypoglycemia risk",
                "recommendation": "Consider reducing sulfonylurea dose",
            },
        ],

        "dosing": {
            "starting_dose": "0.75 mg SC weekly",
            "max_dose": "4.5 mg SC weekly",
            "renal_adjustment": "No adjustment needed",
            "hepatic_adjustment": "No adjustment needed",
        },

        "cost_tier": "$$$$",
        "generic_available": False,
        "route": "subcutaneous",
        "frequency": "once_weekly",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": True,
            "titration_required": True,
            "food_requirements": "none",
        },
    },

    # -----------------------------------------------------------------------
    # BIGUANIDES
    # -----------------------------------------------------------------------

    "metformin": {
        "name": "metformin",
        "brand_names": ["Glucophage", "Glumetza", "Fortamet"],
        "rxcui": "6809",
        "drug_class": "Biguanide",
        "atc_code": "A10BA02",
        "mechanism": (
            "Decreases hepatic glucose production (primary effect), increases "
            "peripheral insulin sensitivity, reduces intestinal glucose absorption. "
            "Activates AMPK pathway."
        ),
        "indications": ["type_2_diabetes", "prediabetes", "polycystic_ovary_syndrome"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": -1.0,
                "hba1c_range": [-1.0, -2.0],
                "weight_change_kg": -1.5,
                "weight_range_kg": [-2.5, 0.0],
                "hypoglycemia_risk": "very_low",
                "mechanism_of_glycemic_effect": "decreased hepatic gluconeogenesis",
                "evidence": "UKPDS 34, ADA Standards of Care",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_acute_reversible": False,
                "egfr_slope_modifier": 1.0,  # neutral
                "albuminuria_reduction_percent": 0,
                "evidence_trial": "no direct renoprotective benefit demonstrated",
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.86,
                "mace_evidence": "UKPDS 34 (Lancet 1998) — overweight subgroup",
                "hf_hospitalization_rr": 1.0,
                "bp_systolic_change_mmhg": 0,
                "bp_diastolic_change_mmhg": 0,
            },
            "hepatic": {
                "alt_effect": "decrease",
                "hepatotoxicity_risk": "very_low",
                "masld_benefit": "possible",
            },
            "weight": {
                "direction": "loss",
                "expected_kg": -1.5,
                "mechanism": "GI side effects + modest appetite reduction",
            },
        },

        "contraindications": [
            {"condition": "egfr_below_30", "severity": "absolute"},
            {"condition": "acute_kidney_injury", "severity": "absolute"},
            {"condition": "metabolic_acidosis", "severity": "absolute"},
            {"condition": "iv_contrast_within_48h", "severity": "relative"},
            {"condition": "severe_hepatic_impairment", "severity": "relative"},
            {"condition": "decompensated_heart_failure", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "diarrhea", "frequency": "very_common", "percent": 53.2},
            {"effect": "nausea", "frequency": "very_common", "percent": 25.5},
            {"effect": "abdominal_discomfort", "frequency": "common", "percent": 12.1},
            {"effect": "metallic_taste", "frequency": "common", "percent": 4.5},
            {"effect": "vitamin_b12_deficiency", "frequency": "common", "percent": 5.8},
            {"effect": "lactic_acidosis", "frequency": "very_rare", "percent": 0.003},
        ],

        "monitoring": [
            {"test": "renal_function", "timing": "annually_or_more_frequently_if_CKD"},
            {"test": "vitamin_b12", "timing": "annually_after_4_years_of_use"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "iodinated_contrast",
                "severity": "high",
                "effect": "Risk of contrast-induced AKI and lactic acidosis",
                "recommendation": "Hold metformin at time of contrast; resume after 48h if renal function stable",
            },
            {
                "interacting_drug_class": "alcohol",
                "severity": "moderate",
                "effect": "Increased lactic acidosis risk",
                "recommendation": "Avoid heavy alcohol use",
            },
            {
                "interacting_drug_class": "carbonic_anhydrase_inhibitors",
                "severity": "moderate",
                "effect": "Additive metabolic acidosis risk",
                "recommendation": "Monitor acid-base status",
            },
        ],

        "dosing": {
            "starting_dose": "500 mg twice daily with meals",
            "max_dose": "2000-2550 mg/day in divided doses",
            "renal_adjustment": (
                "Reduce dose if eGFR 30-45; do not initiate if eGFR < 45; "
                "discontinue if eGFR < 30"
            ),
            "hepatic_adjustment": "Avoid in severe hepatic impairment",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "twice_daily",

        "adherence_factors": {
            "pill_burden": "moderate",
            "injection": False,
            "titration_required": True,
            "food_requirements": "with_meals",
        },
    },

    # -----------------------------------------------------------------------
    # SULFONYLUREAS
    # -----------------------------------------------------------------------

    "glipizide": {
        "name": "glipizide",
        "brand_names": ["Glucotrol", "Glucotrol XL"],
        "rxcui": "4821",
        "drug_class": "Sulfonylurea",
        "atc_code": "A10BB07",
        "mechanism": (
            "Stimulates insulin release from pancreatic beta cells by closing "
            "ATP-sensitive K+ channels (insulin secretagogue). "
            "Glucose-independent action."
        ),
        "indications": ["type_2_diabetes"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": -1.0,
                "hba1c_range": [-1.0, -2.0],
                "weight_change_kg": 2.0,
                "weight_range_kg": [1.0, 3.0],
                "hypoglycemia_risk": "moderate",
                "mechanism_of_glycemic_effect": "glucose-independent insulin secretion",
                "evidence": "UKPDS, ADA Standards of Care",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_acute_reversible": False,
                "egfr_slope_modifier": 1.0,
                "albuminuria_reduction_percent": 0,
                "evidence_trial": "no renoprotective effect",
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 1.0,
                "mace_evidence": "neutral cardiovascular effect overall",
                "hf_hospitalization_rr": 1.0,
                "bp_systolic_change_mmhg": 0,
                "bp_diastolic_change_mmhg": 0,
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "low",
                "masld_benefit": "none",
            },
            "weight": {
                "direction": "gain",
                "expected_kg": 2.0,
                "mechanism": "increased insulin secretion promotes lipogenesis",
            },
        },

        "contraindications": [
            {"condition": "type_1_diabetes", "severity": "absolute"},
            {"condition": "severe_renal_impairment", "severity": "relative"},
            {"condition": "severe_hepatic_impairment", "severity": "absolute"},
            {"condition": "sulfa_allergy_severe", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "hypoglycemia", "frequency": "common", "percent": 12.0},
            {"effect": "weight_gain", "frequency": "common", "percent": 30.0},
            {"effect": "nausea", "frequency": "uncommon", "percent": 3.0},
            {"effect": "rash", "frequency": "uncommon", "percent": 1.4},
        ],

        "monitoring": [
            {"test": "blood_glucose", "timing": "regularly"},
            {"test": "hba1c", "timing": "every_3-6_months"},
            {"test": "renal_function", "timing": "periodically"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "insulin",
                "severity": "high",
                "effect": "Severe hypoglycemia risk",
                "recommendation": "Avoid combination or use with extreme caution",
            },
            {
                "interacting_drug_class": "beta_blockers",
                "severity": "moderate",
                "effect": "Masks hypoglycemia symptoms",
                "recommendation": "Patient education on hypoglycemia awareness",
            },
            {
                "interacting_drug_class": "warfarin",
                "severity": "moderate",
                "effect": "Increased bleeding risk via protein binding displacement",
                "recommendation": "Monitor INR closely",
            },
        ],

        "dosing": {
            "starting_dose": "5 mg once daily before breakfast",
            "max_dose": "20 mg/day (immediate release); 20 mg/day (XL)",
            "renal_adjustment": "Use lowest effective dose if CKD; avoid in severe CKD",
            "hepatic_adjustment": "Use with caution; reduce dose",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_or_twice_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": True,
            "food_requirements": "before_meals",
        },
    },

    "glimepiride": {
        "name": "glimepiride",
        "brand_names": ["Amaryl"],
        "rxcui": "25789",
        "drug_class": "Sulfonylurea",
        "atc_code": "A10BB12",
        "mechanism": (
            "Third-generation sulfonylurea; stimulates pancreatic insulin "
            "secretion via ATP-sensitive K+ channel closure."
        ),
        "indications": ["type_2_diabetes"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": -1.5,
                "hba1c_range": [-1.0, -2.0],
                "weight_change_kg": 2.0,
                "weight_range_kg": [1.0, 3.0],
                "hypoglycemia_risk": "moderate",
                "mechanism_of_glycemic_effect": "glucose-independent insulin secretion",
                "evidence": "ADOPT, ADA Standards of Care",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_acute_reversible": False,
                "egfr_slope_modifier": 1.0,
                "albuminuria_reduction_percent": 0,
                "evidence_trial": "no renoprotective effect",
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 1.0,
                "mace_evidence": "CAROLINA — non-inferior to linagliptin",
                "hf_hospitalization_rr": 1.0,
                "bp_systolic_change_mmhg": 0,
                "bp_diastolic_change_mmhg": 0,
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "low",
                "masld_benefit": "none",
            },
            "weight": {
                "direction": "gain",
                "expected_kg": 2.0,
                "mechanism": "insulin-mediated lipogenesis",
            },
        },

        "contraindications": [
            {"condition": "type_1_diabetes", "severity": "absolute"},
            {"condition": "severe_renal_impairment", "severity": "relative"},
            {"condition": "severe_hepatic_impairment", "severity": "absolute"},
            {"condition": "g6pd_deficiency", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "hypoglycemia", "frequency": "common", "percent": 16.0},
            {"effect": "weight_gain", "frequency": "common", "percent": 25.0},
            {"effect": "dizziness", "frequency": "uncommon", "percent": 2.0},
            {"effect": "nausea", "frequency": "uncommon", "percent": 1.0},
        ],

        "monitoring": [
            {"test": "blood_glucose", "timing": "regularly"},
            {"test": "hba1c", "timing": "every_3-6_months"},
            {"test": "renal_function", "timing": "periodically"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "insulin",
                "severity": "high",
                "effect": "Severe hypoglycemia risk",
                "recommendation": "Avoid combination",
            },
            {
                "interacting_drug_class": "beta_blockers",
                "severity": "moderate",
                "effect": "Masks hypoglycemia",
                "recommendation": "Patient education",
            },
        ],

        "dosing": {
            "starting_dose": "1-2 mg once daily with breakfast",
            "max_dose": "8 mg/day",
            "renal_adjustment": "Start at 1 mg in CKD; use lowest effective dose",
            "hepatic_adjustment": "Use with caution",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": True,
            "food_requirements": "with_breakfast",
        },
    },

    # -----------------------------------------------------------------------
    # INSULINS
    # -----------------------------------------------------------------------

    "insulin_glargine": {
        "name": "insulin_glargine",
        "brand_names": ["Lantus", "Basaglar", "Toujeo"],
        "rxcui": "274783",
        "drug_class": "Long-acting insulin analog",
        "atc_code": "A10AE04",
        "mechanism": (
            "Long-acting basal insulin analog providing relatively flat "
            "24-hour glucose-lowering effect. Replaces endogenous basal insulin."
        ),
        "indications": ["type_1_diabetes", "type_2_diabetes"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": -1.5,
                "hba1c_range": [-1.0, -3.0],  # dose-dependent
                "weight_change_kg": 2.5,
                "weight_range_kg": [1.0, 5.0],
                "hypoglycemia_risk": "high",
                "mechanism_of_glycemic_effect": "exogenous insulin replacement",
                "evidence": "ORIGIN, EDITION trials",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_acute_reversible": False,
                "egfr_slope_modifier": 1.0,
                "albuminuria_reduction_percent": 0,
                "evidence_trial": "no direct renal effect",
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 1.0,
                "mace_evidence": "ORIGIN (NEJM 2012) — neutral",
                "hf_hospitalization_rr": 1.0,
                "bp_systolic_change_mmhg": 0,
                "bp_diastolic_change_mmhg": 0,
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "none",
                "masld_benefit": "none",
            },
            "weight": {
                "direction": "gain",
                "expected_kg": 2.5,
                "mechanism": "anabolic effects of insulin",
            },
        },

        "contraindications": [
            {"condition": "hypoglycemia_unawareness_severe", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "hypoglycemia", "frequency": "very_common", "percent": 30.0},
            {"effect": "weight_gain", "frequency": "very_common", "percent": 50.0},
            {"effect": "injection_site_reactions", "frequency": "common", "percent": 5.0},
            {"effect": "lipohypertrophy", "frequency": "common", "percent": 4.0},
        ],

        "monitoring": [
            {"test": "blood_glucose", "timing": "multiple_times_daily"},
            {"test": "hba1c", "timing": "every_3_months"},
            {"test": "injection_sites", "timing": "regularly"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "sulfonylurea",
                "severity": "high",
                "effect": "Severe hypoglycemia risk",
                "recommendation": "Avoid combination if possible",
            },
            {
                "interacting_drug_class": "beta_blockers",
                "severity": "moderate",
                "effect": "Masks hypoglycemia symptoms",
                "recommendation": "Patient education",
            },
            {
                "interacting_drug_class": "glp1_agonist",
                "severity": "moderate",
                "effect": "Additive glucose lowering",
                "recommendation": "Reduce insulin dose by 20% on initiation",
            },
        ],

        "dosing": {
            "starting_dose": "10 units SC daily (or 0.1-0.2 units/kg/day)",
            "max_dose": "highly individualized",
            "renal_adjustment": "Reduce dose in CKD due to decreased insulin clearance",
            "hepatic_adjustment": "Reduce dose in hepatic impairment",
        },

        "cost_tier": "$$$",
        "generic_available": True,  # Basaglar is biosimilar
        "route": "subcutaneous",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": True,
            "titration_required": True,
            "food_requirements": "none",
        },
    },

    "insulin_lispro": {
        "name": "insulin_lispro",
        "brand_names": ["Humalog", "Admelog"],
        "rxcui": "86009",
        "drug_class": "Rapid-acting insulin analog",
        "atc_code": "A10AB04",
        "mechanism": (
            "Rapid-acting prandial insulin analog. Onset 15 min, peak 1-2 hrs, "
            "duration 3-5 hrs. Used to cover meals and correct hyperglycemia."
        ),
        "indications": ["type_1_diabetes", "type_2_diabetes"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": -1.0,
                "hba1c_range": [-0.5, -2.0],
                "weight_change_kg": 2.0,
                "weight_range_kg": [1.0, 4.0],
                "hypoglycemia_risk": "high",
                "mechanism_of_glycemic_effect": "exogenous prandial insulin",
                "evidence": "FDA prescribing information",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_acute_reversible": False,
                "egfr_slope_modifier": 1.0,
                "albuminuria_reduction_percent": 0,
                "evidence_trial": "no direct renal effect",
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 1.0,
                "mace_evidence": "neutral",
                "hf_hospitalization_rr": 1.0,
                "bp_systolic_change_mmhg": 0,
                "bp_diastolic_change_mmhg": 0,
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "none",
                "masld_benefit": "none",
            },
            "weight": {
                "direction": "gain",
                "expected_kg": 2.0,
                "mechanism": "anabolic effects of insulin",
            },
        },

        "contraindications": [
            {"condition": "hypoglycemia", "severity": "absolute"},
        ],

        "side_effects": [
            {"effect": "hypoglycemia", "frequency": "very_common", "percent": 35.0},
            {"effect": "weight_gain", "frequency": "common", "percent": 30.0},
            {"effect": "injection_site_reactions", "frequency": "common", "percent": 4.0},
        ],

        "monitoring": [
            {"test": "blood_glucose", "timing": "before_meals_and_bedtime"},
            {"test": "hba1c", "timing": "every_3_months"},
            {"test": "carb_counting_skills", "timing": "ongoing_education"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "sulfonylurea",
                "severity": "high",
                "effect": "Hypoglycemia risk",
                "recommendation": "Avoid combination",
            },
            {
                "interacting_drug_class": "alcohol",
                "severity": "moderate",
                "effect": "Hypoglycemia risk",
                "recommendation": "Patient education on alcohol effects",
            },
        ],

        "dosing": {
            "starting_dose": "individualized; typically 4 units before largest meal",
            "max_dose": "highly individualized",
            "renal_adjustment": "Reduce dose in CKD",
            "hepatic_adjustment": "Reduce dose in hepatic impairment",
        },

        "cost_tier": "$$$",
        "generic_available": True,  # Admelog is biosimilar
        "route": "subcutaneous",
        "frequency": "with_meals",

        "adherence_factors": {
            "pill_burden": "moderate",
            "injection": True,
            "titration_required": True,
            "food_requirements": "before_meals",
        },
    },

    # -----------------------------------------------------------------------
    # ACE INHIBITORS
    # -----------------------------------------------------------------------

    "lisinopril": {
        "name": "lisinopril",
        "brand_names": ["Zestril", "Prinivil"],
        "rxcui": "29046",
        "drug_class": "ACE inhibitor",
        "atc_code": "C09AA03",
        "mechanism": (
            "Inhibits angiotensin-converting enzyme, blocking conversion of "
            "angiotensin I to angiotensin II. Reduces vasoconstriction, "
            "aldosterone secretion, and glomerular efferent arteriolar tone."
        ),
        "indications": [
            "hypertension", "heart_failure", "ckd_with_albuminuria",
            "post_myocardial_infarction"
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0,
                "hba1c_range": [0, 0],
                "weight_change_kg": 0,
                "weight_range_kg": [0, 0],
                "hypoglycemia_risk": "very_low",
                "mechanism_of_glycemic_effect": "none",
                "evidence": "no glycemic effect",
            },
            "renal": {
                "egfr_acute_effect": -5,  # initial dip due to efferent arteriolar dilation
                "egfr_acute_reversible": True,
                "egfr_slope_modifier": 0.65,  # ~35% slowing of decline in proteinuric CKD
                "albuminuria_reduction_percent": -35,
                "evidence_trial": "REIN, AIPRI",
                "renoprotective": True,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.78,
                "mace_evidence": "HOPE, ALLHAT",
                "hf_hospitalization_rr": 0.71,
                "bp_systolic_change_mmhg": -10,
                "bp_diastolic_change_mmhg": -5,
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "very_low",
                "masld_benefit": "none",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0,
                "mechanism": "no significant weight effect",
            },
        },

        "contraindications": [
            {"condition": "pregnancy", "severity": "absolute"},
            {"condition": "history_of_angioedema", "severity": "absolute"},
            {"condition": "bilateral_renal_artery_stenosis", "severity": "absolute"},
            {"condition": "hyperkalemia", "severity": "relative"},
            {"condition": "egfr_below_30", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "dry_cough", "frequency": "common", "percent": 11.0},
            {"effect": "hyperkalemia", "frequency": "common", "percent": 5.0},
            {"effect": "hypotension", "frequency": "common", "percent": 4.0},
            {"effect": "acute_kidney_injury", "frequency": "uncommon", "percent": 2.0},
            {"effect": "angioedema", "frequency": "rare", "percent": 0.3},
        ],

        "monitoring": [
            {"test": "renal_function", "timing": "1-2_weeks_after_initiation_then_periodically"},
            {"test": "potassium", "timing": "1-2_weeks_after_initiation_then_periodically"},
            {"test": "blood_pressure", "timing": "regularly"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "potassium_sparing_diuretic",
                "severity": "high",
                "effect": "Severe hyperkalemia risk",
                "recommendation": "Monitor potassium closely; consider alternative",
            },
            {
                "interacting_drug_class": "nsaid",
                "severity": "moderate",
                "effect": "Reduced antihypertensive effect; AKI risk",
                "recommendation": "Avoid chronic NSAID use; monitor renal function",
            },
            {
                "interacting_drug_class": "lithium",
                "severity": "moderate",
                "effect": "Increased lithium levels",
                "recommendation": "Monitor lithium level",
            },
            {
                "interacting_drug_class": "arb",
                "severity": "high",
                "effect": "Hyperkalemia, AKI, hypotension",
                "recommendation": "Avoid combination",
            },
        ],

        "dosing": {
            "starting_dose": "10 mg once daily (HTN); 5 mg daily (HF)",
            "max_dose": "40 mg/day",
            "renal_adjustment": "Reduce starting dose if eGFR < 30",
            "hepatic_adjustment": "No adjustment needed",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": True,
            "food_requirements": "none",
        },
    },

    # -----------------------------------------------------------------------
    # ARBs
    # -----------------------------------------------------------------------

    "losartan": {
        "name": "losartan",
        "brand_names": ["Cozaar"],
        "rxcui": "203160",
        "drug_class": "Angiotensin II receptor blocker",
        "atc_code": "C09CA01",
        "mechanism": (
            "Selectively blocks the angiotensin II type 1 (AT1) receptor, "
            "preventing vasoconstriction and aldosterone secretion."
        ),
        "indications": [
            "hypertension", "diabetic_nephropathy", "heart_failure"
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0,
                "hba1c_range": [0, 0],
                "weight_change_kg": 0,
                "weight_range_kg": [0, 0],
                "hypoglycemia_risk": "very_low",
                "mechanism_of_glycemic_effect": "none",
                "evidence": "no glycemic effect",
            },
            "renal": {
                "egfr_acute_effect": -5,
                "egfr_acute_reversible": True,
                "egfr_slope_modifier": 0.74,  # RENAAL trial
                "albuminuria_reduction_percent": -35,
                "evidence_trial": "RENAAL (NEJM 2001)",
                "renoprotective": True,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.87,
                "mace_evidence": "LIFE trial",
                "hf_hospitalization_rr": 0.81,
                "bp_systolic_change_mmhg": -10,
                "bp_diastolic_change_mmhg": -5,
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "very_low",
                "masld_benefit": "none",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0,
                "mechanism": "no significant weight effect",
            },
        },

        "contraindications": [
            {"condition": "pregnancy", "severity": "absolute"},
            {"condition": "bilateral_renal_artery_stenosis", "severity": "absolute"},
            {"condition": "hyperkalemia", "severity": "relative"},
            {"condition": "severe_hepatic_impairment", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "dizziness", "frequency": "common", "percent": 4.1},
            {"effect": "hyperkalemia", "frequency": "common", "percent": 3.5},
            {"effect": "hypotension", "frequency": "common", "percent": 2.8},
            {"effect": "acute_kidney_injury", "frequency": "uncommon", "percent": 1.5},
            {"effect": "angioedema", "frequency": "very_rare", "percent": 0.05},
        ],

        "monitoring": [
            {"test": "renal_function", "timing": "1-2_weeks_after_initiation_then_periodically"},
            {"test": "potassium", "timing": "1-2_weeks_after_initiation_then_periodically"},
            {"test": "blood_pressure", "timing": "regularly"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "potassium_sparing_diuretic",
                "severity": "high",
                "effect": "Severe hyperkalemia",
                "recommendation": "Monitor potassium closely",
            },
            {
                "interacting_drug_class": "nsaid",
                "severity": "moderate",
                "effect": "Reduced BP control; AKI risk",
                "recommendation": "Avoid chronic NSAIDs",
            },
            {
                "interacting_drug_class": "ace_inhibitor",
                "severity": "high",
                "effect": "Hyperkalemia, AKI",
                "recommendation": "Avoid combination",
            },
        ],

        "dosing": {
            "starting_dose": "50 mg once daily",
            "max_dose": "100 mg/day",
            "renal_adjustment": "No initial adjustment; monitor",
            "hepatic_adjustment": "Start at 25 mg in hepatic impairment",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": True,
            "food_requirements": "none",
        },
    },

    # -----------------------------------------------------------------------
    # STATINS
    # -----------------------------------------------------------------------

    "atorvastatin": {
        "name": "atorvastatin",
        "brand_names": ["Lipitor"],
        "rxcui": "83367",
        "drug_class": "HMG-CoA reductase inhibitor (statin)",
        "atc_code": "C10AA05",
        "mechanism": (
            "Competitively inhibits HMG-CoA reductase, the rate-limiting enzyme "
            "in cholesterol biosynthesis. Reduces hepatic cholesterol synthesis "
            "and upregulates LDL receptors."
        ),
        "indications": [
            "hyperlipidemia", "ascvd_prevention", "diabetes_with_cv_risk"
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.1,  # mild HbA1c increase reported
                "hba1c_range": [0.0, 0.3],
                "weight_change_kg": 0,
                "weight_range_kg": [0, 0],
                "hypoglycemia_risk": "very_low",
                "mechanism_of_glycemic_effect": "small increase in insulin resistance",
                "evidence": "JUPITER, meta-analyses",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_acute_reversible": False,
                "egfr_slope_modifier": 1.0,
                "albuminuria_reduction_percent": -5,  # mild benefit in some studies
                "evidence_trial": "PLANET I/II",
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.64,  # ~36% reduction with high-intensity statin
                "mace_evidence": "TNT, IDEAL, JUPITER",
                "hf_hospitalization_rr": 0.85,
                "bp_systolic_change_mmhg": 0,
                "bp_diastolic_change_mmhg": 0,
                "ldl_reduction_percent": -50,  # high-intensity (40-80 mg)
            },
            "hepatic": {
                "alt_effect": "increase",  # mild, usually transient
                "hepatotoxicity_risk": "low",
                "masld_benefit": "possible",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0,
                "mechanism": "no significant weight effect",
            },
        },

        "contraindications": [
            {"condition": "pregnancy", "severity": "absolute"},
            {"condition": "active_liver_disease", "severity": "absolute"},
            {"condition": "unexplained_persistent_alt_elevation", "severity": "absolute"},
            {"condition": "history_of_rhabdomyolysis", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "myalgia", "frequency": "common", "percent": 5.0},
            {"effect": "alt_elevation", "frequency": "common", "percent": 1.3},
            {"effect": "new_onset_diabetes", "frequency": "uncommon", "percent": 0.5},
            {"effect": "rhabdomyolysis", "frequency": "very_rare", "percent": 0.01},
        ],

        "monitoring": [
            {"test": "lipid_panel", "timing": "4-12_weeks_after_initiation_then_annually"},
            {"test": "liver_enzymes", "timing": "baseline_and_if_symptoms"},
            {"test": "ck", "timing": "if_muscle_symptoms"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "cyp3a4_strong_inhibitor",
                "severity": "high",
                "effect": "Increased atorvastatin exposure; rhabdomyolysis risk",
                "recommendation": "Reduce dose or use alternative statin",
            },
            {
                "interacting_drug_class": "fibrate",
                "severity": "moderate",
                "effect": "Increased myopathy risk",
                "recommendation": "Use with caution; prefer fenofibrate over gemfibrozil",
            },
            {
                "interacting_drug_class": "warfarin",
                "severity": "moderate",
                "effect": "Slightly increased INR",
                "recommendation": "Monitor INR after initiation",
            },
        ],

        "dosing": {
            "starting_dose": "10-20 mg daily (moderate); 40-80 mg daily (high-intensity)",
            "max_dose": "80 mg daily",
            "renal_adjustment": "No adjustment needed",
            "hepatic_adjustment": "Contraindicated in active liver disease",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": False,
            "food_requirements": "none",
        },
    },

    "rosuvastatin": {
        "name": "rosuvastatin",
        "brand_names": ["Crestor"],
        "rxcui": "301542",
        "drug_class": "HMG-CoA reductase inhibitor (statin)",
        "atc_code": "C10AA07",
        "mechanism": (
            "Highly potent statin; competitively inhibits HMG-CoA reductase "
            "with greater LDL-lowering potency than other statins per mg."
        ),
        "indications": [
            "hyperlipidemia", "ascvd_prevention", "primary_prevention_high_crp"
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.1,
                "hba1c_range": [0.0, 0.3],
                "weight_change_kg": 0,
                "weight_range_kg": [0, 0],
                "hypoglycemia_risk": "very_low",
                "mechanism_of_glycemic_effect": "small insulin resistance increase",
                "evidence": "JUPITER (NEJM 2008)",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_acute_reversible": False,
                "egfr_slope_modifier": 1.0,
                "albuminuria_reduction_percent": -5,
                "evidence_trial": "PLANET I",
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.56,
                "mace_evidence": "JUPITER (NEJM 2008)",
                "hf_hospitalization_rr": 0.85,
                "bp_systolic_change_mmhg": 0,
                "bp_diastolic_change_mmhg": 0,
                "ldl_reduction_percent": -55,
            },
            "hepatic": {
                "alt_effect": "increase",
                "hepatotoxicity_risk": "low",
                "masld_benefit": "possible",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0,
                "mechanism": "no significant weight effect",
            },
        },

        "contraindications": [
            {"condition": "pregnancy", "severity": "absolute"},
            {"condition": "active_liver_disease", "severity": "absolute"},
            {"condition": "asian_ancestry_high_dose", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "myalgia", "frequency": "common", "percent": 5.0},
            {"effect": "alt_elevation", "frequency": "common", "percent": 2.2},
            {"effect": "proteinuria_transient", "frequency": "uncommon", "percent": 1.0},
            {"effect": "new_onset_diabetes", "frequency": "uncommon", "percent": 0.7},
            {"effect": "rhabdomyolysis", "frequency": "very_rare", "percent": 0.01},
        ],

        "monitoring": [
            {"test": "lipid_panel", "timing": "4-12_weeks_after_initiation"},
            {"test": "liver_enzymes", "timing": "baseline_and_if_symptoms"},
            {"test": "ck", "timing": "if_muscle_symptoms"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "cyclosporine",
                "severity": "high",
                "effect": "Markedly increased rosuvastatin exposure",
                "recommendation": "Limit dose to 5 mg daily",
            },
            {
                "interacting_drug_class": "warfarin",
                "severity": "moderate",
                "effect": "Increased INR",
                "recommendation": "Monitor INR",
            },
            {
                "interacting_drug_class": "antacids",
                "severity": "low",
                "effect": "Reduced absorption",
                "recommendation": "Separate doses by 2 hours",
            },
        ],

        "dosing": {
            "starting_dose": "10-20 mg daily",
            "max_dose": "40 mg daily",
            "renal_adjustment": "Limit to 10 mg if eGFR < 30",
            "hepatic_adjustment": "Contraindicated in active liver disease",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": False,
            "food_requirements": "none",
        },
    },

    # -----------------------------------------------------------------------
    # DIURETICS
    # -----------------------------------------------------------------------

    "furosemide": {
        "name": "furosemide",
        "brand_names": ["Lasix"],
        "rxcui": "4603",
        "drug_class": "Loop diuretic",
        "atc_code": "C03CA01",
        "mechanism": (
            "Inhibits the Na-K-2Cl cotransporter in the thick ascending limb "
            "of the loop of Henle, producing potent natriuresis and diuresis."
        ),
        "indications": [
            "heart_failure", "edema", "hypertension_in_ckd",
            "hyperkalemia_acute"
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.2,  # may worsen glucose control
                "hba1c_range": [0.0, 0.4],
                "weight_change_kg": -1.5,  # fluid loss
                "weight_range_kg": [-3.0, 0.0],
                "hypoglycemia_risk": "very_low",
                "mechanism_of_glycemic_effect": "may worsen insulin resistance",
                "evidence": "FDA prescribing information",
            },
            "renal": {
                "egfr_acute_effect": -3,  # may decline with overdiuresis
                "egfr_acute_reversible": True,
                "egfr_slope_modifier": 1.0,
                "albuminuria_reduction_percent": 0,
                "evidence_trial": "no renoprotective effect",
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 1.0,
                "mace_evidence": "symptomatic relief in HF without mortality benefit",
                "hf_hospitalization_rr": 0.7,  # symptomatic improvement
                "bp_systolic_change_mmhg": -7,
                "bp_diastolic_change_mmhg": -3,
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "very_low",
                "masld_benefit": "none",
            },
            "weight": {
                "direction": "loss",
                "expected_kg": -1.5,
                "mechanism": "fluid loss via natriuresis",
            },
        },

        "contraindications": [
            {"condition": "anuria", "severity": "absolute"},
            {"condition": "severe_hypokalemia", "severity": "relative"},
            {"condition": "severe_hyponatremia", "severity": "relative"},
            {"condition": "sulfa_allergy_severe", "severity": "relative"},
            {"condition": "hepatic_coma", "severity": "absolute"},
        ],

        "side_effects": [
            {"effect": "hypokalemia", "frequency": "very_common", "percent": 20.0},
            {"effect": "dehydration", "frequency": "common", "percent": 10.0},
            {"effect": "hypotension", "frequency": "common", "percent": 8.0},
            {"effect": "hyponatremia", "frequency": "common", "percent": 7.0},
            {"effect": "ototoxicity", "frequency": "uncommon", "percent": 1.0},
            {"effect": "hyperuricemia", "frequency": "common", "percent": 15.0},
        ],

        "monitoring": [
            {"test": "electrolytes", "timing": "1_week_after_initiation_then_periodically"},
            {"test": "renal_function", "timing": "regularly"},
            {"test": "volume_status", "timing": "ongoing"},
            {"test": "weight", "timing": "daily_in_HF_patients"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "ace_inhibitor",
                "severity": "moderate",
                "effect": "Hypotension on initiation",
                "recommendation": "Hold diuretic before first ACE-I dose",
            },
            {
                "interacting_drug_class": "lithium",
                "severity": "high",
                "effect": "Increased lithium toxicity",
                "recommendation": "Avoid combination",
            },
            {
                "interacting_drug_class": "nsaid",
                "severity": "moderate",
                "effect": "Reduced diuretic effect; AKI risk",
                "recommendation": "Avoid chronic NSAIDs",
            },
            {
                "interacting_drug_class": "aminoglycoside",
                "severity": "high",
                "effect": "Additive ototoxicity and nephrotoxicity",
                "recommendation": "Avoid combination",
            },
        ],

        "dosing": {
            "starting_dose": "20-40 mg PO once daily (HF/edema)",
            "max_dose": "600 mg/day (rarely needed)",
            "renal_adjustment": "Higher doses needed in CKD",
            "hepatic_adjustment": "Use with caution",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral_or_iv",
        "frequency": "once_or_twice_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": True,
            "food_requirements": "none",
        },
    },

    "spironolactone": {
        "name": "spironolactone",
        "brand_names": ["Aldactone"],
        "rxcui": "9997",
        "drug_class": "Mineralocorticoid receptor antagonist",
        "atc_code": "C03DA01",
        "mechanism": (
            "Competitively antagonizes aldosterone at the mineralocorticoid "
            "receptor in the distal nephron, producing potassium-sparing diuresis."
        ),
        "indications": [
            "heart_failure_reduced_ef", "resistant_hypertension",
            "primary_aldosteronism", "ascites_cirrhosis", "hirsutism"
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0,
                "hba1c_range": [0, 0],
                "weight_change_kg": -1.0,
                "weight_range_kg": [-2.0, 0.0],
                "hypoglycemia_risk": "very_low",
                "mechanism_of_glycemic_effect": "minimal",
                "evidence": "RALES, EMPHASIS-HF",
            },
            "renal": {
                "egfr_acute_effect": -3,
                "egfr_acute_reversible": True,
                "egfr_slope_modifier": 0.85,
                "albuminuria_reduction_percent": -25,
                "evidence_trial": "EMPHASIS-HF, AMBER",
                "renoprotective": True,  # in HF and proteinuric CKD
            },
            "cardiovascular": {
                "mace_relative_risk": 0.70,
                "mace_evidence": "RALES (NEJM 1999), EMPHASIS-HF (NEJM 2011)",
                "hf_hospitalization_rr": 0.65,
                "bp_systolic_change_mmhg": -8,
                "bp_diastolic_change_mmhg": -3,
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "very_low",
                "masld_benefit": "none",
            },
            "weight": {
                "direction": "loss",
                "expected_kg": -1.0,
                "mechanism": "mild diuresis",
            },
        },

        "contraindications": [
            {"condition": "hyperkalemia", "severity": "absolute"},
            {"condition": "egfr_below_30", "severity": "relative"},
            {"condition": "addison_disease", "severity": "absolute"},
            {"condition": "anuria", "severity": "absolute"},
        ],

        "side_effects": [
            {"effect": "hyperkalemia", "frequency": "common", "percent": 12.0},
            {"effect": "gynecomastia", "frequency": "common", "percent": 9.0},
            {"effect": "menstrual_irregularities", "frequency": "common", "percent": 8.0},
            {"effect": "decreased_libido", "frequency": "uncommon", "percent": 4.0},
            {"effect": "acute_kidney_injury", "frequency": "uncommon", "percent": 2.0},
        ],

        "monitoring": [
            {"test": "potassium", "timing": "1_week_2_weeks_then_monthly_x_3_then_quarterly"},
            {"test": "renal_function", "timing": "concurrent_with_potassium"},
            {"test": "blood_pressure", "timing": "regularly"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "ace_inhibitor",
                "severity": "high",
                "effect": "Severe hyperkalemia",
                "recommendation": "Monitor potassium closely; avoid in eGFR < 30",
            },
            {
                "interacting_drug_class": "arb",
                "severity": "high",
                "effect": "Severe hyperkalemia",
                "recommendation": "Monitor potassium closely",
            },
            {
                "interacting_drug_class": "potassium_supplement",
                "severity": "high",
                "effect": "Severe hyperkalemia",
                "recommendation": "Avoid combination",
            },
            {
                "interacting_drug_class": "nsaid",
                "severity": "moderate",
                "effect": "Hyperkalemia, AKI",
                "recommendation": "Avoid chronic NSAIDs",
            },
        ],

        "dosing": {
            "starting_dose": "12.5-25 mg once daily (HF); 25-50 mg daily (HTN)",
            "max_dose": "200 mg/day (HTN); 50 mg/day (HF)",
            "renal_adjustment": "Avoid if eGFR < 30; reduce dose if eGFR 30-50",
            "hepatic_adjustment": "Use with caution; useful in cirrhotic ascites",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": True,
            "food_requirements": "with_food",
        },
    },

    "hydrochlorothiazide": {
        "name": "hydrochlorothiazide",
        "brand_names": ["Microzide", "HydroDiuril"],
        "rxcui": "5487",
        "drug_class": "Thiazide diuretic",
        "atc_code": "C03AA03",
        "mechanism": (
            "Inhibits Na-Cl cotransporter in the distal convoluted tubule, "
            "producing modest natriuresis. Long-term BP lowering may be due "
            "to vasodilation."
        ),
        "indications": ["hypertension", "edema"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.2,  # may worsen glucose
                "hba1c_range": [0.0, 0.4],
                "weight_change_kg": -1.0,
                "weight_range_kg": [-2.0, 0.0],
                "hypoglycemia_risk": "very_low",
                "mechanism_of_glycemic_effect": "may worsen insulin resistance via hypokalemia",
                "evidence": "ALLHAT",
            },
            "renal": {
                "egfr_acute_effect": -2,
                "egfr_acute_reversible": True,
                "egfr_slope_modifier": 1.0,
                "albuminuria_reduction_percent": 0,
                "evidence_trial": "no renoprotective effect",
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.85,
                "mace_evidence": "ALLHAT",
                "hf_hospitalization_rr": 0.85,
                "bp_systolic_change_mmhg": -8,
                "bp_diastolic_change_mmhg": -4,
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "very_low",
                "masld_benefit": "none",
            },
            "weight": {
                "direction": "loss",
                "expected_kg": -1.0,
                "mechanism": "fluid loss via natriuresis",
            },
        },

        "contraindications": [
            {"condition": "anuria", "severity": "absolute"},
            {"condition": "egfr_below_30", "severity": "relative"},
            {"condition": "severe_hyponatremia", "severity": "relative"},
            {"condition": "sulfa_allergy_severe", "severity": "relative"},
            {"condition": "gout", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "hypokalemia", "frequency": "common", "percent": 15.0},
            {"effect": "hyponatremia", "frequency": "common", "percent": 10.0},
            {"effect": "hyperuricemia", "frequency": "common", "percent": 12.0},
            {"effect": "hypercalcemia", "frequency": "uncommon", "percent": 3.0},
            {"effect": "photosensitivity", "frequency": "uncommon", "percent": 2.0},
            {"effect": "dyslipidemia", "frequency": "common", "percent": 5.0},
        ],

        "monitoring": [
            {"test": "electrolytes", "timing": "2-4_weeks_after_initiation_then_annually"},
            {"test": "renal_function", "timing": "annually"},
            {"test": "uric_acid", "timing": "if_gout_history"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "lithium",
                "severity": "high",
                "effect": "Increased lithium toxicity",
                "recommendation": "Avoid combination",
            },
            {
                "interacting_drug_class": "nsaid",
                "severity": "moderate",
                "effect": "Reduced antihypertensive effect",
                "recommendation": "Avoid chronic NSAIDs",
            },
            {
                "interacting_drug_class": "digoxin",
                "severity": "moderate",
                "effect": "Hypokalemia increases digoxin toxicity",
                "recommendation": "Monitor potassium and digoxin levels",
            },
        ],

        "dosing": {
            "starting_dose": "12.5-25 mg once daily",
            "max_dose": "50 mg/day",
            "renal_adjustment": "Less effective if eGFR < 30; consider loop diuretic",
            "hepatic_adjustment": "Use with caution",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": True,
            "food_requirements": "none",
        },
    },

    # -----------------------------------------------------------------------
    # NSAIDs
    # -----------------------------------------------------------------------

    "ibuprofen": {
        "name": "ibuprofen",
        "brand_names": ["Advil", "Motrin"],
        "rxcui": "5640",
        "drug_class": "NSAID",
        "atc_code": "M01AE01",
        "mechanism": (
            "Non-selective inhibitor of cyclooxygenase (COX-1 and COX-2), "
            "reducing prostaglandin synthesis. Anti-inflammatory, analgesic, "
            "and antipyretic effects."
        ),
        "indications": ["pain", "fever", "inflammation", "dysmenorrhea"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0,
                "hba1c_range": [0, 0],
                "weight_change_kg": 0,
                "weight_range_kg": [0, 0],
                "hypoglycemia_risk": "very_low",
                "mechanism_of_glycemic_effect": "none",
                "evidence": "no glycemic effect",
            },
            "renal": {
                "egfr_acute_effect": -10,  # significant in CKD/dehydration
                "egfr_acute_reversible": True,  # often, but can persist
                "egfr_slope_modifier": 1.3,  # accelerates decline in CKD
                "albuminuria_reduction_percent": 0,
                "evidence_trial": "FDA boxed warnings; KDIGO 2024",
                "renoprotective": False,  # NEPHROTOXIC
            },
            "cardiovascular": {
                "mace_relative_risk": 1.31,  # increased CV risk with chronic use
                "mace_evidence": "PRECISION trial, FDA warnings",
                "hf_hospitalization_rr": 1.5,  # may worsen HF
                "bp_systolic_change_mmhg": 5,  # raises BP
                "bp_diastolic_change_mmhg": 2,
            },
            "hepatic": {
                "alt_effect": "increase",
                "hepatotoxicity_risk": "low",
                "masld_benefit": "none",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0,
                "mechanism": "no significant weight effect",
            },
        },

        "contraindications": [
            {"condition": "ckd_stage_4_or_5", "severity": "absolute"},
            {"condition": "active_gi_bleeding", "severity": "absolute"},
            {"condition": "third_trimester_pregnancy", "severity": "absolute"},
            {"condition": "severe_heart_failure", "severity": "relative"},
            {"condition": "history_of_peptic_ulcer", "severity": "relative"},
            {"condition": "concurrent_anticoagulation", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "gi_upset", "frequency": "common", "percent": 15.0},
            {"effect": "peptic_ulcer", "frequency": "uncommon", "percent": 1.0},
            {"effect": "acute_kidney_injury", "frequency": "uncommon", "percent": 1.5},
            {"effect": "hypertension_worsening", "frequency": "common", "percent": 10.0},
            {"effect": "edema", "frequency": "common", "percent": 5.0},
            {"effect": "gi_bleeding", "frequency": "rare", "percent": 0.5},
        ],

        "monitoring": [
            {"test": "renal_function", "timing": "if_chronic_use"},
            {"test": "blood_pressure", "timing": "if_chronic_use"},
            {"test": "gi_symptoms", "timing": "ongoing"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "ace_inhibitor",
                "severity": "moderate",
                "effect": "Reduced antihypertensive effect; AKI risk (triple whammy)",
                "recommendation": "Avoid chronic NSAID with ACE-I + diuretic",
            },
            {
                "interacting_drug_class": "arb",
                "severity": "moderate",
                "effect": "Reduced BP control; AKI risk",
                "recommendation": "Avoid chronic combination",
            },
            {
                "interacting_drug_class": "anticoagulant",
                "severity": "high",
                "effect": "Major bleeding risk",
                "recommendation": "Avoid; use acetaminophen instead",
            },
            {
                "interacting_drug_class": "loop_diuretic",
                "severity": "moderate",
                "effect": "Reduced diuretic effect",
                "recommendation": "Monitor volume and renal function",
            },
            {
                "interacting_drug_class": "lithium",
                "severity": "moderate",
                "effect": "Increased lithium levels",
                "recommendation": "Monitor lithium",
            },
        ],

        "dosing": {
            "starting_dose": "200-400 mg PO every 4-6 hours as needed",
            "max_dose": "3200 mg/day (Rx); 1200 mg/day (OTC)",
            "renal_adjustment": "Avoid in CKD",
            "hepatic_adjustment": "Use with caution",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "as_needed_or_three_times_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": False,
            "food_requirements": "with_food",
        },
    },

    # -----------------------------------------------------------------------
    # BETA BLOCKERS
    # -----------------------------------------------------------------------

    "metoprolol": {
        "name": "metoprolol",
        "brand_names": ["Lopressor", "Toprol-XL"],
        "rxcui": "6918",
        "drug_class": "Beta-1 selective blocker",
        "atc_code": "C07AB02",
        "mechanism": (
            "Selectively blocks beta-1 adrenergic receptors, reducing heart "
            "rate, contractility, and renin release. Cardioselective at "
            "lower doses."
        ),
        "indications": [
            "hypertension", "heart_failure_reduced_ef", "angina",
            "post_myocardial_infarction", "atrial_fibrillation_rate_control"
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.1,  # may worsen glucose slightly
                "hba1c_range": [0.0, 0.3],
                "weight_change_kg": 1.0,  # mild weight gain reported
                "weight_range_kg": [0.0, 2.0],
                "hypoglycemia_risk": "low",
                "mechanism_of_glycemic_effect": "mild insulin resistance; masks hypoglycemia",
                "evidence": "ALLHAT subgroup analyses",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_acute_reversible": False,
                "egfr_slope_modifier": 1.0,
                "albuminuria_reduction_percent": 0,
                "evidence_trial": "no direct renal effect",
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.75,  # post-MI
                "mace_evidence": "MERIT-HF (Lancet 1999); post-MI trials",
                "hf_hospitalization_rr": 0.65,
                "bp_systolic_change_mmhg": -8,
                "bp_diastolic_change_mmhg": -5,
                "heart_rate_change_bpm": -10,
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "very_low",
                "masld_benefit": "none",
            },
            "weight": {
                "direction": "gain",
                "expected_kg": 1.0,
                "mechanism": "reduced metabolic rate, mild fluid retention",
            },
        },

        "contraindications": [
            {"condition": "severe_bradycardia", "severity": "absolute"},
            {"condition": "second_or_third_degree_heart_block", "severity": "absolute"},
            {"condition": "decompensated_heart_failure", "severity": "relative"},
            {"condition": "severe_asthma", "severity": "relative"},
            {"condition": "severe_peripheral_arterial_disease", "severity": "relative"},
            {"condition": "cardiogenic_shock", "severity": "absolute"},
        ],

        "side_effects": [
            {"effect": "fatigue", "frequency": "common", "percent": 10.0},
            {"effect": "bradycardia", "frequency": "common", "percent": 7.0},
            {"effect": "dizziness", "frequency": "common", "percent": 6.0},
            {"effect": "depression", "frequency": "uncommon", "percent": 4.0},
            {"effect": "erectile_dysfunction", "frequency": "uncommon", "percent": 3.0},
            {"effect": "bronchospasm", "frequency": "uncommon", "percent": 1.0},
            {"effect": "cold_extremities", "frequency": "common", "percent": 5.0},
        ],

        "monitoring": [
            {"test": "heart_rate", "timing": "regularly"},
            {"test": "blood_pressure", "timing": "regularly"},
            {"test": "signs_of_heart_failure_decompensation", "timing": "ongoing"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "calcium_channel_blocker_nondhp",
                "severity": "high",
                "effect": "Severe bradycardia, AV block",
                "recommendation": "Avoid combination with verapamil/diltiazem",
            },
            {
                "interacting_drug_class": "insulin",
                "severity": "moderate",
                "effect": "Masks hypoglycemia symptoms",
                "recommendation": "Patient education on hypoglycemia awareness",
            },
            {
                "interacting_drug_class": "sulfonylurea",
                "severity": "moderate",
                "effect": "Masks hypoglycemia",
                "recommendation": "Patient education",
            },
            {
                "interacting_drug_class": "clonidine",
                "severity": "high",
                "effect": "Rebound hypertension on clonidine withdrawal",
                "recommendation": "Discontinue beta-blocker first",
            },
        ],

        "dosing": {
            "starting_dose": "25-50 mg twice daily (tartrate); 25 mg daily (succinate XL)",
            "max_dose": "400 mg/day",
            "renal_adjustment": "No adjustment needed",
            "hepatic_adjustment": "Reduce dose in hepatic impairment",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_or_twice_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": True,
            "food_requirements": "none",
        },
    },


    "sitagliptin": {
        "name": "sitagliptin",
        "brand_names": ["Januvia"],
        "rxcui": "593411",
        "drug_class": "DPP-4 inhibitor",
        "atc_code": "A10BH01",
        "mechanism": (
            "Inhibits dipeptidyl peptidase-4 (DPP-4), prolonging the action "
            "of incretin hormones (GLP-1 and GIP) which increase glucose-"
            "dependent insulin release and reduce glucagon."
        ),
        "indications": ["type_2_diabetes"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": -0.7,
                "hba1c_range": [-0.5, -0.9],
                "weight_change_kg": 0.0,
                "weight_range_kg": [-0.5, 0.5],
                "hypoglycemia_risk": "low",
                "mechanism_of_glycemic_effect": "incretin enhancement, glucose-dependent",
                "evidence": "TECOS trial (NEJM 2015)",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_slope_modifier": 1.0,
                "albuminuria_reduction_percent": 0,
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.98,
                "mace_evidence": "TECOS (PMID 26052984) - cardiovascular neutral",
                "hf_hospitalization_rr": 1.0,
                "bp_systolic_change_mmhg": 0,
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "very_rare",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0.0,
                "mechanism": "weight-neutral incretin enhancement",
            },
        },

        "contraindications": [
            {"condition": "type_1_diabetes", "severity": "absolute"},
            {"condition": "dka_history", "severity": "absolute"},
            {"condition": "pancreatitis_history", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "nasopharyngitis", "frequency": "common", "percent": 6.0},
            {"effect": "headache", "frequency": "common", "percent": 5.0},
            {"effect": "acute_pancreatitis", "frequency": "rare", "percent": 0.1},
            {"effect": "arthralgia", "frequency": "uncommon", "percent": 1.0},
            {"effect": "hypersensitivity_reaction", "frequency": "rare", "percent": 0.1},
        ],

        "monitoring": [
            {"test": "renal_function", "timing": "before_initiation_and_periodically"},
            {"test": "amylase_lipase", "timing": "if_pancreatitis_symptoms"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "sulfonylurea",
                "severity": "moderate",
                "effect": "Increased hypoglycemia risk",
                "recommendation": "Consider reducing sulfonylurea dose",
            },
            {
                "interacting_drug_class": "insulin",
                "severity": "moderate",
                "effect": "Increased hypoglycemia risk",
                "recommendation": "Consider reducing insulin dose",
            },
        ],

        "dosing": {
            "starting_dose": "100 mg once daily",
            "max_dose": "100 mg once daily",
            "renal_adjustment": "50 mg daily if eGFR 30-45; 25 mg daily if eGFR <30",
            "hepatic_adjustment": "No adjustment for mild-moderate impairment",
        },

        "cost_tier": "$$$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": False,
            "food_requirements": "none",
        },
    },

    "linagliptin": {
        "name": "linagliptin",
        "brand_names": ["Tradjenta"],
        "rxcui": "1043563",
        "drug_class": "DPP-4 inhibitor",
        "atc_code": "A10BH05",
        "mechanism": (
            "Inhibits DPP-4, prolonging incretin hormone action. "
            "Unique among DPP-4 inhibitors in being eliminated primarily "
            "via the bile, requiring no renal dose adjustment."
        ),
        "indications": ["type_2_diabetes"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": -0.6,
                "hba1c_range": [-0.4, -0.8],
                "weight_change_kg": 0.0,
                "weight_range_kg": [-0.5, 0.5],
                "hypoglycemia_risk": "low",
                "mechanism_of_glycemic_effect": "incretin enhancement, glucose-dependent",
                "evidence": "CARMELINA trial (PMID 30193283)",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_slope_modifier": 1.0,
                "albuminuria_reduction_percent": -6,
                "renoprotective": False,
                "renal_safety_note": "No dose adjustment required at any eGFR",
            },
            "cardiovascular": {
                "mace_relative_risk": 1.02,
                "mace_evidence": "CARMELINA - cardiovascular neutral",
                "hf_hospitalization_rr": 0.90,
                "bp_systolic_change_mmhg": 0,
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "very_rare",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0.0,
                "mechanism": "weight-neutral incretin enhancement",
            },
        },

        "contraindications": [
            {"condition": "type_1_diabetes", "severity": "absolute"},
            {"condition": "dka_history", "severity": "absolute"},
            {"condition": "pancreatitis_history", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "nasopharyngitis", "frequency": "common", "percent": 5.7},
            {"effect": "cough", "frequency": "uncommon", "percent": 1.7},
            {"effect": "acute_pancreatitis", "frequency": "rare", "percent": 0.1},
            {"effect": "hypersensitivity_reaction", "frequency": "rare", "percent": 0.1},
        ],

        "monitoring": [
            {"test": "amylase_lipase", "timing": "if_pancreatitis_symptoms"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "sulfonylurea",
                "severity": "moderate",
                "effect": "Increased hypoglycemia risk",
                "recommendation": "Consider reducing sulfonylurea dose",
            },
            {
                "interacting_drug_class": "rifampin",
                "severity": "moderate",
                "effect": "Strong CYP3A4/P-gp inducer reduces linagliptin exposure",
                "recommendation": "Consider alternative DPP-4 inhibitor",
            },
        ],

        "dosing": {
            "starting_dose": "5 mg once daily",
            "max_dose": "5 mg once daily",
            "renal_adjustment": "No adjustment required at any eGFR (including dialysis)",
            "hepatic_adjustment": "No adjustment needed",
        },

        "cost_tier": "$$$$",
        "generic_available": False,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": False,
            "food_requirements": "none",
        },
    },

    "amlodipine": {
        "name": "amlodipine",
        "brand_names": ["Norvasc"],
        "rxcui": "197361",
        "drug_class": "calcium channel blocker",
        "atc_code": "C08CA01",
        "mechanism": (
            "Dihydropyridine calcium channel blocker. Inhibits L-type "
            "calcium channels in vascular smooth muscle, producing "
            "peripheral arterial vasodilation and reduced systemic "
            "vascular resistance."
        ),
        "indications": ["hypertension", "stable_angina", "vasospastic_angina"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.0,
                "hypoglycemia_risk": "none",
                "evidence": "ALLHAT (PMID 12479763) - metabolic neutral",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_slope_modifier": 1.0,
                "albuminuria_reduction_percent": -10,
                "renoprotective": False,
                "renal_safety_note": "May reduce proteinuria modestly",
            },
            "cardiovascular": {
                "mace_relative_risk": 0.97,
                "mace_evidence": "ALLHAT - similar to other antihypertensives",
                "bp_systolic_change_mmhg": -12,
                "bp_diastolic_change_mmhg": -7,
                "stroke_risk_reduction": "yes - in hypertensive patients",
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "rare",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0.0,
            },
        },

        "contraindications": [
            {"condition": "severe_aortic_stenosis", "severity": "absolute"},
            {"condition": "cardiogenic_shock", "severity": "absolute"},
            {"condition": "severe_hypotension", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "peripheral_edema", "frequency": "common", "percent": 10.8},
            {"effect": "headache", "frequency": "common", "percent": 7.3},
            {"effect": "flushing", "frequency": "common", "percent": 4.5},
            {"effect": "fatigue", "frequency": "uncommon", "percent": 4.5},
            {"effect": "gingival_hyperplasia", "frequency": "rare", "percent": 0.3},
        ],

        "monitoring": [
            {"test": "blood_pressure", "timing": "at_each_visit"},
            {"test": "peripheral_edema", "timing": "at_each_visit"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "simvastatin",
                "severity": "moderate",
                "effect": "Increased simvastatin exposure, myopathy risk",
                "recommendation": "Limit simvastatin to 20 mg daily with amlodipine",
            },
            {
                "interacting_drug_class": "cyclosporine",
                "severity": "moderate",
                "effect": "Increased amlodipine exposure",
                "recommendation": "Monitor for hypotension and edema",
            },
            {
                "interacting_drug_class": "cyp3a4_inhibitors",
                "severity": "moderate",
                "effect": "Increased amlodipine plasma levels",
                "recommendation": "Monitor BP closely, consider dose reduction",
            },
        ],

        "dosing": {
            "starting_dose": "2.5-5 mg once daily",
            "max_dose": "10 mg once daily",
            "renal_adjustment": "No adjustment needed",
            "hepatic_adjustment": "Start with 2.5 mg daily in hepatic impairment",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": True,
            "food_requirements": "none",
        },
    },

    "diltiazem": {
        "name": "diltiazem",
        "brand_names": ["Cardizem", "Tiazac"],
        "rxcui": "197468",
        "drug_class": "calcium channel blocker",
        "atc_code": "C08DB01",
        "mechanism": (
            "Non-dihydropyridine calcium channel blocker. Inhibits L-type "
            "calcium channels in vascular smooth muscle and cardiac tissue, "
            "producing vasodilation, negative chronotropy, and slowed AV "
            "nodal conduction."
        ),
        "indications": ["hypertension", "stable_angina", "atrial_fibrillation_rate_control"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.0,
                "hypoglycemia_risk": "none",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_slope_modifier": 1.0,
                "albuminuria_reduction_percent": -15,
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 1.0,
                "bp_systolic_change_mmhg": -10,
                "bp_diastolic_change_mmhg": -7,
                "heart_rate_change_bpm": -8,
                "av_node_effect": "slowed_conduction",
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "uncommon",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0.0,
            },
        },

        "contraindications": [
            {"condition": "severe_left_ventricular_dysfunction", "severity": "absolute"},
            {"condition": "second_or_third_degree_heart_block", "severity": "absolute"},
            {"condition": "sick_sinus_syndrome", "severity": "absolute"},
            {"condition": "severe_hypotension", "severity": "absolute"},
            {"condition": "wpw_with_atrial_fibrillation", "severity": "absolute"},
        ],

        "side_effects": [
            {"effect": "peripheral_edema", "frequency": "common", "percent": 6.0},
            {"effect": "headache", "frequency": "common", "percent": 5.0},
            {"effect": "bradycardia", "frequency": "uncommon", "percent": 2.0},
            {"effect": "constipation", "frequency": "common", "percent": 4.0},
            {"effect": "av_block", "frequency": "rare", "percent": 0.6},
        ],

        "monitoring": [
            {"test": "blood_pressure", "timing": "at_each_visit"},
            {"test": "heart_rate", "timing": "at_each_visit"},
            {"test": "ecg", "timing": "if_av_block_suspected"},
            {"test": "lft", "timing": "periodically"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "beta_blocker",
                "severity": "major",
                "effect": "Additive bradycardia and AV block; risk of severe bradycardia",
                "recommendation": "Avoid combination if possible; monitor closely if necessary",
            },
            {
                "interacting_drug_class": "statin",
                "severity": "moderate",
                "effect": "Increased statin exposure (CYP3A4 inhibition)",
                "recommendation": "Limit simvastatin to 10 mg, lovastatin to 20 mg",
            },
            {
                "interacting_drug_class": "digoxin",
                "severity": "moderate",
                "effect": "Increased digoxin levels",
                "recommendation": "Monitor digoxin level",
            },
        ],

        "dosing": {
            "starting_dose": "120-180 mg once daily (extended-release)",
            "max_dose": "480 mg once daily",
            "renal_adjustment": "Use cautiously in severe renal impairment",
            "hepatic_adjustment": "Reduce dose by 50% in hepatic impairment",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_or_twice_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": True,
            "food_requirements": "none",
        },
    },

    "carvedilol": {
        "name": "carvedilol",
        "brand_names": ["Coreg"],
        "rxcui": "200031",
        "drug_class": "non-selective beta blocker with alpha-1 blockade",
        "atc_code": "C07AG02",
        "mechanism": (
            "Non-selective beta-1 and beta-2 receptor blocker with additional "
            "alpha-1 receptor blockade. Reduces heart rate, contractility, "
            "and systemic vascular resistance. Antioxidant properties."
        ),
        "indications": ["heart_failure_reduced_ef", "hypertension", "post_mi"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.0,
                "hypoglycemia_risk": "low",
                "metabolic_note": "More glucose-neutral than other non-selective beta blockers",
                "evidence": "GEMINI trial",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_slope_modifier": 1.0,
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.65,
                "mace_evidence": "COPERNICUS, US Carvedilol HF trials",
                "hf_mortality_rr": 0.65,
                "bp_systolic_change_mmhg": -8,
                "heart_rate_change_bpm": -8,
                "lvef_improvement": "yes",
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "rare",
            },
            "weight": {
                "direction": "slight_gain",
                "expected_kg": 0.5,
            },
        },

        "contraindications": [
            {"condition": "decompensated_heart_failure", "severity": "absolute"},
            {"condition": "severe_bradycardia", "severity": "absolute"},
            {"condition": "second_or_third_degree_heart_block", "severity": "absolute"},
            {"condition": "severe_hepatic_impairment", "severity": "absolute"},
            {"condition": "severe_asthma", "severity": "absolute"},
            {"condition": "cardiogenic_shock", "severity": "absolute"},
        ],

        "side_effects": [
            {"effect": "dizziness", "frequency": "common", "percent": 24.0},
            {"effect": "fatigue", "frequency": "common", "percent": 24.0},
            {"effect": "hypotension", "frequency": "common", "percent": 14.0},
            {"effect": "bradycardia", "frequency": "common", "percent": 10.0},
            {"effect": "weight_gain", "frequency": "uncommon", "percent": 5.0},
            {"effect": "bronchospasm", "frequency": "rare", "percent": 0.2},
        ],

        "monitoring": [
            {"test": "blood_pressure", "timing": "at_each_visit"},
            {"test": "heart_rate", "timing": "at_each_visit"},
            {"test": "weight", "timing": "weekly_during_titration"},
            {"test": "renal_function", "timing": "before_initiation"},
            {"test": "lft", "timing": "periodically"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "calcium_channel_blocker_non_dhp",
                "severity": "major",
                "effect": "Additive bradycardia and AV block",
                "recommendation": "Avoid combination if possible",
            },
            {
                "interacting_drug_class": "insulin",
                "severity": "moderate",
                "effect": "Masks hypoglycemia symptoms",
                "recommendation": "Counsel patient on alternative hypoglycemia recognition",
            },
            {
                "interacting_drug_class": "amiodarone",
                "severity": "moderate",
                "effect": "Increased carvedilol exposure",
                "recommendation": "Monitor for bradycardia",
            },
        ],

        "dosing": {
            "starting_dose": "3.125 mg twice daily (HF), titrate every 2 weeks",
            "max_dose": "25 mg twice daily (50 mg twice daily if >85 kg)",
            "renal_adjustment": "No adjustment needed",
            "hepatic_adjustment": "Contraindicated in severe hepatic impairment",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "twice_daily",

        "adherence_factors": {
            "pill_burden": "moderate",
            "injection": False,
            "titration_required": True,
            "food_requirements": "take_with_food_to_slow_absorption",
        },
    },

    "bisoprolol": {
        "name": "bisoprolol",
        "brand_names": ["Zebeta"],
        "rxcui": "200030",
        "drug_class": "beta-1 selective blocker",
        "atc_code": "C07AB07",
        "mechanism": (
            "Highly selective beta-1 adrenergic receptor blocker. Reduces "
            "heart rate, contractility, and renin release with minimal "
            "beta-2 activity at therapeutic doses."
        ),
        "indications": ["heart_failure_reduced_ef", "hypertension", "post_mi"],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.0,
                "hypoglycemia_risk": "low",
                "metabolic_note": "Beta-1 selectivity preserves glucose homeostasis",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_slope_modifier": 1.0,
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.66,
                "mace_evidence": "CIBIS-II trial (PMID 9988708)",
                "hf_mortality_rr": 0.66,
                "bp_systolic_change_mmhg": -8,
                "heart_rate_change_bpm": -10,
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "rare",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0.0,
            },
        },

        "contraindications": [
            {"condition": "decompensated_heart_failure", "severity": "absolute"},
            {"condition": "severe_bradycardia", "severity": "absolute"},
            {"condition": "second_or_third_degree_heart_block", "severity": "absolute"},
            {"condition": "cardiogenic_shock", "severity": "absolute"},
            {"condition": "severe_asthma", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "fatigue", "frequency": "common", "percent": 8.0},
            {"effect": "bradycardia", "frequency": "common", "percent": 8.0},
            {"effect": "dizziness", "frequency": "common", "percent": 7.0},
            {"effect": "hypotension", "frequency": "uncommon", "percent": 3.0},
            {"effect": "cold_extremities", "frequency": "uncommon", "percent": 2.0},
        ],

        "monitoring": [
            {"test": "blood_pressure", "timing": "at_each_visit"},
            {"test": "heart_rate", "timing": "at_each_visit"},
            {"test": "weight", "timing": "weekly_during_titration_for_HF"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "calcium_channel_blocker_non_dhp",
                "severity": "major",
                "effect": "Additive bradycardia and AV block",
                "recommendation": "Avoid combination if possible",
            },
            {
                "interacting_drug_class": "insulin",
                "severity": "moderate",
                "effect": "Masks hypoglycemia symptoms (less than non-selective)",
                "recommendation": "Counsel patient",
            },
        ],

        "dosing": {
            "starting_dose": "1.25 mg once daily (HF), titrate every 2 weeks",
            "max_dose": "10 mg once daily",
            "renal_adjustment": "Reduce dose if eGFR <40",
            "hepatic_adjustment": "Reduce dose in severe hepatic impairment",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": True,
            "food_requirements": "none",
        },
    },

    "apixaban": {
        "name": "apixaban",
        "brand_names": ["Eliquis"],
        "rxcui": "1364430",
        "drug_class": "direct oral anticoagulant",
        "atc_code": "B01AF02",
        "mechanism": (
            "Direct, reversible inhibitor of activated factor X (Xa). "
            "Inhibits both free and prothrombinase-bound factor Xa, "
            "preventing thrombin generation and clot formation."
        ),
        "indications": [
            "atrial_fibrillation",
            "venous_thromboembolism_treatment",
            "venous_thromboembolism_prophylaxis",
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.0,
                "hypoglycemia_risk": "none",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_slope_modifier": 1.0,
                "renal_safety_note": "Preferred DOAC in moderate CKD; usable down to eGFR 15",
            },
            "cardiovascular": {
                "stroke_risk_reduction_in_afib": "yes",
                "stroke_rr_vs_warfarin": 0.79,
                "major_bleeding_rr_vs_warfarin": 0.69,
                "evidence": "ARISTOTLE (NEJM 2011, PMID 21870978)",
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "rare",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0.0,
            },
        },

        "contraindications": [
            {"condition": "active_pathological_bleeding", "severity": "absolute"},
            {"condition": "severe_hepatic_impairment", "severity": "absolute"},
            {"condition": "mechanical_heart_valve", "severity": "absolute"},
            {"condition": "antiphospholipid_syndrome_triple_positive", "severity": "absolute"},
            {"condition": "egfr_below_15", "severity": "relative"},
            {"condition": "pregnancy", "severity": "absolute"},
        ],

        "side_effects": [
            {"effect": "major_bleeding", "frequency": "uncommon", "percent": 2.1},
            {"effect": "minor_bleeding", "frequency": "common", "percent": 12.0},
            {"effect": "epistaxis", "frequency": "common", "percent": 4.0},
            {"effect": "hematuria", "frequency": "uncommon", "percent": 2.0},
            {"effect": "intracranial_hemorrhage", "frequency": "rare", "percent": 0.3},
        ],

        "monitoring": [
            {"test": "renal_function", "timing": "at_least_annually"},
            {"test": "hemoglobin", "timing": "annually_or_if_bleeding"},
            {"test": "lft", "timing": "if_baseline_abnormal"},
            {"test": "bleeding_assessment", "timing": "at_each_visit"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "antiplatelet",
                "severity": "major",
                "effect": "Markedly increased bleeding risk",
                "recommendation": "Avoid combination unless clear indication; minimize duration",
            },
            {
                "interacting_drug_class": "nsaid",
                "severity": "major",
                "effect": "Increased bleeding risk and renal injury",
                "recommendation": "Avoid; use acetaminophen instead",
            },
            {
                "interacting_drug_class": "ssri",
                "severity": "moderate",
                "effect": "Increased bleeding risk",
                "recommendation": "Use with caution; counsel on bleeding signs",
            },
            {
                "interacting_drug_class": "strong_cyp3a4_inducers",
                "severity": "major",
                "effect": "Reduced apixaban exposure (rifampin, phenytoin, carbamazepine)",
                "recommendation": "Avoid combination",
            },
        ],

        "dosing": {
            "starting_dose": "5 mg twice daily (afib); 10 mg BID x7d then 5 mg BID (VTE)",
            "max_dose": "10 mg twice daily (acute VTE)",
            "renal_adjustment": "2.5 mg BID if 2 of: age >=80, weight <=60kg, Cr >=1.5",
            "hepatic_adjustment": "Avoid in severe hepatic impairment",
        },

        "cost_tier": "$$$$",
        "generic_available": False,
        "route": "oral",
        "frequency": "twice_daily",

        "adherence_factors": {
            "pill_burden": "moderate",
            "injection": False,
            "titration_required": False,
            "food_requirements": "none",
        },
    },

    "warfarin": {
        "name": "warfarin",
        "brand_names": ["Coumadin", "Jantoven"],
        "rxcui": "855332",
        "drug_class": "vitamin K antagonist",
        "atc_code": "B01AA03",
        "mechanism": (
            "Inhibits vitamin K epoxide reductase (VKORC1), preventing "
            "regeneration of reduced vitamin K. Reduces synthesis of "
            "vitamin K-dependent clotting factors II, VII, IX, X, and "
            "proteins C and S."
        ),
        "indications": [
            "atrial_fibrillation",
            "venous_thromboembolism",
            "mechanical_heart_valve",
            "antiphospholipid_syndrome",
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.0,
                "hypoglycemia_risk": "none",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_slope_modifier": 1.0,
                "renal_safety_note": "Acceptable at any eGFR; preferred over DOACs at eGFR <15",
            },
            "cardiovascular": {
                "stroke_risk_reduction_in_afib": "yes",
                "evidence": "Reference standard for anticoagulation",
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "rare",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0.0,
            },
        },

        "contraindications": [
            {"condition": "active_pathological_bleeding", "severity": "absolute"},
            {"condition": "pregnancy", "severity": "absolute"},
            {"condition": "severe_thrombocytopenia", "severity": "absolute"},
            {"condition": "recent_surgery_high_bleeding_risk", "severity": "relative"},
            {"condition": "uncontrolled_hypertension", "severity": "relative"},
            {"condition": "alcoholism", "severity": "relative"},
        ],

        "side_effects": [
            {"effect": "major_bleeding", "frequency": "common", "percent": 3.5},
            {"effect": "minor_bleeding", "frequency": "common", "percent": 15.0},
            {"effect": "intracranial_hemorrhage", "frequency": "rare", "percent": 0.8},
            {"effect": "skin_necrosis", "frequency": "very_rare", "percent": 0.01},
            {"effect": "purple_toe_syndrome", "frequency": "very_rare", "percent": 0.01},
        ],

        "monitoring": [
            {"test": "inr", "timing": "weekly_initially_then_monthly_when_stable"},
            {"test": "cbc", "timing": "periodically"},
            {"test": "bleeding_assessment", "timing": "at_each_visit"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "antibiotics",
                "severity": "major",
                "effect": "Increased INR via gut flora disruption or CYP inhibition",
                "recommendation": "Check INR within 3-5 days of starting any antibiotic",
            },
            {
                "interacting_drug_class": "amiodarone",
                "severity": "major",
                "effect": "Markedly increased INR",
                "recommendation": "Reduce warfarin dose by 30-50%, monitor INR closely",
            },
            {
                "interacting_drug_class": "nsaid",
                "severity": "major",
                "effect": "Increased bleeding risk (no INR change)",
                "recommendation": "Avoid; use acetaminophen instead",
            },
            {
                "interacting_drug_class": "antiplatelet",
                "severity": "major",
                "effect": "Markedly increased bleeding risk",
                "recommendation": "Avoid combination unless clear indication",
            },
        ],

        "dosing": {
            "starting_dose": "5 mg daily (or 2.5 mg if elderly/frail)",
            "max_dose": "Titrated to INR 2-3 (or 2.5-3.5 for mechanical valves)",
            "renal_adjustment": "No adjustment by eGFR; titrate to INR",
            "hepatic_adjustment": "Reduce dose in hepatic impairment",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": True,
            "food_requirements": "consistent_vitamin_k_intake",
            "monitoring_burden": "high - frequent INR checks",
        },
    },

    "rivaroxaban": {
        "name": "rivaroxaban",
        "brand_names": ["Xarelto"],
        "rxcui": "1114195",
        "drug_class": "direct oral anticoagulant",
        "atc_code": "B01AF01",
        "mechanism": (
            "Direct, selective inhibitor of activated factor X (Xa). "
            "Once-daily dosing for most indications."
        ),
        "indications": [
            "atrial_fibrillation",
            "venous_thromboembolism",
            "stable_cad_pad_secondary_prevention",
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.0,
                "hypoglycemia_risk": "none",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_slope_modifier": 1.0,
                "renal_safety_note": "Avoid if eGFR <15; reduce dose if eGFR 15-50",
            },
            "cardiovascular": {
                "stroke_risk_reduction_in_afib": "yes",
                "stroke_rr_vs_warfarin": 0.88,
                "major_bleeding_rr_vs_warfarin": 1.04,
                "evidence": "ROCKET-AF (NEJM 2011, PMID 21830957)",
            },
            "hepatic": {
                "alt_effect": "neutral",
                "hepatotoxicity_risk": "uncommon",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0.0,
            },
        },

        "contraindications": [
            {"condition": "active_pathological_bleeding", "severity": "absolute"},
            {"condition": "severe_hepatic_impairment", "severity": "absolute"},
            {"condition": "mechanical_heart_valve", "severity": "absolute"},
            {"condition": "antiphospholipid_syndrome_triple_positive", "severity": "absolute"},
            {"condition": "egfr_below_15", "severity": "absolute"},
            {"condition": "pregnancy", "severity": "absolute"},
        ],

        "side_effects": [
            {"effect": "major_bleeding", "frequency": "uncommon", "percent": 3.6},
            {"effect": "minor_bleeding", "frequency": "common", "percent": 14.0},
            {"effect": "gi_bleeding", "frequency": "uncommon", "percent": 3.2},
            {"effect": "intracranial_hemorrhage", "frequency": "rare", "percent": 0.5},
        ],

        "monitoring": [
            {"test": "renal_function", "timing": "at_least_annually"},
            {"test": "hemoglobin", "timing": "annually_or_if_bleeding"},
            {"test": "lft", "timing": "if_baseline_abnormal"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "antiplatelet",
                "severity": "major",
                "effect": "Markedly increased bleeding risk",
                "recommendation": "Avoid combination unless clear indication",
            },
            {
                "interacting_drug_class": "nsaid",
                "severity": "major",
                "effect": "Increased bleeding risk",
                "recommendation": "Avoid; use acetaminophen",
            },
            {
                "interacting_drug_class": "strong_cyp3a4_inhibitors",
                "severity": "major",
                "effect": "Increased rivaroxaban exposure (ketoconazole, ritonavir)",
                "recommendation": "Avoid combination",
            },
        ],

        "dosing": {
            "starting_dose": "20 mg once daily with food (afib); 15 mg BID x21d then 20 mg daily (VTE)",
            "max_dose": "20 mg once daily (most indications)",
            "renal_adjustment": "15 mg daily if eGFR 15-50 (afib); avoid if eGFR <15",
            "hepatic_adjustment": "Avoid in moderate-severe hepatic impairment",
        },

        "cost_tier": "$$$$",
        "generic_available": False,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": False,
            "food_requirements": "take_with_evening_meal",
        },
    },

    "aspirin_low_dose": {
        "name": "aspirin_low_dose",
        "brand_names": ["Bayer Aspirin", "Ecotrin"],
        "rxcui": "1191",
        "drug_class": "antiplatelet",
        "atc_code": "B01AC06",
        "mechanism": (
            "Irreversibly inhibits cyclooxygenase-1 (COX-1) in platelets, "
            "preventing thromboxane A2 synthesis and reducing platelet "
            "aggregation. Effect persists for the platelet lifespan (7-10 days)."
        ),
        "indications": [
            "secondary_cv_prevention",
            "post_mi",
            "post_stroke_ischemic",
            "post_pci",
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.0,
                "hypoglycemia_risk": "none",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_slope_modifier": 1.0,
                "renal_safety_note": "Avoid in late-stage CKD due to bleeding risk",
            },
            "cardiovascular": {
                "mace_relative_risk_secondary_prevention": 0.78,
                "stroke_risk_reduction_secondary": 0.78,
                "primary_prevention_benefit": "marginal_or_negative",
                "evidence": "Antithrombotic Trialists Collaboration (BMJ 2002)",
            },
            "hepatic": {
                "alt_effect": "rare_elevation",
                "hepatotoxicity_risk": "rare",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0.0,
            },
        },

        "contraindications": [
            {"condition": "active_gi_bleeding", "severity": "absolute"},
            {"condition": "aspirin_allergy", "severity": "absolute"},
            {"condition": "hemophilia", "severity": "absolute"},
            {"condition": "children_with_viral_illness", "severity": "absolute"},
            {"condition": "severe_thrombocytopenia", "severity": "absolute"},
            {"condition": "recent_intracranial_hemorrhage", "severity": "absolute"},
        ],

        "side_effects": [
            {"effect": "gi_bleeding", "frequency": "uncommon", "percent": 1.5},
            {"effect": "dyspepsia", "frequency": "common", "percent": 5.0},
            {"effect": "intracranial_hemorrhage", "frequency": "rare", "percent": 0.2},
            {"effect": "tinnitus", "frequency": "rare", "percent": 0.1},
            {"effect": "asthma_exacerbation", "frequency": "rare", "percent": 0.5},
        ],

        "monitoring": [
            {"test": "bleeding_assessment", "timing": "at_each_visit"},
            {"test": "hemoglobin", "timing": "if_bleeding_signs"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "anticoagulant",
                "severity": "major",
                "effect": "Markedly increased bleeding risk",
                "recommendation": "Avoid combination unless clear indication; minimize duration",
            },
            {
                "interacting_drug_class": "nsaid",
                "severity": "moderate",
                "effect": "Reduced cardioprotective effect of aspirin; increased GI bleeding",
                "recommendation": "Take aspirin 2 hours before NSAID; avoid chronic NSAIDs",
            },
            {
                "interacting_drug_class": "p2y12_inhibitor",
                "severity": "moderate",
                "effect": "Additive antiplatelet effect (intentional in DAPT)",
                "recommendation": "Use as DAPT only with clear indication and time-limited",
            },
        ],

        "dosing": {
            "starting_dose": "81 mg once daily",
            "max_dose": "81 mg once daily (cardioprotection)",
            "renal_adjustment": "Avoid in late CKD",
            "hepatic_adjustment": "Avoid in severe hepatic impairment",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "very_low",
            "injection": False,
            "titration_required": False,
            "food_requirements": "take_with_food_to_reduce_gi_irritation",
        },
    },

    "clopidogrel": {
        "name": "clopidogrel",
        "brand_names": ["Plavix"],
        "rxcui": "309362",
        "drug_class": "P2Y12 inhibitor",
        "atc_code": "B01AC04",
        "mechanism": (
            "Prodrug requiring CYP2C19 activation. Active metabolite "
            "irreversibly blocks the P2Y12 ADP receptor on platelets, "
            "preventing platelet aggregation."
        ),
        "indications": [
            "post_pci_dapt",
            "post_acs",
            "post_stroke_ischemic",
            "pad_symptomatic",
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.0,
                "hypoglycemia_risk": "none",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_slope_modifier": 1.0,
            },
            "cardiovascular": {
                "mace_relative_risk_post_acs": 0.80,
                "evidence": "CURE, CAPRIE trials",
                "dapt_benefit": "yes - reduced stent thrombosis",
            },
            "hepatic": {
                "alt_effect": "rare_elevation",
                "hepatotoxicity_risk": "rare",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0.0,
            },
        },

        "contraindications": [
            {"condition": "active_pathological_bleeding", "severity": "absolute"},
            {"condition": "severe_hepatic_impairment", "severity": "absolute"},
            {"condition": "recent_intracranial_hemorrhage", "severity": "absolute"},
        ],

        "side_effects": [
            {"effect": "major_bleeding", "frequency": "uncommon", "percent": 3.7},
            {"effect": "minor_bleeding", "frequency": "common", "percent": 9.3},
            {"effect": "bruising", "frequency": "common", "percent": 5.0},
            {"effect": "ttp", "frequency": "very_rare", "percent": 0.0001},
            {"effect": "rash", "frequency": "uncommon", "percent": 4.0},
        ],

        "monitoring": [
            {"test": "bleeding_assessment", "timing": "at_each_visit"},
            {"test": "cbc", "timing": "if_bleeding_or_bruising"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "ppi",
                "severity": "moderate",
                "effect": "Omeprazole and esomeprazole reduce clopidogrel activation (CYP2C19)",
                "recommendation": "Use pantoprazole or H2 blocker if PPI needed",
            },
            {
                "interacting_drug_class": "anticoagulant",
                "severity": "major",
                "effect": "Markedly increased bleeding risk",
                "recommendation": "Avoid unless triple therapy clearly indicated",
            },
            {
                "interacting_drug_class": "nsaid",
                "severity": "major",
                "effect": "Increased GI bleeding risk",
                "recommendation": "Avoid; use acetaminophen",
            },
            {
                "interacting_drug_class": "ssri",
                "severity": "moderate",
                "effect": "Increased bleeding risk",
                "recommendation": "Use with caution; counsel on bleeding",
            },
        ],

        "dosing": {
            "starting_dose": "75 mg once daily (or 300-600 mg loading dose for ACS/PCI)",
            "max_dose": "75 mg once daily (maintenance)",
            "renal_adjustment": "No adjustment needed",
            "hepatic_adjustment": "Avoid in severe hepatic impairment",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "low",
            "injection": False,
            "titration_required": False,
            "food_requirements": "none",
        },
    },

    "ezetimibe": {
        "name": "ezetimibe",
        "brand_names": ["Zetia"],
        "rxcui": "341248",
        "drug_class": "cholesterol absorption inhibitor",
        "atc_code": "C10AX09",
        "mechanism": (
            "Inhibits the Niemann-Pick C1-Like 1 (NPC1L1) transporter at "
            "the brush border of the small intestine, reducing absorption "
            "of dietary and biliary cholesterol."
        ),
        "indications": [
            "primary_hypercholesterolemia",
            "ascvd_secondary_prevention_add_on",
            "statin_intolerance",
            "homozygous_familial_hypercholesterolemia",
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.0,
                "hypoglycemia_risk": "none",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_slope_modifier": 1.0,
                "renoprotective": False,
            },
            "cardiovascular": {
                "ldl_reduction_percent": -20,
                "ldl_reduction_with_statin_percent": -25,
                "mace_relative_risk": 0.94,
                "mace_evidence": "IMPROVE-IT (NEJM 2015, PMID 26039521)",
                "bp_systolic_change_mmhg": 0,
            },
            "hepatic": {
                "alt_effect": "minor_elevation",
                "hepatotoxicity_risk": "rare",
                "lft_monitoring_with_statin": "yes",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0.0,
            },
        },

        "contraindications": [
            {"condition": "active_liver_disease", "severity": "absolute"},
            {"condition": "unexplained_persistent_elevations_of_alt", "severity": "absolute"},
            {"condition": "pregnancy_with_statin", "severity": "absolute"},
        ],

        "side_effects": [
            {"effect": "myalgia", "frequency": "uncommon", "percent": 4.0},
            {"effect": "diarrhea", "frequency": "uncommon", "percent": 4.0},
            {"effect": "fatigue", "frequency": "uncommon", "percent": 2.0},
            {"effect": "elevated_lft", "frequency": "uncommon", "percent": 1.7},
            {"effect": "rhabdomyolysis", "frequency": "very_rare", "percent": 0.01},
        ],

        "monitoring": [
            {"test": "lipid_panel", "timing": "4_to_12_weeks_after_initiation"},
            {"test": "lft", "timing": "before_initiation_and_if_symptoms"},
            {"test": "ck", "timing": "if_muscle_symptoms"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "statin",
                "severity": "minor",
                "effect": "Additive LDL lowering (intentional combination)",
                "recommendation": "Effective combination; monitor LFT and muscle symptoms",
            },
            {
                "interacting_drug_class": "fibrate",
                "severity": "moderate",
                "effect": "Increased risk of cholelithiasis",
                "recommendation": "Avoid combination if possible",
            },
            {
                "interacting_drug_class": "cyclosporine",
                "severity": "moderate",
                "effect": "Increased ezetimibe and cyclosporine exposure",
                "recommendation": "Monitor cyclosporine levels",
            },
            {
                "interacting_drug_class": "bile_acid_sequestrant",
                "severity": "moderate",
                "effect": "Reduced ezetimibe absorption",
                "recommendation": "Take ezetimibe 2 hours before or 4 hours after",
            },
        ],

        "dosing": {
            "starting_dose": "10 mg once daily",
            "max_dose": "10 mg once daily",
            "renal_adjustment": "No adjustment needed",
            "hepatic_adjustment": "Avoid in moderate-severe hepatic impairment",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "very_low",
            "injection": False,
            "titration_required": False,
            "food_requirements": "none",
        },
    },

    "omeprazole": {
        "name": "omeprazole",
        "brand_names": ["Prilosec", "Losec"],
        "rxcui": "7646",
        "drug_class": "proton pump inhibitor",
        "atc_code": "A02BC01",
        "mechanism": (
            "Irreversibly inhibits the H+/K+ ATPase (proton pump) on "
            "gastric parietal cells, reducing gastric acid secretion. "
            "Activated in the acidic environment of parietal cell canaliculi."
        ),
        "indications": [
            "gerd",
            "peptic_ulcer_disease",
            "h_pylori_eradication_combination",
            "stress_ulcer_prophylaxis",
            "zollinger_ellison_syndrome",
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.0,
                "hypoglycemia_risk": "none",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_slope_modifier": 1.0,
                "renal_safety_note": "Long-term use associated with acute interstitial nephritis and possible CKD progression",
            },
            "cardiovascular": {
                "mace_relative_risk": 1.0,
                "bp_systolic_change_mmhg": 0,
            },
            "hepatic": {
                "alt_effect": "rare_elevation",
                "hepatotoxicity_risk": "very_rare",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0.0,
            },
        },

        "contraindications": [
            {"condition": "hypersensitivity_to_ppi", "severity": "absolute"},
            {"condition": "concurrent_rilpivirine", "severity": "absolute"},
        ],

        "side_effects": [
            {"effect": "headache", "frequency": "common", "percent": 7.0},
            {"effect": "diarrhea", "frequency": "common", "percent": 4.0},
            {"effect": "abdominal_pain", "frequency": "common", "percent": 5.0},
            {"effect": "vitamin_b12_deficiency", "frequency": "uncommon_long_term", "percent": 3.0},
            {"effect": "magnesium_deficiency", "frequency": "uncommon_long_term", "percent": 2.0},
            {"effect": "c_difficile_infection", "frequency": "uncommon", "percent": 1.5},
            {"effect": "fracture_risk_long_term", "frequency": "uncommon", "percent": 2.0},
            {"effect": "acute_interstitial_nephritis", "frequency": "rare", "percent": 0.1},
        ],

        "monitoring": [
            {"test": "magnesium", "timing": "annually_if_long_term_use"},
            {"test": "vitamin_b12", "timing": "annually_if_long_term_use"},
            {"test": "renal_function", "timing": "if_symptoms_of_ain"},
            {"test": "indication_review", "timing": "every_6_to_12_months"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "clopidogrel",
                "severity": "moderate",
                "effect": "Reduces clopidogrel activation via CYP2C19 inhibition",
                "recommendation": "Use pantoprazole or H2 blocker instead",
            },
            {
                "interacting_drug_class": "methotrexate",
                "severity": "moderate",
                "effect": "Increased methotrexate toxicity",
                "recommendation": "Hold PPI around high-dose methotrexate",
            },
            {
                "interacting_drug_class": "warfarin",
                "severity": "moderate",
                "effect": "May increase INR",
                "recommendation": "Monitor INR after initiation",
            },
            {
                "interacting_drug_class": "atazanavir",
                "severity": "major",
                "effect": "Markedly reduced atazanavir absorption",
                "recommendation": "Avoid combination",
            },
        ],

        "dosing": {
            "starting_dose": "20 mg once daily before breakfast",
            "max_dose": "40 mg twice daily (severe disease)",
            "renal_adjustment": "No adjustment needed",
            "hepatic_adjustment": "Consider lower dose in severe hepatic impairment",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "once_daily",

        "adherence_factors": {
            "pill_burden": "very_low",
            "injection": False,
            "titration_required": False,
            "food_requirements": "take_30_to_60_min_before_meal",
        },
    },

    "hydralazine": {
        "name": "hydralazine",
        "brand_names": ["Apresoline"],
        "rxcui": "5470",
        "drug_class": "direct vasodilator",
        "atc_code": "C02DB02",
        "mechanism": (
            "Direct arteriolar vasodilator. Acts via stimulation of "
            "guanylyl cyclase and reduction of intracellular calcium "
            "in vascular smooth muscle, primarily affecting arterioles."
        ),
        "indications": [
            "resistant_hypertension",
            "heart_failure_hfref_african_american",
            "hypertension_in_pregnancy",
        ],

        "effects": {
            "metabolic": {
                "hba1c_reduction_percent": 0.0,
                "hypoglycemia_risk": "none",
            },
            "renal": {
                "egfr_acute_effect": 0,
                "egfr_slope_modifier": 1.0,
                "renoprotective": False,
            },
            "cardiovascular": {
                "mace_relative_risk": 0.57,
                "mace_evidence": "A-HeFT trial (NEJM 2004, PMID 15533851) - in combination with isosorbide dinitrate, African American HFrEF patients",
                "bp_systolic_change_mmhg": -10,
                "bp_diastolic_change_mmhg": -8,
                "afterload_reduction": "yes",
                "reflex_tachycardia": "yes",
            },
            "hepatic": {
                "alt_effect": "rare_elevation",
                "hepatotoxicity_risk": "uncommon",
            },
            "weight": {
                "direction": "neutral",
                "expected_kg": 0.0,
            },
        },

        "contraindications": [
            {"condition": "coronary_artery_disease_active", "severity": "relative"},
            {"condition": "mitral_valve_rheumatic_disease", "severity": "absolute"},
            {"condition": "dissecting_aortic_aneurysm", "severity": "absolute"},
            {"condition": "hydralazine_induced_lupus_history", "severity": "absolute"},
        ],

        "side_effects": [
            {"effect": "headache", "frequency": "common", "percent": 15.0},
            {"effect": "tachycardia", "frequency": "common", "percent": 12.0},
            {"effect": "palpitations", "frequency": "common", "percent": 10.0},
            {"effect": "flushing", "frequency": "common", "percent": 8.0},
            {"effect": "drug_induced_lupus", "frequency": "uncommon", "percent": 5.0},
            {"effect": "peripheral_neuropathy", "frequency": "rare", "percent": 0.5},
            {"effect": "hepatitis", "frequency": "rare", "percent": 0.1},
        ],

        "monitoring": [
            {"test": "blood_pressure", "timing": "at_each_visit"},
            {"test": "heart_rate", "timing": "at_each_visit"},
            {"test": "ana_titer", "timing": "if_lupus_symptoms"},
            {"test": "cbc", "timing": "periodically"},
        ],

        "drug_interactions": [
            {
                "interacting_drug_class": "nitrate",
                "severity": "minor",
                "effect": "Additive hypotension (intentional combination in HFrEF)",
                "recommendation": "Use as combination therapy in indicated populations",
            },
            {
                "interacting_drug_class": "mao_inhibitor",
                "severity": "moderate",
                "effect": "Increased hypotensive effect",
                "recommendation": "Use with caution; monitor BP",
            },
            {
                "interacting_drug_class": "beta_blocker",
                "severity": "minor",
                "effect": "Beta blocker offsets reflex tachycardia",
                "recommendation": "Often used together",
            },
        ],

        "dosing": {
            "starting_dose": "10-25 mg three or four times daily",
            "max_dose": "300 mg per day in divided doses",
            "renal_adjustment": "Extend dosing interval if eGFR <30",
            "hepatic_adjustment": "Use cautiously in hepatic impairment",
        },

        "cost_tier": "$",
        "generic_available": True,
        "route": "oral",
        "frequency": "three_or_four_times_daily",

        "adherence_factors": {
            "pill_burden": "high",
            "injection": False,
            "titration_required": True,
            "food_requirements": "none",
        },
    },                
}


# ===========================================================================
# DRUG-CLASS LOOKUP (helper index)
# ===========================================================================

# Maps drug class names to lists of generic names within that class.
# Built at module-load time.
_DRUGS_BY_CLASS: dict[str, list[str]] = {}
for _name, _data in _DRUGS.items():
    _cls = _data.get("drug_class", "unknown").lower()
    _DRUGS_BY_CLASS.setdefault(_cls, []).append(_name)


# Class-name aliases for fuzzier lookups (e.g., "sglt2i" -> "SGLT2 inhibitor")
_CLASS_ALIASES = {
    "sglt2i": "sglt2 inhibitor",
    "sglt2_inhibitor": "sglt2 inhibitor",
    "glp1": "glp-1 receptor agonist",
    "glp1_ra": "glp-1 receptor agonist",
    "glp_1_ra": "glp-1 receptor agonist",
    "ace_inhibitor": "ace inhibitor",
    "acei": "ace inhibitor",
    "arb": "angiotensin ii receptor blocker",
    "statin": "hmg-coa reductase inhibitor (statin)",
    "loop_diuretic": "loop diuretic",
    "thiazide": "thiazide diuretic",
    "mra": "mineralocorticoid receptor antagonist",
    "beta_blocker": "beta-1 selective blocker",
    "nsaid": "nsaid",
    "biguanide": "biguanide",
    "sulfonylurea": "sulfonylurea",
}


# ===========================================================================
# CONTRAINDICATION CONDITION-MATCHING HELPERS
# ===========================================================================


def _condition_matches(
    contraindication_condition: str,
    patient_conditions: list[str],
    patient_egfr: Optional[float],
) -> bool:
    """
    Determine whether a contraindication condition is satisfied by the
    patient's current state.

    Handles eGFR threshold conditions like 'egfr_below_30' specially.
    Other conditions are matched by substring against patient_conditions.
    """
    cond = contraindication_condition.lower()

    # eGFR-threshold contraindications
    if cond.startswith("egfr_below_") and patient_egfr is not None:
        try:
            threshold = float(cond.split("_")[-1])
            return patient_egfr < threshold
        except ValueError:
            return False

    # Direct or substring match against patient conditions
    patient_set = {c.lower() for c in patient_conditions}
    if cond in patient_set:
        return True
    # Fuzzy: any patient condition contains the contraindication keyword
    for pc in patient_set:
        if cond in pc or pc in cond:
            return True
    return False


# ===========================================================================
# PUBLIC API
# ===========================================================================

def get_drug(name: str) -> Optional[dict]:
    """
    Retrieve a drug profile by generic name (case-insensitive).

    Parameters
    ----------
    name : str
        Generic name of the drug (e.g., "empagliflozin", "Metformin").

    Returns
    -------
    dict or None
        Drug profile dict, or None if not found.
    """
    if not name:
        return None
    return _DRUGS.get(name.lower().strip())


def get_drug_by_rxcui(rxcui: str) -> Optional[dict]:
    """
    Retrieve a drug profile by RxNorm Concept Unique Identifier.

    Parameters
    ----------
    rxcui : str
        RxNorm RxCUI string.

    Returns
    -------
    dict or None
    """
    if not rxcui:
        return None
    rxcui_str = str(rxcui).strip()
    for drug in _DRUGS.values():
        if drug.get("rxcui") == rxcui_str:
            return drug
    return None


def get_drug_by_class(drug_class: str) -> list[dict]:
    """
    Retrieve all drugs belonging to a therapeutic class.

    Class name is matched case-insensitively, and common aliases are
    accepted (e.g., "sglt2i" -> "SGLT2 inhibitor").

    Parameters
    ----------
    drug_class : str
        Therapeutic class name or alias.

    Returns
    -------
    list of dict
        All matching drug profiles. Empty list if none found.
    """
    if not drug_class:
        return []
    key = drug_class.lower().strip()
    canonical = _CLASS_ALIASES.get(key, key)
    names = _DRUGS_BY_CLASS.get(canonical, [])
    return [_DRUGS[n] for n in names]


def get_drug_effects(name: str) -> Optional[dict]:
    """
    Retrieve only the 'effects' subsection of a drug's profile.

    Useful when the simulation engine needs to apply expected
    metabolic/renal/CV/hepatic/weight effects without the full profile.

    Returns
    -------
    dict or None
        The 'effects' dict, or None if drug not found.
    """
    drug = get_drug(name)
    if not drug:
        return None
    return drug.get("effects")


def check_contraindications(
    name: str,
    patient_conditions: list[str],
    patient_egfr: Optional[float] = None,
) -> list[dict]:
    """
    Check a drug against a patient's conditions and eGFR for contraindications.

    Parameters
    ----------
    name : str
        Generic drug name.
    patient_conditions : list of str
        Patient's active diagnoses, normalized condition keys
        (e.g., ["type_2_diabetes", "ckd_stage_3a", "hypertension"]).
    patient_egfr : float, optional
        Current eGFR in mL/min/1.73m². Used for threshold-based
        contraindications (e.g., "egfr_below_30").

    Returns
    -------
    list of dict
        Triggered contraindications, each with 'condition', 'severity',
        and 'drug' fields. Empty list if no contraindications triggered.
    """
    drug = get_drug(name)
    if not drug:
        return []

    triggered = []
    for ci in drug.get("contraindications", []):
        if _condition_matches(ci["condition"], patient_conditions, patient_egfr):
            triggered.append({
                "drug": drug["name"],
                "condition": ci["condition"],
                "severity": ci["severity"],
            })
    return triggered


def get_drug_interactions(
    name: str,
    current_medications: list[str],
) -> list[dict]:
    """
    Check a drug against a patient's current medication list for interactions.

    Matches by drug class — looks up each current medication's class and
    checks whether the candidate drug has an interaction entry for that class.

    Parameters
    ----------
    name : str
        Generic name of the candidate drug.
    current_medications : list of str
        Generic names of patient's current medications.

    Returns
    -------
    list of dict
        Triggered interactions, each annotated with the specific
        interacting medication, severity, effect, and recommendation.
    """
    drug = get_drug(name)
    if not drug:
        return []

    interactions_db = drug.get("drug_interactions", [])
    triggered = []

    for med_name in current_medications:
        med = get_drug(med_name)
        if not med:
            continue
        med_class = med.get("drug_class", "").lower().replace(" ", "_").replace("-", "_")
        for interaction in interactions_db:
            interaction_class = (
                interaction["interacting_drug_class"]
                .lower()
                .replace(" ", "_")
                .replace("-", "_")
            )
            # Match if candidate's interaction class is in the current med's
            # class string (e.g., interaction class "loop_diuretics" matches
            # med class "loop_diuretic")
            if (
                interaction_class in med_class
                or med_class in interaction_class
                or interaction_class.rstrip("s") == med_class.rstrip("s")
            ):
                triggered.append({
                    "candidate_drug": drug["name"],
                    "interacting_medication": med["name"],
                    "interacting_class": interaction["interacting_drug_class"],
                    "severity": interaction["severity"],
                    "effect": interaction["effect"],
                    "recommendation": interaction["recommendation"],
                })
    return triggered


def get_all_drug_names() -> list[str]:
    """
    Return all generic drug names present in the knowledge base.

    Returns
    -------
    list of str
        Sorted list of generic names.
    """
    return sorted(_DRUGS.keys())


def get_monitoring_requirements(name: str) -> list[dict]:
    """
    Retrieve the monitoring requirements for a drug.

    Parameters
    ----------
    name : str
        Generic drug name.

    Returns
    -------
    list of dict
        Each entry has 'test' and 'timing' fields.
    """
    drug = get_drug(name)
    if not drug:
        return []
    return drug.get("monitoring", [])


# ===========================================================================
# Module-level metadata
# ===========================================================================

__all__ = [
    "get_drug",
    "get_drug_by_rxcui",
    "get_drug_by_class",
    "get_drug_effects",
    "check_contraindications",
    "get_drug_interactions",
    "get_all_drug_names",
    "get_monitoring_requirements",
]