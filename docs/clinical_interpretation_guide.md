# Phantom Clinical Interpretation Guide

> **Purpose:** Standardized clinical language and interpretation rules
> for all Phantom outputs. This guide ensures every briefing, comparison,
> diagnostic gap analysis, and trajectory projection uses consistent
> terminology, urgency levels, confidence framing, and evidence citation
> style.
>
> **Audience:** Phantom developers, prompt engineers, agent designers,
> evaluators, and any consuming agent.
>
> **Status:** Living document — update as evidence base evolves.

---

## Table of Contents

1. [Trajectory Severity Interpretation](#1-trajectory-severity-interpretation)
2. [Risk Interpretation Language](#2-risk-interpretation-language)
3. [Urgency Classification](#3-urgency-classification)
4. [Confidence Interpretation](#4-confidence-interpretation)
5. [Evidence Citation Style](#5-evidence-citation-style)
6. [General Tone & Voice](#6-general-tone--voice)

---

## 1. Trajectory Severity Interpretation

A "trajectory" is a longitudinal pattern in a single clinical marker
(eGFR, HbA1c, BP, weight, platelets, etc.) over time. Phantom must
classify trajectories using consistent language so clinicians can
compare findings across visits and across patients.

### General trajectory categories

| Category | Definition | Standard phrasing |
|----------|-----------|-------------------|
| **Stable** | No clinically meaningful change | *"Trajectory is stable over [time period]."* |
| **Mild decline** | Slow worsening, below clinical action threshold | *"Mild decline observed — within expected range, monitor."* |
| **Moderate decline** | Worsening above expected aging rate | *"Moderate decline — warrants attention but not urgent."* |
| **Rapid decline** | Above guideline-defined rapid-progression threshold | *"Rapid decline — urgent intervention warranted."* |
| **Critical decline** | Imminent organ-threatening trajectory | *"Critical decline — immediate clinical action required."* |

### eGFR slope interpretation

| Slope (mL/min/1.73m²/year) | Category | Standard phrasing |
|---------------------------|----------|-------------------|
| ≤ 1 (decline) | **Stable** | *"eGFR is stable at [value]."* |
| 1–3 | **Expected aging** | *"eGFR decline within expected aging range."* |
| 3–5 | **Mild progression** | *"Mild CKD progression — slope of [X] mL/min/year."* |
| 5–10 | **Rapid progression** (KDIGO) | *"**Rapid progression** per KDIGO — slope of [X] mL/min/year exceeds the 5 mL/min/year threshold."* |
| > 10 | **Critical decline** | *"**Critical decline** — investigate for AKI, nephrotoxin exposure, or other reversible cause."* |

**Example phrasing for the briefing:**
> *"Maria's eGFR has declined from 62 to 44 mL/min over 36 months —
> a slope of approximately −6 mL/min/year. This meets KDIGO criteria
> for rapid progression and warrants intervention."*

### HbA1c trajectory interpretation

| Pattern | Category | Standard phrasing |
|---------|----------|-------------------|
| Stable at goal (<7.0%) | **At goal** | *"HbA1c stable at goal."* |
| Stable above goal | **Persistently uncontrolled** | *"HbA1c persistently above target — consider escalation."* |
| Rising < 0.5%/year | **Mild upward drift** | *"Mild upward trend — re-examine adherence and barriers."* |
| Rising 0.5–1.0%/year | **Moderate worsening** | *"Worsening glycemic control — escalation indicated."* |
| Rising > 1.0%/year | **Rapid worsening** | *"**Rapid glycemic decompensation** — urgent escalation needed."* |

### Blood pressure trajectory interpretation

| Pattern | Category | Standard phrasing |
|---------|----------|-------------------|
| Stable at <130/80 | **At goal** | *"BP stable at goal."* |
| Stable above goal | **Uncontrolled** | *"BP persistently above target."* |
| Rising slowly | **Trending upward** | *"BP trending upward — escalate or intensify."* |
| Sudden rise (>20 mmHg systolic) | **Acute change** | *"**Acute BP rise** — investigate cause (medication non-adherence, secondary HTN, NSAID use, etc.)."* |
| Sudden drop (>20 mmHg systolic) | **Acute change** | *"**Acute BP drop** — assess for over-medication, fluid loss, sepsis, falls risk."* |

### Universal trajectory phrasing rules

- **Always include the slope or rate of change**, not just current value
- **Always reference the time window** (e.g., "over 12 months")
- **Always tie to a guideline threshold** when one exists
- **Use bold for category labels** (Rapid progression, Critical decline)
- **Avoid vague phrases** like "things are getting worse" — quantify

---

## 2. Risk Interpretation Language

Phantom must communicate risk in language that is clinically meaningful,
actionable, and honest about uncertainty.

### General risk-tier vocabulary

| Tier | Definition | Standard phrasing |
|------|-----------|-------------------|
| **Very low** | Below population baseline | *"Risk is below average for this patient's age and sex."* |
| **Low** | At or below population baseline | *"Risk is in the lower range — continue current management."* |
| **Moderate** | Elevated above baseline, monitor | *"Moderate risk — preventive intervention worth discussing."* |
| **High** | Substantially elevated, intervention warranted | *"High risk — preventive intervention indicated."* |
| **Very high** | Imminent or near-certain risk | *"Very high risk — immediate intervention warranted."* |

### ASCVD risk (10-year, ACC/AHA Pooled Cohort Equations)

| Score | Category | Standard phrasing |
|-------|----------|-------------------|
| <5% | **Low** | *"10-year ASCVD risk: [X]% — low risk."* |
| 5–7.4% | **Borderline** | *"Borderline ASCVD risk — consider risk-enhancing factors."* |
| 7.5–19.9% | **Intermediate** | *"Intermediate ASCVD risk — discuss statin therapy."* |
| ≥20% | **High** | *"High ASCVD risk — high-intensity statin recommended."* |

**Example:**
> *"James's 10-year ASCVD risk is approximately 18% (intermediate-high).
> This is the population in which SUSTAIN-6 and EMPA-REG OUTCOME showed
> the most consistent CV benefit."*

### CKD progression risk

| Indicator | Category | Standard phrasing |
|-----------|----------|-------------------|
| eGFR slope <3 mL/min/yr, UACR <30 | **Low** | *"Low CKD progression risk — annual monitoring."* |
| eGFR slope 3–5 OR UACR 30–300 | **Moderate** | *"Moderate progression risk — optimize BP and glycemia."* |
| eGFR slope >5 OR UACR >300 | **High** | *"**High** progression risk — initiate renoprotective therapy."* |
| KFRE 5-year >10% | **Very high** | *"**Very high** kidney failure risk — nephrology referral."* |

### MASLD fibrosis risk (FIB-4 based)

| FIB-4 score | Category | Standard phrasing |
|-------------|----------|-------------------|
| <1.30 | **Low** | *"Low fibrosis probability — advanced fibrosis effectively excluded."* |
| 1.30–2.67 | **Indeterminate** | *"Indeterminate FIB-4 — non-invasive fibrosis staging (FibroScan) warranted."* |
| >2.67 | **High** | *"**High** fibrosis probability — hepatology referral indicated."* |

### Medication burden risk

| Number of meds + complexity | Category | Standard phrasing |
|----------------------------|----------|-------------------|
| <5 meds | **Low** | *"Medication burden is manageable."* |
| 5–9 meds | **Moderate** | *"Polypharmacy present — annual reconciliation recommended."* |
| ≥10 meds OR Beers Criteria flags | **High** | *"**High** medication burden — comprehensive review and deprescribing opportunities indicated."* |
| Drug-drug or drug-disease interaction present | **Critical** | *"**Critical** interaction risk — address before patient leaves visit."* |

### Universal risk phrasing rules

- **Always quote the numeric value** when available (e.g., "18%", not "elevated")
- **Always cite the source equation or trial** (e.g., "per ACC/AHA PCE")
- **Always couple risk with an action** ("...warrants statin discussion")
- **Avoid alarm without action** — don't say "very high risk" without
  what to do about it
- **Use comparative framing** when helpful ("higher than 75% of patients
  her age")

---

## 3. Urgency Classification

Urgency is the answer to: *"How fast does this need to happen?"*

### Standard urgency levels

| Level | Time horizon | Standard phrasing | Example trigger |
|-------|--------------|-------------------|-----------------|
| **🟢 LOW** | Address at next routine visit (3–6 months) | *"Address at next routine visit."* | Mild lab abnormality, non-urgent screening overdue |
| **🟡 MODERATE** | Address within 30 days | *"Address within the next month."* | Worsening trajectory not yet at action threshold, intermediate risk findings |
| **🔴 HIGH** | Address at this visit or within 1 week | *"Address at today's visit."* | Trajectory crossing guideline threshold, missing high-yield diagnostic, suboptimal medication regimen |
| **🚨 CRITICAL** | Immediate — before patient leaves clinic | *"**Immediate clinical action required.**"* | Hyperkalemia, severe BP elevation/drop, suspected acute condition |

### Examples by urgency level

**🟢 LOW examples:**
- Vitamin D not measured in stable CKD Stage 3
- Cervical cancer screening due in next 6 months
- Mildly elevated triglycerides on otherwise controlled lipid panel

**🟡 MODERATE examples:**
- HbA1c rising from 7.0 → 7.4 over 12 months
- New microalbuminuria (UACR 30–60)
- Mild anemia in CKD without severe symptoms
- BMI increase of 5% over 12 months

**🔴 HIGH examples:**
- eGFR slope ≥5 mL/min/year (rapid progression)
- HbA1c ≥9% in a patient not on insulin or GLP-1
- Resistant hypertension without secondary workup
- FIB-4 ≥2.67 with no hepatology referral

**🚨 CRITICAL examples:**
- Potassium ≥5.5 in patient on ACEi + MRA + NSAID
- Symptomatic orthostatic hypotension on ≥3 antihypertensives
- Hemoglobin <8 in non-dialysis patient
- Acute eGFR drop ≥30% from baseline
- Suspected acute coronary syndrome, stroke symptoms

### Urgency phrasing rules

- **Always pair urgency with an action verb** ("address," "investigate,"
  "discontinue," "refer")
- **Always anchor to time** ("today," "within 30 days," "before patient
  leaves")
- **Use the emoji + label combination** for visual scanning
  (🚨 CRITICAL, 🔴 HIGH, 🟡 MODERATE, 🟢 LOW)
- **Reserve CRITICAL for safety-of-life issues** — overuse erodes trust
- **Never escalate urgency without justification** — clinicians lose
  trust in over-alarming systems

---

## 4. Confidence Interpretation

Phantom must be honest about how confident it is in each output. Every
significant claim should carry a confidence label.

### Standard confidence levels

| Level | When to use | Standard phrasing |
|-------|-------------|-------------------|
| **High** | Multiple data points, validated equation, trial-level evidence | *"High confidence — based on [N] data points and validated equation."* |
| **Moderate** | Limited data, extrapolation from trials, indirect evidence | *"Moderate confidence — trial population overlaps but is not identical to this patient."* |
| **Low** | Sparse data, multiple assumptions, weak evidence | *"Low confidence — limited data available; consider repeat measurement."* |
| **Insufficient data** | Cannot make a meaningful claim | *"**Insufficient data** to project trajectory — additional measurements needed."* |

### Confidence by output type

| Output | Drivers of HIGH confidence | Drivers of LOW confidence |
|--------|---------------------------|--------------------------|
| **Trajectory projection** | ≥5 longitudinal data points, consistent slope, no missing intervals | <3 data points, irregular intervals, recent acute illness |
| **Risk score** | Validated equation, all inputs available | Missing inputs (proxies used), patient outside equation's derivation population |
| **Intervention ranking** | Direct trial evidence in matching population | Trial population substantially different from this patient |
| **Diagnostic gap detection** | Clear guideline rule with explicit thresholds | Inferred from indirect evidence |
| **Drug interaction** | RxNorm-validated, well-documented mechanism | Theoretical or rare interaction |

### Honesty rules

- **Always declare confidence explicitly** at the bottom of every
  significant output
- **When confidence is moderate or low, state WHY** — don't just say
  "moderate"
- **List limitations as a separate section** — don't bury them
- **Never fabricate confidence** — if data is insufficient, say so
- **Use "approximately" and ranges** when point estimates are not
  warranted ("eGFR ~38 ± 4")

### Sample confidence footer (use this template):

```markdown
## Confidence Assessment

| Component | Confidence | Basis |
|-----------|-----------|-------|
| [Claim 1] | **High** | [Reason] |
| [Claim 2] | **Moderate** | [Reason] |
| [Claim 3] | **Low** | [Reason] |

**Limitations:**
- [Limitation 1]
- [Limitation 2]
- [Limitation 3]
```

---

## 5. Evidence Citation Style

Every clinical claim Phantom makes should be traceable to a source.
The format must be consistent so consuming agents and clinicians can
verify.

### Sources Phantom may cite

1. **Clinical trials** (e.g., DAPA-CKD, SUSTAIN-6)
2. **Practice guidelines** (e.g., KDIGO 2024, ADA 2024 Standards of Care)
3. **Risk equations** (e.g., CKD-EPI 2021, Pooled Cohort Equations)
4. **USPSTF recommendations** (e.g., USPSTF Grade A/B/C/D/I)
5. **Drug labels and RxNorm data**

### Citation format rules

#### Trial citations

**Format:** `[Trial Name] ([Journal] [Year], [First Author])`

**Examples:**
- *"Per DAPA-CKD (NEJM 2020, Heerspink et al.), HR 0.61 for CKD progression."*
- *"SUSTAIN-6 (NEJM 2016, Marso et al.) showed HR 0.74 for 3-point MACE."*

**Required elements:**
- Trial name (acronym)
- Journal (NEJM, Lancet, JAMA, Circulation, etc.)
- Year of publication
- First author + "et al."
- The specific outcome and effect size being cited

#### Guideline citations

**Format:** `[Organization] [Year] [Guideline Name]`

**Examples:**
- *"Per ADA Standards of Care 2024, Section 12: Retinopathy."*
- *"KDIGO 2024 Clinical Practice Guideline for CKD."*
- *"ACC/AHA 2017 Hypertension Guideline."*

#### USPSTF citations

**Format:** `USPSTF [Year], Grade [Letter]`

**Examples:**
- *"USPSTF 2021, Grade A: colorectal cancer screening starting age 45."*
- *"USPSTF 2020, Grade B: hepatitis C screening, all adults 18–79."*

#### Risk equation citations

**Format:** `[Equation Name] ([Source Year])`

**Examples:**
- *"CKD-EPI 2021 (NEJM 2021, Inker et al.) — race-free creatinine equation."*
- *"Kidney Failure Risk Equation, 4-variable (Tangri et al., JAMA 2011)."*

### Evidence strength language

When the underlying evidence is graded, mirror that grade:

| Evidence quality | Standard phrasing |
|-----------------|-------------------|
| RCT, large trial, replicated | *"Strong evidence from [trial]."* |
| RCT, single trial | *"Trial-level evidence from [trial]."* |
| Observational, large cohort | *"Cohort-level evidence."* |
| Expert consensus, guideline opinion | *"Per [guideline] expert consensus."* |
| Mechanism / extrapolation | *"Based on mechanism — direct trial evidence is limited."* |
| No evidence | *"Limited evidence — clinical judgment required."* |

### What NOT to do

- ❌ Vague citations: *"Studies show..."*, *"Research suggests..."*
- ❌ Unverifiable claims: *"It is well known that..."*
- ❌ Overstating evidence: *"definitively proven"* when the trial showed
  *"associated with"*
- ❌ Citing without effect size: *"DAPA-CKD showed benefit"* (what
  benefit? What size?)
- ❌ Citing the wrong direction: e.g., quoting EMPA-REG OUTCOME for renal
  outcomes when it was a CV trial (it had renal secondary outcomes, but
  the primary citation should be precise)

---

## 6. General Tone & Voice

Phantom outputs should sound like a senior clinical colleague — informed,
calibrated, and respectful of the clinician's expertise.

### Voice principles

| Do | Don't |
|----|-------|
| Be specific and quantified | Be vague or hand-wavy |
| State uncertainty honestly | Pretend to certainty you don't have |
| Pair every concern with an action | Raise concerns without guidance |
| Cite evidence inline | Make unsupported claims |
| Respect the clinician's judgment | Override clinical decision-making |
| Use clinical language correctly | Over-explain basic terminology |
| Be concise — every word should earn its place | Pad with filler phrases |

### Clinician-respecting framing

| Avoid | Prefer |
|-------|--------|
| *"You should..."* | *"Consider..."* / *"Indicated..."* |
| *"You missed..."* | *"Diagnostic gap detected:"* |
| *"You need to..."* | *"Recommended next step:"* |
| *"Don't..."* | *"Caution:..."* / *"Avoid..."* |
| *"This is wrong"* | *"This may warrant reconsideration"* |

### Patient-respecting language

- Refer to the patient by name when known (humanizes the briefing)
- Avoid stigmatizing terms ("non-compliant" → "adherence challenges")
- Acknowledge social determinants without assumptions
- Treat patient preferences as a clinical input, not an obstacle

### Length and density

- **Briefings:** comprehensive but scannable — use tables, headers, bullets
- **Comparisons:** dense tables + short prose for "why this ranking"
- **Diagnostic gap analyses:** structured by gap, with clear actions
- **Trajectory projections:** numeric + visual (ASCII charts) + prose
  interpretation

### Final voice rule

Phantom is a **decision-support colleague**, not an authority figure.
Every output should feel like a thoughtful peer review of the case,
not a lecture or a rebuke.

---

## Appendix: Quick Reference Card

When writing or reviewing a Phantom output, check:

- [ ] Does every trajectory have a slope and time window?
- [ ] Does every risk have a numeric value and source?
- [ ] Does every urgency level have an action and timeline?
- [ ] Does every claim have a citation?
- [ ] Is confidence stated for major outputs?
- [ ] Are limitations disclosed?
- [ ] Is the tone collegial, not authoritative?
- [ ] Is the patient referred to by name?
- [ ] Are evidence sources verifiable (trial name, year, journal)?
- [ ] Could a clinician fact-check any claim within 60 seconds?

If yes to all → ship it.
If no to any → revise.

---

*Phantom — Clinical Interpretation Guide — v1.0*
*Maintained alongside the evidence base — update with each major guideline release.*