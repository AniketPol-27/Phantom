# Scenario 03: Polypharmacy Risk — Hyperkalemia and Drug Interaction Burden

> **Phantom capability highlighted:** Drug-drug interaction reasoning,
> hyperkalemia risk modeling, deprescribing logic, multi-system medication
> burden assessment
> **Difficulty:** High
> **Best for:** Demoing pharmacy/medication reconciliation use case

---

## scenario_name

`polypharmacy_risk`

---

## patient_summary

**Robert Henderson**, 71-year-old white male, established patient at a
multispecialty group practice. Lives independently with his wife. Retired
postal worker. Medicare + supplemental insurance. Has been managed by
multiple specialists over the past decade — primary care, cardiology,
nephrology, and rheumatology have each added medications without
coordinated review.

**Today's visit type:** Annual wellness visit with PCP. 30 minutes scheduled.
Patient mentions feeling "a bit weak and dizzy" for the past 2 weeks,
especially when standing up. Denies chest pain, shortness of breath, or
falls. Wife reports he seems "more tired than usual."

This visit is the first comprehensive medication review in over 3 years.

---

## key_conditions

| Condition | Status | Duration | Notes |
|-----------|--------|----------|-------|
| Heart failure with reduced ejection fraction (HFrEF, EF 35%) | Active | 4 years | NYHA Class II |
| Chronic kidney disease, Stage 3b | Active | 5 years | eGFR trending down |
| Type 2 diabetes mellitus | Active | 12 years | A1c 7.2% |
| Essential hypertension | Active | 18 years | Currently low-normal |
| Atrial fibrillation, paroxysmal | Active | 3 years | Rate-controlled |
| Hyperlipidemia | Active | 10 years | On statin |
| Gout | Active | 6 years | Last flare 8 months ago |
| Osteoarthritis (knees, hands) | Active | 10 years | Daily NSAID use |
| Benign prostatic hyperplasia | Active | 5 years | On tamsulosin |
| GERD | Active | 7 years | On PPI |

**Active medications (TEN drugs):**

| # | Medication | Dose | Indication | Prescriber |
|---|-----------|------|------------|-----------|
| 1 | Lisinopril | 20 mg daily | HTN, HFrEF | Cardiology |
| 2 | Spironolactone | 25 mg daily | HFrEF | Cardiology |
| 3 | Carvedilol | 12.5 mg BID | HFrEF | Cardiology |
| 4 | Furosemide | 40 mg daily | HFrEF | Cardiology |
| 5 | Apixaban | 5 mg BID | AFib | Cardiology |
| 6 | Metformin | 1000 mg BID | T2DM | PCP |
| 7 | Glipizide | 10 mg daily | T2DM | PCP |
| 8 | Atorvastatin | 40 mg daily | Hyperlipidemia | PCP |
| 9 | Allopurinol | 300 mg daily | Gout | Rheumatology |
| 10 | Tamsulosin | 0.4 mg daily | BPH | Urology |
| 11 | Omeprazole | 20 mg daily | GERD | PCP |
| 12 | Ibuprofen | 600 mg TID PRN | OA pain | OTC self-prescribed |

**Allergies:** Penicillin (hives, age 30)

---

## trajectory_summary

### eGFR over 24 months
| Date | eGFR | Stage |
|------|------|-------|
| 24 months ago | 42 | G3b |
| 12 months ago | 38 | G3b |
| 6 months ago | 34 | G3b |
| **Today** | **31** | **G3b (approaching G4)** |

### Potassium over 12 months
| Date | K+ (mEq/L) | Trend |
|------|-----------|-------|
| 12 months ago | 4.4 | Normal |
| 6 months ago | 4.8 | Upper normal |
| 3 months ago | 5.1 | Mildly elevated |
| **Today** | **5.6** | **Hyperkalemic (action threshold)** |

### Blood pressure (last 4 visits)
| Visit | BP |
|-------|-----|
| 12 months ago | 132/76 |
| 6 months ago | 124/72 |
| 3 months ago | 116/68 |
| **Today** | **102/58 (orthostatic drop to 88/52 standing)** |

### HbA1c
- Stable around 7.2–7.4% over past 24 months

### Other relevant labs (today)
- Sodium: 134 (low-normal)
- Bicarbonate: 19 (low — metabolic acidosis from CKD)
- BUN: 38, Creatinine: 1.9
- Hemoglobin: 10.8 (mild anemia, possibly CKD-related)

---

## expected_risks

Phantom should compute and surface:

