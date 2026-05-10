# Scenario 02: Uncontrolled Diabetes — Medication Escalation Decision

> **Phantom capability highlighted:** Head-to-head intervention comparison
> (GLP-1 vs SGLT2 vs insulin) with personalized ranking
> **Difficulty:** Moderate
> **Best for:** Demoing the `compare_interventions` tool and shared
> decision-making support

---

## scenario_name

`uncontrolled_diabetes`

---

## patient_summary

**James Walker**, 54-year-old African American male, established patient at
an academic endocrinology clinic. Type 2 diabetes diagnosed 7 years ago,
initially well-controlled on metformin alone. Over the past 18 months his
glycemic control has deteriorated despite adherence. Works as a long-haul
truck driver — irregular meal schedule, prolonged sitting, frequent
fast-food meals. Has commercial insurance through employer. Married,
two adult children.

**Today's visit type:** Endocrinology follow-up. 30 minutes scheduled.
Referred back from PCP for "medication escalation decision." Patient
explicitly says he does not want to start insulin.

---

## key_conditions

| Condition | Status | Duration | Notes |
|-----------|--------|----------|-------|
| Type 2 diabetes mellitus | Active, uncontrolled | 7 years | A1c 9.2% |
| Obesity (Class II) | Active | Lifelong | BMI 36.8 |
| Essential hypertension | Active | 5 years | Controlled on lisinopril |
| Dyslipidemia | Active | 5 years | On statin |
| Obstructive sleep apnea | Active | 3 years | CPAP-adherent |
| Mild fatty liver (imaging incidental) | Active | 2 years | No biopsy |

**Active medications:**
- Metformin 1000 mg BID (max tolerated dose)
- Lisinopril 20 mg daily
- Atorvastatin 40 mg daily
- Aspirin 81 mg daily

**Allergies:** None known

---

## trajectory_summary

### HbA1c over 24 months
| Date | HbA1c |
|------|-------|
| 24 months ago | 7.1% |
| 18 months ago | 7.6% |
| 12 months ago | 8.3% |
| 6 months ago | 8.8% |
| **Today** | **9.2%** |

**Trend:** Steady upward trajectory of approximately +0.9% per year despite
adherence to metformin. ADA target for this patient: <7.0%.

### Weight / BMI
| Date | Weight (lbs) | BMI |
|------|--------------|-----|
| 24 months ago | 245 | 35.2 |
| **Today** | **256** | **36.8** |

**Trend:** Gradual weight gain of ~5 kg over 2 years.

### eGFR
- Stable at 88 mL/min/1.73m² (CKD-EPI 2021) — normal renal function
- UACR: 18 mg/g (A1, normal range)

### Blood pressure
- Well-controlled: averaging 124/78 in clinic, similar at home

### Lipid panel (3 months ago)
- LDL 78 mg/dL (at goal on statin)
- HDL 38 mg/dL
- Triglycerides 188 mg/dL

### Cardiovascular risk
- No prior MI, no prior stroke
- 10-year ASCVD risk (Pooled Cohort Equations): approximately 18%
  (intermediate-high)

---

## expected_risks

Phantom should compute and surface:

| Risk | Value | Source |
|------|-------|--------|
| **Microvascular complications progression (5 years)** | High at A1c 9.2% | UKPDS, DCCT |
| **10-year ASCVD risk** | ~18% | Pooled Cohort Equations |
| **Future CKD development** | Moderate (rising A1c, obesity, HTN) | KDIGO risk modeling |
| **MASLD progression to fibrosis** | Moderate (obesity + diabetes + fatty liver) | FIB-4 needed for stratification |
| **Future insulin dependence (if uncontrolled)** | High within 2–3 years | Natural history |

---

## likely_tool_calls

The agent should invoke:

1. **`build_patient_model`**
   - Surfaces: rising A1c trajectory, weight trajectory, normal renal
     function, intermediate ASCVD risk, MASLD suspicion, CV risk factors

