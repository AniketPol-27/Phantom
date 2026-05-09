"""
test_evidence.py — Comprehensive unit tests for Phantom evidence modules.

Tests cover all 5 evidence modules:
  - risk_equations.py
  - drug_knowledge.py
  - trial_data.py
  - guidelines.py
  - disease_progression.py

Run with:
    cd mcp-server
    uv run pytest tests/test_evidence.py -v
"""

import pytest

# ─── Imports ────────────────────────────────────────────────────────────────

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

from src.evidence.trial_data import (
    get_trial,
    get_trials_for_drug,
    get_trials_for_condition,
    get_outcome_data,
    get_egfr_slope_data,
    get_subgroup_data,
    get_all_trial_names,
)

from src.evidence.guidelines import (
    get_all_care_gap_rules,
    get_all_diagnostic_gap_rules,
    evaluate_care_gaps,
    evaluate_diagnostic_gaps,
)

from src.evidence.disease_progression import (
    project_ckd_progression,
    project_diabetes_progression,
    project_cv_risk_progression,
    project_masld_progression,
    get_cascade_modifiers,
)


# ═══════════════════════════════════════════════════════════════════════════
# MODULE 1: risk_equations.py (9 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestRiskEquations:

    def test_egfr_ckd_epi_2021_known_value_female(self):
        """
        CKD-EPI 2021 (race-free) for a 60-year-old female with creatinine 1.0
        should yield eGFR between 60 and 65 mL/min/1.73m2.
        Source: Inker LA et al. NEJM 2021 (PMID: 34554658)
        """
        result = calculate_egfr_ckd_epi_2021(
            serum_creatinine=1.0,
            age=60,
            sex="female"
        )
        egfr = result["egfr"] if isinstance(result, dict) else result
        assert 60 <= egfr <= 65, (
            f"Expected eGFR 60-65 for female, creatinine=1.0, age=60. Got {egfr}"
        )

    def test_egfr_ckd_epi_2021_known_value_male(self):
        """
        CKD-EPI 2021 for a 60-year-old male with creatinine 1.0.
        Actual computed value is ~86.2 — range widened to 75-92 to match
        the published equation output exactly.
        Source: Inker LA et al. NEJM 2021 (PMID: 34554658)
        """
        result = calculate_egfr_ckd_epi_2021(
            serum_creatinine=1.0,
            age=60,
            sex="male"
        )
        egfr = result["egfr"] if isinstance(result, dict) else result
        assert 75 <= egfr <= 92, (
            f"Expected eGFR 75-92 for male, creatinine=1.0, age=60. Got {egfr}"
        )

    def test_egfr_handles_severe_renal_impairment(self):
        """
        With serum creatinine of 4.0 mg/dL in a 70-year-old male,
        eGFR should be severely reduced (< 20 mL/min/1.73m2),
        consistent with CKD Stage 4 or 5.
        """
        result = calculate_egfr_ckd_epi_2021(
            serum_creatinine=4.0,
            age=70,
            sex="male"
        )
        egfr = result["egfr"] if isinstance(result, dict) else result
        assert egfr < 20, (
            f"Expected eGFR < 20 for severe impairment (creatinine=4.0). Got {egfr}"
        )

    def test_classify_ckd_stage_returns_correct_stages(self):
        """
        KDIGO 2024 eGFR staging should return the correct stage for each
        eGFR threshold. Checks G1 through G5.
        """
        test_cases = [
            (95, "G1"),
            (72, "G2"),
            (52, "G3a"),
            (38, "G3b"),
            (22, "G4"),
            (10, "G5"),
        ]
        for egfr_val, expected_stage in test_cases:
            result = classify_ckd_stage(egfr_val)
            assert isinstance(result, dict), "classify_ckd_stage must return a dict"
            assert "stage" in result, "Result must contain 'stage' key"
            assert result["stage"] == expected_stage, (
                f"eGFR {egfr_val} should be {expected_stage}, got {result['stage']}"
            )

    def test_ascvd_high_risk_patient(self):
        """
        65-year-old Black male, total cholesterol 240, HDL 35, SBP 160,
        smoker, diabetic, on BP treatment — should yield >= 20% 10-year
        ASCVD risk (very high risk category).
        Source: Goff DC et al. JACC 2014 (PMID: 24239921)
        """
        result = calculate_ascvd_10yr_risk(
            age=65,
            sex="male",
            race="black",
            total_cholesterol=240,
            hdl_cholesterol=35,
            systolic_bp=160,
            bp_treated=True,
            diabetes=True,
            current_smoker=True
        )
        risk = result["risk_percent"] if isinstance(result, dict) else result
        assert risk is not None, "risk_percent should not be None for age=65"
        assert risk >= 20, (
            f"High-risk patient should have ASCVD risk >= 20%. Got {risk}%"
        )

    def test_ascvd_out_of_range_age_handled_gracefully(self):
        """
        The Pooled Cohort Equations are only validated for ages 40-79.
        Age 35 should return risk_percent=None with risk_category='out_of_range'
        and a clear recommendation explaining the limitation.
        Source: Goff DC et al. JACC 2014 (PMID: 24239921)
        """
        result = calculate_ascvd_10yr_risk(
            age=35,
            sex="female",
            race="white",
            total_cholesterol=180,
            hdl_cholesterol=60,
            systolic_bp=110,
            bp_treated=False,
            diabetes=False,
            current_smoker=False
        )
        assert isinstance(result, dict), "Must return a dict"
        assert result.get("risk_category") == "out_of_range", (
            f"Age 35 is outside PCE validated range (40-79). "
            f"Expected risk_category='out_of_range', got: {result.get('risk_category')}"
        )
        assert result.get("risk_percent") is None, (
            "risk_percent should be None for out-of-range age"
        )
        assert "recommendation" in result, (
            "Should include a recommendation explaining the out-of-range result"
        )

    def test_ascvd_low_risk_patient_valid_age(self):
        """
        40-year-old white female with optimal risk factors should yield
        < 5% 10-year ASCVD risk (low risk category).
        Uses age=40 which is within the validated PCE range (40-79).
        Source: Goff DC et al. JACC 2014 (PMID: 24239921)
        """
        result = calculate_ascvd_10yr_risk(
            age=40,
            sex="female",
            race="white",
            total_cholesterol=180,
            hdl_cholesterol=60,
            systolic_bp=110,
            bp_treated=False,
            diabetes=False,
            current_smoker=False
        )
        assert isinstance(result, dict), "Must return a dict"
        risk = result.get("risk_percent")
        assert risk is not None, (
            f"risk_percent should not be None for age=40. Got result: {result}"
        )
        assert risk < 5, (
            f"Low-risk 40yo female should have ASCVD risk < 5%. Got {risk}%"
        )

    def test_fib4_calculation_known_values(self):
        """
        FIB-4 = (age x AST) / (platelets x sqrt(ALT)).
        For age=58, AST=40, ALT=51, platelets=210, expect score in [1.0, 2.5].
        Source: Sterling RK et al. Hepatology 2006 (PMID: 16729309)
        """
        result = calculate_fib4(
            age=58,
            ast=40,
            alt=51,
            platelet_count=210
        )
        assert isinstance(result, dict), "calculate_fib4 must return a dict"
        score = result["score"]
        assert 1.0 <= score <= 2.5, (
            f"FIB-4 score expected 1.0-2.5, got {score}"
        )
        assert "category" in result, "Result must contain 'category'"
        assert result["category"] in ["low", "indeterminate", "high"], (
            f"Category must be low/indeterminate/high, got {result['category']}"
        )

    def test_compute_trajectory_returns_valid_slope(self):
        """
        Given declining eGFR values over time, compute_trajectory should
        detect a negative slope, 'declining' direction, and return projections.
        Function expects:
          - data_points with 'date' keys (ISO date strings), not 'time_months'
          - rate_thresholds with 'normal' and 'moderate' keys (not 'rapid')
        """
        data_points = [
            {"date": "2023-01-15", "value": 58},
            {"date": "2023-07-15", "value": 55},
            {"date": "2024-01-15", "value": 52},
            {"date": "2024-07-15", "value": 49},
            {"date": "2025-01-15", "value": 47},
            {"date": "2025-07-15", "value": 44},
        ]
        result = compute_trajectory(
            data_points=data_points,
            rate_thresholds={"normal": 1.0, "moderate": 3.0}
        )
        assert isinstance(result, dict), "compute_trajectory must return a dict"
        assert "slope_per_year" in result, "Must include slope_per_year"
        assert result["slope_per_year"] < 0, (
            f"Slope should be negative for declining data. "
            f"Got {result['slope_per_year']}"
        )
        assert result.get("direction") == "declining", (
            f"Direction should be 'declining', got {result.get('direction')}"
        )
        projections = result.get("projections", {})
        assert "6_months" in projections, "Must project at 6 months"
        assert "12_months" in projections, "Must project at 12 months"
        assert "24_months" in projections, "Must project at 24 months"


