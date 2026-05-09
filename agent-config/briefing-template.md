# Pre-Visit Briefing — Output Template

This document defines the exact structure the Pre-Visit Intelligence Agent must follow when generating a Pre-Visit Briefing. Every section is required. Do not add sections not listed here. Do not skip sections.

The example patient used throughout: **Maria Santos, 58F** — T2DM (8 years), CKD Stage 3a, Hypertension, Obesity (BMI 34), Dyslipidemia. Medications: metformin, glipizide, lisinopril, furosemide, spironolactone, atorvastatin, ibuprofen PRN. HbA1c: 7.2% → 8.2% over 2 years. eGFR: declining at -4.2 mL/min/year (now 52). BP: 148/88. LDL: 128 mg/dL on atorvastatin.

---

## SECTION 1: HEADER

**Format:** Single line block
**Purpose:** Patient identification, visit context, data freshness
**Length:** 1 block, 4 lines

Required content: patient name, age + sex, visit date, generation timestamp, overall data confidence with per-system breakdown.

Format template:
- Line 1: PRE-VISIT BRIEFING | [Patient Name], [Age][Sex]
- Line 2: Visit: [YYYY-MM-DD] | Generated: [YYYY-MM-DD HH:MM]
- Line 3: Data Confidence: Overall [0.00-1.00]
- Line 4: (Labs: [x.xx] | Meds: [x.xx] | Vitals: [x.xx])

Example:
PRE-VISIT BRIEFING | Maria Santos, 58F
Visit: 2025-11-15 | Generated: 2025-11-15 08:30
Data Confidence: Overall 0.81
(Labs: 0.88 | Meds: 0.95 | Vitals: 0.72)

---

## SECTION 2: PATIENT SNAPSHOT

**Format:** 3-4 sentences, prose paragraph
**Purpose:** Clinical summary of who this patient is — the 30-second orientation before the visit
**Length:** 3-4 sentences maximum

Required content:
- Sentence 1: Demographics + active major conditions
- Sentence 2: Current treatment trajectory (what is happening despite therapy)
- Sentence 3: **Bold the single most important finding** the clinician must not miss
- Sentence 4 (optional): Key context that changes the visit plan

Example:
58-year-old female with Type 2 diabetes (8 years), CKD Stage 3a, hypertension, obesity (BMI 34), and dyslipidemia on 7 medications. HbA1c has risen from 7.2% to 8.2% over 2 years on metformin + glipizide, and eGFR is declining at -4.2 mL/min/year (now 52) without SGLT2i coverage. **She is on a triple nephrotoxic combination (lisinopril + furosemide + ibuprofen PRN) — this must be addressed today.** LDL remains 128 mg/dL on atorvastatin 40mg, suggesting statin intensification or addition of ezetimibe.

---

## SECTION 3: TRAJECTORY ALERT

**Format:** Structured block with bullet list and urgency rating
**Purpose:** Where this patient is heading in the next 12 months without intervention — the cost of inaction
**Length:** 4-6 bullet points + urgency rating + time-sensitivity statement

Required content:
- Projected key lab values at 12 months (from simulate_scenario inaction)
- Probability of disease-stage progression
- Active cascade effects triggered by inaction
- Urgency rating: CRITICAL / HIGH / MODERATE / LOW
- Time-sensitivity statement (why this visit, not the next)

Urgency rating definitions:
- 🔴 CRITICAL — irreversible harm likely without same-visit action
- 🟠 HIGH — intervention needed this visit or within 2 weeks
- 🟡 MODERATE — address within 1-3 months
- 🟢 LOW — routine follow-up acceptable

Example:

⚠️ TRAJECTORY ALERT — Urgency: 🟠 HIGH

Without intervention at today's visit:
- eGFR: 52 → ~42 mL/min/year at 12 months (CKD Stage 3b threshold: 45). Probability of staging to G3b within 12 months: 68%
- HbA1c: 8.2% → ~8.9% at 12 months (rising slope +0.35%/6 months)
- BP: 148/88 → projected 152/90 if untreated (worsening HTN-CKD cascade)
- Active cascades: Diabetes↔CKD bidirectional acceleration, CKD→anemia progression (Hgb 11.8, trending down)
- Triple whammy nephrotoxicity (lisinopril + furosemide + ibuprofen) is actively accelerating eGFR decline

