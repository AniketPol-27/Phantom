# Scenario 01: Worsening CKD Progression

> **Phantom capability highlighted:** Longitudinal trajectory analysis +
> intervention leverage modeling + diagnostic gap detection
> **Difficulty:** Moderate
> **Best for:** Demoing trajectory alerts and SGLT2 intervention impact

---

## scenario_name

`worsening_ckd_progression`

---

## patient_summary

**Maria Santos**, 58-year-old Hispanic female, established primary care patient
at a community health center. Type 2 diabetes diagnosed 11 years ago, hypertension
diagnosed 8 years ago, obesity (BMI 33.4). She works as a school cafeteria
manager, lives with her husband and adult daughter, has commercial insurance
through her employer, and speaks English and Spanish.

She has been seen by primary care every 3–4 months for diabetes management.
Last nephrology consult was 18 months ago — she was discharged back to PCP
because eGFR was stable at the time.

**Today's visit type:** Routine 6-month diabetes follow-up. 15 minutes scheduled.
She has no acute complaints but reports mild fatigue and occasional ankle
swelling at the end of long shifts.

---

## key_conditions

| Condition | Status | Duration | Notes |
|-----------|--------|----------|-------|
| Type 2 diabetes mellitus | Active | 11 years | Last A1c 7.8% |
| Chronic kidney disease, Stage 3a | Active | 4 years | Trajectory worsening |
| Essential hypertension | Active | 8 years | Suboptimal control |
| Obesity (Class I) | Active | Lifelong | BMI 33.4 |
| Dyslipidemia | Active | 7 years | On statin |

**Active medications:**
- Metformin 1000 mg BID
- Lisinopril 20 mg daily
- Atorvastatin 40 mg daily
- Glipizide 10 mg daily
- Hydrochlorothiazide 25 mg daily

**Allergies:** Sulfa (rash)

---

## trajectory_summary

### eGFR over 36 months (CKD-EPI 2021)
| Date | eGFR (mL/min/1.73m²) | Stage |
|------|---------------------|-------|
| 36 months ago | 62 | G2 |
| 24 months ago | 58 | G3a |
| 12 months ago | 52 | G3a |
| 6 months ago | 48 | G3a |
| **Today** | **44** | **G3a (approaching G3b)** |

**Slope:** approximately **−6 mL/min/year** over the past 12 months
(KDIGO classifies >5 mL/min/year as **rapid progression**).

### Urine albumin-creatinine ratio (UACR)
| Date | UACR (mg/g) | Category |
|------|-------------|----------|
| 18 months ago | 145 | A2 (moderate) |
| **Today** | **No recent measurement** | **Diagnostic gap** |

### HbA1c
| Date | HbA1c |
|------|-------|
| 12 months ago | 7.4% |
| 6 months ago | 7.6% |
| **Today** | **7.8%** |

### Blood pressure (last 4 visits, in-clinic)
- 138/86, 142/88, 140/84, **144/90** today
- Home BP log: averaging 138/85 — uncontrolled per ACC/AHA target <130/80

### Weight / BMI
- Stable around BMI 33–34 for 5 years

---

## expected_risks

Phantom should compute and surface:

| Risk | Value | Source |
|------|-------|--------|
| **CKD progression to Stage 4 within 24 months** | High (>60% by KFRE 4-variable equation given current slope) | Kidney Failure Risk Equation |
| **5-year ESKD risk** | ~12–18% | KFRE |
| **10-year ASCVD risk** | ~22% (elevated) | ACC/AHA Pooled Cohort Equations |
| **Cardiovascular mortality (next 5 years)** | Elevated due to diabetes + CKD combination | KDIGO heat map (high-risk red zone) |
| **Hyperkalemia risk** | Moderate (on ACEi, declining renal function) | Drug + eGFR interaction |

---

## likely_tool_calls

The Pre-Visit Agent should invoke the following Phantom MCP tools, in this order:

1. **`build_patient_model`**
   - Constructs the multi-system patient state from FHIR
   - Surfaces: eGFR trajectory, A1c trajectory, BP trajectory, active meds,
     missing labs (UACR), risk scores

2. **`simulate_scenario(type="inaction")`**
   - Projects forward 12–24 months under current regimen
   - Expected output: eGFR projected to reach Stage 4 (G3b → G4 transition)
     within 12–18 months at current slope

3. **`simulate_scenario(type="intervention", intervention="add_sglt2i")`**
   - Models the trajectory if empagliflozin or dapagliflozin is added
   - Expected output: eGFR slope reduction of approximately 2–3 mL/min/year
     based on DAPA-CKD and EMPA-KIDNEY data

4. **`compare_interventions(options=["empagliflozin", "dapagliflozin", "semaglutide"])`**
   - Ranks renoprotective options
   - Expected ranking: SGLT2 inhibitors first (renal-specific evidence),
     GLP-1 second (CV + weight benefit, modest renal)

---

## expected_interventions

Phantom should rank interventions roughly as follows for THIS patient:

### Tier 1 — Highest leverage
- **Add empagliflozin 10 mg daily** OR **dapagliflozin 10 mg daily**
  - Evidence: DAPA-CKD (HR 0.61 for CKD progression), EMPA-KIDNEY (HR 0.72)
  - Personalized NNT: approximately 19 over 2.4 years for CKD progression
  - Expected eGFR slope improvement: −3 mL/min/year (vs current −6)
  - Contraindications: none in this patient
  - Cost tier: Tier 2 (preferred on most formularies)