# ═══════════════════════════════════════════════════════════════════════════
# MODULE 2: drug_knowledge.py (9 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestDrugKnowledge:

    def test_all_drugs_have_required_fields(self):
        """
        Every drug in the knowledge base must have a complete schema with
        all required fields for clinical use.
        """
        required_fields = [
            "name", "rxcui", "drug_class", "mechanism", "effects",
            "contraindications", "side_effects", "monitoring",
            "drug_interactions", "dosing", "cost_tier", "route", "frequency"
        ]
        for drug_name in get_all_drug_names():
            drug = get_drug(drug_name)
            assert drug is not None, f"get_drug('{drug_name}') returned None"
            for field in required_fields:
                assert field in drug, (
                    f"Drug '{drug_name}' is missing required field '{field}'"
                )

    def test_get_drug_returns_none_for_unknown_drug(self):
        """
        Querying a drug that doesn't exist should return None gracefully,
        not raise an exception.
        """
        result = get_drug("nonexistent_drug_xyz_123")
        assert result is None, (
            f"Expected None for unknown drug, got {result}"
        )

    def test_get_drug_by_rxcui_works(self):
        """
        RxNorm lookup for empagliflozin (RxCUI 1545653) should return
        the correct drug record.
        """
        drug = get_drug_by_rxcui("1545653")
        assert drug is not None, "RxCUI 1545653 should return empagliflozin"
        assert drug["name"] == "empagliflozin", (
            f"Expected empagliflozin, got {drug['name']}"
        )

    def test_get_drug_by_class_returns_all_sglt2_inhibitors(self):
        """
        Class lookup for SGLT2 inhibitors should return at least 3 drugs:
        empagliflozin, dapagliflozin, canagliflozin.
        """
        drugs = get_drug_by_class("SGLT2 inhibitor")
        drug_names = [d["name"] for d in drugs]
        assert len(drugs) >= 3, (
            f"Expected >= 3 SGLT2 inhibitors, got {len(drugs)}: {drug_names}"
        )
        for expected in ["empagliflozin", "dapagliflozin", "canagliflozin"]:
            assert expected in drug_names, (
                f"'{expected}' not found in SGLT2i class. Got: {drug_names}"
            )

    def test_sglt2_inhibitors_all_have_renoprotective_effect(self):
        """
        All SGLT2 inhibitors should be encoded with renoprotective effects
        and a favorable eGFR slope modifier (< 1.0, slowing decline).
        Supported by DAPA-CKD, CREDENCE, EMPA-KIDNEY trials.
        """
        sglt2_drugs = get_drug_by_class("SGLT2 inhibitor")
        for drug in sglt2_drugs:
            renal = drug["effects"].get("renal", {})
            assert renal.get("renoprotective") is True, (
                f"{drug['name']}: expected renoprotective=True in renal effects"
            )
            slope_mod = renal.get("egfr_slope_modifier")
            assert slope_mod is not None, (
                f"{drug['name']}: missing egfr_slope_modifier"
            )
            assert 0 < slope_mod < 1, (
                f"{drug['name']}: egfr_slope_modifier should be 0-1 "
                f"(slowing decline), got {slope_mod}"
            )

    def test_glp1_agonists_all_show_weight_loss(self):
        """
        All GLP-1 receptor agonists should have weight.direction == 'loss'
        in their effects profile.
        Supported by SUSTAIN-6, LEADER, REWIND, SURPASS-4 trials.
        """
        glp1_drugs = ["semaglutide", "liraglutide", "tirzepatide", "dulaglutide"]
        for drug_name in glp1_drugs:
            drug = get_drug(drug_name)
            assert drug is not None, f"Drug '{drug_name}' not found"
            weight_effect = drug["effects"].get("weight", {})
            assert weight_effect.get("direction") == "loss", (
                f"{drug_name}: expected weight direction='loss', "
                f"got {weight_effect.get('direction')}"
            )

    def test_metformin_contraindicated_in_severe_ckd(self):
        """
        Metformin should be contraindicated when eGFR < 30 (severe CKD)
        due to risk of lactic acidosis.
        Source: FDA metformin labeling; ADA 2024 Standards of Care.
        """
        result = check_contraindications(
            name="metformin",
            patient_conditions=[],
            patient_egfr=20
        )
        assert isinstance(result, list), "check_contraindications must return a list"
        assert len(result) >= 1, (
            "Metformin should have >= 1 contraindication at eGFR=20 (severe CKD)"
        )

    def test_drug_interactions_detects_known_dangerous_combo(self):
        """
        Spironolactone + lisinopril is a known dangerous combination causing
        hyperkalemia. The interaction should be detected and mention
        potassium or hyperkalemia.
        """
        interactions = get_drug_interactions(
            name="spironolactone",
            current_medications=["lisinopril"]
        )
        assert isinstance(interactions, list), "Must return a list"
        assert len(interactions) >= 1, (
            "Spironolactone + lisinopril interaction should be detected"
        )
        combined_text = " ".join(
            str(i.get("description", "")) + str(i.get("recommendation", ""))
            for i in interactions
        ).lower()
        assert "potassium" in combined_text or "hyperkalemia" in combined_text, (
            f"Interaction should mention potassium/hyperkalemia. "
            f"Got: {combined_text}"
        )

    def test_nsaid_nephrotoxicity_documented(self):
        """
        Ibuprofen (NSAID) should document nephrotoxicity in side_effects
        or monitoring. Critical for patients with CKD.
        """
        drug = get_drug("ibuprofen")
        assert drug is not None, "ibuprofen should be in drug database"
        side_effects_text = str(drug.get("side_effects", "")).lower()
        monitoring_text = str(drug.get("monitoring", "")).lower()
        combined = side_effects_text + monitoring_text
        assert (
            "nephr" in combined
            or "renal" in combined
            or "kidney" in combined
        ), (
            "Ibuprofen should document nephrotoxicity risk in side_effects "
            "or monitoring"
        )


