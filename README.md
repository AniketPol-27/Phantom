<div align="center">

# Phantom Clinical Intelligence

### Longitudinal Clinical Intelligence Through MCP-Native FHIR Reasoning and Interoperable Specialist Agents

<p align="center">
  <img src="https://img.shields.io/badge/FHIR-R4-blue" />
  <img src="https://img.shields.io/badge/Python-3.11-green" />
  <img src="https://img.shields.io/badge/MCP-Protocol-orange" />
  <img src="https://img.shields.io/badge/A2A-Interoperability-purple" />
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" />
</p>

<p>
<i>
A longitudinal clinical reasoning platform for proactive, preventative, and systems-level healthcare intelligence.
</i>
</p>

</div>

---

# Executive Summary

Phantom Clinical Intelligence is a FHIR-native longitudinal clinical reasoning system designed to transform fragmented patient records into structured, forward-looking clinical intelligence.

The platform combines:
- MCP-native patient-aware reasoning
- computational disease modeling
- multi-system longitudinal analysis
- preventative care prioritization
- interoperable specialist-agent consultation

to generate clinician-ready intelligence before patient encounters occur.

Rather than summarizing isolated visits, Phantom reasons across time — identifying preventable deterioration pathways, forecasting chronic disease progression, surfacing unresolved care gaps, and prioritizing interventions across interconnected organ systems.

---

# System Overview

The Phantom ecosystem is composed of three major components:

| Component | Role |
|---|---|
| **Phantom Nexus Agent** | Central orchestration and intelligence coordination layer |
| **Phantom MCP Server** | Computational patient modeling and longitudinal reasoning engine |
| **Phantom Specialist Intelligence Agent** | Interoperable specialist consultation and escalation layer |

---

# Platform Architecture

```text
                    ┌──────────────────────┐
                    │    Prompt Opinion    │
                    └──────────┬───────────┘
                               │
                               ▼
              ┌────────────────────────────────┐
              │     Phantom Nexus Agent        │
              │   (Central Orchestration AI)   │
              └────────────────┬───────────────┘
                               │
          ┌────────────────────┴────────────────────┐
          │                                         │
          ▼                                         ▼
┌────────────────────────┐         ┌────────────────────────────┐
│   Phantom MCP Server   │         │ Phantom Specialist         │
│                        │         │ Intelligence Agent         │
│ - FHIR Retrieval       │         │                            │
│ - Patient Modeling     │         │ - Advanced Longitudinal    │
│ - Risk Analysis        │         │   Consultation             │
│ - Simulation           │         │ - Specialist Reasoning     │
│ - Forecasting          │         │ - Interoperable A2A Logic  │
└────────────────────────┘         └────────────────────────────┘
```

---

# Component Responsibilities

---

# 1. Phantom Nexus Agent

The **Phantom Nexus Agent** acts as the central intelligence and orchestration layer for the entire platform.

This agent is configured directly within Prompt Opinion and serves as the primary user-facing intelligence interface.

Responsibilities include:
- coordinating longitudinal clinical workflows
- managing MCP tool invocation
- orchestrating patient-model generation
- triggering longitudinal simulations
- identifying care gaps and intervention priorities
- escalating to specialist consultation when appropriate
- generating structured clinician-ready outputs

The Nexus Agent acts as the bridge between:
- Prompt Opinion
- the Phantom MCP Server
- and the Phantom Specialist Intelligence Agent

### Built Using
- Prompt Opinion Agent Framework
- A2A orchestration logic
- Custom middleware integration

### Published Endpoint
`<ADD_PHANTOM_NEXUS_AGENT_LINK_HERE>`

---

# 2. Phantom MCP Server

The **Phantom MCP Server** is the computational clinical intelligence engine of the platform.

It performs patient-aware longitudinal reasoning directly over FHIR R4 resources.

Core responsibilities include:
- FHIR retrieval and contextualization
- computational patient-model construction
- organ-system longitudinal analysis
- disease trajectory forecasting
- intervention simulation
- preventative care intelligence
- longitudinal monitoring analysis
- medication burden assessment