Time sensitivity: SGLT2i initiation before eGFR falls below 20 preserves the treatment window. Current eGFR 52 is well within DAPA-CKD eligibility (eGFR 25-75). Each month of delay costs approximately 0.35 mL/min of irreversible nephron loss.

---

## SECTION 4: TOP VISIT PRIORITIES (RANKED 1-3)

**Format:** 3 numbered priorities, each with a structured block
**Purpose:** The 3 most important things to address this visit, ranked by clinical impact
**Length:** Exactly 3 priorities — if more exist, cut the lower ones

Required content per priority:
- Priority number + ⭐ star indicator for #1
- **Bold action title**
- Why it matters (1-2 sentences, quantified where possible)
- Specific recommendation with evidence citation in parentheses
- ⚡ Action item (what to do in this visit, specifically)

Example:

⭐ Priority 1: Initiate SGLT2 Inhibitor for CKD Protection

**Why it matters:** eGFR is declining at -4.2 mL/min/year in a patient with T2DM + CKD who has never received SGLT2i therapy. DAPA-CKD demonstrated 39% relative risk reduction in CKD progression (HR 0.61, NNT 19 over 2.4 years). EMPA-KIDNEY confirmed benefit down to eGFR 20. This patient's current eGFR of 52 is squarely within the treatment window.

**Recommendation:** Initiate empagliflozin 10mg daily or dapagliflozin 10mg daily. Check potassium before initiating (current K+ 5.0 on lisinopril + spironolactone — borderline). Discontinue ibuprofen same visit (triple whammy). (Source: DAPA-CKD NEJM 2020, EMPA-KIDNEY NEJM 2023, KDIGO 2024 Grade 1A)

⚡ Action: Order empagliflozin 10mg QD. Discontinue ibuprofen. Check K+ if not done in last 4 weeks.

Priority 2: Address Glycemic Deterioration

**Why it matters:** HbA1c has risen 1.0% over 2 years (7.2% → 8.2%) on metformin + glipizide, indicating secondary sulfonylurea failure. Adding SGLT2i will provide additional HbA1c lowering (~0.5-1.0%), but GLP-1 RA should be considered if HbA1c remains above target. Ongoing hyperglycemia accelerates nephropathy, neuropathy, and retinopathy.

**Recommendation:** SGLT2i initiation (Priority 1) will partially address this. If HbA1c remains above 7.5% at 3-month follow-up, add GLP-1 RA (semaglutide preferred — SUSTAIN-6 CV benefit data). Consider discontinuing glipizide if hypoglycemia risk is a concern with SGLT2i. (Source: ADA Standards of Care 2024, Section 9)

⚡ Action: Repeat HbA1c in 3 months post-SGLT2i initiation. Counsel patient on SGLT2i mechanism and signs of DKA.

Priority 3: Statin Intensification / LDL Target

**Why it matters:** LDL 128 mg/dL on atorvastatin 40mg in a patient with T2DM + CKD (10-year ASCVD risk ~15.8%). ADA/ACC target for diabetes + CKD is LDL < 70 mg/dL. Current LDL is 58 mg/dL above target.

**Recommendation:** Intensify to atorvastatin 80mg or switch to rosuvastatin 20-40mg. If LDL remains above 70 mg/dL, add ezetimibe 10mg (generic, low cost, well-tolerated). (Source: ACC/AHA 2018 Cholesterol Guideline, ADA Standards of Care 2024)

⚡ Action: Intensify statin today. Recheck lipids in 6-8 weeks.

---

## SECTION 5: DECISION POINT

**Format:** Clinical question + comparison table + recommendation paragraph
**Purpose:** The key clinical decision for this visit, with options presented side-by-side for clinician choice
**Length:** 1 question + 1 table + 2-3 sentences of recommendation

