# Phantom Use Cases

This document grounds Phantom in the day-to-day realities of clinical practice. Three personas illustrate the kinds of clinicians who would equip Phantom in their workflow. Five end-to-end use cases walk through specific scenarios where Phantom changes the outcome.

---

## User Personas

### Persona 1: Dr. Sarah Lee — Primary Care Physician

**Role:** Internal medicine physician, primary care
**Setting:** Federally Qualified Health Center (FQHC) in Atlanta, GA
**Patient panel:** ~1,800 patients, predominantly Medicaid and uninsured
**Daily volume:** 18-24 patients, with morning blocks of 8 patients in 4 hours
**Time per chart prep:** 90 seconds (realistic), 30 seconds (typical)

**Pain points:**
- Patients she sees once or twice a year arrive with 2-3 chronic conditions and no continuity narrative — she has to rebuild the clinical picture from scratch in each visit
- Care gaps that span multiple specialties (a diabetic with rising LDL, declining eGFR, overdue mammogram, and rising A1c) routinely fall through the cracks because no single piece of EHR alerting catches all of them
- She knows she should be considering SGLT2 inhibitors and GLP-1 agonists more aggressively, but the time cost of looking up trial evidence per-patient is prohibitive
- Diagnostic gaps (the patient with persistent ALT elevation that nobody has worked up for MASLD) are the most professionally distressing thing she encounters

**How Phantom helps:**
- Pre-visit briefings condense 24 months of labs, vitals, and conditions into a 1-page document she can scan in the 90 seconds before walking into the room
- Care gaps are surfaced with priority ranking, so she knows which one to address *today* vs. defer to a follow-up
- Decision points come pre-populated with a comparison table — she can have a 90-second shared decision-making conversation with the patient without leaving the room to look anything up
- Diagnostic gaps are flagged with explanation and recommended workup — she can place the order without running a separate differential

**Daily workflow with Phantom:**
1. 7:45am — Opens her schedule for the morning, reviews 8 patient names
2. 7:50am — For each patient, opens the Pre-Visit Intelligence Agent, types "Prep me for my next patient"
3. 7:51am — Receives 1-page briefing per patient; spends 60-90 seconds reviewing each
4. 8:00am — First patient walks in. Sarah already knows: rising eGFR slope, missing SGLT2i, ALT trending up
5. 8:00–8:15am — Visit. Addresses the SGLT2i gap (initiates empagliflozin), orders FIB-4 and abdominal ultrasound for MASLD workup, schedules diabetes education referral
6. 8:15am — Documentation prefilled by Phantom; Sarah edits and signs in 60 seconds
7. Repeat for 7 more patients
8. 12:00pm — Sarah finishes morning block having addressed care gaps that would have taken weeks to surface through traditional alerting

---

### Persona 2: Dr. James Chen — Endocrinologist

**Role:** Endocrinologist with a focus on complex diabetes
**Setting:** Academic medical center, outpatient clinic
**Patient panel:** ~600 patients, mostly tertiary referrals
**Daily volume:** 4 new consults + 8 follow-ups
**Time per chart prep:** 5-10 minutes for new consults, 2-3 minutes for follow-ups

**Pain points:**
- New consults arrive with massive outside records (sometimes 200+ pages of PDFs) that he has to synthesize manually
- He's expected to make tertiary-level recommendations on patients with multiple competing comorbidities — every recommendation requires balancing renal, cardiovascular, weight, and glycemic effects simultaneously
- Trial evidence is changing fast (SURPASS, FLOW, SELECT trials in the last 18 months alone) — staying current is a constant struggle
- Insurance prior authorizations require him to document why a specific drug was chosen *for this patient* — generic justifications get denied

**How Phantom helps:**
- The patient model collapses outside records into a structured digital twin he can reason against directly
- The `compare_interventions` tool runs head-to-head simulations across the metabolic-cardiovascular-renal axis, producing a personalized ranking that captures all the competing considerations
- Trial citations on every recommendation make prior authorization documentation effectively automatic
- The simulation engine surfaces *why* a particular drug is best for *this* patient (e.g., "DAPA-CKD inclusion criteria match closely")

