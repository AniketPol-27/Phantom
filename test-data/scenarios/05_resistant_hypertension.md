# Scenario 05: Resistant Hypertension — Suspected Secondary Cause

> **Phantom capability highlighted:** Diagnostic workup reasoning,
> secondary HTN evaluation, structured differential generation,
> medication optimization in resistant disease
> **Difficulty:** High
> **Best for:** Demoing diagnostic reasoning support and how Phantom
> helps clinicians escape "just add another drug" reflex

---

## scenario_name

`resistant_hypertension`

---

## patient_summary

**Marcus Johnson**, 46-year-old African American male, established patient
at a primary care clinic. Works in IT operations, married, two children.
Commercial insurance through employer. Engaged in his health — checks BP
at home regularly, generally adherent to medications, exercises 3x weekly.
No tobacco use. Drinks 2–3 beers on weekends. No recreational drug use.
No NSAID use, no decongestant use, no licorice consumption.

**Today's visit type:** BP follow-up. 20 minutes scheduled. Patient is
frustrated. He has been on three antihypertensive medications for the past
8 months and his blood pressure remains uncontrolled both in clinic and
at home. He asks: *"What are we missing?"*

This is the right question. He has resistant hypertension by definition,
and a secondary cause workup has never been initiated.

---

## key_conditions

| Condition | Status | Duration | Notes |
|-----------|--------|----------|-------|
| Essential hypertension | Active, uncontrolled | 6 years | "Resistant" by JNC criteria |
| Obesity (Class I) | Active | 8 years | BMI 32.4 |
| Hyperlipidemia | Active | 4 years | On statin |
| Obstructive sleep apnea | Suspected, undiagnosed | Unknown | Loud snoring per spouse, witnessed apneas |

**Active medications:**
- Lisinopril 40 mg daily (max dose)
- Amlodipine 10 mg daily (max dose)
- Hydrochlorothiazide 25 mg daily
- Atorvastatin 20 mg daily

**Allergies:** None known

**Adherence assessment:**
- Pharmacy refill records confirm 95%+ medication possession ratio
- Home BP log shows consistent twice-daily measurements
- Patient brings written log of dates and values to every visit

---

## trajectory_summary

### In-clinic blood pressure (last 6 visits)
| Date | BP | Notes |
|------|-----|-------|
| 12 months ago | 158/96 | On lisinopril + HCTZ |
| 9 months ago | 154/94 | Added amlodipine |
| 6 months ago | 150/92 | Up-titrated lisinopril to 40 |
| 3 months ago | 148/90 | Up-titrated amlodipine to 10 |
| 1 month ago | 146/92 | All three meds at max or near-max |
| **Today** | **150/94** | **Unchanged despite optimization** |

### Home BP log (averages over past 3 months)
- Morning average: 148/92
- Evening average: 144/90
- Weekend average: 147/91
- **No significant difference between clinic and home — rules out
  white-coat hypertension**
- **No significant nocturnal dipping pattern available** (no overnight
  monitoring done)

### Definition check: Resistant hypertension
American Heart Association definition: BP above target despite use of
3 antihypertensive medications of different classes — including a
diuretic — at maximally tolerated doses, OR controlled BP requiring 4+
medications.

**Marcus meets criteria for resistant hypertension.**

### Other relevant labs (recent)
- Potassium: 3.4 (low-normal, mildly hypokalemic — NOTE: relevant to
  primary aldosteronism workup)
- Sodium: 142
- Bicarbonate: 26
- Creatinine: 1.0 (eGFR 92 — normal renal function)
- HbA1c: 5.8% (no diabetes)
- TSH: 2.1 (normal)
- UACR: 35 mg/g (mildly elevated A2 — early hypertensive nephropathy)
- LDL: 88 (at goal)
- 10-year ASCVD risk: ~14% (intermediate)