Required content:
- Clinical question being decided (1 sentence)
- Comparison table with 2-4 options across key dimensions
- Recommended option with patient-specific reasoning
- Patient factors that drove the recommendation

Example:

**Clinical Question:** Which glucose-lowering agent should be added to metformin for this patient with T2DM + CKD Stage 3a + obesity?

| Dimension | Empagliflozin 10mg | Semaglutide 0.5mg | Insulin Glargine |
|---|---|---|---|
| HbA1c reduction | ~0.8% | ~1.4% | ~1.5-2.0% |
| Weight effect | -2 to -3 kg | -4 to -6 kg | +2 to +4 kg |
| eGFR protection | ✅ Strong (EMPA-KIDNEY) | ⚠️ Partial (FLOW) | ❌ None |
| CV benefit | ✅ EMPA-REG OUTCOME | ✅ SUSTAIN-6 | ❌ Not established |
| Hypoglycemia risk | Low | Low | Moderate-High |
| Cost | Moderate ($50-80/mo) | High ($800-900/mo) | Low ($30-50/mo) |
| Renal dose adjustment | Hold if eGFR < 20 | None needed | Caution |
| Composite score | 0.91 | 0.78 | 0.44 |

**Recommendation:** Empagliflozin is the preferred first addition for this patient. Her rapidly declining eGFR (-4.2 mL/min/year) makes renoprotection the highest-priority dimension, and empagliflozin has the strongest evidence base for CKD progression in T2DM (EMPA-KIDNEY, DAPA-CKD, CREDENCE). Semaglutide is a strong second agent if HbA1c remains above target after SGLT2i initiation.

**Patient-specific factors:** eGFR 52 (within SGLT2i window), K+ 5.0 (check before initiating — borderline with current RAAS therapy), BMI 34 (weight loss benefit relevant), ibuprofen PRN (must discontinue with any SGLT2i initiation).

---

## SECTION 6: DIAGNOSTIC GAPS DETECTED

**Format:** Bulleted list
**Purpose:** Conditions that may be present but are not yet diagnosed, based on lab and clinical patterns
**Length:** 3-5 bullets maximum

Required content per gap:
- **Bold suspected condition** + likelihood qualifier
- Data pattern that triggered it (specific values)
- Recommended workup (specific tests)

Example:

- **CKD-associated anemia (likely):** Hgb 11.8 g/dL (trending down from 12.4 over 15 months) in CKD Stage 3a without anemia on problem list. KDIGO 2024: evaluate anemia in CKD eGFR < 60. Workup: reticulocyte count, iron panel, ferritin, TSAT, consider EPO level.

- **MASLD (possible):** ALT persistently elevated (42 → 51 U/L over 18 months) in patient with T2DM + obesity (BMI 34) without liver diagnosis. FIB-4 = 1.8 (indeterminate zone). Workup: fibroscan or MR elastography, rule out viral hepatitis, hepatology referral if FIB-4 > 2.67.

- **Obstructive sleep apnea (possible):** Obesity (BMI 34) + hypertension + T2DM without OSA diagnosis — classic OSA phenotype. Untreated OSA worsens glycemic control and BP. Workup: STOP-BANG questionnaire today, home sleep test if score ≥ 3.

- **Diabetic neuropathy (unscreened):** 8-year diabetes history without documented neuropathy assessment on chart. ADA 2024: annual monofilament testing from diagnosis. Workup: 10g monofilament + 128Hz vibration testing at today's visit (takes 3 minutes).

---

## SECTION 7: SUGGESTED VISIT AGENDA

**Format:** 3 numbered versions by available time
**Purpose:** Help the clinician allocate limited visit time to highest-value activities
**Length:** 3 versions — 10 minutes, 20 minutes, 30 minutes

Required content per version:
- Time blocks with specific topics
- Prioritized to fit the time available
- Must-do items come first in every version

Example:

If you have 10 minutes:
1. (0-2 min) Confirm ibuprofen PRN use → discontinue today
2. (2-6 min) Discuss SGLT2i initiation (empagliflozin 10mg) — mechanism, benefit, genital hygiene counseling, when to hold
3. (6-9 min) Check K+ result if available. E-prescribe empagliflozin.
4. (9-10 min) Schedule 3-month follow-up (HbA1c, BMP, BP recheck)

