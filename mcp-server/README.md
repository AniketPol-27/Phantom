# Phantom MCP Server

The clinical simulation engine that powers the Phantom system.

## Overview

This MCP server exposes three tools that any AI agent can invoke to perform clinical reasoning on FHIR patient data:

| Tool | Purpose |
|------|---------|
| `build_patient_model` | Constructs a computational patient model from FHIR with trajectories and confidence scoring |
| `simulate_scenario` | Forward simulation of clinical scenarios (medication changes, inaction, diagnostic gaps) |
| `compare_interventions` | Head-to-head intervention comparison personalized to the patient |

## Local Development

### Setup

```bash
# From mcp-server/ directory
uv sync
cp ../.env.example .env
```

### Run

```bash
uv run python -m src.server
```

Server will be available at `http://localhost:8080/mcp`.

### Test

```bash
uv run pytest
```

## Deployment

See [`../docs/deployment.md`](../docs/deployment.md).

## Architecture

See [`../docs/architecture.md`](../docs/architecture.md).