<div align="center">

# Phantom Clinical Intelligence

**Longitudinal Clinical Intelligence Through MCP-Native FHIR Reasoning and Interoperable Specialist Agents**

*Hackathon Submission*

</div>

---

## Overview

Phantom Clinical Intelligence is a longitudinal clinical reasoning and pre-visit intelligence system built on FHIR-native healthcare infrastructure. The platform combines MCP-based patient-aware reasoning with interoperable external specialist agents to generate clinically actionable longitudinal insights from structured patient data.

Rather than summarizing isolated encounters, the system reasons across time — modeling chronic disease progression, identifying preventable deterioration pathways, prioritizing interventions, and surfacing unresolved care gaps before clinical encounters occur.

---

## Problem Statement

Modern clinical environments suffer from several systemic limitations:

- **Fragmented clinical context** — Patient data is distributed across medications, labs, diagnoses, procedures, and social history. Clinicians must synthesize these manually under severe time constraints.
- **Reactive care models** — Most systems detect disease after deterioration has already occurred rather than forecasting risk trajectories or recommending early interventions.
- **Lack of longitudinal intelligence** — Existing tools focus on snapshots, encounter summaries, or static risk scores — not interconnected multi-system reasoning over time.
- **Increasing chronic disease complexity** — Patients present with multimorbidity, metabolic syndrome, CKD, cardiovascular disease, and complex medication interactions that require systems-level reasoning, not isolated guideline application.

---

## Architecture

```
                    ┌──────────────────────┐
                    │   Prompt Opinion     │
                    └──────────┬───────────┘
                               │
                               ▼
              ┌────────────────────────────────┐
              │   Phantom Clinical Intelligence│
              │    (Primary MCP-native Agent)  │
              └────────────────┬───────────────┘
                               │
          ┌────────────────────┴────────────────────┐
          │                                         │
          ▼                                         ▼
┌────────────────────┐              ┌────────────────────────┐
│  MCP Clinical Layer│              │  External Specialist   │
│                    │              │  A2A Agent             │
│  - FHIR Retrieval  │              │                        │
│  - Patient Modeling│              │  - Advanced Longitudinal│
│  - Risk Analysis   │              │    Analysis            │
│  - Simulation      │              │  - Specialist Reasoning│
└────────────────────┘              └────────────────────────┘
```

---

## Core Capabilities

### Longitudinal Clinical Intelligence
- Multi-year disease trajectory forecasting across organ systems
- Chronic disease progression and cascade modeling
- Preventable deterioration pathway identification
- Cross-system risk prioritization

### FHIR-Native Reasoning
- Direct integration with FHIR R4 resources
- SHARP context propagation for patient-aware workflows
- Real-time clinical context extraction per encounter

### Preventative Intervention Planning
- Medication optimization and nephrotoxic burden assessment
- Care-gap detection and monitoring recommendations
- Early intervention prioritization ranked by clinical impact

### Computational Risk Modeling
- CKD progression with KDIGO staging and eGFR trajectory analysis
- ASCVD risk and cardiovascular deterioration modeling
- Metabolic syndrome forecasting and diabetes conversion risk
- MASLD progression and hepatic risk assessment

### Specialist Escalation Architecture
- MCP-native orchestration layer
- External A2A specialist consultation for complex multimorbidity
- Modular interoperability design with distributed agent workflows

---

## Organ System Intelligence Modules

### Renal Intelligence
eGFR trend analysis, CKD staging, albuminuria classification, KDIGO risk stratification, nephrotoxic medication exposure assessment, renoprotective coverage evaluation, and CKD trajectory forecasting.

### Cardiovascular Intelligence
Hypertension control analysis, ASCVD risk reasoning, long-term myocardial infarction and stroke risk modeling, heart failure progression assessment, and medication optimization opportunities.

### Metabolic Intelligence
Obesity trajectory modeling, prediabetes and metabolic syndrome progression, diabetes conversion risk forecasting, and weight-based intervention identification.

### Hepatic Intelligence
MASLD risk assessment, obesity-related liver disease modeling, cirrhosis progression identification, and missing monitoring detection (AST, ALT, bilirubin, platelets, albumin).

---

## Longitudinal Disease Reasoning