2. **`simulate_scenario(type="inaction")`**
   - Projects A1c trajectory if current regimen continues
   - Expected: A1c projected to exceed 10% within 12 months
   - Microvascular risk escalation visualized

3. **`compare_interventions(options=["semaglutide", "empagliflozin", "basal_insulin"])`**
   - Ranks the three escalation options head-to-head
   - Multi-dimensional scoring: A1c reduction, weight, CV benefit,
     hypoglycemia risk, adherence burden, cost, patient preference

4. **`simulate_scenario(type="intervention", intervention="add_glp1")`**
   - Models 12-month projection if semaglutide added
   - Expected: A1c reduction 1.5–1.8%, weight loss 6–8 kg

---

## expected_interventions

Phantom should rank interventions for THIS patient as follows:

### Tier 1 — Best fit
- **Semaglutide 0.25 mg weekly → titrate to 1 mg weekly**
  - Evidence: SUSTAIN-6 (CV benefit, HR 0.74 for MACE), STEP trials (weight)
  - Expected A1c reduction: 1.5–1.8%
  - Expected weight loss: 6–8 kg over 6 months
  - CV benefit: significant (relevant given 18% ASCVD risk)
  - Hypoglycemia risk: low
  - Adherence: weekly injection (compatible with truck driver schedule)
  - Patient preference: aligns with stated preference to avoid insulin
  - Cost concern: Tier 3 — verify coverage; consider tirzepatide as alternative
  - **Patient fit score: 9/10**

### Tier 2 — Strong alternative
- **Empagliflozin 10 mg daily**
  - Evidence: EMPA-REG OUTCOME (CV benefit, HR 0.86 MACE)
  - Expected A1c reduction: 0.7–1.0%
  - Expected weight loss: 2–3 kg
  - CV benefit: significant
  - Hypoglycemia risk: very low
  - Adherence: oral daily (excellent for truck driver)
  - Limitations: smaller A1c reduction than GLP-1 — may not be enough alone
    to reach target from 9.2%
  - Could be added in COMBINATION with semaglutide for compounded benefit
  - **Patient fit score: 7/10 alone, 9/10 if combined**

### Tier 3 — Aligned with patient preference but suboptimal as first choice
- **Basal insulin (glargine) 10 units nightly, titrate**
  - Expected A1c reduction: 1.5–2.5% (highest of the three)
  - Hypoglycemia risk: moderate (concerning for a truck driver — DOT
    medical exam implications)
  - Weight effect: weight gain of 2–4 kg expected
  - No CV benefit
  - Adherence burden: daily injection + glucose monitoring
  - Patient preference: explicitly declined
  - Occupational risk: hypoglycemia in a long-haul driver is a safety
    issue for both patient and public
  - **Patient fit score: 4/10**

### Tier 4 — Combination consideration
- **Semaglutide + empagliflozin** (after titration of either)
  - Compounded A1c reduction: ~2.0–2.5%
  - Compounded CV/renal benefit
  - Compounded weight loss
  - Best long-term trajectory for this patient
  - **Patient fit score: 10/10 over 6–12 month horizon**

### Not appropriate
- Sulfonylurea (glipizide, glimepiride) — hypoglycemia risk in driver,
  weight gain, no CV benefit
- DPP-4 inhibitor (sitagliptin) — modest A1c effect, no weight or CV
  benefit, would not move the needle from 9.2%

---

## expected_diagnostic_gaps

Phantom should surface:

1. **FIB-4 not calculated despite known fatty liver**
   - With AST, ALT, platelets available in recent labs, FIB-4 can be
     computed automatically
   - Critical for MASLD fibrosis risk stratification
   - May change management (refer to hepatology if FIB-4 >2.67)

2. **Diabetic retinopathy screening**
   - Last documented dilated eye exam: 18 months ago
   - With A1c 9.2%, screening should be annual (some guidelines: every
     6 months if uncontrolled)

3. **Diabetic foot exam**
   - No comprehensive foot exam in past 12 months
   - Important given driver occupation (prolonged pressure on feet)