# ═══════════════════════════════════════════════════════════════════════════
# MODULE 3: trial_data.py (6 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestTrialData:

    def test_all_required_trials_present(self):
        """
        The key landmark trials must all be present in the evidence base.
        Note: UKPDS is stored as 'UKPDS-33' — matched with startswith.
        """
        required = [
            "DAPA-CKD", "CREDENCE", "EMPA-REG OUTCOME",
            "EMPA-KIDNEY", "SUSTAIN-6", "LEADER", "REWIND",
        ]
        all_names_upper = [n.upper() for n in get_all_trial_names()]

        for trial in required:
            assert trial.upper() in all_names_upper, (
                f"Required trial '{trial}' not found. "
                f"Available: {get_all_trial_names()}"
            )

        # UKPDS is stored as UKPDS-33
        ukpds_found = any(
            n.upper().startswith("UKPDS") for n in get_all_trial_names()
        )
        assert ukpds_found, (
            f"UKPDS trial (stored as UKPDS-33) not found. "
            f"Available: {get_all_trial_names()}"
        )

    def test_dapa_ckd_has_expected_structure(self):
        """
        DAPA-CKD trial entry must have all required fields for clinical
        use by the simulation engine.
        """
        trial = get_trial("DAPA-CKD")
        assert trial is not None, "DAPA-CKD trial must exist"
        required_fields = [
            "drug_studied", "comparator", "year_published", "pmid",
            "population", "primary_outcome", "secondary_outcomes",
            "egfr_slope_data", "safety", "subgroups"
        ]
        for field in required_fields:
            assert field in trial, (
                f"DAPA-CKD missing required field '{field}'"
            )

    def test_dapa_ckd_egfr_slope_shows_benefit(self):
        """
        In DAPA-CKD, dapagliflozin slowed eGFR decline vs placebo.
        Keys: drug_slope_ml_per_min_per_year and
        placebo_slope_ml_per_min_per_year.
        Drug slope should be less negative (closer to 0) than placebo slope.
        PMID: 32970396
        """
        slope_data = get_egfr_slope_data("DAPA-CKD")
        assert slope_data is not None, "DAPA-CKD must have eGFR slope data"

        drug_slope = slope_data.get("drug_slope_ml_per_min_per_year")
        placebo_slope = slope_data.get("placebo_slope_ml_per_min_per_year")

        assert drug_slope is not None, (
            f"Must have drug_slope_ml_per_min_per_year. "
            f"Keys: {list(slope_data.keys())}"
        )
        assert placebo_slope is not None, (
            f"Must have placebo_slope_ml_per_min_per_year. "
            f"Keys: {list(slope_data.keys())}"
        )
        assert drug_slope > placebo_slope, (
            f"Drug slope ({drug_slope}) should be > placebo slope "
            f"({placebo_slope}) i.e. less decline with treatment"
        )
        difference = slope_data.get("difference")
        if difference is not None:
            assert difference > 0, (
                f"Slope difference should be positive (benefit). "
                f"Got {difference}"
            )

    def test_get_trials_for_drug_returns_correct_trials(self):
        """
        get_trials_for_drug returns a list of dicts (not strings).
        Finds the name key dynamically then checks membership.
        """
        dapa_trials_raw = get_trials_for_drug("dapagliflozin")
        assert isinstance(dapa_trials_raw, list), "Must return a list"
        assert len(dapa_trials_raw) >= 1, (
            "Should find at least 1 trial for dapagliflozin"
        )

        # Each item is a dict — find which key holds the trial name
        first = dapa_trials_raw[0]
        name_key = None
        for key in ["trial_name", "name", "id", "title"]:
            if key in first:
                name_key = key
                break

        assert name_key is not None, (
            f"Cannot find name key in trial dict. "
            f"Keys available: {list(first.keys())}"
        )

        dapa_trial_names = [t[name_key].upper() for t in dapa_trials_raw]
        assert "DAPA-CKD" in dapa_trial_names, (
            f"DAPA-CKD not in dapagliflozin trials: {dapa_trial_names}"
        )

        empa_trials_raw = get_trials_for_drug("empagliflozin")
        empa_trial_names = [t[name_key].upper() for t in empa_trials_raw]
        assert "EMPA-REG OUTCOME" in empa_trial_names, (
            f"EMPA-REG OUTCOME not in empagliflozin trials: {empa_trial_names}"
        )
        assert "EMPA-KIDNEY" in empa_trial_names, (
            f"EMPA-KIDNEY not in empagliflozin trials: {empa_trial_names}"
        )

    def test_empa_reg_shows_cv_benefit(self):
        """
        EMPA-REG OUTCOME demonstrated cardiovascular benefit (HR < 1.0)
        for the primary composite endpoint.
        PMID: 26378978
        """
        trial = get_trial("EMPA-REG OUTCOME")
        assert trial is not None, "EMPA-REG OUTCOME must exist"
        primary = trial.get("primary_outcome", {})
        hr = primary.get("hazard_ratio") or primary.get("hr")
        assert hr is not None, "Primary outcome must include hazard_ratio"
        assert hr < 1.0, (
            f"EMPA-REG OUTCOME HR should be < 1.0 (benefit). Got {hr}"
        )

    def test_all_trials_have_pmid(self):
        """
        Data integrity: every trial must have a non-empty PMID for
        citation traceability.
        """
        for trial_name in get_all_trial_names():
            trial = get_trial(trial_name)
            pmid = trial.get("pmid", "")
            assert pmid and str(pmid).strip() != "", (
                f"Trial '{trial_name}' has empty or missing PMID"
            )


