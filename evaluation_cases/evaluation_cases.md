# Phantom Evaluation Cases

> 10 benchmark cases covering Phantom's core capabilities.
> See `README.md` for usage instructions.

---

## Case 01 — Comprehensive Pre-Visit Briefing

**user_prompt:**
> *"Prep me for my next patient."*

**Patient:** Maria Santos
**Visit context:** Routine 6-month diabetes follow-up, 15 minutes scheduled

**expected_tools:**
1. `build_patient_model(patient_id="maria-santos-001")`
2. `simulate_scenario(scenario_type="inaction", horizon_months=24)`
3. `simulate_scenario(scenario_type="diagnostic_gap")`
4. `compare_interventions(options=["empagliflozin", "dapagliflozin", "semaglutide"])`

**expected_reasoning:**
- Recognize the rapid eGFR decline (−6 mL/min/year) as the dominant
  clinical issue
- Identify SGLT2 inhibitor as the highest-leverage intervention
- Surface the missing UACR as a critical diagnostic gap
- Flag glipizide as inappropriate as 2nd-line therapy in this patient
- Recognize BP is uncontrolled and HCTZ is suboptimal at eGFR <50

**expected_key_findings:**
- eGFR trajectory: rapid progression by KDIGO criteria
- Projected Stage 4 transition within 12–18 months without intervention
- UACR overdue by 6 months
- BP averaging 140/87 (above target)
- HbA1c trending upward

**expected_priorities:**
1. Initiate empagliflozin 10 mg daily
2. Order missing labs (UACR, BMP, lipid panel, vitamin D)
3. Optimize BP regimen (switch HCTZ to chlorthalidone OR add amlodipine)

**expected_failure_conditions:**
- ❌ Recommends adding insulin or sulfonylurea as primary intervention
- ❌ Does not surface the missing UACR
- ❌ Does not detect rapid eGFR progression
- ❌ Generates a generic A1c-focused briefing without renal context

---

## Case 02 — Risk Identification

**user_prompt:**
> *"What's the biggest risk for this patient?"*

**Patient:** Robert Henderson (polypharmacy patient, K+ 5.6)
**Visit context:** Annual wellness visit

**expected_tools:**
1. `build_patient_model(patient_id="robert-henderson-003")`
2. `simulate_scenario(scenario_type="inaction", horizon_months=6)` (optional)

**expected_reasoning:**
- Identify hyperkalemia (K+ 5.6) as the immediate, life-threatening risk
- Recognize the multi-factorial driver: ACEi + spironolactone + NSAID +
  declining eGFR
- Recognize fall risk as the second priority (orthostatic hypotension on
  multiple antihypertensives)
- Frame the problem as a polypharmacy crisis, not as individual abnormal
  values

**expected_key_findings:**
- K+ trending up over 12 months (4.4 → 5.6)
- BP trending down (132/76 → 102/58 with orthostatic drop)
- eGFR declining (42 → 31)
- 12 active medications including OTC ibuprofen
- Multiple Beers Criteria flags

**expected_priorities:**
1. Address hyperkalemia BEFORE patient leaves clinic
2. Reverse over-medication of blood pressure
3. Comprehensive medication reconciliation

**expected_failure_conditions:**
- ❌ Does not identify hyperkalemia as the top risk
- ❌ Does not connect NSAID + ACEi + spironolactone + CKD
- ❌ Recommends adding any new medication before deprescribing
- ❌ Does not flag fall risk
- ❌ Misses the orthostatic vital significance

---

## Case 03 — Inaction Simulation

**user_prompt:**
> *"What happens if we do nothing?"*

**Patient:** Maria Santos
**Visit context:** Patient asking about whether to start a new medication

**expected_tools:**
1. `build_patient_model(patient_id="maria-santos-001")`
2. `simulate_scenario(scenario_type="inaction", horizon_months=60)`

**expected_reasoning:**
- Project trajectory across multiple time horizons (6, 12, 18, 24, 36,
  60 months)
- Tie projections to clinical milestones (Stage 4 transition, dialysis
  evaluation)
- Quantify cardiovascular and quality-of-life consequences
- Acknowledge uncertainty and assumptions