**Daily workflow with Phantom:**
1. 8:00am — First new consult: 62-year-old with poorly controlled T2DM, CKD Stage 3b, NAFLD, BMI 38
2. 8:00–8:05am — Opens the Pre-Visit Agent. The briefing surfaces: SGLT2i gap, GLP-1 gap, FIB-4 = 2.8 (suggests advanced fibrosis), missing hep B vaccination
3. 8:05–8:10am — Reviews the comparison table for second-line glycemic agents: tirzepatide ranked #1 for this patient (highest weight loss, FIB-4 reduction in SURPASS-4 sub-analysis, modest renoprotection)
4. 8:15am — Patient walks in. James spends the visit on shared decision-making rather than chart review
5. 8:45am — Documentation drafted from briefing template; James edits and signs
6. Prior authorization for tirzepatide submitted with auto-populated trial citations. Approved on first pass.

---

### Persona 3: Maria Rodriguez, NP — Nephrology Nurse Practitioner

**Role:** Nurse practitioner specializing in CKD management
**Setting:** Outpatient nephrology practice
**Patient panel:** ~400 patients, predominantly CKD Stage 3-5
**Daily volume:** 12-14 patients
**Time per chart prep:** 3-5 minutes

**Pain points:**
- Most of her work is *trajectory monitoring* — is this patient progressing faster than expected? Should we adjust anything? — but the EHR doesn't compute trajectory in any usable way
- Patients on ACEi + spironolactone + diuretic regimens require constant potassium monitoring and dose adjustment; getting the timing wrong leads to ER visits
- Identifying who needs a transplant referral and when is a constant struggle — current practice is "eGFR drops below 20" but ideally would be predictive
- CKD-mineral bone disorder, anemia, acidosis are routinely under-managed because they require coordinating across multiple specialty domains

**How Phantom helps:**
- Trajectory regression on eGFR with 95% prediction intervals is *exactly* the data she needs to anticipate progression
- The simulation engine projects time-to-dialysis under current management, which gives her a defensible objective basis for transplant referral timing
- Cascade modifiers surface CKD complications (anemia, MBD, acidosis) that are guideline-required but often missed
- The hyperkalemia interaction between ACEi + spironolactone + low eGFR is automatically flagged in the patient model

**Daily workflow with Phantom:**
1. Each morning, Maria runs Phantom's risk stratification across her panel
2. Patients with rapid eGFR decline (>5 mL/min/year) are pulled to the top — Maria proactively reaches out for unscheduled visits
3. During visits, Maria uses Phantom's simulation tools to model dose adjustments before changing anything
4. Transplant referrals are made with Phantom's projected time-to-dialysis as the supporting documentation

---

## End-to-End Use Cases

### Use Case 1: Pre-Visit Preparation for Chronic Disease Patient

**Setting:** Primary care, morning rush
**Trigger:** Dr. Sarah Lee opens the next patient's chart 5 minutes before the scheduled visit time
**Patient:** Maria Santos, 58F, T2DM × 8 years, CKD Stage 3a × 2 years, HTN, obesity (BMI 34)

**Step-by-step workflow:**
1. Sarah opens the Pre-Visit Intelligence Agent within Po
2. Po automatically propagates Maria's patient context via SHARP headers
3. Sarah types: *"Prep me for my next patient"*
4. Agent calls `build_patient_model` — receives structured patient state including 24-month eGFR trajectory (-6.5 mL/min/year, classified as rapid)
5. Agent calls `simulate_scenario` with `scenario_type="inaction"` — projects eGFR will drop to 41 in 12 months
6. Agent calls `simulate_scenario` with `scenario_type="diagnostic_workup"` for the rising ALT pattern
7. Agent calls `compare_interventions` for empagliflozin, semaglutide, tirzepatide
8. Agent composes the briefing using the 10-section template

**Tools invoked:** `build_patient_model`, `simulate_scenario` (×2), `compare_interventions`

**Outcome:** Sarah receives a 1-page briefing with:
- Trajectory alert: rapid eGFR decline, projected to G3b in 12 months
- Top priority: initiate SGLT2i (gap)
- Decision point: empagliflozin ranked #1 for this patient (renoprotection priority)
- Diagnostic gaps: MASLD workup (persistent ALT >40), CKD-anemia screening (Hb trending down)
- Suggested visit agenda with time blocks for a 20-minute slot
- Pre-drafted orders: empagliflozin 10mg daily, FIB-4, abdominal ultrasound, iron studies

**Time saved:** 18 minutes (vs. manual chart review and lookups)
**Quality improvement:** Catches the MASLD diagnostic gap that would otherwise wait until next year's labs

---

### Use Case 2: Medication Change Decision Support

**Setting:** Endocrinology consult
**Trigger:** Dr. James Chen is weighing whether to add an SGLT2 inhibitor to a patient already on lisinopril and spironolactone
**Patient:** 67M, T2DM, HFrEF (EF 38%), CKD Stage 3b (eGFR 38), recent K+ = 4.9

