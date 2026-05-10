# Phantom Architecture

## System Overview

Phantom is a clinical simulation platform composed of two artifacts that communicate through standardized protocols. The MCP server exposes structured clinical tools; the Pre-Visit Intelligence Agent on the Prompt Opinion platform consumes those tools to generate clinician-facing briefings. SHARP-on-MCP carries patient context between layers, FHIR R4 carries patient data, and validated clinical algorithms generate the simulation outputs.

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Clinician                                  │
│                              │                                      │
│                    "Prep me for my next patient"                    │
│                              ▼                                      │
│ ┌───────────────────────────────────────────────────────────────┐   │
│ │              Prompt Opinion Platform (Po)                     │   │
│ │                                                               │   │
│ │   ┌─────────────────────────────────────────────────────┐     │   │
│ │   │      Pre-Visit Intelligence Agent (A2A)             │     │   │
│ │   │                                                     │     │   │
│ │   │   - System prompt (agent identity, workflow)        │     │   │
│ │   │   - Briefing template (10 sections, structured)     │     │   │
│ │   │   - Reasoning loop over MCP tool calls              │     │   │
│ │   └─────────────────────────────────────────────────────┘     │   │
│ │                              │                                │   │
│ │           SHARP context: X-FHIR-Server-URL, SMART JWT         │   │
│ │           MCP transport:   Streamable HTTP                    │   │
│ │                              ▼                                │   │
│ └───────────────────────────────────────────────────────────────┘   │
│                                │                                    │
│ ┌──────────────────────────────────────────────────────────────┐    │
│ │                  Phantom MCP Server                          │    │
│ │                                                              │    │
│ │   FastAPI mount → FastMCP → Tool router                      │    │
│ │                                                              │    │
│ │   ┌──────────────────────────────────────────────────┐       │    │
│ │   │             3 MCP Tools                          │       │    │
│ │   │  - build_patient_model                           │       │    │
│ │   │  - simulate_scenario                             │       │    │
│ │   │  - compare_interventions                         │       │    │
│ │   └──────────────────────────────────────────────────┘       │    │
│ │                                                              │    │
│ │   ┌──────────────────────────────────────────────────┐       │    │
│ │   │            Patient Model Builder                 │       │    │
│ │   │  - Trajectory regression (numpy/scipy)           │       │    │
│ │   │  - Multi-system state assembly                   │       │    │
│ │   └──────────────────────────────────────────────────┘       │    │
│ │                                                              │    │
│ │   ┌──────────────────────────────────────────────────┐       │    │
│ │   │            Simulation Engine                     │       │    │
│ │   │  - Disease progression models                    │       │    │
│ │   │  - Drug effect modifiers                         │       │    │
│ │   │  - Comorbidity cascade application               │       │    │
│ │   └──────────────────────────────────────────────────┘       │    │
│ │                                                              │    │
│ │   ┌──────────────────────────────────────────────────┐       │    │
│ │   │         Clinical Evidence Base                   │       │    │
│ │   │  - risk_equations.py    (8 algorithms)           │       │    │
│ │   │  - drug_knowledge.py    (21 drugs)               │       │    │
│ │   │  - trial_data.py        (10 trials)              │       │    │
│ │   │  - guidelines.py        (36 rules)               │       │    │
│ │   │  - disease_progression.py (4 models)             │       │    │
│ │   └──────────────────────────────────────────────────┘       │    │
│ │                                                              │    │
│ │   ┌──────────────────────────────────────────────────┐       │    │
│ │   │             FHIR Client                          │       │    │
│ │   │  - httpx async client                            │       │    │
│ │   │  - Pagination handling                           │       │    │
│ │   │  - SMART JWT authentication                      │       │    │
│ │   └──────────────────────────────────────────────────┘       │    │
│ └──────────────────────────────────────────────────────────────┘    │
│                                │                                    │
│                  FHIR R4 REST API                                   │
│                                ▼                                    │
│ ┌──────────────────────────────────────────────────────────────┐    │
│ │              FHIR Server (HAPI / Epic / Cerner)              │    │
│ │   - Patient, Condition, Observation, MedicationRequest...    │    │
│ └──────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Components

### Phantom MCP Server (`mcp-server/src/`)

**`server.py`** — Entry point. Mounts FastMCP onto FastAPI. Registers the 3 tools. Patches the FastMCP capabilities object to advertise the SHARP-on-MCP `prompt-opinion-fhir-context` extension. Configures structlog for JSON logging.