**expected_key_findings:**
- Stage 4 transition projected within 12–18 months
- Dialysis evaluation likely within 4–5 years
- 5-year kidney failure risk: 12–18% (KFRE)
- Concurrent worsening of glycemic and BP control likely
- Polypharmacy complexity will increase as renal dosing becomes critical

**expected_priorities:**
1. Communicate the trajectory clearly to the patient
2. Frame the decision as time-sensitive
3. Quantify the difference vs intervention scenario

**expected_failure_conditions:**
- ❌ Generic "things will get worse" without quantification
- ❌ No timeline for clinical milestones
- ❌ No KFRE or other validated risk score
- ❌ Does not acknowledge uncertainty
- ❌ Does not contrast with intervention scenario

---

## Case 04 — Intervention Comparison

**user_prompt:**
> *"Compare semaglutide vs empagliflozin vs basal insulin for this
> patient."*

**Patient:** James Walker (uncontrolled T2DM, truck driver)
**Visit context:** Endocrinology consult for medication escalation

**expected_tools:**
1. `build_patient_model(patient_id="james-walker-002")`
2. `compare_interventions(options=["semaglutide", "empagliflozin", "basal_insulin"])`

**expected_reasoning:**
- Multi-dimensional comparison (A1c, weight, CV benefit, hypoglycemia,
  cost, occupational fit)
- Patient preference (declined insulin) treated as a clinical input
- Occupational context (truck driver, DOT exam, public safety)
  incorporated into ranking
- Consider combination pathway, not just single-agent decision

**expected_key_findings:**
- Semaglutide best fit (9/10) — addresses A1c, weight, CV risk, low
  hypoglycemia, weekly dosing
- Empagliflozin strong alternative (7/10 alone, 9/10 if combined)
- Insulin ranked third (4/10) — patient preference + occupational risk
- Combination pathway recommended over single-agent escalation

**expected_priorities:**
1. Initiate semaglutide today
2. Plan for SGLT2i addition at 3–6 months if needed
3. Reserve insulin for second-line escalation

**expected_failure_conditions:**
- ❌ Recommends insulin as top choice (ignores preference + occupation)
- ❌ Does not differentiate semaglutide from empagliflozin quantitatively
- ❌ Does not cite SUSTAIN-6 or EMPA-REG OUTCOME trial evidence
- ❌ Recommends sulfonylurea (would worsen hypoglycemia risk in driver)
- ❌ Does not acknowledge cost as a real-world factor

---

## Case 05 — Diagnostic Gap Detection

**user_prompt:**
> *"Are there any missed diagnoses I should look at?"*

**Patient:** Maria Santos
**Visit context:** Annual physical / diabetes follow-up

**expected_tools:**
1. `build_patient_model(patient_id="maria-santos-001")`
2. `simulate_scenario(scenario_type="diagnostic_gap")`

**expected_reasoning:**
- Surface gaps that change today's clinical decisions (high-priority)
- Surface gaps that should be addressed within 30 days (moderate)
- For each gap, explain WHY it matters now (not just "missing")
- Calculate FIB-4 from existing labs if applicable
- Group orderable items into a single workflow

**expected_key_findings:**
- CKD anemia not investigated (Hgb 10.8, no iron studies)
- Suspected MASLD never worked up (FIB-4 calculable from existing labs)
- Diabetic retinopathy screening overdue
- Sleep apnea suspected, never evaluated
- Diabetic foot exam overdue
- Vitamin D never measured

**expected_priorities:**
1. Address CKD anemia workup today (iron studies, B12, folate)
2. Calculate FIB-4 and order FibroScan for MASLD evaluation
3. Refer for retinopathy screening and OSA evaluation

**expected_failure_conditions:**
- ❌ Does not calculate FIB-4 from available labs
- ❌ Does not flag the CKD anemia
- ❌ Lists gaps without explaining clinical relevance
- ❌ Misses guideline-mandated screenings (foot exam, retinopathy)
- ❌ Generic recommendations without ordering specifics

---

## Case 06 — Order Recommendation

**user_prompt:**
> *"What should I order today?"*

**Patient:** Maria Santos
**Visit context:** Routine diabetes follow-up

