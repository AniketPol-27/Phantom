# Phantom Pitch Deck Outline
> 10-slide outline for a 5-minute pitch to hackathon judges

---

## Slide 1: Title

**Title:** Phantom — The Patient Digital Twin for Clinical Reasoning

**Tagline:** Simulate before you decide.

**Team:**
- Aniket Pol — Backend & Platform Integration
- Jasnoor Kaur — Clinical Knowledge Base & Documentation

**Event:** Agents Assemble — The Healthcare AI Endgame Challenge
**Platform:** Prompt Opinion
**Prize Pool:** $25,000

**Visual suggestion:** Clean dark background, pulse/heartbeat line graphic,
Phantom name in white. Subtle FHIR + MCP logos in corner.

---

## Slide 2: The Problem

**Headline:** Clinicians make high-stakes decisions in under 90 seconds —
with no way to simulate the consequences first.

**Supporting points:**
- Clinicians spend 6+ hours per day in the EHR, yet still walk into
  visits under-prepared for complex chronic disease patients
- Every medication change, every test order, every watchful-waiting
  decision is a "what-if" with no simulator — just intuition and memory
- Care gaps (missed screenings, undertreated conditions, dangerous drug
  interactions) are caught late or not at all

**Statistic:** A 2022 JAMA study found that primary care physicians have
an average of 27 minutes of EHR work for every hour of patient care.
Complex chronic disease patients require 3–5x more cognitive load than
average.

**Visual suggestion:** Split image — left side: overwhelmed clinician at
screen; right side: empty "simulation" panel that doesn't exist yet.

---

## Slide 3: The Insight

**What's been missing in clinical AI:**

Until now, AI in healthcare has been reactive — summarizing what
happened, not projecting what will happen. The gap isn't data. It's
simulation. Clinicians don't need more information — they need a way to
test decisions before making them.

**Why now — MCP, A2A, and SHARP enable this:**
- **MCP (Model Context Protocol):** Gives AI agents structured access to
  clinical tools — not just text, but validated computation
- **A2A (Agent-to-Agent Protocol):** Lets agents compose and delegate —
  a pre-visit agent can call a simulation agent without rebuilding logic
- **SHARP-on-MCP:** Propagates real patient context (FHIR server URL,
  patient ID, clinician identity) securely from EHR session into every
  tool call — no manual input required

**The combination of these three standards makes a patient digital twin
possible at the point of care, for the first time.**

**Visual suggestion:** Timeline — "Before MCP/SHARP: static summaries"
vs "After: live simulation at point of care"

---

## Slide 4: The Solution

**Phantom in one sentence:**
Phantom is an MCP server that transforms a patient's FHIR record into a
computational digital twin, then lets AI agents simulate clinical
scenarios and compare interventions — grounded in trial evidence, not
LLM hallucination.

**Visual:** Architecture diagram

```
Clinician → Po Workspace → Pre-Visit Agent
                                ↓
                         Phantom MCP Server
                                ↓
                    ┌───────────┴───────────┐
                    ↓                       ↓
              FHIR R4 Server        Evidence Base
              (real patient)    (14 trials, 35 drugs,
                                 70+ guidelines)
```

**Three key capabilities:**
1. **build_patient_model** — Constructs a multi-system patient model
   with trajectories, risk scores, and diagnostic gaps from raw FHIR data
2. **simulate_scenario** — Projects forward: what happens to this patient
   over the next 6–24 months under a given intervention or inaction?
3. **compare_interventions** — Ranks options head-to-head with
   personalized NNT, contraindication checking, and trial citations

---

## Slide 5: Live Demo

**Demo flow** (matches DEMO_SCRIPT.md Scene 4–6):

1. Open Po workspace — Phantom MCP server registered, FHIR context active
2. Clinician types: *"Prep me for my next patient"*
3. Agent calls `build_patient_model` → FHIR data flows in, patient model
   built (Maria Santos, 58F, T2DM + CKD Stage 3a + HTN + obesity)
4. Agent calls `simulate_scenario(type=inaction)` → trajectory alert
   generated: eGFR projected to reach Stage 4 within 18 months
5. Agent calls `compare_interventions` → empagliflozin vs dapagliflozin
   vs semaglutide ranked with NNT from EMPA-KIDNEY, DAPA-CKD, SUSTAIN-6
6. Pre-Visit Briefing rendered — 3 priorities, decision point, care gaps,
   suggested orders — all in under 45 seconds

**Key moments to emphasize during demo:**
- Real patient ID appearing in tool call arguments (SHARP context working)
- Trial names cited in the briefing (not hallucination — encoded evidence)
- Diagnostic gap detected: no urine albumin/creatinine ratio in 14 months

---

## Slide 6: Technical Innovation

**Four things that make Phantom different from generic clinical AI:**

### 1. Validated Algorithms, Not Hallucination
Every risk score is computed from a validated equation:
- CKD-EPI 2021 (eGFR — no race coefficient, NEJM 2021 standard)
- ACC/AHA Pooled Cohort Equations (10-year ASCVD risk)
- FIB-4 Index (liver fibrosis)
- UKPDS Risk Engine (diabetes-specific CV risk)

