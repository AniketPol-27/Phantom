# Scenario 04: MASLD Progression — Suspected Fibrosis with Missing Workup

> **Phantom capability highlighted:** Multi-system reasoning across
> metabolic + hepatic axes, FIB-4 computation from existing labs,
> diagnostic gap detection that crosses specialty boundaries
> **Difficulty:** Moderate
> **Best for:** Demoing how Phantom catches conditions clinicians weren't
> looking for

---

## scenario_name

`masld_progression`

---

## patient_summary

**Linda Chen**, 49-year-old Asian American female, established patient at a
primary care clinic. Office manager, lives with husband and two teenage
children. Commercial insurance through employer. Active in her community,
walks 30 minutes most days. Drinks alcohol socially — 2–3 glasses of wine
per week (well below thresholds for alcohol-associated liver disease).

**Today's visit type:** Annual physical. 30 minutes scheduled. Chief
complaint: "I just feel tired all the time." No specific pain, no GI
symptoms, no jaundice. She thinks it's "just stress and getting older."

She has not seen a hepatologist. The mildly elevated liver enzymes noted
on prior labs have never been worked up — they were attributed to
"fatty liver, common with weight" by her previous PCP and not followed up.

---

## key_conditions

| Condition | Status | Duration | Notes |
|-----------|--------|----------|-------|
| Type 2 diabetes mellitus | Active | 3 years | A1c 7.4%, on metformin |
| Obesity (Class II) | Active | Lifelong | BMI 35.6 |
| Essential hypertension | Active | 4 years | Controlled on lisinopril |
| Hyperlipidemia | Active | 5 years | On statin |
| Metabolic syndrome | Active | 5 years | Meets all 5 criteria |
| Hepatic steatosis (incidental on CT, 18 months ago) | Documented | 18 months | Never worked up |
| Anxiety, mild | Active | 2 years | No medication |

**Active medications:**
- Metformin 1000 mg BID
- Lisinopril 10 mg daily
- Atorvastatin 20 mg daily
- Multivitamin

**Allergies:** None known

---

## trajectory_summary

### Liver enzymes over 24 months
| Date | ALT (U/L) | AST (U/L) | Alk Phos | Albumin |
|------|----------|----------|----------|---------|
| 24 months ago | 42 | 38 | 88 | 4.4 |
| 12 months ago | 56 | 48 | 92 | 4.3 |
| 6 months ago | 68 | 58 | 95 | 4.2 |
| **Today** | **74** | **66** | **98** | **4.1** |

**Trend:** Steady upward trajectory of transaminases. ALT now nearly
2x upper limit of normal. AST/ALT ratio approaching 1.0 (concerning when
>1.0 in MASLD — suggests fibrosis).

### Platelets (relevant to FIB-4)
| Date | Platelets (×10⁹/L) |
|------|-------------------|
| 24 months ago | 240 |
| 12 months ago | 218 |
| 6 months ago | 195 |
| **Today** | **178** |

**Trend:** Gradual decline — also concerning for fibrosis (splenic
sequestration from portal hypertension is a late finding, but declining
platelets in the right clinical context are a soft signal).

### HbA1c
| Date | HbA1c |
|------|-------|
| 24 months ago | 6.8% |
| 12 months ago | 7.1% |
| **Today** | **7.4%** |

### Weight / BMI
| Date | Weight (lbs) | BMI |
|------|--------------|-----|
| 24 months ago | 198 | 34.0 |
| **Today** | **207** | **35.6** |

### Lipids (today)
- LDL 92 (at goal on statin)
- HDL 38
- Triglycerides 220 (elevated — metabolic syndrome criterion)

### Imaging history
- Abdominal CT (incidental, 18 months ago, ordered for evaluation of
  abdominal pain that resolved): "moderate hepatic steatosis, no focal
  lesion, spleen normal size"
- No FibroScan, no liver biopsy, no liver MRI elastography
- Last hepatology referral: never

---

## expected_risks

Phantom should compute and surface:

| Risk | Value | Driver |
|------|-------|--------|
| **MASLD with significant fibrosis (F2–F4)** | **HIGH** based on FIB-4 calculation (see below) | Rising ALT/AST, declining platelets, T2DM + obesity |
| **Cirrhosis within 10 years if untreated** | Elevated (~10–20%) | Diabetes is independent risk factor for fibrosis progression |
| **Hepatocellular carcinoma (HCC) lifetime risk** | Elevated above baseline | MASLD with possible advanced fibrosis |
| **Cardiovascular mortality** | MASLD is independent CV risk factor | Multiple metabolic risk factors |
| **T2DM progression** | Moderate | Worsening A1c, weight gain |

### FIB-4 calculation (Phantom should do this automatically)