**expected_tools:**
1. `build_patient_model(patient_id="maria-santos-001")`
2. `simulate_scenario(scenario_type="diagnostic_gap")`
3. `compare_interventions(options=["empagliflozin", "dapagliflozin"])`

**expected_reasoning:**
- Synthesize insights from patient model and gap analysis into a concrete
  order set
- Group orders by category (medications, labs, imaging, referrals,
  in-clinic procedures)
- Justify each order briefly
- Flag any pre-requisites (e.g., baseline labs before SGLT2i initiation)

**expected_key_findings:**
- Medications: start empagliflozin, discontinue glipizide, switch HCTZ
  to chlorthalidone
- Labs: UACR, BMP, lipid panel, vitamin D, CBC
- Imaging/Procedures: nothing immediate
- Referrals: ophthalmology, nephrology, podiatry (or in-clinic foot exam)
- Patient education: SGLT2i counseling, DASH diet handout

**expected_priorities:**
1. Start the empagliflozin and adjust regimen now
2. Send labs from same blood draw
3. Place referrals at end of visit

**expected_failure_conditions:**
- ❌ Recommends starting SGLT2i without baseline labs
- ❌ Does not recommend discontinuing glipizide
- ❌ Generic order list without rationale
- ❌ Misses key referrals (nephrology, ophthalmology)

---

## Case 07 — Causal Medication Reasoning

**user_prompt:**
> *"What medication is most likely worsening this patient's renal
> decline?"*

**Patient:** Robert Henderson
**Visit context:** Annual wellness visit, eGFR declining

**expected_tools:**
1. `build_patient_model(patient_id="robert-henderson-003")`
2. `compare_interventions(focus="medication_optimization")` (optional)

**expected_reasoning:**
- Identify NSAIDs (ibuprofen) as the primary culprit — direct
  nephrotoxicity at eGFR 31
- Identify the synergistic effect of NSAID + ACEi + diuretic on renal
  perfusion
- Recognize the OTC nature of ibuprofen — not in EHR med list, only
  caught via patient inquiry
- Secondary contributors: declining cardiac function + furosemide
  over-diuresis (pre-renal component)

**expected_key_findings:**
- Ibuprofen 600 mg TID is the highest-impact medication driving decline
- NSAID + ACEi + spironolactone + diuretic = "triple whammy" effect
- OTC medication missed by standard EHR review
- Furosemide may be over-dosed contributing to pre-renal component

**expected_priorities:**
1. Discontinue ibuprofen immediately
2. Reduce furosemide dose
3. Counsel on NSAID avoidance for life

**expected_failure_conditions:**
- ❌ Does not identify NSAID as the primary culprit
- ❌ Misses the NSAID + ACEi interaction
- ❌ Recommends adding a "kidney-protective" medication without first
  removing the offender
- ❌ Does not explain the "triple whammy" mechanism

---

## Case 08 — Time-Constrained Prioritization

**user_prompt:**
> *"What should I focus on in a 10-minute visit?"*

**Patient:** Maria Santos
**Visit context:** Tight schedule, only 10 minutes available

**expected_tools:**
1. `build_patient_model(patient_id="maria-santos-001")`
2. (Lightweight invocation — no need for full simulation chain)

**expected_reasoning:**
- Triage to the single highest-leverage action
- Recognize that not everything fits in 10 minutes
- Defer lower-priority items to a follow-up visit with clear scheduling
- Provide a minute-by-minute mini-agenda

**expected_key_findings:**
- THE highest-leverage action: initiate empagliflozin
- Second highest: order UACR (single test, takes seconds)
- Defer: BP regimen optimization, full lab workup, referral discussions
- Schedule 30-minute follow-up in 4 weeks for the rest

**expected_priorities:**
1. Start empagliflozin (5 minutes including counseling)
2. Order UACR in same draw as anything routine (1 minute)
3. Schedule extended follow-up visit (1 minute)

**expected_failure_conditions:**
- ❌ Tries to address everything in 10 minutes (unrealistic)
- ❌ Generic "see what's most important" without specific action
- ❌ Does not explicitly defer items
- ❌ Does not schedule follow-up

---

## Case 09 — Trajectory Severity Ranking

**user_prompt:**
> *"Which trajectory worries you most for this patient?"*