The MCP server performs systems-level reasoning across:
- renal disease progression
- cardiovascular risk
- metabolic deterioration
- hepatic disease trajectories

while integrating:
- medication effects
- chronic disease interactions
- longitudinal trends
- preventative opportunities

### Built Using
- Python
- FastAPI
- MCP protocol tooling
- Custom longitudinal reasoning systems

### Published Endpoint
`<ADD_PHANTOM_MCP_SERVER_LINK_HERE>`

---

# 3. Phantom Specialist Intelligence Agent

The **Phantom Specialist Intelligence Agent** provides interoperable specialist consultation capabilities using the A2A protocol.

This component was designed to explore:
- distributed clinical reasoning
- modular specialist escalation
- interoperable multi-agent workflows
- advanced longitudinal consultation architectures

The specialist agent can:
- receive patient-aware contextual requests
- analyze advanced multimorbidity cases
- perform specialist longitudinal reasoning
- return structured consultation intelligence
- support escalation workflows initiated by the Nexus Agent

Custom middleware was implemented to support:
- A2A protocol normalization
- JSON-RPC compatibility handling
- task schema correction
- role normalization
- response shaping for Prompt Opinion interoperability

### Built Using
- Google ADK
- A2A protocol integration
- Custom middleware translation layers

### Published Endpoint
`<ADD_PHANTOM_SPECIALIST_AGENT_LINK_HERE>`

---

# Why This Matters

Modern healthcare systems generate enormous volumes of structured patient data, yet most clinical workflows remain:
- reactive
- fragmented
- encounter-centric

Clinicians are expected to synthesize:
- laboratory histories
- medications
- chronic conditions
- procedures
- preventative gaps
- longitudinal trends

within extremely limited clinical time.

Most existing AI systems focus on:
- summarization
- retrieval
- static risk scoring

Very few systems perform:
- longitudinal disease reasoning
- cross-system causal modeling
- deterioration forecasting
- proactive intervention prioritization

Phantom was designed specifically to address this gap.

---

# Clinical Intelligence Workflow

```text
FHIR Context
    ↓
Phantom Nexus Agent
    ↓
Phantom MCP Server
    ↓
Computational Patient Model
    ↓
Longitudinal Risk Analysis
    ↓
Care Gap Identification
    ↓
Intervention Prioritization
    ↓
Optional Specialist Escalation
    ↓
Phantom Specialist Intelligence Agent
    ↓
Structured Clinical Intelligence Output
```

---

# Core Capabilities

## Longitudinal Disease Intelligence
- Multi-year disease trajectory forecasting
- Chronic disease cascade modeling
- Progressive deterioration identification
- Temporal patient-state reasoning

## FHIR-Native Clinical Reasoning
- Direct FHIR R4 integration
- SHARP context propagation
- Patient-aware MCP workflows
- Real-time contextualized retrieval

## Computational Risk Modeling
- CKD progression analysis
- ASCVD trajectory modeling
- Metabolic syndrome forecasting
- MASLD progression assessment
- Medication burden analysis

## Preventative Care Intelligence
- Intervention prioritization
- Care-gap detection
- Monitoring recommendations
- Early-risk interception
- Medication optimization opportunities

## Interoperable Specialist Escalation
- MCP-native orchestration
- External A2A specialist consultation
- Distributed clinical reasoning
- Modular multi-agent architecture

---

# Organ System Intelligence Modules

## Renal Intelligence
- eGFR trajectory analysis
- CKD staging and KDIGO stratification
- Albuminuria assessment
- Renoprotective coverage analysis
- Nephrotoxic medication burden detection

## Cardiovascular Intelligence
- ASCVD trajectory modeling
- Hypertension progression analysis
- Cardiovascular event forecasting
- Heart failure deterioration assessment

## Metabolic Intelligence
- Obesity progression modeling
- Prediabetes conversion forecasting
- Metabolic syndrome analysis
- Weight-driven deterioration reasoning

## Hepatic Intelligence
- MASLD risk assessment
- Obesity-associated hepatic progression
- Missing liver surveillance detection
- Cirrhosis progression identification

---

# Longitudinal Systems-Level Reasoning

