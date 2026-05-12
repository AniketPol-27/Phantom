<div align="center">

<img src="https://img.shields.io/badge/Phantom-Longitudinal%20Clinical%20Intelligence-0a0a1a?style=for-the-badge&labelColor=0a0a1a&color=4f46e5" />

# 👻 PHANTOM

### Longitudinal Clinical Intelligence Platform

*From static chart summaries to computational foresight — Phantom models where your patient is heading.*

<br/>

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-Protocol-6366f1?style=flat-square)](https://modelcontextprotocol.io)
[![FHIR R4](https://img.shields.io/badge/FHIR-R4-E8173E?style=flat-square)](https://hl7.org/fhir)
[![SHARP](https://img.shields.io/badge/SHARP-Context-0ea5e9?style=flat-square)](https://smarthealthit.org)
[![A2A](https://img.shields.io/badge/A2A-Protocol-f59e0b?style=flat-square)](https://google.github.io/A2A)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

<br/>

> **Agents Assemble Healthcare AI Hackathon** · Prompt Opinion · Path A: MCP Server

<br/>

---

</div>

## The Problem with Healthcare AI Today

Every clinical AI tool on the market does the same thing: **it looks backward**.

- Summarize the chart ✓  
- Retrieve a note ✓  
- Look up a guideline ✓  

None of them answer the question clinicians actually need answered:

> **"Where is this patient heading — and what should I do about it now?"**

---

## What Phantom Does Differently

Phantom is not a summarization tool. It is a **longitudinal clinical reasoning engine**.

It ingests a patient's full FHIR record and builds a **simulation-ready computational patient model** — a living mathematical representation of the patient's physiology, disease trajectory, and intervention opportunities.

Then it uses that model to **forecast the future**.

```
Traditional AI          →      Phantom
─────────────────────────────────────────────────────
"Here's what happened"  →      "Here's what will happen"
Static chart summary    →      Dynamic disease trajectory
Guideline lookup        →      Patient-specific simulation
Reactive              →      Proactive longitudinal foresight
```

---

## Core Capabilities

### 🧠 Computational Patient Modeling
Transforms raw longitudinal FHIR data into a structured computational patient state — synthesizing renal physiology, metabolic dynamics, cardiovascular risk, hepatic burden, medication interactions, and comorbidity cascades into a single coherent model.

### 📈 Longitudinal Disease Forecasting
Projects disease progression under inaction, medication change, or lifestyle intervention — 6, 12, and 24-month horizons — powered by validated clinical algorithms (CKD-EPI 2021, KDIGO, ASCVD, FIB-4, qSOFA).

### ⚖️ Intervention Optimization
Compares competing treatment strategies across multiple physiological dimensions simultaneously — ranking interventions by projected longitudinal impact, safety profile, adherence burden, and patient-specific tradeoffs.

### 🔍 Hidden Deterioration Detection
Surfaces clinically significant patterns invisible to chart review — cross-system disease cascades, trajectory inflection points, and silent risk accumulation before it becomes a crisis.

---

## MCP Tools

Phantom exposes **3 deep, composable healthcare MCP tools** — each one a clinical reasoning engine in its own right.

---

### `build_patient_model`

> *The foundation. Everything starts here.*

Constructs a simulation-ready computational patient model from longitudinal FHIR records.

**Computes:**
| System | What It Builds |
|--------|----------------|
| 🫘 Renal | eGFR trajectory · CKD staging · KDIGO risk matrix · nephrotoxic burden |
| 🩸 Metabolic | HbA1c trends · glycemic instability · obesity analysis |
| ❤️ Cardiovascular | BP trajectory · ASCVD 10-yr risk · lipid status |
| 🏥 Hepatic | FIB-4 scoring · MASLD risk · hepatic injury progression |
| 💊 Medication | Polypharmacy burden · contraindications · interaction analysis |
| 🔗 Comorbidity | Disease cascade detection · cross-system interaction mapping |
| 📊 Confidence | Per-system data quality scoring · evidence completeness |

**Output:** A fully structured, simulation-ready patient model — not a summary, a model.

---

### `simulate_scenario`

> *Ask "what if?" — and get a clinically grounded answer.*

Runs longitudinal forward simulations against the patient model.

**Simulation Modes:**

```
inaction          →  Where is this patient in 12 months if nothing changes?
medication_change →  What happens if we start an SGLT2 inhibitor?
lifestyle         →  What's the projected trajectory with weight loss?
diagnostic_gap    →  What clinical patterns might we be missing?
```

**Output:** Projected future physiological trajectories with deterioration risk quantification across all modeled organ systems.

---

### `compare_interventions`

> *Don't just recommend — optimize.*

Performs head-to-head comparative analysis of competing treatment strategies using longitudinal multi-system simulation.

**Evaluates Each Intervention Across:**
- Renal protection trajectory
- Cardiovascular risk reduction
- Metabolic stabilization
- Safety + contraindication profile
- Adherence and polypharmacy burden
- Longitudinal physiological stability

**Output:** Ranked intervention strategies with evidence-grounded rationale, patient-specific tradeoff analysis, and projected 12-month benefit curves.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Prompt Opinion Platform                   │
│              (SHARP Context · FHIR Context Extension)        │
└─────────────────────────┬────────────────────────────────────┘
                          │  MCP Streamable HTTP
                          ▼
┌──────────────────────────────────────────────────────────────┐
│              Clinical Phantom MCP Server                     │
│                 FastMCP · FastAPI · Uvicorn                  │
└───────┬──────────────────┬───────────────────┬──────────────┘
        │                  │                   │
        ▼                  ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐
│ build_patient│  │  simulate_   │  │  compare_            │
│ _model       │  │  scenario    │  │  interventions       │
└──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘
       └─────────────────┼──────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────────┐
│               Computational Patient Engine                   │
├──────────┬───────────┬───────────┬──────────┬───────────────┤
│  Renal   │ Metabolic │  Cardio-  │ Hepatic  │  Medication   │
│ Modeling │ Modeling  │  vascular │ Modeling │ Intelligence  │
└──────────┴───────────┴───────────┴──────────┴───────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│          Evidence + Clinical Progression Engine              │
│   CKD-EPI 2021 · KDIGO · ASCVD · FIB-4 · qSOFA             │
│   EMPA-KIDNEY · DAPA-CKD · GLP-1 CV Outcomes Evidence      │
└──────────────────────────────────────────────────────────────┘
                         │
              ┌──────────┴───────────┐
              ▼                      ▼
   ┌─────────────────┐    ┌─────────────────────┐
   │   FHIR Server   │    │  External Drug APIs  │
   │   (HAPI FHIR)   │    │  RxNorm · OpenFDA    │
   └─────────────────┘    └─────────────────────┘
```

### Experimental Multi-Agent Layer

Phantom also ships an experimental **Pre-Visit Intelligence Agent** built with Google ADK and the A2A protocol:

```
Clinician: "Prep me for my 2pm with this patient"
    │
    ▼
┌─────────────────────────────────┐
│  Orchestrator Agent (phantom-adk)│
│  patient_model_agent            │  → calls build_patient_model
│  trajectory_agent               │  → calls simulate_scenario
│  intervention_agent             │  → calls compare_interventions
│  briefing_agent                 │  → generates Pre-Visit Briefing
└─────────────────────────────────┘
```

Output: A structured pre-visit clinical briefing — patient snapshot, trajectory alert, top 3 visit priorities, decision-ready recommendations, and a suggested visit agenda — generated in under 30 seconds.

---

## Evidence Engine

Phantom integrates validated clinical science, not heuristics.

| Domain | Integrated Evidence |
|--------|---------------------|
| Renal | CKD-EPI 2021 eGFR · KDIGO Risk Matrix · Albuminuria Classification |
| Cardiovascular | ACC/AHA Pooled Cohort ASCVD Equations · BP trajectory analysis |
| Metabolic | ADA glycemic targets · HbA1c trajectory modeling |
| Hepatic | FIB-4 staging · MASLD risk stratification |
| Sepsis | qSOFA scoring |
| Clinical Trials | EMPA-KIDNEY · DAPA-CKD · GLP-1 cardiovascular outcomes |
| Pharmacology | RxNorm drug database · OpenFDA safety signals · Contraindication mapping |

---

## Technology Stack

```
Backend         Python 3.13 · FastAPI · FastMCP · Uvicorn · Structlog
MCP             Model Context Protocol · Streamable HTTP Transport
Clinical        SMART-on-FHIR · SHARP Context · HL7 FHIR R4
Agent Layer     Google ADK · A2A Protocol · LiteLLM · Gemini · Groq
Package Mgmt    uv
```

---

## Prompt Opinion Integration

Phantom integrates natively with the Prompt Opinion platform:

- **MCP Streamable HTTP transport** — Phantom registers as a standard MCP server
- **SHARP Context** — Patient ID, FHIR server URL, and access token are dynamically injected per-request via SHARP headers, requiring zero manual configuration
- **FHIR Context Extension** — All patient data flows through FHIR R4 using the Prompt Opinion FHIR Context Extension
- **Marketplace ready** — Published as a standalone MCP server any Prompt Opinion agent can equip

---

## Example Clinical Queries

```text
# Hidden deterioration detection
"Analyze this patient for hidden longitudinal deterioration risks."

# Future trajectory simulation  
"Simulate this patient's trajectory over 24 months without intervention."

# Intervention optimization
"Compare SGLT2 inhibitor versus GLP-1 agonist for this patient longitudinally."

# Pre-visit intelligence
"Prepare me for my visit with this patient. What are the highest-yield priorities?"

# Cascade analysis
"What disease interactions are accelerating this patient's decline?"
```

---

## Repository Structure

```
Phantom/
├── mcp-server/                    # Clinical Phantom MCP Server
│   └── src/
│       ├── server.py              # FastMCP + FastAPI entrypoint
│       ├── sharp/                 # SHARP context extraction
│       ├── fhir/                  # FHIR client, parsers, models
│       ├── evidence/              # Clinical algorithms + trial evidence
│       ├── model_builder/         # Computational patient model engine
│       ├── simulation/            # Forward trajectory simulation
│       ├── comparison/            # Intervention comparison engine
│       ├── external/              # RxNorm + OpenFDA API clients
│       └── tools/                 # MCP tool entry points
│           ├── build_patient_model.py
│           ├── simulate_scenario.py
│           └── compare_interventions.py
│
└── phantom-adk/                   # Pre-Visit Intelligence Agent (experimental)
    ├── orchestrator/              # Master A2A orchestrator
    ├── patient_model_agent/       # Patient modeling sub-agent
    ├── trajectory_agent/          # Trajectory simulation sub-agent
    ├── intervention_agent/        # Intervention comparison sub-agent
    ├── briefing_agent/            # Pre-visit briefing generator
    └── shared/                    # MCP client, FHIR hooks, middleware
```

---



## Vision

Healthcare AI has spent a decade getting better at reading the past.

Phantom is built for the next decade — **reading the future**.

> *Not "what does the chart say?"*
> *But "where is this patient going, and what do we do about it today?"*

---

## Hackathon Submission

**Competition:** Prompt Opinion — Agents Assemble Healthcare AI Hackathon  
**Track:** Path A — MCP Server (Superpower)  
**Marketplace:** Clinical Phantom MCP Server + Pre-Visit Intelligence Agent  

---

<div align="center">

**https://github.com/AniketPol-27/Phantom**

<br/>

*Built with clinical rigor. Designed for real clinicians. Powered by longitudinal foresight.*

<br/>

MIT License

</div>