**Formula:** FIB-4 = (Age × AST) / (Platelets × √ALT)

**For Linda Chen today:**
- Age: 49
- AST: 66
- Platelets: 178
- ALT: 74, √ALT ≈ 8.6
- FIB-4 = (49 × 66) / (178 × 8.6) = 3,234 / 1,531 = **2.11**

**Interpretation:**
- FIB-4 <1.30 → low fibrosis probability (rule out advanced fibrosis)
- FIB-4 1.30–2.67 → indeterminate (further testing needed — FibroScan)
- FIB-4 >2.67 → high probability of advanced fibrosis (refer hepatology)

**Linda's FIB-4 of 2.11 is in the indeterminate zone — but trending up
rapidly (was likely <1.3 two years ago). This warrants FibroScan and
hepatology referral.**

---

## likely_tool_calls

The Pre-Visit Agent should invoke:

1. **`build_patient_model`**
   - Surfaces: rising transaminases trajectory, declining platelets,
     metabolic syndrome, obesity trajectory, untreated hepatic steatosis
     finding
   - Should automatically compute FIB-4 from existing labs

2. **`simulate_scenario(type="diagnostic_gap")`**
   - Identifies that MASLD workup is incomplete
   - Surfaces FibroScan and hepatology referral as missing care steps

3. **`simulate_scenario(type="inaction")`**
   - Projects 5–10 year hepatic trajectory if untreated
   - Expected: progression to F2/F3 fibrosis, possible cirrhosis,
     increased HCC risk

4. **`compare_interventions(focus="metabolic_and_hepatic")`**
   - Evaluates interventions that address BOTH glycemic control AND
     hepatic outcomes
   - Should surface GLP-1 (semaglutide) and SGLT2i as preferred over
     sulfonylureas/insulin given MASLD context

---

## expected_interventions

Phantom should rank interventions:

### Tier 1 — Diagnostic actions (today)

- **Order FibroScan (transient elastography)**
  - First-line non-invasive fibrosis assessment
  - Available in most communities, well-tolerated, no biopsy needed
  - Will quantify liver stiffness (kPa) and steatosis (CAP score)

- **Refer to hepatology**
  - FIB-4 in indeterminate zone + trending up + diabetes = appropriate
    for specialty evaluation
  - Hepatologist may pursue FibroScan + liver MRI elastography

- **Order full hepatic workup labs**
  - Hepatitis B surface antigen (rule out HBV — common in Asian populations)
  - Hepatitis C antibody (USPSTF universal screening)
  - Iron studies, ceruloplasmin, ANA (rule out hemochromatosis, Wilson's,
    autoimmune hepatitis — completion of standard MASLD differential)
  - GGT (further characterization)

### Tier 2 — Therapeutic actions (this visit or near-term)

- **Add semaglutide (or tirzepatide if covered)**
  - Evidence for MASLD: STEP-HFpEF, LEAN trial, emerging data on liver
    fibrosis improvement
  - Addresses BOTH glycemic control AND drives meaningful weight loss
  - Weight loss of 7–10% has been shown to improve MASLD histology
  - Replaces consideration of sulfonylurea or insulin

- **Add empagliflozin or dapagliflozin**
  - Emerging evidence for hepatic benefit in MASLD with T2DM
  - Modest weight loss
  - Could be combined with GLP-1 over time

- **Vitamin E 800 IU daily** (only if biopsy confirms NASH and patient
  is non-diabetic — generally NOT recommended in this patient due to T2DM
  and prostate cancer risk concerns in men, but Phantom should know the
  guideline nuance)

### Tier 3 — Lifestyle (foundational, not optional)

- **Mediterranean diet referral** — strongest dietary evidence for MASLD
- **Weight loss target: 7–10% of body weight** — proven to regress
  steatosis and fibrosis
- **Exercise: 150 minutes moderate aerobic + 2 sessions resistance/week**
- **Alcohol counseling: minimize or eliminate** (even social drinking
  worsens MASLD progression)

### Tier 4 — Avoid

- **Avoid acetaminophen >2 g/day** if FibroScan confirms fibrosis
- **Avoid hepatotoxic supplements** — patient should disclose all OTC and
  herbal products (kava, comfrey, high-dose green tea extract, etc.)
- **No insulin if avoidable** — would not address weight, would not address
  liver

---

## expected_diagnostic_gaps

Phantom should surface:

1. **FIB-4 has never been calculated despite 24 months of trending data**
   - This is the headline gap
   - Phantom can calculate it instantly from existing labs
   - Result (2.11) drives the entire workup

2. **No FibroScan ordered despite documented hepatic steatosis**
   - Steatosis was noted on CT 18 months ago and never followed up
   - Standard of care for MASLD with risk factors is non-invasive fibrosis
     staging

