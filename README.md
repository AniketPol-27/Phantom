# Phantom

> The patient digital twin for clinical reasoning

Phantom transforms raw FHIR patient data into a computational model, then lets AI agents simulate clinical scenarios — before real decisions are made. Built on MCP + SHARP + FHIR R4 for the Prompt Opinion platform.

---

## Why Phantom

Clinicians face high-stakes decisions every day with no way to simulate outcomes before acting. Adding a medication, adjusting a dose, ordering a workup — each decision affects interconnected systems in ways that are hard to reason about in real time. Phantom gives clinicians (and the AI agents that assist them) a validated, evidence-grounded simulation layer: a patient digital twin that can be run forward in time, stressed with interventions, and queried for projected outcomes — all before a single order is written.

---

## What's Inside

This monorepo contains two artifacts:

### 1. Phantom MCP Server (`mcp-server/`)

A Python MCP server exposing 3 clinical tools:

- **`build_patient_model`** — Ingests FHIR R4 patient data and constructs a multi-system computational model with trajectories, risk scores, care gaps, and diagnostic gaps
- **`simulate_scenario`** — Runs a forward simulation of a clinical scenario (add a drug, change a dose, do nothing) and projects outcomes across renal, cardiovascular, metabolic, and hepatic systems
- **`compare_interventions`** — Runs multiple simulations head-to-head and returns a personalized ranked comparison, grounded in trial evidence

### 2. Pre-Visit Intelligence Agent (`agent-config/`)

An AI agent configured on the Prompt Opinion platform that uses the 3 MCP tools to generate structured Pre-Visit Briefings for clinicians. A clinician types "Prep me for my next patient" and receives a one-page clinical document with trajectory alerts, ranked visit priorities, a decision comparison table, diagnostic gaps, and a suggested visit agenda.

---

## Architecture

```
Clinician
    │
    ▼
Po Workspace (Prompt Opinion Platform)
    │
    ▼
Pre-Visit Intelligence Agent
    │  (MCP tool calls via Streamable HTTP)
    │  (SHARP context: X-FHIR-Server-URL, SMART JWT)
    ▼
Phantom MCP Server
    │  (FHIR R4 queries via httpx)
    ▼
FHIR Server (patient data)
```

When a clinician sends a message, the Pre-Visit Intelligence Agent decides which tools to call. SHARP-on-MCP propagates the patient's FHIR server URL and identity via HTTP headers — the agent never needs to pass patient IDs as tool arguments. The MCP server extracts this context, fetches the patient's FHIR data, runs validated clinical algorithms, and returns a structured patient model that the agent uses to compose the briefing.

---

## Tools

| Tool | Purpose | Returns |
|------|---------|---------|
| `build_patient_model` | Constructs computational patient model from FHIR R4 data | Multi-system patient state with trajectories, risk scores, care gaps, diagnostic gaps |
| `simulate_scenario` | Forward simulation of a clinical scenario against the patient model | Multi-system impact projection at 6, 12, and 24 months |
| `compare_interventions` | Head-to-head comparison of 2-4 interventions | Personalized ranked options with trial evidence citations |

---

## Clinical Evidence Base

The simulation engine is grounded in structured clinical evidence — not LLM generation:

| Component | Coverage |
|-----------|----------|
| Validated risk equations | CKD-EPI 2021, ACC/AHA Pooled Cohort Equations, FIB-4, qSOFA, KDIGO 2024 |
| Clinical trials encoded | 10 major trials (DAPA-CKD, CREDENCE, EMPA-REG OUTCOME, EMPA-KIDNEY, SUSTAIN-6, LEADER, REWIND, SPRINT, SURPASS-4, UKPDS-33) |
| Drug knowledge base | 21 drugs across 11 therapeutic classes with multi-system effect profiles |
| Care gap rules | 25+ guideline-based rules (ADA, ACC/AHA, KDIGO, USPSTF) |
| Diagnostic gap rules | 11 pattern-based rules for undiagnosed conditions |

Every output cites a trial name and PMID. No hallucination.

---

## Standards Compliance

- ✅ Model Context Protocol (MCP) — Streamable HTTP transport
- ✅ Agent-to-Agent Protocol (A2A)
- ✅ SHARP-on-MCP — Healthcare context propagation
- ✅ FHIR R4 (HL7) — Patient data standard
- ✅ LOINC — Lab and vital observation codes
- ✅ SNOMED CT — Condition coding
- ✅ RxNorm — Medication coding
- ✅ ICD-10 — Diagnosis coding
- ✅ Validated clinical algorithms (CKD-EPI 2021, ACC/AHA PCE, KDIGO 2024)

---

## Quick Start

```bash
git clone https://github.com/AniketPol-27/Phantom.git
cd Phantom/mcp-server
uv sync
uv run python -m src.server
```

Server starts at `http://localhost:8080/mcp`

### Connecting to Prompt Opinion

1. Deploy the MCP server to a public HTTPS URL (e.g., via ngrok for development, or Railway/Fly.io for production)
2. In Po: navigate to **Configuration → MCP Servers**
3. Add your server URL with **Streamable HTTP** transport
4. Enable **"Prompt Opinion FHIR Context"** extension
5. Approve the requested FHIR scopes
6. Open the Pre-Visit Intelligence Agent and start a session

---

## Repository Structure

```
Phantom/
├── mcp-server/                  # Python MCP server
│   ├── src/
│   │   ├── server.py            # FastAPI + FastMCP entry point
│   │   ├── fhir_client.py       # FHIR R4 data fetcher
│   │   ├── patient_model.py     # Patient model builder
│   │   ├── simulation/          # Simulation + comparison engines
│   │   └── evidence/            # Clinical evidence base
│   │       ├── risk_equations.py    # CKD-EPI, ASCVD, FIB-4, qSOFA
│   │       ├── drug_knowledge.py    # 21 drug profiles
│   │       ├── trial_data.py        # 10 clinical trials
│   │       ├── guidelines.py        # 36 guideline rules
│   │       └── disease_progression.py # CKD/DM/CV/MASLD models
│   └── tests/
│       └── test_evidence.py     # 36 passing unit tests
├── agent-config/
│   ├── system-prompt.md         # Pre-Visit Agent system prompt
│   └── briefing-template.md     # 10-section briefing template
├── test-data/
│   └── patient-maria-santos.json  # Synthetic FHIR R4 test patient (96 resources)
├── docs/
│   ├── SUBMISSION.md            # Hackathon submission write-up
│   ├── ARCHITECTURE.md          # System architecture deep-dive
│   ├── TOOLS_REFERENCE.md       # Tool schemas and examples
│   └── SHARP_INTEGRATION.md     # SHARP integration guide
└── README.md                    # This file
```

---

## Documentation

- [Hackathon Submission](docs/SUBMISSION.md)
- [Architecture Deep-Dive](docs/ARCHITECTURE.md)
- [Tools Reference](docs/TOOLS_REFERENCE.md)
- [SHARP Integration Guide](docs/SHARP_INTEGRATION.md)

---

## Hackathon Submission

**Event:** Agents Assemble — The Healthcare AI Endgame Challenge
**Platform:** Prompt Opinion
**Prize Pool:** $25,000 ($7,500 Grand Prize)
**Repository:** https://github.com/AniketPol-27/Phantom

---

## Team

- **Aniket Pol** — Backend, FHIR client, simulation engine, platform integration
- **Jasnoor Kaur** — Clinical knowledge base, evidence modules, agent configuration, documentation

---

## License

MIT — see LICENSE