### Physical exam findings (today)
- BMI 32.4
- Neck circumference: 17.5 inches (elevated — OSA risk)
- Abdominal exam: no bruits
- No abdominal striae, no buffalo hump (Cushing's features absent)
- No tremor, no exophthalmos (hyperthyroid features absent)
- Normal pulses, no radio-femoral delay (coarctation features absent)

---

## expected_risks

Phantom should compute and surface:

| Risk | Value | Driver |
|------|-------|--------|
| **Stroke (10-year)** | Substantially elevated | Sustained BP >150/90 |
| **Hypertensive nephropathy progression** | HIGH | UACR already in A2 range |
| **Left ventricular hypertrophy / HFpEF** | HIGH if untreated | Sustained pressure load |
| **Untreated secondary HTN** | HIGH probability | African American, age <50, resistant pattern, hypokalemia |
| **Untreated OSA contributing to BP** | MODERATE-HIGH probability | Obesity, snoring, witnessed apneas, neck circumference |
| **10-year ASCVD risk** | ~14% (intermediate) | Pooled Cohort Equations |

---

## likely_tool_calls

The Pre-Visit Agent should invoke:

1. **`build_patient_model`**
   - Surfaces: resistant HTN by definition, low-normal K+ (red flag for
     primary aldosteronism), suspected OSA, early hypertensive
     nephropathy (UACR 35), good adherence pattern

2. **`simulate_scenario(type="diagnostic_gap")`**
   - Identifies that secondary HTN workup has never been initiated
   - Generates structured differential of secondary causes
   - Surfaces specific tests for each

3. **`simulate_scenario(type="inaction")`**
   - Projects 5-year cardiovascular and renal trajectory if BP remains
     uncontrolled
   - Expected: significant rise in stroke risk, progressive nephropathy,
     possible LVH/HFpEF development

4. **`compare_interventions(focus="resistant_htn_optimization")`**
   - Evaluates next-line antihypertensive choices
   - Should rank spironolactone (per PATHWAY-2) above further dose
     escalation or beta blocker addition

---

## expected_interventions

Phantom should rank actions:

### Tier 1 — Diagnostic workup (TODAY)

The structured secondary HTN differential Phantom should generate:

**1. Primary aldosteronism (highest pre-test probability)**
- Why: African American + age <50 + resistant HTN + low-normal K+
- Test: aldosterone-to-renin ratio (ARR)
- Important: should ideally be off MRAs and ACEi/ARB for accurate
  testing — but ARR can be screened on these meds with awareness of
  interpretation caveats
- Estimated prevalence in resistant HTN: 15–20%

**2. Obstructive sleep apnea**
- Why: obesity, snoring, witnessed apneas, neck circumference 17.5
- Test: home sleep apnea test or polysomnography
- Estimated contribution to BP: treating OSA reduces BP by 5–10 mmHg
  in adherent CPAP users
- Estimated prevalence in resistant HTN: 60–80%

**3. Renovascular disease (renal artery stenosis)**
- Why: resistant HTN, possible — though pre-test probability lower in
  this age group than in elderly
- Test: renal duplex ultrasound (initial), MRA if duplex suggestive
- Less likely but should not be missed

**4. Pheochromocytoma (lower probability)**
- Why: completeness — though no episodic symptoms (headaches, palpitations,
  diaphoresis) reported
- Test: plasma free metanephrines OR 24-hour urine metanephrines
- Lower yield, but standard in workup

**5. Cushing's syndrome (lower probability)**
- Why: completeness — though no clinical features
- Test: late-night salivary cortisol, 24-hour urine free cortisol, or
  overnight dexamethasone suppression test
- Lower yield given absence of physical findings

**6. Thyroid dysfunction**
- Already screened — TSH 2.1 normal — can be set aside

### Tier 2 — Therapeutic optimization (this visit)

- **Add spironolactone 25 mg daily**
  - Evidence: PATHWAY-2 trial showed spironolactone superior to bisoprolol
    or doxazosin as 4th-line agent in resistant HTN
  - Particularly effective in patients with primary aldosteronism (which
    this patient may have)
  - Caveats: monitor K+ and renal function in 1–2 weeks
  - Note: if ARR testing is being pursued, may want to delay starting
    spironolactone until after testing OR test in awareness of confounding

- **Switch HCTZ to chlorthalidone 12.5–25 mg daily**
  - Chlorthalidone has longer half-life and superior 24-hour BP control
  - Evidence: ALLHAT and other trials suggest greater morbidity/mortality
    benefit
  - Could be done independently of spironolactone decision

- **Verify medication adherence with pharmacy data** (already confirmed
  — but document this)

### Tier 3 — Lifestyle intensification

- **Sodium restriction to <2,000 mg/day** — discuss with patient and
  consider dietitian referral (resistant HTN often has higher sodium
  sensitivity)
- **DASH diet emphasis** — particularly potassium-rich foods (relevant
  given low-normal K+)
- **Weight loss target: 5–10% of body weight** — every 1 kg lost ≈
  1 mmHg BP reduction
- **Alcohol moderation** — 2–3 beers on weekends is within limits but
  worth noting
- **Continued exercise** — already doing well

### Tier 4 — Specialist referrals

- **Hypertension specialist or nephrology** — if secondary workup
  unrevealing OR if primary aldosteronism is confirmed, specialist
  management is appropriate
- **Sleep medicine** — if OSA confirmed by sleep study
- **Cardiology** — if echocardiogram shows LVH or diastolic dysfunction

---

## expected_diagnostic_gaps

Phantom should surface:

1. **Aldosterone-to-renin ratio (ARR) never measured**
   - Most important diagnostic test in this patient
   - Primary aldosteronism is underdiagnosed, especially in African
     American patients with resistant HTN

2. **Sleep study never performed**
   - Multiple OSA risk factors present
   - High prevalence in resistant HTN population

3. **Echocardiogram not on file**
   - Resistant HTN at age 46 — assess for LVH and diastolic function
   - Baseline for monitoring response to treatment

4. **Plasma metanephrines not checked**
   - Standard in resistant HTN workup
   - Low yield but high consequence if missed

5. **Renal duplex ultrasound not performed**
   - Renovascular disease consideration

6. **24-hour ambulatory BP monitoring (ABPM) not done**
   - Gold standard for confirming resistant HTN diagnosis
   - Assesses nocturnal dipping pattern (non-dipping is independent CV
     risk factor)

7. **No documented dietary sodium assessment**
   - Resistant HTN patients often have unrecognized high sodium intake
   - 24-hour urine sodium would quantify this

8. **No retinal exam for hypertensive retinopathy**
   - Useful for staging end-organ damage

9. **Colorectal cancer screening status**
   - Age 46, African American — should have started screening at age 45
     per USPSTF (lowered from 50 in 2021)

---

## expected_clinician_focus

The Pre-Visit Briefing should rank:

### Priority 1 — Initiate secondary HTN workup TODAY
**Why:** This patient has met criteria for resistant hypertension for at
least 6 months. Secondary causes should have been investigated long ago.
The clinical pattern (African American, age <50, low-normal K+, resistant
to 3 medications including a diuretic) raises pre-test probability of
primary aldosteronism to 15–20% — essentially equivalent to the
prevalence of asymptomatic Hashimoto's. Order: ARR, plasma metanephrines,
sleep study referral, renal duplex ultrasound, echocardiogram. This
single action transforms the visit from "add another pill" to "find the
cause."

### Priority 2 — Add spironolactone as 4th-line agent
**Why:** While workup is pending, BP optimization continues. PATHWAY-2
trial established spironolactone as the highest-yield 4th-line agent in
resistant HTN — especially in patients who may have undetected primary
aldosteronism (which is exactly this patient). Start 25 mg daily, recheck
K+ and creatinine in 1–2 weeks. Note: if ARR is pursued before starting
spironolactone, results are cleaner.

### Priority 3 — Switch HCTZ to chlorthalidone
**Why:** Chlorthalidone provides superior 24-hour BP control and has
better cardiovascular outcomes data than HCTZ in resistant disease. This
is an evidence-based optimization that costs nothing and can be done at
the same visit.

---

## expected_demo_highlights

When demoing this scenario live, emphasize:

1. **Phantom escapes the "add another drug" reflex**
   The default clinical response to uncontrolled BP is to add or up-titrate.
   Phantom recognizes that this patient is at the *end* of that road and
   redirects to the diagnostic workup that should have happened first.
   *"This is what experienced clinicians do — but it requires pattern
   recognition that takes years to develop. Phantom does it in seconds."*

2. **Pattern recognition surfaces the primary aldosteronism flag**
   Low-normal K+ in a resistant HTN patient is a clinical pearl most
   clinicians know but easily overlook in a 20-minute visit. Phantom
   foregrounds it with the right context: *"K+ of 3.4 in a patient on
   HCTZ AND lisinopril is unexpectedly low — primary aldosteronism should
   be ruled out."*

3. **Structured differential, not vague suggestions**
   Generic AI says: "consider secondary causes." Phantom says: "Here are
   the 5 most likely secondary causes in order of pre-test probability,
   here are the specific tests for each, here is what each test costs and
   when you should be off other medications for accurate results."

4. **Population-aware reasoning**
   African American patients have higher prevalence of primary
   aldosteronism and worse outcomes from uncontrolled HTN. Phantom
   incorporates this without making assumptions about individual patients
   — it informs pre-test probability, not categorical decisions.

5. **PATHWAY-2 evidence is cited, not implied**
   The recommendation for spironolactone as the next agent isn't generic.
   It's backed by a specific trial that ranked the options head-to-head.
   Judges can see the trial-level evidence behind the suggestion.

6. **OSA is treated as a contributing factor, not an unrelated comorbidity**
   Phantom recognizes that untreated OSA is a major driver of resistant
   HTN — and surfaces the sleep study referral as part of the BP workup,
   not as a separate concern.

7. **The visit is reframed**
   The patient came in expecting another medication change. Phantom
   reframes it as: *"This is the visit where we figure out why the BP
   isn't responding — and that's better news than another pill."*

---

## Notes for evaluation

- If Phantom recommends adding a 4th drug WITHOUT initiating secondary
  workup → **failure** (misses the diagnostic shift)
- If Phantom does not surface primary aldosteronism as the top differential
  → **failure** (pattern recognition broken — low K+ in resistant HTN is
  a textbook flag)
- If Phantom does not recommend ARR testing → **failure** (key diagnostic
  test missing)
- If Phantom does not surface OSA as a likely contributor → **partial
  failure** (multi-factor reasoning incomplete)
- If Phantom recommends a beta blocker as 4th-line over spironolactone
  → **failure** (PATHWAY-2 evidence not applied)
- If Phantom does not differentiate chlorthalidone from HCTZ → **partial
  failure** (medication-specific knowledge incomplete)
- If Phantom assumes non-adherence without pharmacy data → **failure**
  (unfair attribution; data shows adherence)

---
*Phantom — Scenario Library — `resistant_hypertension`*