The system models causal disease cascades rather than isolated diagnoses. Examples of interconnected reasoning chains:

- Obesity → Sleep Apnea → Hypertension → CKD acceleration
- Metabolic Syndrome → MASLD progression
- Nephrotoxic medications → Accelerated renal decline
- Uncontrolled hypertension → Cardiovascular event trajectory

This systems-level reasoning differentiates the platform from traditional clinical summarization.

---

## Clinical Intelligence Workflow

1. FHIR patient context is received through SHARP context propagation
2. MCP retrieves structured patient data from the FHIR server
3. A computational longitudinal patient model is assembled
4. Organ-system intelligence modules analyze disease trajectories
5. Preventable deterioration pathways are identified
6. Care gaps and intervention opportunities are prioritized
7. Specialist escalation is triggered for complex multimorbidity cases
8. Structured, clinician-ready pre-visit intelligence is returned

---

## Repository Structure

```
.
├── agents/
│   ├── orchestrator/
│   │   ├── agent.py
│   │   ├── main.py
│   │   └── prompts/
│   └── external_specialist/
│       ├── agent.py
│       ├── main.py
│       └── middleware.py
│
├── mcp-server/
│   └── src/
│       ├── server.py
│       ├── tools/
│       ├── model_builder/
│       ├── evidence/
│       └── systems/
│           ├── renal.py
│           ├── cardiovascular.py
│           ├── metabolic.py
│           └── hepatic.py
│
├── shared/
│   ├── mcp_client.py
│   ├── fhir_hook.py
│   ├── middleware.py
│   ├── app_factory.py
│   └── adk_tools.py
│
├── examples/
├── docs/
└── README.md
```

---

## Key Components

| File | Responsibility |
|---|---|
| `fhir_hook.py` | Extracts SHARP/FHIR context and propagates patient-aware metadata into the orchestration layer |
| `middleware.py` | Handles A2A protocol normalization, compatibility translation, and response shaping |
| `mcp_client.py` | Communication layer between orchestrator agents and MCP clinical tools |
| `renal.py` | Longitudinal renal risk modeling — eGFR, CKD staging, KDIGO, nephrotoxic burden |
| `agent.py` | Primary clinical intelligence orchestration workflow definition |
| `server.py` | MCP server exposing patient-aware clinical reasoning tools |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.11 |
| Agent Framework | Google ADK |
| Agent Protocol | MCP Protocol, A2A Protocol |
| LLM Backend | LiteLLM + Gemini Models |
| API Layer | FastAPI |
| Clinical Data Standard | FHIR R4 |
| Patient Context | SHARP Context Propagation |
| Deployment | Cloud Run, ngrok |
| Synthetic Data | Synthea™ Synthetic Patient Generator |

---

## Endpoints

| Component | Endpoint |
|---|---|
| MCP Clinical Server | `<ADD_MCP_SERVER_LINK_HERE>` |
| External Specialist Agent | `<ADD_EXTERNAL_AGENT_LINK_HERE>` |
| Orchestrator Agent | `<ADD_ORCHESTRATOR_LINK_HERE>` |

---

## Data Source

Synthetic patient records were generated using [Synthea™](https://synthetichealth.github.io/synthea/). FHIR R4 resources were used throughout — Patients, Conditions, Observations, MedicationRequests, Encounters, Procedures, AllergyIntolerances, Immunizations, and CarePlans — enabling realistic longitudinal testing without real patient data.

---

## Future Work

**Clinical Expansion**
- Oncology and neurological progression modeling
- Polypharmacy interaction analysis
- Personalized treatment simulation

**Infrastructure**
- Unified gateway routing and persistent vector memory
- Asynchronous multi-agent orchestration
- Distributed deployment infrastructure

**Intelligence Layer**
- Confidence-calibrated reasoning with evidence citation
- Adaptive specialist escalation routing
- Temporal patient graph modeling

**Clinical Integration**
- SMART-on-FHIR integration
- EHR-native deployment
- Real-time deterioration monitoring hooks

---

## Disclaimer

This project is intended for research, educational, and hackathon purposes only. It is not a medical device and must not be used for real-world clinical decision-making without appropriate validation and regulatory review.
