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

# System Architecture

```text
                    ┌──────────────────────┐
                    │   Prompt Opinion     │
                    └──────────┬───────────┘
                               │
                               ▼
              ┌────────────────────────────────┐
              │ Phantom Clinical Intelligence  │
              │  (Primary MCP-native Agent)    │
              └────────────────┬───────────────┘
                               │
          ┌────────────────────┴────────────────────┐
          │                                         │
          ▼                                         ▼
┌────────────────────┐              ┌────────────────────────┐
│ MCP Clinical Layer │              │ External Specialist    │
│                    │              │ A2A Agent              │
│ - FHIR Retrieval   │              │                        │
│ - Patient Modeling │              │ - Advanced Longitudinal│
│ - Risk Analysis    │              │   Analysis             │
│ - Simulation       │              │ - Specialist Reasoning │
└────────────────────┘              └────────────────────────┘
```

---

# Core Platform Components

## 1. MCP Clinical Intelligence Server

The MCP Clinical Intelligence Server acts as the primary patient-aware computational reasoning layer.

It is responsible for:
- retrieving FHIR R4 patient resources
- assembling computational longitudinal patient models
- performing organ-system-specific risk analysis
- forecasting disease trajectories
- identifying preventable deterioration pathways
- exposing clinical reasoning tools through MCP

The server performs longitudinal reasoning across:
- renal systems
- cardiovascular systems
- metabolic systems
- hepatic systems

while also integrating:
- medication burden analysis
- preventative care intelligence
- social determinant awareness
- longitudinal monitoring gaps

### Published MCP Endpoint
`<ADD_MCP_SERVER_LINK_HERE>`

---

## 2. External A2A Specialist Agent

The External Specialist Agent provides interoperable specialist consultation capabilities using the A2A protocol.

This component was designed to explore:
- distributed clinical reasoning
- modular specialist escalation
- interoperable multi-agent workflows
- longitudinal consultation architectures

The specialist agent can:
- receive patient-aware contextual requests
- analyze advanced multimorbidity cases
- provide specialist longitudinal intelligence
- return structured clinical outputs compatible with orchestrator workflows

Custom middleware was implemented to support:
- A2A protocol normalization
- JSON-RPC compatibility handling
- task schema correction
- role normalization
- response shaping for Prompt Opinion interoperability

### Published External A2A Endpoint
`<ADD_EXTERNAL_AGENT_LINK_HERE>`

---

## 3. Orchestrator Agent

The Orchestrator Agent coordinates the overall longitudinal intelligence workflow.

It is responsible for:
- receiving clinical requests
- managing MCP tool execution
- coordinating patient-model construction
- triggering longitudinal simulations
- routing specialist escalation when required
- generating structured clinician-ready outputs

The orchestrator serves as the central intelligence layer connecting:
- Prompt Opinion
- MCP-native reasoning tools
- and external A2A specialist agents

It dynamically determines:
- which tools should execute
- which risk domains should be analyzed
- whether specialist escalation is warranted
- and how structured outputs should be generated

### Published Orchestrator Endpoint
`<ADD_ORCHESTRATOR_LINK_HERE>`

---

# Clinical Intelligence Workflow

```text
FHIR Context
    ↓
MCP Retrieval
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
Structured Pre-Visit Intelligence
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
│   │   ├── agent.py
│   │   ├── main.py
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
│       ├── agent.py
│       ├── main.py
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
