# Phantom Clinical Simulation

## Tagline

The patient digital twin for clinical reasoning. Simulate clinical scenarios against real patient data — before making decisions.

---

## Long Description

**Phantom is a clinical simulation server that lets AI agents answer the question every clinician asks but no software has ever answered: *what happens to this specific patient if I do this?*** Today, clinicians make medication decisions, dose adjustments, and diagnostic choices in real time, with no way to forecast downstream effects on a patient's interconnected systems. Phantom closes that gap. It transforms a patient's FHIR data into a computational digital twin that can be run forward in time, stressed with proposed interventions, and queried for projected outcomes across renal, cardiovascular, metabolic, and hepatic systems simultaneously.

**How it works:** Phantom ingests a patient's full FHIR R4 record — conditions, medications, labs, vitals, observations — and builds a structured patient model containing eGFR trajectory with statistical projections, ASCVD 10-year risk via the ACC/AHA Pooled Cohort Equations, FIB-4 hepatic fibrosis index, KDIGO 2024 risk staging, active care gaps evaluated against guideline rules, and diagnostic gaps detected from longitudinal lab patterns. AI agents then call simulation tools that apply drug-specific effect modifiers from a 21-drug knowledge base and trial-derived eGFR slope data (DAPA-CKD, EMPA-KIDNEY, CREDENCE, etc.) to project outcomes at 6, 12, and 24 months.

**What makes it different:** Phantom is grounded in structured clinical evidence, not LLM generation. Every output cites a specific clinical trial, PMID, or guideline. When the agent recommends empagliflozin for a patient with T2DM and CKD Stage 3a, the recommendation traces back to DAPA-CKD's drug-vs-placebo eGFR slope difference of +1.78 mL/min/1.73m²/year. When it flags a diagnostic gap for CKD-associated anemia, it traces back to KDIGO 2024 guidance and the patient's actual hemoglobin trajectory. Clinicians can trust the output because the reasoning is auditable.

**Who should use it:** Practicing clinicians who want pre-visit briefings that surface what matters most for the next patient. Clinical decision support teams looking to embed evidence-grounded simulation in their existing workflows. Agent developers building specialty-specific healthcare AI on the Po platform — Phantom provides the horizontal evidence layer that every clinical agent needs.

---

## Tools Provided

### `build_patient_model`

**For clinical decision-makers:** This tool is the foundation of every Phantom workflow. Given a patient's FHIR record, it constructs a structured computational model that captures not just current state, but trajectory — where this patient is headed if nothing changes. It calculates validated risk scores (CKD-EPI 2021 eGFR, ACC/AHA ASCVD 10-year risk, FIB-4 hepatic fibrosis index), runs linear regression on longitudinal labs to project values at 6/12/24 months with 95% confidence intervals, evaluates the patient against 25+ care gap rules, and detects diagnostic gaps from pattern recognition across the lab history. The output is a single structured object that downstream tools (and reasoning agents) can use without re-parsing raw FHIR.

### `simulate_scenario`

**For clinical decision-makers:** This is where the "what if" question gets answered. Given the patient model, this tool runs a forward simulation of any of four scenario types: a medication change ("what if I start empagliflozin?"), inaction ("what if I do nothing for 12 months?"), a diagnostic workup ("what if we work up the rising ALT?"), or a guideline action ("what if I follow the ADA recommendation here?"). The simulation applies trial-derived effect modifiers — not LLM guesses — to project the impact across renal, cardiovascular, metabolic, and hepatic systems simultaneously. Output includes projected lab values at 6/12/24 months, change in risk scores, time-to-event projections (e.g., dialysis), and citations to the trials supporting each modifier.

### `compare_interventions`

**For clinical decision-makers:** This tool is built for shared decision-making moments. Given a patient model and 2-4 candidate interventions (e.g., empagliflozin vs semaglutide vs tirzepatide for a patient with T2DM, obesity, and CKD), it runs each simulation in parallel and returns a personalized ranked comparison table covering HbA1c reduction, weight change, eGFR protection, cardiovascular benefit, contraindications for this patient, cost tier, and adherence considerations. The ranking is patient-specific — based on this patient's actual eGFR, BMI, and comorbidities — not population averages. Designed to fit directly into a 5-minute visit conversation about treatment options.

---

## Use Cases

### Pre-Visit Briefing Generation