The platform models interconnected disease cascades rather than isolated diagnoses.

### Example Cascades

```text
Obesity
  → Sleep Apnea
    → Hypertension
      → Accelerated CKD Risk
```

```text
Metabolic Syndrome
  → Insulin Resistance
    → Hepatic Steatosis
      → MASLD Progression
```

```text
NSAID Exposure
  → Nephrotoxic Burden
    → Progressive Renal Decline
```

This systems-level reasoning differentiates Phantom from traditional encounter summarization systems.

---

# Repository Structure

```text
.
├── agent-config/
│   ├── prompts/
│   ├── schemas/
│   └── examples/
│
├── docs/
│   ├── architecture/
│   ├── workflows/
│   └── screenshots/
│
├── mcp-server/
│   ├── src/
│   │   ├── server.py
│   │   ├── tools/
│   │   ├── systems/
│   │   │   ├── renal.py
│   │   │   ├── cardiovascular.py
│   │   │   ├── metabolic.py
│   │   │   └── hepatic.py
│   │   ├── model_builder/
│   │   ├── evidence/
│   │   └── clients/
│   │
│   └── requirements.txt
│
├── phantom-adk/
│   ├── orchestrator/
│   │   ├── app.py
│   │   ├── agent.py
│   │   └── prompts/
│   │
│   ├── shared/
│   │   ├── adk_tools.py
│   │   ├── app_factory.py
│   │   ├── fhir_hook.py
│   │   ├── mcp_client.py
│   │   └── middleware.py
│   │
│   └── external_specialist/
│       ├── app.py
│       ├── agent.py
│       └── middleware.py
│
├── test-data/
│   ├── fhir/
│   └── examples/
│
├── README.md
├── LICENSE
├── .gitignore
└── .env.example
```

---

# Key Components

| Component | Responsibility |
|---|---|
| `fhir_hook.py` | Extracts SHARP/FHIR context and propagates patient-aware metadata |
| `middleware.py` | Handles A2A protocol normalization and response compatibility |
| `mcp_client.py` | Communication layer between orchestrator agents and MCP tools |
| `renal.py` | Longitudinal renal risk modeling and CKD intelligence |
| `agent.py` | Primary orchestration workflow for clinical intelligence generation |
| `server.py` | MCP server exposing patient-aware clinical reasoning tools |

---

# Technology Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.11 |
| Agent Framework | Google ADK |
| Protocols | MCP, A2A |
| LLM Layer | LiteLLM + Gemini |
| API Framework | FastAPI |
| Clinical Standard | FHIR R4 |
| Context Propagation | SHARP |
| Deployment | Cloud Run, ngrok |
| Synthetic Data | Synthea™ |

---

# Data Source

Synthetic patient records were generated using:

### Synthea™ Synthetic Patient Generator

https://synthetichealth.github.io/synthea/

FHIR R4 resources used throughout the platform include:
- Patients
- Conditions
- Observations
- MedicationRequests
- Encounters
- Procedures
- Immunizations
- AllergyIntolerances
- CarePlans

This enabled realistic longitudinal testing without real patient data.

---

# Future Directions

## Clinical Modeling
- Oncology progression modeling
- Neurological deterioration forecasting
- Polypharmacy interaction intelligence
- Personalized intervention simulation

## Infrastructure
- Persistent vector memory
- Distributed asynchronous orchestration
- Unified clinical routing gateway
- Event-driven monitoring workflows

## Intelligence Layer
- Confidence-calibrated reasoning
- Evidence citation generation
- Adaptive specialist escalation
- Temporal patient graph modeling

## Clinical Integration
- SMART-on-FHIR deployment
- EHR-native integration
- Real-time deterioration monitoring
- Clinical workflow embedding

---

# Research Direction

This project explores how:
- longitudinal computational reasoning
- interoperable agent systems
- FHIR-native infrastructure
- preventative intelligence

can augment future healthcare decision-support workflows.

---

# Disclaimer

This project is intended for research, educational, and hackathon purposes only.

It is not a medical device and should not be used for real-world clinical decision-making without appropriate clinical validation or regulatory approval.