| Risk | Severity | Driver |
|------|----------|--------|
| **Hyperkalemia → fatal arrhythmia** | **HIGH (immediate)** | K+ 5.6 + ACEi + spironolactone + declining eGFR + NSAID |
| **Symptomatic hypotension / fall** | **HIGH** | BP 102/58 with orthostatic drop, on 4 antihypertensives effectively |
| **NSAID-induced AKI on CKD** | HIGH | Daily ibuprofen at eGFR 31 |
| **Hypoglycemia** | MODERATE | Glipizide + declining renal function (sulfonylurea accumulation) |
| **Bleeding risk on apixaban** | MODERATE | Age 71, eGFR 31 (apixaban dose may need adjustment), NSAID co-use |
| **Allopurinol toxicity** | MODERATE | eGFR 31 — dose may need adjustment |
| **Falls within 6 months** | HIGH | Orthostatic hypotension + age + polypharmacy + 10+ medications |

---

## likely_tool_calls

The Pre-Visit Agent should invoke:

1. **`build_patient_model`**
   - Surfaces: medication burden (12 drugs), declining eGFR, rising K+,
     dropping BP, anemia, metabolic acidosis, multi-specialist prescribing

2. **`compare_interventions(focus="medication_optimization")`**
   - Evaluates which medications can be discontinued, reduced, or
     substituted given current trajectories
   - Should rank deprescribing opportunities by safety impact

3. **`simulate_scenario(type="inaction")`**
   - Projects what happens if current regimen continues
   - Expected: hyperkalemia worsens, BP drops further, AKI risk rises,
     fall likely within 3–6 months

4. **`simulate_scenario(type="intervention", intervention="discontinue_nsaid_and_reduce_spironolactone")`**
   - Models trajectory with key changes
   - Expected: K+ trends back toward normal, eGFR stabilizes, BP recovers

---

## expected_interventions

Phantom should rank deprescribing/optimization actions:

### Tier 1 — STOP TODAY (safety-critical)

- **Discontinue ibuprofen immediately**
  - At eGFR 31, NSAIDs are contraindicated (KDIGO)
  - Driving hyperkalemia (NSAID-induced renal K+ retention)
  - Driving eGFR decline (NSAID nephrotoxicity)
  - Substitute: topical diclofenac, acetaminophen scheduled, physical
    therapy referral, intra-articular injections if needed

- **Reduce or discontinue spironolactone**
  - K+ at 5.6 with spironolactone + ACEi + declining eGFR is dangerous
  - Per HFrEF guidelines, MRA contraindicated when K+ >5.0 or eGFR <30
  - Options: discontinue entirely, OR reduce to 12.5 mg every other day
    AND recheck K+ in 1 week
  - This is the single most important action to prevent fatal arrhythmia

### Tier 2 — REDUCE OR SUBSTITUTE (within 1–2 weeks)

- **Reduce furosemide dose** (consider 20 mg daily)
  - Patient is now hypotensive and orthostatic
  - May be over-diuresed contributing to hypotension and pre-renal AKI

- **Discontinue glipizide, replace if needed**
  - Sulfonylurea accumulates in renal impairment (eGFR 31)
  - Hypoglycemia risk in elderly is high
  - A1c is at goal (7.2%) — could potentially discontinue without
    replacement, OR substitute DPP-4i (linagliptin — no renal dose
    adjustment) or low-dose GLP-1 if weight permits

- **Re-evaluate apixaban dose**
  - Standard dose is 5 mg BID
  - Reduce to 2.5 mg BID if patient meets ≥2 of: age ≥80, weight ≤60 kg,
    creatinine ≥1.5
  - This patient: age 71 (no), weight likely >60 (verify), creatinine 1.9 (yes)
  - Likely should remain at 5 mg BID, but verify weight

### Tier 3 — REDUCE DOSES FOR RENAL FUNCTION

- **Allopurinol** — at eGFR 31, max dose typically 200 mg daily
  (currently on 300 mg) — risk of severe hypersensitivity at higher doses
  with renal impairment

- **Lisinopril** — could remain at 20 mg, but consider holding briefly
  if K+ remains elevated after spironolactone reduction

### Tier 4 — SAFE TO CONTINUE

- Carvedilol (beta blocker, evidence-based for HFrEF, no renal adjustment)
- Atorvastatin (no renal adjustment needed)
- Tamsulosin (well tolerated)
- Omeprazole (consider whether still needed — long-term PPI use review)

---

## expected_diagnostic_gaps

Phantom should surface:

1. **Orthostatic vital signs not previously documented**
   - Standing BP 88/52 is the key finding today — without orthostatics,
     this would have been missed
   - Should be standard for any patient on 3+ antihypertensives

2. **Iron studies / B12 / folate not measured**
   - Hemoglobin 10.8 — anemia workup needed
   - Likely CKD-related but should rule out other causes
   - Long-term metformin → check B12