If you have 20 minutes:
1. (0-2 min) Brief interval history (symptoms, medication adherence, any new concerns)
2. (2-8 min) Discuss SGLT2i initiation + discontinue ibuprofen
3. (8-12 min) Review HbA1c trend — discuss glycemic goals and 3-month plan
4. (12-16 min) BP 148/88 — review medication adherence, discuss uptitration of lisinopril vs adding amlodipine
5. (16-19 min) Order labs (BMP, HbA1c, lipid panel, CBC, UA/UACR)
6. (19-20 min) Confirm follow-up

If you have 30 minutes:
1. (0-3 min) Interval history + medication review
2. (3-10 min) SGLT2i discussion + discontinue ibuprofen + statin intensification
3. (10-15 min) Glycemic review — HbA1c trend, hypoglycemia episodes, discuss semaglutide as future option
4. (15-19 min) BP management discussion
5. (19-22 min) Neuropathy screening (monofilament — do it now)
6. (22-25 min) Review diagnostic gaps — discuss OSA screening (STOP-BANG), order liver labs for MASLD workup
7. (25-28 min) Order all labs + referrals
8. (28-30 min) Patient questions + confirm follow-up plan

---

## SECTION 8: ORDERS TO PLACE TODAY

**Format:** Bulleted lists organized by category
**Purpose:** Specific, actionable orders — ready to place in the EHR

Required categories:
- Labs (with brief reasoning for each)
- Referrals (with specialty and indication)
- Imaging (if applicable, otherwise state "None indicated today")
- Follow-up appointment recommendation

Example:

Labs:
- BMP (potassium before SGLT2i initiation, renal function baseline)
- HbA1c (baseline before therapy change)
- Lipid panel (LDL target assessment — last result 14 months ago)
- CBC with differential (trending anemia workup)
- Iron panel + ferritin + TSAT (CKD-anemia workup)
- Urine albumin/creatinine ratio (UACR — CKD monitoring, last 6 months)
- ALT/AST + bilirubin (MASLD workup — ALT trending up)
- Vitamin D 25-OH (CKD-MBD screening — not checked in 2 years)

Referrals:
- Nephrology: CKD Stage 3a with rapid decline (-4.2 mL/min/year), KDIGO "high risk" category — co-management recommended
- Ophthalmology: Diabetic retinopathy screening — overdue (last exam date not on record)
- Hepatology (conditional): If FIB-4 > 2.67 on today's labs, refer for fibroscan

Imaging:
- None indicated today

Follow-up:
- 3 months: BMP recheck (potassium on SGLT2i + RAAS), HbA1c, BP
- 6 months: Lipid panel recheck post-statin intensification

---

## SECTION 9: DOCUMENTATION STARTER

**Format:** Pre-drafted assessment and plan — clinician edits before signing
**Purpose:** Save documentation time; ensure key findings are captured
**Length:** Full A&P — clinician should edit, not rewrite from scratch

**Note to clinician:** This is a draft. Edit to reflect your clinical judgment and any information gathered during the visit before signing.

Example:

ASSESSMENT AND PLAN

58-year-old female with Type 2 diabetes mellitus (8 years), CKD Stage 3a (eGFR 52, declining at -4.2 mL/min/year), essential hypertension, obesity (BMI 34), and dyslipidemia presenting for diabetes/CKD follow-up.

1. TYPE 2 DIABETES MELLITUS — SUBOPTIMALLY CONTROLLED
   HbA1c 8.2% (rising from 7.2% over 2 years), indicating progressive glycemic failure on current regimen (metformin 1000mg BID + glipizide 10mg BID).
   Plan:
   - Initiate empagliflozin 10mg QD (renoprotection + glycemic benefit)
   - Discontinue ibuprofen PRN (nephrotoxic; triple whammy with lisinopril + furosemide)
   - Repeat HbA1c in 3 months; if above 7.5%, consider adding semaglutide
   - Counseled patient on SGLT2i mechanism, hydration, and when to hold (procedures, poor PO intake)

