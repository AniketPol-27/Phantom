# Phantom Clinical Scenario Library

> A curated set of realistic clinical scenarios used for demos, evaluation,
> and regression testing of the Phantom MCP server and Pre-Visit Intelligence Agent.

---

## Purpose

This scenario library exists for three reasons:

1. **Demo reliability** — Each scenario is designed to showcase a *different*
   Phantom capability (trajectory analysis, intervention comparison, diagnostic
   gap detection, polypharmacy reasoning, multi-system simulation). When recording
   demo videos or running live presentations, these scenarios provide predictable,
   high-impact narratives.

2. **Evaluation benchmarks** — Each scenario specifies expected tool calls,
   expected reasoning steps, expected interventions, and expected diagnostic gaps.
   This lets us validate Phantom's output quality against a known-good baseline.

3. **Regression testing** — As the evidence base, simulation engine, or agent
   prompts evolve, these scenarios act as a fixed reference point. Behavioral
   drift becomes visible immediately.

---

## Scenario Index

| # | Scenario | Phantom Capability Highlighted | Difficulty |
|---|----------|-------------------------------|------------|
| 01 | Worsening CKD Progression | Longitudinal trajectory + intervention leverage | Moderate |
| 02 | Uncontrolled Diabetes | Head-to-head intervention comparison (GLP-1 vs SGLT2 vs insulin) | Moderate |
| 03 | Polypharmacy Risk | Drug interaction reasoning + hyperkalemia risk modeling | High |
| 04 | MASLD Progression | Multi-system reasoning + diagnostic gap detection | Moderate |
| 05 | Resistant Hypertension | Diagnostic workup reasoning + secondary HTN evaluation | High |

---

## Scenario File Structure

Every scenario file follows this structure:

```
1. scenario_name              — Short identifier
2. patient_summary            — Demographics + clinical snapshot
3. key_conditions             — Active problem list
4. trajectory_summary         — Longitudinal pattern (labs/vitals over time)
5. expected_risks             — Quantified risks Phantom should surface
6. likely_tool_calls          — Which Phantom MCP tools the agent should invoke
7. expected_interventions     — Interventions the agent should rank/recommend
8. expected_diagnostic_gaps   — Missing tests/screenings Phantom should detect
9. expected_clinician_focus   — Top 1–3 priorities for the visit
10. expected_demo_highlights  — Specific moments to emphasize during a live demo
```

---

## How to Use These Scenarios

### For demo recording
1. Pick a scenario that aligns with the demo narrative
2. Load the corresponding FHIR test patient (or synthesize one matching the scenario)
3. Use the `expected_demo_highlights` section to script voiceover beats
4. Verify Phantom's actual output matches `expected_clinician_focus`

### For evaluation
1. Run the agent with the scenario's implied prompt (e.g., "Prep me for this patient")
2. Compare actual tool calls to `likely_tool_calls`
3. Compare actual interventions to `expected_interventions`
4. Compare actual gaps surfaced to `expected_diagnostic_gaps`
5. Score qualitatively on clinical reasoning quality

### For regression testing
1. Re-run after any change to evidence base, simulation engine, or system prompt
2. Diff against prior outputs
3. Investigate any divergence

---

## Clinical Realism Standards

All scenarios in this library:
- Use clinically realistic lab values, vital signs, and medication regimens
- Align with current US guidelines (USPSTF, ACC/AHA, ADA, KDIGO 2024)
- Reference real clinical trials encoded in Phantom's evidence base
- Reflect realistic patient complexity (multimorbidity is the norm, not the exception)
- Avoid implausible combinations or values that would never occur in practice

---

## Adding New Scenarios

To add a new scenario:
1. Create a new markdown file: `NN_short_name.md` (zero-padded number)
2. Follow the 10-section structure above
3. Add it to the Scenario Index table
4. Ensure it highlights a *different* Phantom capability than existing scenarios
5. Commit with message: `Add scenario NN: [short description]`

---

## Related Documentation

- [Submission overview](../../docs/SUBMISSION.md)
- [Demo script](../../docs/DEMO_SCRIPT.md)
- [Use cases](../../docs/use-cases.md)
- [Tools reference](../../docs/TOOLS_REFERENCE.md)
- [Architecture](../../docs/architecture.md)

---
*Phantom — Agents Assemble Hackathon — Prompt Opinion Platform*