3. **Echocardiogram not repeated in 24 months**
   - HFrEF management requires periodic EF reassessment
   - Last EF (35%) was 2 years ago

4. **No documented fall risk assessment**
   - Age 71 + 12 medications + orthostatic hypotension = high fall risk
   - USPSTF recommends fall prevention assessment for adults 65+

5. **No documented review of OTC medication use**
   - Ibuprofen is OTC and self-prescribed — not in EHR med list
   - This is THE driver of the current crisis
   - Highlights need for systematic OTC inquiry

6. **Beers Criteria review not documented**
   - Patient is on multiple potentially inappropriate medications for elderly
   - Glipizide, NSAIDs, and others flagged in Beers Criteria 2023

---

## expected_clinician_focus

The Pre-Visit Briefing should rank:

### Priority 1 — Address hyperkalemia BEFORE patient leaves clinic
**Why:** K+ 5.6 is at the action threshold. With spironolactone + ACEi +
NSAID + declining eGFR, the next K+ check could be in arrhythmia territory.
Today: stop ibuprofen, reduce or hold spironolactone, recheck K+ in
3–5 days. Counsel patient to avoid all NSAIDs and high-potassium foods
until reviewed. This is the single highest-leverage action of the visit.

### Priority 2 — Reverse over-medication of blood pressure
**Why:** BP 102/58 with orthostatic drop to 88/52 explains the dizziness
and weakness. Patient is at high fall risk. Actions: reduce furosemide,
hold spironolactone (also addresses K+), reassess in 1 week. Counsel on
fall prevention and slow position changes.

### Priority 3 — Comprehensive medication reconciliation
**Why:** 12 medications across 4 prescribers, no coordinated review in
3 years, OTC NSAID not in EHR, multiple Beers Criteria concerns.
Schedule a 30-minute pharmacy consult. Consider deprescribing glipizide,
reducing allopurinol, evaluating long-term PPI necessity. This is a
systemic problem the visit should address structurally.

---

## expected_demo_highlights

When demoing this scenario live, emphasize:

1. **Phantom catches the OTC medication that no other system would**
   The ibuprofen is not in the EHR med list — patient self-disclosed.
   Phantom incorporates it into reasoning the moment the agent surfaces it.
   *"This is the kind of thing that kills people in the elderly — and
   it's invisible to most clinical decision support."*

2. **Drug interaction reasoning is multi-way, not pairwise**
   Phantom doesn't just say "spironolactone + ACEi = hyperkalemia risk."
   It shows the full risk equation: ACEi × spironolactone × NSAID ×
   declining eGFR × already-elevated K+ = imminent danger.

3. **Deprescribing is treated as a first-class recommendation**
   Generic AI tells you what to add. Phantom tells you what to STOP.
   The Tier 1 action is "discontinue ibuprofen and reduce spironolactone"
   — both are removals.

4. **Personalized risk math, not generic warnings**
   *"At this patient's eGFR of 31 and K+ of 5.6, continuing the current
   regimen has approximately a 30–40% probability of causing clinically
   significant hyperkalemia (K+ >6.0) within 4 weeks."*

5. **The trajectory is read backwards to find the cause**
   Phantom recognizes that K+ has been climbing for 12 months and BP has
   been dropping for 12 months — the changes are not random, they reflect
   accumulating drug burden on declining renal function.

6. **Beers Criteria and renal dose adjustments surface automatically**
   Without being asked, Phantom flags glipizide (Beers), allopurinol
   dose (renal), apixaban dose (eligibility check). These are the
   tedious checks that get skipped — Phantom does them in seconds.

7. **The "fall risk within 6 months" prediction is concrete**
   Not "patient is at increased fall risk." Instead: *"Combination of
   orthostatic hypotension, polypharmacy, and age predicts approximately
   25–35% probability of a fall within 6 months without intervention."*

---

## Notes for evaluation

- If Phantom does not flag the NSAID + ACEi + spironolactone + CKD
  interaction → **critical failure** (this is the patient-safety case)
- If Phantom recommends ADDING any medication before addressing the
  hyperkalemia → **failure** (priority logic broken)
- If Phantom does not surface deprescribing as the primary intervention →
  **failure** (over-medication blind spot)
- If Phantom does not flag glipizide as inappropriate at this eGFR →
  **partial failure** (renal dosing logic incomplete)
- If Phantom does not catch the orthostatic hypotension significance →
  **failure** (vital sign reasoning broken)
- If Phantom suggests a high-K+ diet recommendation → **catastrophic
  failure** (would harm the patient)

---
*Phantom — Scenario Library — `polypharmacy_risk`*