3. **No hepatology referral**
   - With FIB-4 in indeterminate zone and rising, specialist evaluation
     is warranted

4. **Hepatitis B and C screening**
   - HBV: especially relevant given Asian ancestry (higher prevalence)
   - HCV: USPSTF universal adult screening (15–79)
   - Both should be checked before attributing all liver disease to MASLD

5. **Mammogram**
   - Age 49, average risk — biennial screening recommended
   - Last mammogram status not documented in chart

6. **Colon cancer screening**
   - Age 49 — should have started at 45 per USPSTF
   - Status not documented

7. **Diabetic eye exam**
   - T2DM × 3 years — should have annual screening
   - Not documented in past 12 months

8. **Mental health screening (PHQ-9)**
   - Patient reports fatigue and stress — depression screening warranted
   - USPSTF: depression screening for all adults

---

## expected_clinician_focus

The Pre-Visit Briefing should rank:

### Priority 1 — Address the unworked-up MASLD today
**Why:** This patient has had documented hepatic steatosis for 18 months
with steadily rising transaminases and declining platelets. FIB-4
calculated from her existing labs is 2.11 — in the indeterminate-to-high
range with a rising trajectory. The diagnostic gap is the single most
important issue at this visit. Order FibroScan, refer hepatology, complete
hepatitis serologies. The fatigue she came in for may be hepatic in origin.

### Priority 2 — Choose diabetes therapy that addresses BOTH glycemia and liver
**Why:** A1c is rising (6.8 → 7.4 over 24 months) and weight is rising.
Adding a sulfonylurea would worsen weight and not address the liver.
Adding semaglutide (or tirzepatide) addresses A1c, drives meaningful
weight loss (which directly improves MASLD), and has emerging hepatic
benefit data. This is a multi-axis decision — Phantom recognizes that
metabolic and hepatic problems share solutions.

### Priority 3 — Close the catch-up screening gaps
**Why:** Patient is 49 with overdue mammogram, overdue colonoscopy
(since age 45), no documented depression screening despite reporting
fatigue and stress, and no recent diabetic eye exam. None of these are
emergencies, but a comprehensive annual visit is the right time to
catch them all.

---

## expected_demo_highlights

When demoing this scenario live, emphasize:

1. **Phantom calculates FIB-4 from labs the chart already had**
   The numbers were always there. Nobody multiplied them. Phantom does the
   math in milliseconds and surfaces a result that changes the visit.
   *"This is the highest-leverage diagnostic in the entire chart, and it
   was hidden in plain sight."*

2. **Cross-specialty reasoning the EHR doesn't support**
   This patient's diabetes specialist looks at A1c. Her PCP looks at
   weight and BP. Nobody owns "the liver." Phantom doesn't have specialty
   silos — it sees the whole patient.

3. **Trajectory matters, not snapshots**
   ALT of 74 today is concerning. ALT of 74 today, up from 42 two years
   ago, with declining platelets, in a diabetic — that's a different
   story. Phantom tells the longitudinal story.

4. **The intervention decision becomes obvious in context**
   "Choose semaglutide over a sulfonylurea" is a generic recommendation.
   "Choose semaglutide because it addresses both her A1c trajectory AND
   her likely MASLD AND her weight" is a contextualized decision. Phantom
   surfaces the "why" not just the "what."

5. **The fatigue is not dismissed as stress**
   Patient and prior PCP both attributed fatigue to stress. Phantom
   recognizes that progressive MASLD can present with fatigue as the
   only symptom for years. This reframes the chief complaint.

6. **Differential diagnosis is completed, not assumed**
   Phantom doesn't just say "this is MASLD." It says "this is most likely
   MASLD, but Hepatitis B and C must be ruled out, especially given Asian
   ancestry — and we should also check iron studies and autoimmune markers
   to complete the standard differential." This is real diagnostic
   rigor.

---

## Notes for evaluation

- If Phantom does not calculate FIB-4 from existing labs → **failure**
  (key automated diagnostic capability missing)
- If Phantom does not surface FibroScan / hepatology referral → **failure**
  (diagnostic gap detection broken for hepatic axis)
- If Phantom recommends a sulfonylurea or insulin as first-line escalation
  → **failure** (would worsen weight and not address MASLD)
- If Phantom does not mention Hepatitis B screening in this patient →
  **partial failure** (population-aware reasoning broken)
- If Phantom recommends Vitamin E to a diabetic for MASLD → **failure**
  (guideline knowledge incorrect)
- If Phantom dismisses fatigue without considering hepatic origin →
  **partial failure** (multi-system reasoning incomplete)

---
*Phantom — Scenario Library — `masld_progression`*