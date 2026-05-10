"""
Shared helpers for system model builders.

These utilities extract specific lab values, vitals, and conditions
from the parsed FHIR data and prepare them for clinical analysis.
"""

from typing import Any


# ============================================================
# LOINC code constants for labs we care about
# ============================================================

LOINC_CODES = {
    # Renal
    "creatinine": ["2160-0", "38483-4"],
    "egfr": ["98979-8", "33914-3", "62238-1", "48642-3", "48643-1"],
    "uacr": ["9318-7", "13705-9", "32294-1"],
    "bun": ["3094-0"],
    "potassium": ["2823-3", "6298-4"],
    "sodium": ["2951-2"],
    "chloride": ["2075-0"],
    "co2": ["2028-9"],
    "calcium": ["17861-6"],
    "phosphorus": ["2777-1"],

    # Metabolic
    "hba1c": ["4548-4", "17856-6"],
    "fasting_glucose": ["1558-6"],
    "random_glucose": ["2345-7"],
    "insulin": ["20448-7"],

    # Cardiovascular
    "ldl_cholesterol": ["13457-7", "18262-6", "2089-1"],
    "hdl_cholesterol": ["2085-9"],
    "total_cholesterol": ["2093-3"],
    "triglycerides": ["2571-8"],
    "non_hdl_cholesterol": ["43396-1"],

    # Hepatic
    "ast": ["1920-8"],
    "alt": ["1742-6"],
    "alp": ["6768-6"],
    "total_bilirubin": ["1975-2"],
    "albumin": ["1751-7"],
    "platelets": ["777-3", "26515-7"],

    # Hematology
    "hemoglobin": ["718-7"],
    "hematocrit": ["4544-3"],
    "wbc": ["6690-2"],
    "mcv": ["787-2"],

    # Vitals
    "blood_pressure_panel": ["85354-9", "55284-4"],
    "systolic_bp": ["8480-6"],
    "diastolic_bp": ["8462-4"],
    "heart_rate": ["8867-4"],
    "weight_kg": ["29463-7", "3141-9"],
    "height_cm": ["8302-2"],
    "bmi": ["39156-5"],
    "respiratory_rate": ["9279-1"],
    "oxygen_saturation": ["59408-5", "2708-6"],
    "temperature": ["8310-5"],
}


# ============================================================
# Condition keywords for matching
# ============================================================

CONDITION_KEYWORDS = {
    "type_2_diabetes": ["E11", "type 2 diabetes", "diabetes mellitus type 2", "44054006", "73211009"],
    "type_1_diabetes": ["E10", "type 1 diabetes", "46635009"],
    "chronic_kidney_disease": ["N18", "ckd", "chronic kidney disease", "433144002", "709044004"],
    "ckd_stage_3a": ["N18.31", "ckd stage 3a", "433144002"],
    "ckd_stage_3b": ["N18.32", "ckd stage 3b"],
    "ckd_stage_4": ["N18.4", "ckd stage 4"],
    "ckd_stage_5": ["N18.5", "ckd stage 5"],
    "hypertension": ["I10", "essential hypertension", "59621000", "38341003"],
    "obesity": ["E66", "obesity", "414916001", "414915002"],
    "dyslipidemia": ["E78", "dyslipidemia", "hyperlipidemia", "370992007", "55822004"],
    "heart_failure": ["I50", "heart failure", "84114007"],
    "atrial_fibrillation": ["I48", "atrial fibrillation", "49436004"],
    "coronary_artery_disease": ["I25", "coronary artery disease", "53741008"],
    "stroke": ["I63", "I64", "stroke", "230690007"],
    "anemia": ["D50", "D64", "anemia", "271737000"],
    "masld": ["K76.0", "k76", "fatty liver", "metabolic dysfunction", "197321007"],
    "copd": ["J44", "copd", "13645005"],
    "asthma": ["J45", "asthma", "195967001"],
    "depression": ["F32", "F33", "depression", "35489007"],
}


# ============================================================
# Drug class detection from medication lists
# ============================================================

DRUG_CLASS_PATTERNS = {
    "sglt2_inhibitor": ["empagliflozin", "dapagliflozin", "canagliflozin", "ertugliflozin"],
    "glp1_agonist": ["semaglutide", "liraglutide", "tirzepatide", "dulaglutide", "exenatide", "lixisenatide"],
    "biguanide": ["metformin"],
    "sulfonylurea": ["glipizide", "glyburide", "glimepiride"],
    "dpp4_inhibitor": ["sitagliptin", "linagliptin", "saxagliptin", "alogliptin"],
    "insulin": ["insulin glargine", "insulin lispro", "insulin aspart", "insulin detemir", "insulin degludec", "lantus", "humalog", "novolog"],
    "ace_inhibitor": ["lisinopril", "enalapril", "ramipril", "benazepril", "captopril"],
    "arb": ["losartan", "valsartan", "olmesartan", "candesartan", "irbesartan", "telmisartan"],
    "statin": ["atorvastatin", "rosuvastatin", "simvastatin", "pravastatin", "lovastatin", "pitavastatin"],
    "loop_diuretic": ["furosemide", "torsemide", "bumetanide"],
    "thiazide_diuretic": ["hydrochlorothiazide", "chlorthalidone", "indapamide"],
    "potassium_sparing_diuretic": ["spironolactone", "eplerenone", "amiloride"],
    "calcium_channel_blocker": ["amlodipine", "diltiazem", "verapamil", "nifedipine", "felodipine"],
    "beta_blocker": ["metoprolol", "carvedilol", "bisoprolol", "atenolol", "propranolol", "nebivolol"],
    "nsaid": ["ibuprofen", "naproxen", "celecoxib", "meloxicam", "diclofenac", "indomethacin"],
    "anticoagulant": ["warfarin", "apixaban", "rivaroxaban", "dabigatran", "edoxaban"],
    "antiplatelet": ["aspirin", "clopidogrel", "ticagrelor", "prasugrel"],
    "ppi": ["omeprazole", "esomeprazole", "pantoprazole", "lansoprazole"],
}