4. **Sleep study follow-up / CPAP adherence verification**
   - CPAP adherence data not in chart
   - Untreated OSA worsens insulin resistance — relevant to glycemic
     trajectory

5. **UACR**
   - Annual UACR recommended for all T2DM
   - Last measured 14 months ago

6. **Liver imaging follow-up**
   - Fatty liver noted on imaging 2 years ago — no follow-up
   - With rising A1c and weight, MASLD progression risk is elevated

---

## expected_clinician_focus

The Pre-Visit Briefing should rank these as the top 3 priorities:

### Priority 1 — Initiate semaglutide today
**Why:** Best fit across all dimensions for THIS patient. Aligns with stated
preference to avoid insulin. Addresses A1c (1.5–1.8% reduction expected),
weight (6–8 kg loss), and CV risk (HR 0.74 for MACE per SUSTAIN-6) in a
single agent. Hypoglycemia risk is low — important for occupational safety
as a commercial driver. Weekly dosing is highly compatible with irregular
schedule.

### Priority 2 — Calculate FIB-4 today, not later
**Why:** Patient has known fatty liver, obesity, T2DM with rising A1c —
classic MASLD risk profile. FIB-4 can be computed from existing labs in
seconds. If >2.67, refer to hepatology. If 1.3–2.67, consider FibroScan.
This is a high-yield, zero-cost diagnostic gap closure.

### Priority 3 — Address occupational safety considerations
**Why:** Patient is a long-haul truck driver subject to DOT medical exams.
A1c >10% may affect certification. Hypoglycemia from any insulin or
sulfonylurea regimen is a public safety issue. Document the rationale
for choosing semaglutide over insulin in the chart — supports DOT exam
defensibility.

---

## expected_demo_highlights

When demoing this scenario live, emphasize:

1. **Multi-dimensional intervention comparison appears as a real table**
   Not a paragraph. Not a bulleted list. An actual ranked table with
   columns for A1c effect, weight effect, CV benefit, hypoglycemia risk,
   adherence, cost, patient fit. *"This is what shared decision-making
   looks like with evidence in front of you."*

2. **Personalized NNT, not population NNT**
   Phantom doesn't just cite "SUSTAIN-6 reported 26% MACE reduction." It
   says: *"For THIS patient — male, 54, ASCVD risk 18%, A1c 9.2% — the
   personalized NNT for MACE prevention over 2 years is approximately 35."*

3. **Patient preference is treated as a dimension, not ignored**
   The agent surfaces that the patient declined insulin — and incorporates
   that into the ranking. Insulin still appears in the comparison
   (transparency), but is appropriately ranked Tier 3.

4. **Occupational context shapes the recommendation**
   The agent recognizes that "truck driver" is clinically relevant —
   hypoglycemia risk has different consequences than for a desk worker.
   This is exactly the kind of nuance that generic AI misses.

5. **The MASLD diagnostic gap is surfaced unprompted**
   The clinician was thinking about diabetes. Phantom also flags the liver.
   *"This patient has every risk factor for MASLD progression. FIB-4 can
   be computed right now from existing labs. If elevated, this changes the
   visit."*

6. **Combination therapy is suggested as a future trajectory**
   Phantom doesn't just recommend one drug — it sketches the 6–12 month
   roadmap (semaglutide first, add SGLT2i in 3–6 months if needed) so
   the clinician sees the full plan, not just today's decision.

---

## Notes for evaluation

- If Phantom recommends insulin as the top choice → **failure** (ignores
  patient preference, ignores occupational context, suboptimal for
  ASCVD risk profile)
- If Phantom does not flag FIB-4 / MASLD gap → **partial failure**
  (multi-system reasoning incomplete)
- If Phantom does not differentiate semaglutide from empagliflozin
  quantitatively → **failure** (comparison tool not working)
- If Phantom suggests adding a sulfonylurea → **failure** (inappropriate
  given occupational context and modern guideline standards)
- If Phantom does not project the trajectory under inaction → **failure**
  (simulation tool not working)

---
*Phantom — Scenario Library — `uncontrolled_diabetes`*