**Step-by-step workflow:**
1. James asks the agent: *"What happens if I add empagliflozin to this patient?"*
2. Agent calls `build_patient_model`
3. Agent calls `simulate_scenario` with the proposed intervention
4. Simulation surfaces:
   - Renal: projected eGFR slope improves from -3.2 to -1.4 mL/min/year
   - HF: hospitalization risk reduced (HR 0.65, EMPA-REG/EMPEROR-Reduced)
   - Hyperkalemia risk: small additional risk on top of existing ACEi+MRA, K+ projected to rise 0.1-0.2
   - Genitourinary infection: elevated risk in male diabetic with eGFR <45 (~15% in first 6 months)

**Outcome:** James proceeds with empagliflozin 10mg, schedules a 4-week K+ check, counsels on GU hygiene. The decision is documented with simulation citations for the chart.

---

### Use Case 3: Care Gap Identification Before Annual Wellness Visit

**Setting:** Primary care, AWV preparation
**Trigger:** Patient is on Sarah's panel but hasn't been seen in 9 months; AWV scheduled
**Patient:** 71F, hypertension, hyperlipidemia, prediabetes, no known CKD

**Step-by-step workflow:**
1. Sarah opens the agent the day before the AWV
2. She asks: *"What care gaps does this patient have?"*
3. Agent calls `build_patient_model` with `include_care_gaps=true`
4. Briefing surfaces:
   - Mammogram overdue (last in 2022)
   - Colonoscopy overdue (last in 2018)
   - DEXA never done (woman over 65)
   - Pneumococcal vaccine never given
   - Statin underutilization (her ASCVD 10-year risk is 18%, currently on no statin)
   - Diabetes screening overdue (last A1c 2 years ago, was 6.1%)

**Outcome:** Sarah enters the visit with a checklist. She addresses all 6 gaps in 25 minutes — in a "normal" workflow she'd have addressed maybe 2 of them.

---

### Use Case 4: Risk Stratification for High-Risk Patient Panel

**Setting:** Care management workflow
**Trigger:** Maria Rodriguez (NP) wants to identify her highest-risk CKD patients for proactive outreach this week
**Population:** 400 patients, all CKD Stage 3+

**Step-by-step workflow:**
1. Maria's care management agent iterates over the panel
2. For each patient, calls `build_patient_model` (lightweight: trajectories only, no comparison)
3. Filters patients where:
   - eGFR slope < -5 mL/min/year (rapid decline), OR
   - Projected eGFR at 12 months will cross a stage boundary, OR
   - Diagnostic gap "hyperkalemia risk" or "triple whammy nephrotoxicity" detected
4. Returns a ranked list of 14 patients

**Outcome:** Maria proactively schedules 14 unscheduled outreach calls. Three of those patients are caught before an ER visit; one is found to need urgent transplant referral.

---

### Use Case 5: Diagnostic Reasoning Support for a Complex Case

**Setting:** Primary care, undifferentiated symptom workup
**Trigger:** Patient presents with fatigue, weight gain, and new edema. Sarah is uncertain about the differential
**Patient:** 54F, hypertension on HCTZ, otherwise healthy

**Step-by-step workflow:**
1. Sarah asks the agent: *"What diagnostic gaps should I think about for this patient?"*
2. Agent calls `build_patient_model` with `include_diagnostic_gaps=true`
3. Briefing surfaces:
   - Hypothyroidism (no TSH in 3 years, fatigue + weight gain pattern)
   - Sleep apnea (BMI 32, hypertension, fatigue cluster)
   - Heart failure with preserved EF (new edema + uncontrolled HTN)
   - Hyponatremia possibility (long-term HCTZ)
4. Each gap has a recommended workup

**Outcome:** Sarah orders TSH, BMP (sodium), echocardiogram, and refers for sleep study. The differential is now structured rather than gestalt.

---

## Cross-Cutting Themes

Across all five use cases, three properties of Phantom matter most:

1. **Time compression.** Phantom turns 15-30 minutes of chart review into 60-90 seconds of structured briefing reading.
2. **Coverage completeness.** Multi-system care gap and diagnostic gap detection catches things that human cognition routinely misses under time pressure.
3. **Decision auditability.** Every recommendation cites a trial, guideline, and the patient-specific reasoning — so the clinician can defend the decision in documentation, prior authorization, or peer review.

These three properties are what make Phantom valuable not just to individual clinicians but to the systems they work within - health plans see better quality metrics, health systems see fewer ER visits, and patients see better outcomes from earlier intervention.