# ============================================================
# Helpers
# ============================================================

def get_observations_by_loinc(
    observations: list[dict],
    loinc_codes: list[str],
) -> list[dict]:
    """
    Filter observations to those matching any of the given LOINC codes.

    Returns observations sorted by date descending (most recent first).
    """
    matching = [
        obs for obs in observations
        if obs.get("code") in loinc_codes
    ]
    matching.sort(
        key=lambda o: o.get("effective_datetime") or "",
        reverse=True,
    )
    return matching


def get_lab_value_history(
    observations: list[dict],
    lab_key: str,
) -> list[dict]:
    """
    Get longitudinal history for a named lab (uses LOINC_CODES mapping).

    Returns list of {"value": float, "unit": str, "date": str}
    sorted by date ascending (chronological order for trajectory analysis).
    """
    loinc_codes = LOINC_CODES.get(lab_key, [])
    if not loinc_codes:
        return []

    matches = get_observations_by_loinc(observations, loinc_codes)
    history = []
    for obs in matches:
        value = obs.get("value")
        if value is None or not isinstance(value, (int, float)):
            continue
        date = obs.get("effective_datetime")
        if not date:
            continue
        history.append({
            "value": float(value),
            "unit": obs.get("unit"),
            "date": date,
        })

    # Sort ascending for trajectory
    history.sort(key=lambda x: x["date"])
    return history


def get_latest_lab_value(
    observations: list[dict],
    lab_key: str,
) -> dict | None:
    """Get most recent lab value for a named lab."""
    history = get_lab_value_history(observations, lab_key)
    if not history:
        return None
    return history[-1]  # last in ascending order = most recent


def get_bp_history(vital_observations: list[dict]) -> list[dict]:
    """
    Extract systolic + diastolic BP history from vital observations.

    Handles both:
    - Component-based BP observations (LOINC 85354-9 with components)
    - Separate systolic/diastolic observations
    """
    bp_history = []

    for obs in vital_observations:
        code = obs.get("code")
        date = obs.get("effective_datetime")
        if not date:
            continue

        # Component-based BP panel
        if code in LOINC_CODES["blood_pressure_panel"]:
            components = obs.get("components", [])
            systolic = None
            diastolic = None
            for comp in components:
                if comp.get("code") in LOINC_CODES["systolic_bp"]:
                    systolic = comp.get("value")
                elif comp.get("code") in LOINC_CODES["diastolic_bp"]:
                    diastolic = comp.get("value")
            if systolic is not None and diastolic is not None:
                bp_history.append({
                    "systolic": float(systolic),
                    "diastolic": float(diastolic),
                    "date": date,
                })

    # Sort ascending (chronological)
    bp_history.sort(key=lambda x: x["date"])
    return bp_history


def has_condition(active_conditions: list[dict], condition_key: str) -> bool:
    """Check if patient has a specific condition by matching codes/keywords."""
    keywords = CONDITION_KEYWORDS.get(condition_key, [])
    if not keywords:
        return False

    for cond in active_conditions:
        if not cond.get("is_active"):
            continue
        code = (cond.get("code") or "").lower()
        display = (cond.get("display") or "").lower()
        for keyword in keywords:
            kw_lower = keyword.lower()
            if kw_lower in code or kw_lower in display:
                return True
    return False


def get_active_conditions_list(active_conditions: list[dict]) -> list[str]:
    """
    Return list of condition_key strings that match the patient's active conditions.

    Useful for passing to teammate's evaluate_care_gaps() and similar functions.
    """
    matched = []
    for key in CONDITION_KEYWORDS:
        if has_condition(active_conditions, key):
            matched.append(key)
    return matched


def detect_drug_class(drug_name: str | None) -> str | None:
    """Detect drug class from a drug name string."""
    if not drug_name:
        return None
    name_lower = drug_name.lower()
    for drug_class, patterns in DRUG_CLASS_PATTERNS.items():
        for pattern in patterns:
            if pattern in name_lower:
                return drug_class
    return None


def get_active_drug_classes(medications: list[dict]) -> list[str]:
    """Get list of unique drug classes from active medications."""
    classes = set()
    for med in medications:
        if not med.get("is_active"):
            continue
        drug_class = detect_drug_class(med.get("drug_name"))
        if drug_class:
            classes.add(drug_class)
    return sorted(classes)


def get_active_medication_names(medications: list[dict]) -> list[str]:
    """Get list of active medication names (lowercase, deduped)."""
    names = set()
    for med in medications:
        if not med.get("is_active"):
            continue
        name = med.get("drug_name")
        if name:
            # Extract just the drug name (strip dose/form info)
            name_clean = name.lower().split()[0]
            names.add(name_clean)
    return sorted(names)


def days_since(date_str: str | None) -> int | None:
    """Calculate days since an ISO date string."""
    if not date_str:
        return None
    from datetime import datetime
    try:
        date_only = date_str.split("T")[0]
        target = datetime.fromisoformat(date_only)
        now = datetime.utcnow()
        return (now - target).days
    except (ValueError, AttributeError):
        return None