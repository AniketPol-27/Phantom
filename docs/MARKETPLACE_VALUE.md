# Why Phantom Belongs in Every Clinical Agent
> The composability, reusability, and standards argument for equipping Phantom across the Po marketplace

---

## The Composability Argument

Phantom is not a vertical clinical agent. It is a **horizontal capability
layer** — a standards-compliant evidence and simulation engine that any
specialty agent can equip without rebuilding the underlying clinical
knowledge.

This matters because every clinical agent — regardless of specialty —
needs the same foundational primitives:

| Specialty Agent | What It Needs from Phantom |
|----------------|---------------------------|
| **Cardiology agent** | ASCVD risk scores, beta blocker / ACE inhibitor / SGLT2 evidence, HFrEF trial data (DAPA-HF, EMPEROR-Reduced) |
| **Nephrology agent** | CKD-EPI 2021 eGFR, KDIGO staging, DAPA-CKD / CREDENCE / EMPA-KIDNEY trial outcomes, renal-dose drug adjustments |
| **Endocrinology agent** | A1c trajectory modeling, GLP-1 vs SGLT2 vs DPP-4 head-to-head comparisons, cardiovascular outcomes from SUSTAIN-6 / LEADER / REWIND |
| **Pharmacy / med-rec agent** | Drug-drug interactions, contraindication checking by eGFR/LFTs, cost tier comparisons, adherence factor data |
| **Care coordination agent** | USPSTF-based care gap detection, screening overdue rules, vaccination schedules |
| **Hospitalist / inpatient agent** | Discharge medication reconciliation, transition-of-care risk scoring, readmission risk |
| **Population health agent** | Care gap aggregation across panels, risk stratification at scale |
| **Geriatrics agent** | Falls prevention rules, polypharmacy detection, deprescribing logic |

Every one of these agents would otherwise need to build — and maintain —
their own version of:
- A drug knowledge base
- A trial evidence database
- Validated clinical risk equations
- Guideline-based care gap rules
- A FHIR client and patient model schema

**With Phantom equipped, they don't.** They call three MCP tools and get
back validated, evidence-grounded clinical reasoning — already
specialty-aware through the patient model.

---

## The Reusability Multiplier

Quantify the value:

**One Phantom MCP server contains:**
- 35 drugs with multi-system effect profiles
- 14 major clinical trials with structured outcomes (NNT, HR, eGFR slope, CV outcomes, safety signals)
- 70+ guideline-based care gap rules (USPSTF, ACC/AHA, KDIGO, ADA)
- 11 diagnostic gap detection rules
- 5 validated risk equations (CKD-EPI 2021, ACC/AHA PCE, FIB-4, UKPDS, KFRE)
- Multi-system disease progression models (renal, cardiovascular, metabolic, hepatic)

**Without Phantom:**
Every agent rebuilds this from scratch. Every team duplicates effort.
Knowledge bases drift. Guidelines go stale at different rates across
agents. Risk equations get misimplemented. Trial citations get
hallucinated.

**With Phantom:**
- Build once, used N times
- Update once, every consumer benefits immediately
- Single source of clinical truth
- Provenance and citations are standardized
- Risk equation correctness is centrally validated

**The math:**
If 20 clinical agents each spent 40 hours building a minimal evidence
base, that's 800 hours of duplicated work. Phantom replaces all of it
with one MCP integration call — minutes of work per consuming agent.

This is the same dynamic that made standard libraries valuable in
software engineering. Phantom is the standard library for clinical
reasoning on Po.

---

## The Standards Moat

Phantom is built on four open standards:

- **MCP** — Model Context Protocol (Anthropic, 2024)
- **A2A** — Agent-to-Agent Protocol
- **SHARP-on-MCP** — Healthcare context propagation
- **FHIR R4** — HL7 patient data standard

**Why standards-compliant tools win:**

### 1. No vendor lock-in
A clinic adopting Phantom on Po can move to any other MCP-compatible
platform tomorrow without losing the integration. Compare to
EHR-embedded clinical decision support, which is locked to the EHR
vendor and dies when the contract ends.

### 2. Future-proof
As MCP and SHARP evolve, Phantom evolves with them. Every new agent
platform that supports MCP automatically becomes a potential Phantom
host. No proprietary SDK to chase.

### 3. Plug-and-play across platforms
Phantom is one HTTPS endpoint and one configuration entry. Any agent on
any MCP host can equip it in under a minute. No custom integration
work, no platform-specific adapters.