No LLM is asked to estimate a risk score. The math is always the math.

### 2. Multi-System Simulation
Most clinical decision support looks at one problem at a time.
Phantom models how an intervention affects renal function AND
cardiovascular risk AND metabolic control AND cost AND adherence —
simultaneously. Because patients don't have one disease.

### 3. Trial Evidence Grounding
14 major clinical trials encoded with structured outcomes — EMPA-REG
OUTCOME, DAPA-CKD, CREDENCE, SUSTAIN-6, LEADER, REWIND, and more.
When Phantom recommends empagliflozin, it cites the trial, the hazard
ratio, and the NNT. When it says dapagliflozin slows eGFR decline, it
reports the exact slope from DAPA-CKD.

### 4. Standards Composability
MCP + A2A + SHARP + FHIR R4. Any agent on any MCP-compatible platform
can equip Phantom. One server, unlimited consumers.

---

## Slide 7: Standards Compliance

**Badges:**
- ✅ Model Context Protocol (MCP) — Streamable HTTP transport
- ✅ Agent-to-Agent Protocol (A2A) — composable tool delegation
- ✅ SHARP-on-MCP — healthcare context propagation
- ✅ FHIR R4 (HL7) — patient data standard
- ✅ SMART on FHIR — JWT-based patient identity
- ✅ Clinical algorithms — CKD-EPI 2021, ACC/AHA PCE, KDIGO 2024

**Why this matters — interoperability:**
Standards-compliant tools don't need custom integrations. Every
MCP-compatible agent platform — today and in the future — can consume
Phantom without modification. This is the difference between a project
and infrastructure.

**Marketplace multiplier effect:**
One Phantom deployment serves every agent on the platform. A cardiology
agent, a nephrology agent, a care coordination agent, a pharmacy
reconciliation agent — all can call the same Phantom tools, each
interpreting results through their own specialty lens.

**Visual suggestion:** Logos of MCP, FHIR, SMART, SHARP arranged around
Phantom in center. Arrows pointing inward from each standard.

---

## Slide 8: Use Cases & Market

**Three specific clinician personas:**

| Persona | Role | Volume | Pain → Phantom Fix |
|---------|------|--------|-------------------|
| Dr. Sarah Lee | Primary care, community health | 8 patients/morning, 90s per chart | No time to simulate → 45-second briefing auto-generated |
| Dr. James Chen | Endocrinologist, academic center | 4 complex diabetes consults/day | Medication comparison is manual → ranked options with trial citations |
| Maria Rodriguez, NP | Nephrology NP, outpatient CKD | 12 CKD patients/day | eGFR trends are in charts but not synthesized → trajectory alerts |

**Market context:**
- US has 1.1 million active physicians + 335,000 NPs/PAs
- Clinical decision support software market: $1.9B (2024), growing 12%
  annually
- EHR-embedded CDS is expensive, vendor-locked, and static
- AI-native clinical tools on open standards are the emerging alternative

**Po marketplace as distribution:**
Every clinician on the Prompt Opinion platform is a potential Phantom
user. No sales cycle — equip the tool, start generating briefings.

---

## Slide 9: Roadmap

**Today (hackathon submission):**
- 3 clinical tools (build, simulate, compare)
- 35 drugs with multi-system effect profiles
- 14 major trials with structured outcome data
- 70+ guideline-based care gap rules
- 1 reference agent (Pre-Visit Intelligence)
- Validated risk equations: CKD-EPI, PCE, FIB-4, UKPDS

**Next quarter:**
- Specialty packs — Cardiology Pack, Nephrology Pack, Oncology Pack
- Drug knowledge base expanded to 100+ drugs
- Real-time alert system (trajectory threshold crossings → push notification
  to agent)
- Population-level analytics tool (4th MCP tool)
- Longitudinal trend visualization

**Next year:**
- Direct EHR integrations (Epic, Cerner via SMART app launch)
- Multi-language support (Spanish, Mandarin — for patient-facing
  summaries)
- Outcome tracking — did Phantom's recommendation match what the
  clinician chose? Did it improve outcomes?
- Research mode — anonymized aggregate data for clinical research
- FDA SaMD regulatory pathway exploration

**Visual suggestion:** Three-column roadmap: Today / Q2 / 2026, each
column with icon-led bullet list.

---

## Slide 10: Ask / Close

**What we built:**
In 72 hours, we built a standards-compliant clinical simulation MCP
server with a validated evidence base — 35 drugs, 14 trials, 70+
guidelines, 5 validated risk equations — and a Pre-Visit Intelligence
Agent that uses it to generate clinician briefings in under 45 seconds.

**Why it matters:**
Clinicians make life-changing decisions under time pressure every day.
Phantom gives them a simulator. Not more data — a way to test what will
happen before they decide. Evidence-grounded. Standards-compliant.
Composable across every agent on the platform.

**Closing tagline:**
*"Before you decide, simulate."*

**Contact & Resources:**
- Repository: https://github.com/AniketPol-27/Phantom
- Branch: evidence-base
- Submission: docs/SUBMISSION.md
- Demo: docs/DEMO_SCRIPT.md

---
*Phantom — Agents Assemble Hackathon — Prompt Opinion Platform*