Agents equipped with Phantom can transform a 90-second chart skim into a structured 1-page briefing. Clinician opens the patient chart, types "Prep me for my next patient," and receives a document with the patient snapshot, trajectory alert (where they're headed), top 3 visit priorities ranked by urgency, a decision comparison table for the most important treatment question, detected diagnostic gaps, and a suggested visit agenda with time blocks. Saves an estimated 18 minutes per visit while catching care gaps that manual chart review often misses.

### Medication Change Decision Support

When a clinician is considering adding, removing, or switching a medication, Phantom can simulate the projected impact across all affected systems before the order is written. For example: a nephrologist considering whether to add an SGLT2 inhibitor to a patient already on lisinopril and spironolactone can simulate the renoprotective benefit alongside the hyperkalemia risk, with citations to the relevant trials and the patient's actual potassium trajectory.

### Care Gap Identification

Phantom evaluates each patient against 25+ guideline-based care gap rules from ADA, ACC/AHA, KDIGO, USPSTF, and other major bodies. Gaps are flagged with priority, evidence grade, citation, and actionable recommendation. Particularly valuable before annual wellness visits and during care manager outreach.

### Risk Stratification

The validated risk equations (CKD-EPI 2021, ACC/AHA Pooled Cohort Equations, FIB-4, KDIGO 2024) make Phantom suitable for population-level risk stratification workflows. Agents can iterate over a panel of patients and surface the highest-risk individuals for proactive outreach.

### Diagnostic Gap Detection

Beyond guideline-based screening, Phantom detects diagnostic gaps from pattern recognition across longitudinal data: undiagnosed CKD-associated anemia from trending hemoglobin, MASLD from persistently elevated ALT, sleep apnea suspicion from a constellation of findings, triple-whammy nephrotoxicity from drug combinations, and 7 more pattern-based detection rules.

---

## Required FHIR Scopes

Phantom requires read access to the following FHIR R4 resources:

| Scope | Why It's Needed |
|-------|-----------------|
| `patient/Patient.rs` | Demographics for risk equation parameters (age, sex, race) |
| `patient/Condition.rs` | Active problem list — drives care gap evaluation, contraindication checks, and cascade modeling |
| `patient/Observation.rs` | Lab values and vital signs — the core input for trajectory regression and risk score calculation |
| `patient/MedicationRequest.rs` | Current medication list — drives interaction checks, contraindication checks, and effect modifier application |
| `patient/AllergyIntolerance.rs` | Drug allergy detection — surfaced as a hard contraindication during intervention simulation |
| `patient/Procedure.rs` | Recent procedures — informs screening status (last colonoscopy, last DEXA, etc.) |
| `patient/Immunization.rs` | Vaccination status — drives immunization care gap rules |
| `patient/Encounter.rs` | Visit history — provides temporal context for the briefing |

All access is read-only. Phantom never writes back to the FHIR server. SHARP-on-MCP context propagation handles authentication via SMART on FHIR JWT — Phantom never sees or stores credentials.

---

## Limitations

- **US population focus.** The ACC/AHA Pooled Cohort Equations are derived from US cohorts and validated for US populations. International users should interpret ASCVD risk scores with that limitation in mind.
- **Drug knowledge base coverage.** Phantom currently encodes 21 drugs across 11 therapeutic classes — focused on diabetes, cardiovascular, renal, and lipid management. Expansion to oncology, psychiatry, and rheumatology drugs is on the roadmap.
- **Decision support, not autonomous prescribing.** Phantom outputs are designed to support clinician decision-making, not replace it. Every recommendation surfaces evidence and trade-offs; the clinician makes the final call.
- **Simulation horizon.** Projections at 6, 12, and 24 months are based on linear trajectory extrapolation and trial-derived effect sizes. Longer-horizon projections (5+ years) carry significantly more uncertainty and are not currently exposed.
- **Pediatric coverage.** Phantom is currently optimized for adult patients. Pediatric-specific risk equations and dosing are not yet implemented.

---

## Disclaimer

Phantom is a clinical decision support tool intended for use by licensed healthcare professionals. It is not a substitute for clinical judgment, diagnosis, or treatment by a qualified clinician. All outputs are advisory only. Clinicians remain solely responsible for clinical decisions made for their patients. Phantom is not FDA-cleared as a medical device and is not intended for use in life-threatening situations or as the sole basis for any clinical decision. Use of Phantom is subject to the terms of the Prompt Opinion platform.