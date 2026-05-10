"""
Clinical evidence base for the Phantom MCP server.

This package contains the clinical knowledge that powers Phantom's
simulation engine. The five modules together provide:

  - risk_equations       : Validated risk score calculations
                           (eGFR CKD-EPI 2021, ASCVD PCE, FIB-4, qSOFA,
                           CKD/albuminuria staging, KDIGO heat map,
                           linear trajectory regression)

  - drug_knowledge       : 21 drugs with multi-system effects, FDA
                           contraindications, drug-drug interactions,
                           and monitoring requirements
                           (SGLT2i, GLP-1 RA, biguanide, sulfonylureas,
                           insulins, ACEi, ARB, statins, diuretics,
                           NSAID, beta blocker)

  - trial_data           : 10 major clinical trials with structured
                           outcome data, eGFR slopes, and subgroups
                           (DAPA-CKD, CREDENCE, EMPA-REG, EMPA-KIDNEY,
                           SUSTAIN-6, LEADER, REWIND, SURPASS-4,
                           UKPDS-33, SPRINT)

  - guidelines           : 25 care gap rules + 11 diagnostic gap rules
                           with evaluators that take patient state and
                           return triggered gaps with citations
                           (KDIGO, ADA, ACC/AHA, USPSTF, AASLD, CDC)

  - disease_progression  : Natural disease history models for CKD,
                           diabetes, CV risk, MASLD, plus 12 comorbidity
                           cascade definitions

All exports are re-exported here so consumers can do:
    from src.evidence import calculate_egfr_ckd_epi_2021, get_drug
instead of:
    from src.evidence.risk_equations import calculate_egfr_ckd_epi_2021
    from src.evidence.drug_knowledge import get_drug

This package has zero dependencies on FHIR, MCP, SHARP, or platform code.
Pure Python with numpy + scipy.
"""

# ---------------------------------------------------------------------------
# Risk equations
# ---------------------------------------------------------------------------
from src.evidence.risk_equations import (
    calculate_egfr_ckd_epi_2021,
    classify_ckd_stage,
    classify_albuminuria,
    kdigo_risk_matrix,
    calculate_ascvd_10yr_risk,
    calculate_fib4,
    calculate_qsofa,
    compute_trajectory,
)

# ---------------------------------------------------------------------------
# Drug knowledge
# ---------------------------------------------------------------------------
from src.evidence.drug_knowledge import (
    get_drug,
    get_drug_by_rxcui,
    get_drug_by_class,
    get_drug_effects,
    check_contraindications,
    get_drug_interactions,
    get_all_drug_names,
    get_monitoring_requirements,
)

# ---------------------------------------------------------------------------
# Trial data
# ---------------------------------------------------------------------------
from src.evidence.trial_data import (
    get_trial,
    get_trials_for_drug,
    get_trials_for_condition,
    get_outcome_data,
    get_egfr_slope_data,
    get_subgroup_data,
    get_all_trial_names,
)

# ---------------------------------------------------------------------------
# Guidelines (care gaps + diagnostic gaps)
# ---------------------------------------------------------------------------
from src.evidence.guidelines import (
    CARE_GAP_RULES,
    DIAGNOSTIC_GAP_RULES,
    get_all_care_gap_rules,
    get_care_gap_rules_for_condition,
    get_all_diagnostic_gap_rules,
    get_diagnostic_gap_rules_for_condition,
    evaluate_care_gaps,
    evaluate_diagnostic_gaps,
)

# ---------------------------------------------------------------------------
# Disease progression
# ---------------------------------------------------------------------------
from src.evidence.disease_progression import (
    project_ckd_progression,
    project_diabetes_progression,
    project_cv_risk_progression,
    project_masld_progression,
    get_cascade_modifiers,
)


__all__ = [
    # Risk equations
    "calculate_egfr_ckd_epi_2021",
    "classify_ckd_stage",
    "classify_albuminuria",
    "kdigo_risk_matrix",
    "calculate_ascvd_10yr_risk",
    "calculate_fib4",
    "calculate_qsofa",
    "compute_trajectory",
    # Drug knowledge
    "get_drug",
    "get_drug_by_rxcui",
    "get_drug_by_class",
    "get_drug_effects",
    "check_contraindications",
    "get_drug_interactions",
    "get_all_drug_names",
    "get_monitoring_requirements",
    # Trial data
    "get_trial",
    "get_trials_for_drug",
    "get_trials_for_condition",
    "get_outcome_data",
    "get_egfr_slope_data",
    "get_subgroup_data",
    "get_all_trial_names",
    # Guidelines
    "CARE_GAP_RULES",
    "DIAGNOSTIC_GAP_RULES",
    "get_all_care_gap_rules",
    "get_care_gap_rules_for_condition",
    "get_all_diagnostic_gap_rules",
    "get_diagnostic_gap_rules_for_condition",
    "evaluate_care_gaps",
    "evaluate_diagnostic_gaps",
    # Disease progression
    "project_ckd_progression",
    "project_diabetes_progression",
    "project_cv_risk_progression",
    "project_masld_progression",
    "get_cascade_modifiers",
]