**`fhir_client.py`** — Async FHIR R4 client built on httpx. Handles bundle pagination, retry logic, and timeout management. Accepts the FHIR server URL and SMART JWT extracted from request headers.

**`patient_model.py`** — Patient model builder. Takes raw FHIR resources and produces a structured patient state object containing demographics, conditions, medications, lab trajectories, vital trajectories, calculated risk scores, care gaps, and diagnostic gaps.

**`simulation/engine.py`** — Forward simulation engine. Takes a patient model and a scenario specification, applies drug effect modifiers from the evidence base, projects outcomes at 6/12/24 months across all affected systems.

**`simulation/comparison.py`** — Comparison engine. Runs N simulations in parallel, ranks them by patient-specific outcome dimensions, returns a structured comparison table.

### Clinical Evidence Base (`mcp-server/src/evidence/`)

The evidence base is pure Python with no external database dependency. All clinical knowledge is encoded as Python data structures and re-exported from `__init__.py`. This makes the server deployable as a single container with no DB provisioning.

| Module | Lines | Public API |
|--------|-------|-----------|
| `risk_equations.py` | 986 | 8 functions: CKD-EPI 2021, ASCVD PCE, FIB-4, qSOFA, KDIGO matrix, trajectory regression |
| `drug_knowledge.py` | 2,757 | 8 functions: drug lookup by name/RxCUI/class, contraindication checking, interaction detection |
| `trial_data.py` | 1,578 | 7 functions: trial lookup, drug-to-trial mapping, eGFR slope data, subgroup analysis |
| `guidelines.py` | 1,626 | 2 evaluators: care gap evaluation (25+ rules), diagnostic gap evaluation (11 rules) |
| `disease_progression.py` | 941 | 5 functions: CKD/DM/CV/MASLD progression models + comorbidity cascade modifiers |

### Pre-Visit Intelligence Agent (`agent-config/`)

**`system-prompt.md`** — 257-line agent system prompt with 8 sections: agent identity, core principles, workflow decision tree, tool output interpretation, prioritization rules, output formatting, example interactions, and guardrails.

**`briefing-template.md`** — 349-line structured briefing template with 10 required sections: header, patient snapshot, trajectory alert, top visit priorities, decision point, diagnostic gaps, suggested visit agenda, orders to place today, documentation starter, confidence footer.

---

## Data Flow Diagrams

### Tool Invocation Flow

```
1. Clinician sends message in Po workspace
        │
        ▼
2. Pre-Visit Agent reasoning loop decides which tool to call
        │
        ▼
3. Po platform issues MCP tool call over Streamable HTTP
   - Headers: X-FHIR-Server-URL, Authorization (SMART JWT)
   - Body: tool name + arguments
        │
        ▼
4. Phantom server middleware extracts SHARP context
   - Validates JWT
   - Decodes patient ID from JWT claims
   - Stores context for tool execution
        │
        ▼
5. Tool handler executes
   - Fetches FHIR resources via FHIR client
   - Builds patient model
   - Runs simulation / comparison
        │
        ▼
6. Structured response returned to agent
        │
        ▼
7. Agent decides next action (call another tool, or compose briefing)
        │
        ▼
8. Final briefing rendered in Po workspace
```

### SHARP Context Propagation

```
EHR Session
    │
    │  patient context (patient ID, FHIR server URL)
    │
    ▼
Po Workspace
    │
    │  X-FHIR-Server-URL: https://fhir.example.com/r4
    │  Authorization: Bearer <SMART JWT containing patient ID>
    │
    ▼
Pre-Visit Agent
    │
    │  (same headers passed transparently)
    │
    ▼
Phantom MCP Server middleware
    │
    │  Extract X-FHIR-Server-URL → use as FHIR base URL
    │  Decode JWT → extract `patient` claim
    │
    ▼
Tool execution
    │
    │  fhir_client = FHIRClient(base_url, jwt)
    │  patient_data = await fhir_client.fetch_patient(patient_id)
    │
    ▼
FHIR Server
```

The agent never sees or passes patient IDs as arguments. Tool schemas are context-agnostic. This is the architectural benefit of SHARP — clean tool interfaces decoupled from session state.

### Multi-Tool Orchestration