**Patient:** Marcus Johnson (resistant hypertension)
**Visit context:** BP follow-up, patient frustrated

**expected_tools:**
1. `build_patient_model(patient_id="marcus-johnson-005")`

**expected_reasoning:**
- Compare multiple trajectories: BP (uncontrolled, sustained),
  potassium (low-normal trending), UACR (early hypertensive nephropathy),
  weight (stable)
- Rank by severity AND reversibility
- Identify BP as the dominant concern with multi-organ implications
- Surface the low-K+ pattern as a diagnostic clue (primary aldosteronism)

**expected_key_findings:**
- BP trajectory: uncontrolled despite max-dose triple therapy (most
  worrying)
- Potassium trajectory: low-normal (3.4) — consistent with aldosterone
  excess, NOT just from HCTZ alone
- UACR trajectory: 35 mg/g — early hypertensive nephropathy already
  present
- Weight: stable (not contributing)

**expected_priorities:**
1. BP trajectory is the dominant clinical concern
2. The low-K+ pattern is a diagnostic clue, not just a side effect
3. Early renal involvement is a downstream consequence already manifesting

**expected_failure_conditions:**
- ❌ Ranks weight (stable) as a top concern
- ❌ Misses the diagnostic significance of low-K+
- ❌ Does not recognize early hypertensive nephropathy
- ❌ Treats trajectories in isolation rather than as a connected pattern

---

## Case 10 — Intervention Leverage Analysis

**user_prompt:**
> *"What single intervention would have the highest leverage for this
> patient?"*

**Patient:** Maria Santos
**Visit context:** Patient asking what one change matters most

**expected_tools:**
1. `build_patient_model(patient_id="maria-santos-001")`
2. `compare_interventions(focus="leverage_analysis")`
3. `simulate_scenario(scenario_type="intervention", intervention="empagliflozin_10mg")`

**expected_reasoning:**
- Define "leverage" as benefit per unit of intervention cost/burden
- Compare candidate interventions across multiple axes simultaneously
- Identify SGLT2i as the highest-leverage option for this multi-system
  patient
- Quantify the leverage with personalized NNT and projected trajectory
  improvement

**expected_key_findings:**
- Empagliflozin: addresses renal, cardiovascular, and glycemic axes
  simultaneously
- Single oral medication, once daily, well-tolerated
- Personalized NNT for CKD progression: ~19 over 2.4 years
- eGFR slope improvement: from −6 to −3 mL/min/year
- Cardiovascular benefit: ~12% MACE reduction

**expected_priorities:**
1. Empagliflozin is THE single highest-leverage intervention
2. The leverage comes from multi-system effect, not from being
   "most powerful in any one dimension"
3. Cost and access are the only meaningful barriers

**expected_failure_conditions:**
- ❌ Recommends a lifestyle change as the "single highest leverage"
  (unrealistic for this clinical urgency)
- ❌ Recommends insulin (high A1c effect but no multi-system benefit)
- ❌ Does not explain WHY SGLT2i has multi-system leverage
- ❌ Does not quantify the leverage with NNT or trajectory shift
- ❌ Recommends adding multiple medications when one is asked for

---

## Summary Scorecard Template

For tracking evaluation runs:

```
| Case | Tool selection | Reasoning (1–5) | Completeness (1–5) | Pass? |
|------|---------------|----------------|-------------------|-------|
| 01   |               |                |                   |       |
| 02   |               |                |                   |       |
| 03   |               |                |                   |       |
| 04   |               |                |                   |       |
| 05   |               |                |                   |       |
| 06   |               |                |                   |       |
| 07   |               |                |                   |       |
| 08   |               |                |                   |       |
| 09   |               |                |                   |       |
| 10   |               |                |                   |       |
```

**Pass criteria (per case):**
- Tool selection: pass
- Reasoning quality: ≥4
- Output completeness: ≥4
- No `expected_failure_conditions` triggered

**Overall benchmark health:**
- 🟢 9–10 passing: Phantom is performing as designed
- 🟡 7–8 passing: Investigate failures, may indicate drift
- 🔴 ≤6 passing: Significant regression — block release

---
*Phantom — Evaluation Cases — `evaluation_cases/evaluation_cases.md`*