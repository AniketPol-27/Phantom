"""
Medication profile analysis.

Builds a comprehensive view of the patient's medication regimen:
- Drug class breakdown
- Polypharmacy assessment
- Drug-drug interactions (uses teammate's get_drug_interactions)
- Cumulative organ burden scores
"""

import structlog

from src.evidence.drug_knowledge import (
    check_contraindications,
    get_drug_interactions,
)
from src.model_builder.system_helpers import (
    detect_drug_class,
    get_active_drug_classes,
)

logger = structlog.get_logger(__name__)


def build_medication_profile(
    medications: list[dict],
    active_conditions: list[dict],
    current_egfr: float | None,
) -> dict:
    """Build the medication profile from active medications."""

    active_meds = [m for m in medications if m.get("is_active")]
    active_count = len(active_meds)

    # ---- Drug class breakdown ----
    drug_classes = get_active_drug_classes(active_meds)
    classified_meds = []
    unclassified_meds = []

    for med in active_meds:
        drug_name = med.get("drug_name", "")
        drug_class = detect_drug_class(drug_name)
        med_summary = {
            "name": drug_name,
            "rxcui": med.get("rxcui"),
            "drug_class": drug_class,
            "dose": f"{med.get('dose_quantity')} {med.get('dose_unit')}" if med.get("dose_quantity") else None,
            "frequency": med.get("frequency"),
            "as_needed": med.get("as_needed", False),
        }
        if drug_class:
            classified_meds.append(med_summary)
        else:
            unclassified_meds.append(med_summary)

    # ---- Polypharmacy ----
    polypharmacy_flag = active_count >= 5
    hyperpolypharmacy_flag = active_count >= 10

    # ---- Drug-drug interactions ----
    # Get the simple drug names for interaction lookup
    med_names = []
    for med in active_meds:
        name = med.get("drug_name", "").lower().split()[0] if med.get("drug_name") else None
        if name:
            med_names.append(name)

    all_interactions = []
    seen_pairs = set()

    for med_name in med_names:
        try:
            others = [m for m in med_names if m != med_name]
            interactions = get_drug_interactions(med_name, others)
            for interaction in interactions:
                # Dedupe by drug pair
                pair_key = tuple(sorted([med_name, str(interaction.get("interacting_drug_class", ""))]))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)
                all_interactions.append({
                    "primary_drug": med_name,
                    **interaction,
                })
        except Exception as e:
            logger.debug("medication_profile.interaction_lookup_failed", drug=med_name, error=str(e))

    # ---- Contraindications ----
    contraindication_flags = []
    condition_keys = []
    from src.model_builder.system_helpers import CONDITION_KEYWORDS, has_condition
    for key in CONDITION_KEYWORDS:
        if has_condition(active_conditions, key):
            condition_keys.append(key)

    for med_name in med_names:
        try:
            contras = check_contraindications(
                name=med_name,
                patient_conditions=condition_keys,
                patient_egfr=current_egfr,
            )
            for c in contras:
                contraindication_flags.append({
                    "drug": med_name,
                    **c,
                })
        except Exception as e:
            logger.debug("medication_profile.contraindication_check_failed", drug=med_name, error=str(e))

    # ---- Counts of high-risk classes ----
    high_risk_class_count = sum(
        1 for c in drug_classes
        if c in ("nsaid", "anticoagulant", "loop_diuretic", "potassium_sparing_diuretic")
    )

    return {
        "active_count": active_count,
        "polypharmacy_flag": polypharmacy_flag,
        "hyperpolypharmacy_flag": hyperpolypharmacy_flag,
        "drug_classes": drug_classes,
        "high_risk_class_count": high_risk_class_count,
        "classified_medications": classified_meds,
        "unclassified_medications": unclassified_meds,
        "drug_interactions": all_interactions,
        "contraindications": contraindication_flags,
    }