```
Agent: build_patient_model()
   │
   ▼
   patient_model {
     trajectories: { eGFR: -1.6/yr, HbA1c: +0.5/yr },
     risk_scores: { ASCVD_10yr: 22%, KDIGO: G3a/A2 },
     care_gaps: [SGLT2i missing, statin titration],
     diagnostic_gaps: [CKD-anemia, MASLD pattern]
   }
   │
   ▼
Agent: simulate_scenario(scenario="inaction", horizon=12)
   │
   ▼
   inaction_projection {
     eGFR_at_12mo: 41,
     HbA1c_at_12mo: 8.7,
     time_to_dialysis: 8.2 years,
     stage_progression_probability: 0.58
   }
   │
   ▼
Agent: compare_interventions(["empagliflozin", "semaglutide", "tirzepatide"])
   │
   ▼
   comparison {
     ranked: [
       { drug: "empagliflozin", reason: "renoprotection priority", citation: "DAPA-CKD" },
       { drug: "semaglutide", reason: "weight + CV", citation: "SUSTAIN-6" },
       { drug: "tirzepatide", reason: "max HbA1c reduction", citation: "SURPASS-4" }
     ]
   }
   │
   ▼
Agent: compose briefing using template
```

---

## Tech Stack Rationale

### Why Python (over TypeScript)
The clinical algorithm ecosystem (numpy, scipy, scikit-learn, lifelines) is overwhelmingly Python. Translating CKD-EPI or Cox regression to TypeScript would have meant either reimplementing or calling a Python service anyway. Building natively in Python kept the stack simple and let us use scipy for the trajectory regression directly.

### Why FastMCP (over the raw MCP SDK)
FastMCP provides clean decorator-based tool registration, automatic JSON schema generation from type hints, and transport abstraction. Writing the same server with the raw MCP SDK would have required manual schema construction and transport plumbing. FastMCP let us focus on the clinical logic.

### Why FastAPI mount pattern
Mounting FastMCP onto FastAPI gave us a single ASGI application with both standard HTTP endpoints (health checks, debug routes) and the MCP endpoint. This matches deployment expectations for production hosting platforms (Railway, Fly.io, Cloud Run) that expect a single ASGI app.

### Why structlog for logging
Healthcare systems require auditable logs. structlog produces structured JSON logs out of the box, with consistent context propagation across async boundaries. This is the right primitive for clinical audit trails.

### Why pure-Python evidence base (no DB)
Every external dependency is a deployment risk. A SQL database means provisioning, migrations, connection pooling, and a failure mode. By encoding the evidence base as Python data structures, the server has zero runtime dependencies beyond the Python process. Updating the evidence base means a code change and a redeploy — auditable through git history. The performance cost is negligible (the evidence base loads in milliseconds at startup).

---

## Module Dependency Graph

```
server.py
    ├── fhir_client.py
    ├── patient_model.py
    │       ├── evidence/risk_equations.py
    │       ├── evidence/drug_knowledge.py
    │       └── evidence/guidelines.py
    │
    └── simulation/
            ├── engine.py
            │       ├── evidence/disease_progression.py
            │       ├── evidence/drug_knowledge.py
            │       └── evidence/trial_data.py
            │
            └── comparison.py
                    └── engine.py

evidence/__init__.py
    ├── risk_equations.py     (independent)
    ├── drug_knowledge.py     (independent)
    ├── trial_data.py         (independent)
    ├── guidelines.py         (uses risk_equations)
    └── disease_progression.py (uses drug_knowledge)
```

The evidence base modules have minimal cross-dependencies, which keeps testing and refactoring straightforward.

---

## Scaling Considerations

The current architecture is designed for a hackathon-scale deployment: one MCP server instance, synchronous tool execution, in-memory evidence base. Scaling to production would involve:

- **Horizontal scaling:** The MCP server is stateless (all state lives in FHIR or in the request). Multiple instances can run behind a load balancer with no coordination required.
- **Caching:** Patient models could be cached per session to avoid redundant FHIR fetches and risk calculations on repeated tool calls within the same workflow.
- **FHIR client pooling:** A single shared httpx connection pool would reduce per-request overhead.
- **Async-first evidence access:** The evidence base could be moved to an async-friendly format (e.g., loaded into Redis at startup) if the in-memory footprint becomes a problem with much larger drug/trial coverage.
- **Observability:** Adding OpenTelemetry tracing would let operators trace a clinician's question end-to-end across Po → Agent → MCP → FHIR.
- **Rate limiting:** Production deployments would need per-tenant rate limiting at the MCP server boundary to protect the FHIR server from runaway agent loops.
- **Audit log persistence:** Structured logs would need to be shipped to a persistent audit log store (e.g., Elasticsearch, Datadog) for compliance.