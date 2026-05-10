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