# ═══════════════════════════════════════════════════════════════════════════
# MODULE 4: guidelines.py (5 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestGuidelines:

    def test_sglt2i_care_gap_triggered_for_diabetic_ckd_patient(self):
        """
        A patient with T2DM + CKD on metformin + lisinopril but NO SGLT2i
        should trigger the 'diabetes_sglt2i_ckd' care gap.
        patient_egfr must be passed explicitly to satisfy egfr_min=20 criterion.
        Confirmed gap dict contains 'sglt2' in rule_id, description, recommendation.
        Supported by KDIGO 2024, ADA 2024 Standards of Care.
        """
        gaps = evaluate_care_gaps(
            patient_conditions=["type_2_diabetes", "chronic_kidney_disease"],
            patient_medications=["metformin", "lisinopril"],
            patient_labs={"egfr": 52},
            patient_age=58,
            patient_sex="female",
            patient_egfr=52,
        )
        assert isinstance(gaps, list), "evaluate_care_gaps must return a list"

        def gap_mentions_sglt2(gap: dict) -> bool:
            return any(
                "sglt2" in str(v).lower()
                for v in gap.values()
            )

        sglt2_gaps = [g for g in gaps if gap_mentions_sglt2(g)]
        assert len(sglt2_gaps) >= 1, (
            f"SGLT2i care gap should be triggered for T2DM+CKD patient "
            f"without SGLT2i. Got rule_ids: {[g.get('rule_id') for g in gaps]}"
        )

    def test_no_sglt2i_gap_when_already_prescribed(self):
        """
        If the patient is already on empagliflozin (an SGLT2i), the SGLT2i
        care gap should NOT appear.
        The evaluator checks medication_class_absent, not medication names.
        patient_medication_classes must be passed explicitly with 'sglt2_inhibitor'
        to correctly suppress the gap.
        """
        gaps = evaluate_care_gaps(
            patient_conditions=["type_2_diabetes", "chronic_kidney_disease"],
            patient_medications=["metformin", "lisinopril", "empagliflozin"],
            patient_labs={"egfr": 52},
            patient_age=58,
            patient_sex="female",
            patient_egfr=52,
            patient_medication_classes=["sglt2_inhibitor"],
        )

        def gap_mentions_sglt2(gap: dict) -> bool:
            return any(
                "sglt2" in str(v).lower()
                for v in gap.values()
            )

        sglt2_gaps = [g for g in gaps if gap_mentions_sglt2(g)]
        assert len(sglt2_gaps) == 0, (
            f"SGLT2i gap should NOT appear when patient is on empagliflozin. "
            f"Found: {sglt2_gaps}"
        )

    def test_hba1c_above_target_triggers_glycemic_gap(self):
        """
        A diabetic patient with HbA1c of 8.5% (above ADA 2024 target)
        should trigger a glycemic control care gap.
        """
        gaps = evaluate_care_gaps(
            patient_conditions=["type_2_diabetes"],
            patient_medications=["metformin"],
            patient_labs={"egfr": 75, "hba1c": 8.5},
            patient_age=55,
            patient_sex="male",
        )

        def gap_mentions_glycemic(gap: dict) -> bool:
            return any(
                kw in str(v).lower()
                for v in gap.values()
                for kw in ["hba1c", "glycemic", "a1c", "glucose"]
            )

        glycemic_gaps = [g for g in gaps if gap_mentions_glycemic(g)]
        assert len(glycemic_gaps) >= 1, (
            f"HbA1c=8.5% should trigger a glycemic control care gap. "
            f"Got rule_ids: {[g.get('rule_id') for g in gaps]}"
        )

    def test_ckd_anemia_diagnostic_gap_detected(self):
        """
        A patient with CKD (eGFR 50) and hemoglobin 11.5 g/dL but no anemia
        diagnosis should trigger a CKD-associated anemia diagnostic gap.
        patient_egfr passed explicitly so egfr_below=60 criterion is met.
        Source: KDIGO 2024 CKD anemia guidelines.
        """
        gaps = evaluate_diagnostic_gaps(
            patient_conditions=["chronic_kidney_disease"],
            patient_labs={"egfr": 50, "hemoglobin": 11.5},
            patient_vitals={},
            patient_age=60,
            patient_sex="female",
            patient_egfr=50,
        )
        assert isinstance(gaps, list), "evaluate_diagnostic_gaps must return a list"

        def gap_mentions_anemia(gap: dict) -> bool:
            return any("anemia" in str(v).lower() for v in gap.values())

        anemia_gaps = [g for g in gaps if gap_mentions_anemia(g)]
        assert len(anemia_gaps) >= 1, (
            f"CKD + Hgb 11.5 should trigger CKD-anemia diagnostic gap. "
            f"Got rule_ids: {[g.get('rule_id') for g in gaps]}"
        )

    def test_masld_pattern_detected_in_metabolic_syndrome(self):
        """
        A patient with obesity + T2DM + persistently elevated ALT should
        trigger the MASLD diagnostic gap.
        The MASLD rule uses lab_above_threshold_persistent which requires
        persistent_lab_history={'alt': [list of numeric values]}.
        At least 2 values must exceed threshold=40.
        Source: AASLD MASLD guidance 2023.
        """
        gaps = evaluate_diagnostic_gaps(
            patient_conditions=["type_2_diabetes", "obesity"],
            patient_labs={"egfr": 75, "alt": 58},
            patient_vitals={"bmi": 34},
            patient_age=52,
            patient_sex="female",
            persistent_lab_history={"alt": [42, 58, 51]},
        )

        def gap_mentions_masld(gap: dict) -> bool:
            return any(
                kw in str(v).lower()
                for v in gap.values()
                for kw in ["masld", "fatty liver", "nafld", "steatotic", "hepatic"]
            )

        masld_gaps = [g for g in gaps if gap_mentions_masld(g)]
        assert len(masld_gaps) >= 1, (
            f"Obesity + T2DM + persistent ALT elevation should trigger "
            f"MASLD diagnostic gap. "
            f"Got rule_ids: {[g.get('rule_id') for g in gaps]}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# MODULE 5: disease_progression.py (5 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestDiseaseProgression:

    def test_ckd_progression_projects_decline(self):
        """
        With eGFR=52, slope=-4.2 mL/min/year, diabetes, and no SGLT2i,
        the 12-month projected eGFR should be below the current 52.
        """
        result = project_ckd_progression(
            current_egfr=52,
            egfr_slope=-4.2,
            has_diabetes=True,
            has_hypertension=True,
            albuminuria_category="A2",
            on_acei_or_arb=True,
            on_sglt2i=False,
            age=58
        )
        assert isinstance(result, dict), (
            "project_ckd_progression must return a dict"
        )
        egfr_12mo = (
            result.get("projected_egfr_12mo")
            or result.get("egfr_12mo")
        )
        assert egfr_12mo is not None, "Must include 12-month eGFR projection"
        assert egfr_12mo < 52, (
            f"eGFR should decline from 52 over 12 months. Got {egfr_12mo}"
        )
        modifiers = result.get("modifiers_applied", [])
        diabetes_mod = any("diabetes" in str(m).lower() for m in modifiers)
        assert diabetes_mod, (
            f"Diabetes modifier should be applied. Got modifiers: {modifiers}"
        )

    def test_ckd_progression_with_sglt2i_slows_decline(self):
        """
        Adding SGLT2i should slow eGFR decline. The 12-month projected eGFR
        with SGLT2i should be HIGHER than without SGLT2i.
        Supported by DAPA-CKD (HR 0.61), EMPA-KIDNEY, CREDENCE.
        """
        result_no_sglt2i = project_ckd_progression(
            current_egfr=52,
            egfr_slope=-4.2,
            has_diabetes=True,
            has_hypertension=True,
            albuminuria_category="A2",
            on_acei_or_arb=True,
            on_sglt2i=False,
            age=58
        )
        result_with_sglt2i = project_ckd_progression(
            current_egfr=52,
            egfr_slope=-4.2,
            has_diabetes=True,
            has_hypertension=True,
            albuminuria_category="A2",
            on_acei_or_arb=True,
            on_sglt2i=True,
            age=58
        )
        egfr_without = (
            result_no_sglt2i.get("projected_egfr_12mo")
            or result_no_sglt2i.get("egfr_12mo")
        )
        egfr_with = (
            result_with_sglt2i.get("projected_egfr_12mo")
            or result_with_sglt2i.get("egfr_12mo")
        )
        assert egfr_with > egfr_without, (
            f"SGLT2i should slow decline: eGFR with SGLT2i ({egfr_with}) "
            f"should be > without ({egfr_without})"
        )

    def test_diabetes_progression_rising_hba1c(self):
        """
        With current HbA1c=8.2% and positive slope (0.3 per 6 months),
        projected HbA1c at 12 months should be HIGHER than 8.2%.
        """
        result = project_diabetes_progression(
            current_hba1c=8.2,
            hba1c_slope=0.3,
            years_since_diagnosis=8,
            current_medications=["metformin", "glipizide"],
            bmi=34,
            on_max_oral_therapy=False
        )
        assert isinstance(result, dict), (
            "project_diabetes_progression must return a dict"
        )
        hba1c_12mo = (
            result.get("projected_hba1c_12mo")
            or result.get("hba1c_12mo")
        )
        assert hba1c_12mo is not None, "Must include 12-month HbA1c projection"
        assert hba1c_12mo > 8.2, (
            f"Rising HbA1c should project > 8.2% at 12 months. "
            f"Got {hba1c_12mo}"
        )

    def test_cascade_modifiers_diabetes_ckd_acceleration(self):
        """
        Comorbid T2DM + CKD should trigger bidirectional acceleration
        cascades, as each condition worsens the other.
        """
        cascades = get_cascade_modifiers(
            ["type_2_diabetes", "chronic_kidney_disease"]
        )
        assert isinstance(cascades, list), (
            "get_cascade_modifiers must return a list"
        )
        assert len(cascades) >= 1, (
            "T2DM + CKD should trigger at least 1 comorbidity cascade"
        )
        has_bidirectional = any(
            "bidirectional" in str(c).lower()
            or (
                "diabetes" in str(c).lower()
                and ("ckd" in str(c).lower() or "kidney" in str(c).lower())
            )
            for c in cascades
        )
        assert has_bidirectional, (
            f"T2DM+CKD should trigger bidirectional acceleration cascade. "
            f"Got: {cascades}"
        )

    def test_cv_risk_progression_rises_with_uncontrolled_factors(self):
        """
        A patient with rising BP, elevated LDL, and diabetes should show
        increasing projected ASCVD risk at 12 months.
        Exact output key confirmed: 'projected_ascvd_risk_12mo_percent'
        """
        result = project_cv_risk_progression(
            current_ascvd_risk=14.2,
            current_bp_systolic=148,
            bp_trend_per_year=3.0,
            current_ldl=128,
            on_statin=True,
            has_diabetes=True,
            has_ckd=True,
            current_bmi=34,
            smoking=False,
            age=58
        )
        assert isinstance(result, dict), (
            "project_cv_risk_progression must return a dict"
        )
        risk_12mo = result.get("projected_ascvd_risk_12mo_percent")
        assert risk_12mo is not None, (
            f"Must include 'projected_ascvd_risk_12mo_percent'. "
            f"Keys returned: {list(result.keys())}"
        )
        assert risk_12mo >= 14.2, (
            f"Uncontrolled CV risk factors should not decrease ASCVD risk. "
            f"Current: 14.2%, Projected: {risk_12mo}%"
        )


# ═══════════════════════════════════════════════════════════════════════════
# DATA INTEGRITY TESTS (2 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestDataIntegrity:

    def test_no_duplicate_drug_names(self):
        """
        Data integrity: the drug database should have no duplicate entries.
        Each drug name should appear exactly once.
        """
        all_names = get_all_drug_names()
        assert len(all_names) == len(set(all_names)), (
            f"Duplicate drug names found: "
            f"{[n for n in all_names if all_names.count(n) > 1]}"
        )

    def test_21_drugs_in_knowledge_base(self):
        """
        The drug knowledge base should contain exactly 21 drugs as built.
        """
        all_names = get_all_drug_names()
        assert len(all_names) == 21, (
            f"Expected 21 drugs, found {len(all_names)}: {all_names}"
        )