2. CHRONIC KIDNEY DISEASE STAGE 3a — RAPIDLY PROGRESSIVE
   eGFR 52 mL/min/1.73m2, declining at estimated -4.2 mL/min/year. KDIGO risk category: High. UACR 120 mg/g (category A2, rising).
   Plan:
   - Initiate SGLT2i as above (KDIGO 2024 Grade 1A recommendation)
   - Check BMP today (potassium — patient on lisinopril + spironolactone, K+ 5.0 at last check)
   - Nephrology referral placed (rapid decline, KDIGO high risk)
   - CKD-anemia workup ordered (Hgb 11.8, trending down): CBC, iron panel, ferritin, TSAT
   - Vitamin D 25-OH ordered (CKD-MBD screening)
   - UACR ordered

3. HYPERTENSION — ABOVE TARGET
   BP 148/88 today. Target < 130/80 (ACC/AHA 2017, ADA 2024).
   Plan:
   - Reinforce medication adherence
   - Consider uptitrating lisinopril (current 20mg) after confirming potassium is acceptable
   - Recheck BP at 3-month visit

4. DYSLIPIDEMIA — LDL ABOVE TARGET
   LDL 128 mg/dL on atorvastatin 40mg. Target < 70 mg/dL (T2DM + CKD, ACC/AHA 2018).
   Plan:
   - Intensify to atorvastatin 80mg daily
   - Recheck lipid panel in 6-8 weeks
   - If LDL remains > 70 mg/dL, add ezetimibe 10mg

5. OBESITY — BMI 34
   Plan:
   - SGLT2i will provide modest weight loss (~2-3 kg)
   - Discussed GLP-1 RA (semaglutide) as future option for additional glycemic control + weight loss if HbA1c above target at follow-up
   - Nutrition referral discussed; patient to consider

6. DIAGNOSTIC WORKUP INITIATED
   - MASLD: ALT trending up in metabolic syndrome context — liver panel ordered, FIB-4 to be calculated from today's labs
   - OSA: STOP-BANG administered today (score: ___/8); home sleep test ordered if score ≥ 3
   - Neuropathy: Monofilament + vibration testing performed today (results: ___)

FOLLOW-UP: 3 months with BMP, HbA1c, BP recheck. 6 months with lipid panel. Ophthalmology referral placed for diabetic retinopathy screening.

---

## SECTION 10: CONFIDENCE FOOTER

**Format:** 1-3 lines bordered block
**Purpose:** Transparency about data quality — what to trust, what to verify
**Length:** Maximum 3 lines

Required content:
- Per-system confidence rating
- Notable data gaps or stale data
- Any data the clinician should verify at the visit

Confidence scale:
- 0.9-1.0: High confidence — recent, complete, verified data
- 0.7-0.89: Good confidence — mostly recent with minor gaps
- 0.5-0.69: Moderate confidence — some stale or missing data
- Below 0.5: Low confidence — significant data gaps, interpret carefully

Example:

DATA CONFIDENCE
Labs: 0.88 (Good) — BMP 6 weeks old; lipid panel 14 months old ⚠️
Medications: 0.95 (High) — reconciled at last visit; ibuprofen PRN use frequency unverified
Vitals: 0.72 (Good) — BP from last visit; no today's BP yet
Notable gap: Ophthalmology records not in EHR — retinopathy status unknown

---

## TEMPLATE USAGE NOTES

1. All 10 sections are required. Do not skip any section.
2. Fill every section with real tool output data. No placeholder text in the final output — replace all bracketed placeholders with actual values.
3. If a section has no findings (e.g., no diagnostic gaps), write: "No diagnostic gaps identified with current data."
4. The Documentation Starter is a draft. Label it clearly as such. The clinician must review and edit before signing.
5. Bold is reserved for the most important finding in Section 2 and action titles in Section 4. Do not bold other text.
6. Total briefing length (excluding Documentation Starter): target 500-600 words. The Documentation Starter adds ~300-400 words and is expected to be longer.