# Phantom Evaluation Cases

> A reusable benchmark dataset for validating Phantom's clinical reasoning,
> tool selection, and output quality.

---

## Purpose

This evaluation dataset exists to:

1. **Validate demos** — Confirm Phantom produces expected outputs for
   judge-facing scenarios before recording or live presentation
2. **Regression testing** — Detect behavioral drift after changes to
   evidence base, simulation engine, or system prompt
3. **Output quality scoring** — Provide a known-good baseline for both
   manual review and (eventually) automated evaluation
4. **Future model evaluation** — Compare alternative agent backbones,
   prompt revisions, or evidence base versions against a fixed benchmark

---

## File Structure

- `README.md` — this file
- `evaluation_cases.md` — the 10 benchmark cases with expected behaviors

---

## How to Use These Cases

### For demo validation

1. Pick a case from `evaluation_cases.md`
2. Load the corresponding patient (Maria Santos, James Walker, Robert
   Henderson, Linda Chen, or Marcus Johnson — see scenario library)
3. Send the case's `user_prompt` to the Pre-Visit Agent
4. Verify the agent's response matches `expected_tools`, `expected_reasoning`,
   `expected_key_findings`, and `expected_priorities`
5. Flag any divergence as either an evaluator update or an agent fix

### For regression testing

1. Re-run all 10 cases after any meaningful change to:
   - Evidence base (drug_knowledge, trial_data, guidelines, risk_equations,
     disease_progression)
   - System prompt or briefing template
   - Simulation engine or tool implementations
2. Diff outputs against last known-good run
3. Investigate any divergence in expected vs actual behavior
4. Update either the test case (if behavior change is intended) or the
   code (if behavior change is unintended)

### For output quality review

Each case includes `expected_failure_conditions` — explicit failure modes
that should trigger investigation. Use these as a checklist when
manually reviewing outputs.

---

## Case Categories

The 10 cases are designed to cover Phantom's full capability surface:

| # | Category | Tests |
|---|----------|-------|
| 01 | Comprehensive briefing | All 3 tools chained, full pipeline |
| 02 | Risk identification | `build_patient_model` + clinical reasoning |
| 03 | Inaction simulation | `simulate_scenario(inaction)` |
| 04 | Intervention comparison | `compare_interventions` head-to-head |
| 05 | Diagnostic gap detection | `simulate_scenario(diagnostic_gap)` |
| 06 | Order recommendation | Tool synthesis into actionable orders |
| 07 | Causal medication reasoning | Drug-disease interaction logic |
| 08 | Time-constrained prioritization | Triage logic for short visits |
| 09 | Trajectory severity ranking | Multi-trajectory comparison |
| 10 | Intervention leverage analysis | Cross-axis reasoning |

---

## Patient Reference Map

The cases reference patients defined in the scenario library:

| Patient | Used in cases | Defining clinical pattern |
|---------|--------------|--------------------------|
| **Maria Santos** | 01, 03, 05, 06, 08, 10 | T2DM + CKD Stage 3a, rapid eGFR decline |
| **James Walker** | 04 | Uncontrolled diabetes, occupational complexity |
| **Robert Henderson** | 02, 07 | Polypharmacy, hyperkalemia risk |
| **Linda Chen** | (referenced) | Suspected MASLD progression |
| **Marcus Johnson** | 09 | Resistant hypertension, suspected secondary cause |

See `test-data/scenarios/` for full clinical detail on each patient.

---

## Scoring Guidance

For each case, score on three dimensions:

### 1. Tool selection (binary: pass / fail)
Did the agent invoke the expected MCP tools in a reasonable order?

### 2. Reasoning quality (1–5 scale)
- 5 = matches `expected_reasoning` precisely with appropriate clinical nuance
- 4 = captures core reasoning, minor omissions
- 3 = partial match, missing important elements
- 2 = significant misinterpretation
- 1 = wrong direction entirely

### 3. Output completeness (1–5 scale)
- 5 = all `expected_key_findings` and `expected_priorities` present
- 4 = most findings present, minor gaps
- 3 = key findings present but priorities miscategorized
- 2 = major findings missing
- 1 = output unusable

### Pass criteria
- Tool selection: pass
- Reasoning quality: ≥4
- Output completeness: ≥4
- No `expected_failure_conditions` triggered

---

## Adding New Cases

To add a new evaluation case:

1. Open `evaluation_cases.md`
2. Use the existing case structure as a template
3. Reference an existing patient OR add a new one to the scenario library
4. Define expected tools, reasoning, findings, priorities, and failure
   conditions
5. Update the case category table above
6. Commit with message: `Add evaluation case [N]: [short description]`

---

## Related Documentation

- [Scenario library](../test-data/scenarios/README.md)
- [Clinical interpretation guide](../docs/clinical_interpretation_guide.md)
- [Example outputs](../docs/example_outputs/)
- [Tools reference](../docs/TOOLS_REFERENCE.md)
- [Demo script](../docs/DEMO_SCRIPT.md)

---
*Phantom — Evaluation Dataset — `evaluation_cases/`*