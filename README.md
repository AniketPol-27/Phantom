# Phantom

> The patient digital twin for clinical reasoning.

Phantom is a clinical simulation system built for the Prompt Opinion **Agents Assemble** hackathon. It transforms raw FHIR patient data into a computational model that AI agents can simulate clinical scenarios against — answering "what if" questions before real clinical decisions are made.

---

## What's in this repo

This monorepo contains two artifacts that together form the Phantom system:

### 1. Phantom MCP Server (`mcp-server/`)
A Model Context Protocol server exposing three clinical simulation tools:
- **`build_patient_model`** — Constructs a computational patient model from FHIR data with derived trajectories, comorbidity cascades, and confidence scoring.
- **`simulate_scenario`** — Runs forward simulations: medication changes, treatment inaction projections, and diagnostic gap detection.
- **`compare_interventions`** — Head-to-head intervention comparison personalized to the patient.

### 2. Pre-Visit Intelligence Agent (`agent-config/`)
An A2A agent configured on the Prompt Opinion platform that consumes the Phantom MCP server to generate structured pre-visit briefings for clinicians.

---

## Architecture

```
Clinician → Po Workspace → Pre-Visit Agent (A2A) → Phantom MCP Server → FHIR Server
```

SHARP context (patient ID, FHIR token) propagates automatically from the EHR session through every layer. See [`docs/architecture.md`](docs/architecture.md) for full detail.

---

## Project Structure

```
phantom/
├── mcp-server/          # Clinical Phantom MCP Server (Python)
├── agent-config/        # Pre-Visit Agent configuration for Prompt Opinion
├── test-data/           # FHIR test patient bundles
└── docs/                # Architecture, deployment, and reference docs
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker (for deployment)
- A Prompt Opinion account

### Local Development

```bash
cd mcp-server
uv sync
uv run python -m src.server
```

The MCP server will start on `http://localhost:8080/mcp`.

See [`docs/deployment.md`](docs/deployment.md) for production deployment instructions.

---

## Standards Used

- **MCP** — Model Context Protocol (tool exposure)
- **A2A** — Agent-to-Agent protocol (agent communication)
- **SHARP** — Prompt Opinion's healthcare context propagation spec
- **FHIR R4** — HL7 healthcare data standard
- **RxNorm** — NLM drug nomenclature
- **OpenFDA** — Drug interaction and label data

---

## Hackathon Submission

**Event:** Agents Assemble — The Healthcare AI Endgame Challenge
**Platform:** Prompt Opinion
**Team:** [Your team name]
**Submission Date:** [Date]

---

## License

MIT — see [`LICENSE`](LICENSE)