### 4. Network effects
Every clinical agent that equips Phantom validates the standards stack.
Every Phantom user generates evidence that MCP + SHARP + FHIR is the
right substrate for healthcare AI. The ecosystem compounds.

**The moat is not the code — it's the standards alignment.** A
proprietary clinical reasoning engine is a product. A standards-native
one is infrastructure.

---

## Cost Comparison

What clinicians and agent developers use today, and how Phantom compares:

| Tool | Cost | Integration | Patient Context | Evidence Grounding | Composable |
|------|------|-------------|-----------------|-------------------|------------|
| **UpToDate** | $559/year per clinician | Manual lookup, no API | None — clinician types query | High (peer-reviewed) | No |
| **Epocrates** | $175/year per clinician | Manual lookup | None | Drug-only | No |
| **EHR-embedded CDS** (Epic, Cerner) | Bundled in 6-figure EHR contracts | Tightly coupled to EHR vendor | Yes, but locked in | Vendor-curated | No |
| **Generic ChatGPT / Claude** | $20/month | None for healthcare | None — clinician copies data | **Hallucination risk — no citations** | No |
| **Phantom on Po** | Open / marketplace | One-line MCP config | **Yes — via SHARP context propagation** | **Yes — every output cites trial / guideline source** | **Yes — every agent can equip it** |

**The Phantom advantage in plain terms:**
- ✅ **Validated** — risk scores from validated equations, not LLM
  estimation
- ✅ **Integrated** — patient context flows automatically via SHARP, no
  copy-paste
- ✅ **Composable** — one server serves every agent on the platform
- ✅ **Standards-based** — no vendor lock-in, future-proof
- ✅ **Cited** — every recommendation traceable to a trial, guideline, or
  equation

UpToDate is excellent at being a textbook. Epocrates is excellent at
being a drug reference. EHR-CDS is excellent at being EHR-locked.
ChatGPT is excellent at being confidently wrong about NNT.

**Phantom is the only option that is simultaneously evidence-grounded,
patient-contextual, agent-composable, and standards-compliant.**

---

## Who Should Equip Phantom

### Primary recommendation: every Po agent that touches patient data

If an agent ever needs to reason about a patient's medications, labs,
conditions, or risk — it should equip Phantom. The cost of integration
is one configuration entry. The benefit is access to a 35-drug, 14-trial,
70-guideline evidence base with validated risk computation.

### Specific agent archetypes that should equip Phantom on day one:

**1. Pre-visit and chart-review agents**
- Use case: Generate briefings before clinic visits
- Tools used: All three (build_patient_model, simulate_scenario,
  compare_interventions)
- Reference implementation: The Pre-Visit Intelligence Agent in this
  repo

**2. Specialty consultation agents (cardiology, nephrology, endocrinology)**
- Use case: Specialty-specific reasoning with custom prompting on top of
  Phantom's evidence
- Tools used: build_patient_model + compare_interventions, with
  specialty-filtered drug classes

**3. Care coordination and population health agents**
- Use case: Identify care gaps across patient panels
- Tools used: build_patient_model, with focus on care_gaps and
  diagnostic_gaps output

**4. Pharmacy and medication reconciliation agents**
- Use case: Drug-drug interaction checking, deprescribing
  recommendations, dose adjustments by renal function
- Tools used: build_patient_model + compare_interventions

**5. Patient-facing education and shared-decision-making agents**
- Use case: Explain medication options to patients in plain language
- Tools used: compare_interventions, with output translated to lay
  language by the agent

**6. Quality improvement and risk-adjustment agents**
- Use case: Population-level care gap analytics, HCC coding support
- Tools used: build_patient_model across patient cohorts

### Who should NOT equip Phantom (yet):

- Pure administrative agents (scheduling, billing) — no clinical
  reasoning needed
- Agents working outside US population norms — Pooled Cohort Equations
  and some guidelines are US-derived (international expansion is on the
  roadmap)
- Pediatric agents — Phantom's evidence base currently focuses on adult
  chronic disease (pediatric pack is future work)

---

## The Bottom Line

Phantom is positioned to be the clinical reasoning layer that every
healthcare agent on Prompt Opinion equips by default — the way every
web app equips an HTTP library, every data pipeline equips pandas,
every LLM app equips a tokenizer.

It's not a feature. It's infrastructure.

And because it's standards-compliant from day one, it doesn't just serve
the Po marketplace — it serves every MCP-compatible agent platform that
exists today or emerges tomorrow.

**Equip Phantom. Build the agent. Skip the evidence base.**

---
*Phantom — Agents Assemble Hackathon — Prompt Opinion Platform*