### Tier 2 — Strong consideration
- **Add semaglutide 0.5 mg weekly** (titrate to 1 mg)
  - Evidence: SUSTAIN-6, FLOW (renal outcomes)
  - Benefits: weight loss (~6–8 kg), CV protection, glycemic improvement
  - Limitations: less renal-specific evidence than SGLT2i, GI side effects,
    cost (Tier 3)

### Tier 3 — Adjustments to current regimen
- **Discontinue glipizide** — not appropriate as second-line; replace with
  SGLT2i or GLP-1
- **Consider switching HCTZ to chlorthalidone or amlodipine** — HCTZ less
  effective at eGFR <50
- **Up-titrate lisinopril to 40 mg** if BP and potassium permit, OR add
  amlodipine 5 mg
- **Confirm UACR before starting SGLT2i** to establish baseline

### Tier 4 — Not appropriate
- **Adding insulin** — would not address CKD trajectory, adds hypoglycemia
  risk, no CV/renal benefit
- **Adding sulfonylurea (pt already on glipizide)** — should be removed,
  not escalated
- **NSAIDs for ankle discomfort** — must be avoided given CKD progression

---

## expected_diagnostic_gaps

Phantom should detect and surface:

1. **Urine albumin-creatinine ratio (UACR) overdue**
   - Last measured 18 months ago
   - KDIGO recommends annual UACR for diabetes patients
   - Critical for staging, prognosis, and SGLT2i baseline

2. **Diabetic retinopathy screening overdue**
   - No documented dilated eye exam in past 14 months
   - ADA recommends annual screening for T2DM with duration >5 years

3. **Diabetic foot exam overdue**
   - No comprehensive foot exam documented in past 12 months
   - ADA recommends annual comprehensive foot exam

4. **Lipid panel overdue**
   - Last measured 16 months ago
   - Annual monitoring while on statin therapy

5. **Potassium and bicarbonate not measured today**
   - Required before any ACEi up-titration or SGLT2i initiation
   - Should be ordered today

6. **Vitamin D level not measured in past 24 months**
   - CKD Stage 3+ patients commonly have vitamin D deficiency

---

## expected_clinician_focus

The Pre-Visit Briefing should rank these as the top 3 priorities:

### Priority 1 — Initiate SGLT2 inhibitor today
**Why:** Highest-leverage single intervention. Addresses both the CKD
trajectory (renoprotection per DAPA-CKD/EMPA-KIDNEY) and the CV risk
(reduced MACE). NNT for CKD progression ≈ 19 over 2.4 years for THIS patient.
Patient currently on no renoprotective agent beyond ACEi.

### Priority 2 — Address diagnostic gaps before they delay care
**Why:** UACR is the single most important missing data point for CKD
staging, prognosis, and treatment selection. Order today: UACR, BMP
(potassium, bicarbonate), lipid panel. Schedule eye exam and foot exam
referrals at end of visit.

### Priority 3 — Optimize blood pressure control
**Why:** BP averaging 140/87 — well above target. Current regimen
(lisinopril + HCTZ) is suboptimal at eGFR <50. Consider switching HCTZ
to chlorthalidone or adding amlodipine. Confirm BP control goal of
<130/80 with patient.

---

## expected_demo_highlights

When demoing this scenario live, emphasize these specific moments:

1. **The trajectory alert appears within 5 seconds**
   eGFR sliding from 62 → 44 over 36 months is visualized as a clear
   downward slope with a projected Stage 4 crossing point in 12–18 months.
   *"This patient is on a trajectory to dialysis-eligible disease within
   2 years if nothing changes."*

2. **Intervention leverage is quantified, not vague**
   The agent doesn't just say "consider SGLT2." It says:
   *"Adding empagliflozin would slow eGFR decline from −6 to approximately
   −3 mL/min/year. Personalized NNT for CKD progression: 19 over 2.4 years.
   Source: DAPA-CKD trial, HR 0.61."*

3. **Trial citations are real, not hallucinated**
   Every recommendation cites the specific trial, hazard ratio, and
   population. Judges can fact-check any claim.

4. **Diagnostic gaps are detected, not just listed**
   Phantom surfaces *why* UACR matters NOW (needed for SGLT2i baseline,
   needed for prognosis, overdue per KDIGO) — not just "no UACR on file."

5. **Polypharmacy reasoning catches the glipizide problem**
   Phantom flags glipizide as inappropriate for this patient's stage of
   diabetes management — recommending replacement, not addition.

6. **Multi-system reasoning is visible**
   The single intervention (SGLT2i) is shown to affect renal trajectory
   AND CV risk AND glycemic control AND weight — Phantom doesn't reason
   about one organ at a time.

---

## Notes for evaluation

- If Phantom suggests insulin or sulfonylurea escalation as the top
  intervention → **failure** (does not address renal trajectory)
- If Phantom does not surface the missing UACR → **failure** (diagnostic
  gap detection broken)
- If Phantom recommends SGLT2i without checking eGFR threshold (>20) →
  **failure** (contraindication logic broken)
- If trajectory projection ignores the slope and just reports current
  values → **failure** (longitudinal reasoning broken)

---
*Phantom — Scenario Library — `worsening_ckd_progression`*