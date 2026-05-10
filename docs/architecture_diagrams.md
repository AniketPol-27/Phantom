# Phantom Architecture Diagrams

> Visual reference for Phantom's system design, data flow, and
> standards-based composability. All diagrams use Mermaid syntax and
> render natively on GitHub.
>
> **Audience:** developers integrating with Phantom, agent designers,
> hackathon judges, technical reviewers.

---

## Table of Contents

1. [Full Phantom System Architecture](#1-full-phantom-system-architecture)
2. [MCP Tool Invocation Flow](#2-mcp-tool-invocation-flow)
3. [SHARP Context Propagation](#3-sharp-context-propagation)
4. [FHIR Data Processing Pipeline](#4-fhir-data-processing-pipeline)
5. [Pre-Visit Agent Workflow](#5-pre-visit-agent-workflow)
6. [Multi-System Clinical Reasoning Pipeline](#6-multi-system-clinical-reasoning-pipeline)

---

## 1. Full Phantom System Architecture

```mermaid
flowchart TB
    Clinician["👨‍⚕️ Clinician"]
    PoWorkspace["🖥️ Prompt Opinion<br/>Workspace"]
    Agent["🤖 Pre-Visit<br/>Intelligence Agent"]
    PhantomMCP["⚡ Phantom MCP Server<br/>(FastAPI + FastMCP)"]
    SHARP["🔐 SHARP-on-MCP<br/>Context Layer"]
    FHIRClient["📡 FHIR R4 Client<br/>(httpx + pagination)"]
    EHR["🏥 FHIR R4 Server<br/>(EHR / SMART app)"]

    EvidenceBase["📚 Evidence Base"]
    DrugKB["💊 Drug Knowledge<br/>(35 drugs)"]
    TrialDB["🧪 Trial Data<br/>(14 trials)"]
    Guidelines["📋 Guidelines<br/>(70 care gap rules)"]
    RiskEq["📊 Risk Equations<br/>(CKD-EPI, PCE, FIB-4)"]
    Progression["📈 Disease Progression<br/>Models"]

    Clinician -->|"natural language<br/>query"| PoWorkspace
    PoWorkspace -->|"agent orchestration"| Agent
    Agent -->|"MCP tool calls"| PhantomMCP
    PhantomMCP --> SHARP
    SHARP -->|"X-FHIR-Server-URL<br/>X-Patient-ID<br/>JWT identity"| FHIRClient
    FHIRClient -->|"FHIR R4 queries"| EHR
    EHR -->|"Patient bundles"| FHIRClient
    FHIRClient -->|"raw FHIR resources"| PhantomMCP

    PhantomMCP --> EvidenceBase
    EvidenceBase --> DrugKB
    EvidenceBase --> TrialDB
    EvidenceBase --> Guidelines
    EvidenceBase --> RiskEq
    EvidenceBase --> Progression

    PhantomMCP -->|"computed patient model<br/>+ simulations<br/>+ comparisons"| Agent
    Agent -->|"clinician-facing<br/>briefing"| PoWorkspace
    PoWorkspace --> Clinician

    style Clinician fill:#e1f5ff,stroke:#0288d1,stroke-width:2px
    style PhantomMCP fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style EvidenceBase fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style EHR fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
```

**Why this architecture matters:**

- **Standards-native:** Every layer speaks an open standard (MCP, SHARP,
  FHIR R4). No proprietary protocols.
- **Composable:** The same Phantom MCP server can serve any agent on any
  MCP-compatible platform — not just Po, not just Pre-Visit Agent.
- **Decoupled evidence base:** The clinical knowledge (drugs, trials,
  guidelines) is independent of the orchestration logic. Updates to
  evidence don't require code changes to consumers.
- **Pluggable FHIR backend:** Phantom doesn't care whether the FHIR
  server is HAPI, Epic, Cerner, or a sandbox — only that it speaks
  FHIR R4.

---

## 2. MCP Tool Invocation Flow

```mermaid
sequenceDiagram
    participant Clinician
    participant Agent as Pre-Visit Agent
    participant MCP as Phantom MCP Server
    participant SHARP as SHARP Context Layer
    participant FHIR as FHIR R4 Server
    participant EB as Evidence Base

    Clinician->>Agent: "Prep me for my next patient"
    Agent->>MCP: build_patient_model(patient_id)
    MCP->>SHARP: extract context (FHIR URL, patient ID, JWT)
    SHARP->>MCP: validated context
    MCP->>FHIR: GET Patient/{id} + bundles
    FHIR-->>MCP: 96 resources
    MCP->>EB: lookup drug data, risk equations
    EB-->>MCP: drug profiles + scores
    MCP-->>Agent: patient model (multi-system state)

    Agent->>MCP: simulate_scenario(inaction, 24mo)
    MCP->>EB: load disease progression model
    EB-->>MCP: trajectory parameters
    MCP-->>Agent: projected eGFR, A1c, BP, risk scores

    Agent->>MCP: simulate_scenario(diagnostic_gap)
    MCP->>EB: evaluate 70 care gap rules + 11 dx gap rules
    EB-->>MCP: 6 gaps detected
    MCP-->>Agent: gap list with rationale

    Agent->>MCP: compare_interventions(options)
    MCP->>EB: trial data + drug profiles + patient context
    EB-->>MCP: ranked options with NNT
    MCP-->>Agent: ranked comparison table

    Agent->>Clinician: Pre-Visit Briefing (38s total)

    Note over Agent,EB: All 4 calls completed in 38 seconds
```

**Why this flow matters:**

- **Composability of tools:** The agent chains 3 distinct MCP tool calls
  to produce one briefing. Each tool is independently callable and
  reusable.
- **Evidence base reuse:** The same evidence base is queried across
  multiple tool invocations — no duplicate lookups, fast in aggregate.
- **Single context propagation:** SHARP context is extracted once, used
  across all subsequent FHIR calls — no re-authentication required.
- **Time-bounded:** Total generation time (~38 seconds) is suitable for
  pre-visit workflows.

---

## 3. SHARP Context Propagation

```mermaid
flowchart LR
    EHRSession["🏥 EHR Patient Session<br/>(Maria Santos chart open)"]
    SMARTLaunch["🚀 SMART App Launch<br/>JWT issued"]
    PoWorkspace["🖥️ Po Workspace<br/>(receives SHARP context)"]
    Agent["🤖 Pre-Visit Agent"]
    MCPHeaders["📨 MCP Request Headers<br/>X-FHIR-Server-URL<br/>X-Patient-ID<br/>Authorization: Bearer {JWT}"]
    PhantomServer["⚡ Phantom MCP Server<br/>(extracts from headers)"]
    SHARPLayer["🔐 SHARP Layer<br/>validates + parses"]
    PatientContext["✅ Validated Context:<br/>• FHIR URL<br/>• Patient ID<br/>• Clinician identity<br/>• Authorized scopes"]
    FHIRCall["📡 Authenticated FHIR call<br/>with patient ID injected"]

    EHRSession --> SMARTLaunch
    SMARTLaunch -->|"OAuth + scopes"| PoWorkspace
    PoWorkspace -->|"SHARP context attached"| Agent
    Agent -->|"MCP tool call"| MCPHeaders
    MCPHeaders --> PhantomServer
    PhantomServer --> SHARPLayer
    SHARPLayer --> PatientContext
    PatientContext --> FHIRCall

    style EHRSession fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style PatientContext fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style PhantomServer fill:#fff3e0,stroke:#f57c00,stroke-width:3px
```

**Why SHARP matters:**

- **No manual patient ID entry:** The clinician's EHR session
  automatically scopes every Phantom tool call to the right patient.
- **Security-first:** OAuth scopes and JWT identity are propagated and
  validated — the agent cannot exceed authorized scopes.
- **Auditable:** Every Phantom call is traceable to a clinician identity
  and a specific patient context — meets healthcare audit requirements.
- **Vendor-neutral:** SHARP-on-MCP works with any EHR that supports
  SMART on FHIR — not locked to a specific vendor.

---

## 4. FHIR Data Processing Pipeline

```mermaid
flowchart TB
    Start(["FHIR query initiated<br/>via build_patient_model"])
    Auth["🔐 Authenticate with<br/>SHARP-provided JWT"]
    QueryPatient["GET Patient/{id}"]
    QueryConditions["GET Condition?patient={id}"]
    QueryObservations["GET Observation?patient={id}"]
    QueryMeds["GET MedicationRequest?patient={id}"]
    QueryProcedures["GET Procedure?patient={id}"]
    QueryImmunizations["GET Immunization?patient={id}"]
    QueryEncounters["GET Encounter?patient={id}"]
    QueryAllergies["GET AllergyIntolerance?patient={id}"]

    Pagination{"More pages?"}
    NextPage["Fetch next page<br/>via Bundle.link.next"]

    Normalize["📋 Normalize to internal schema<br/>(types, units, dates)"]
    Filter["🔍 Filter by relevance<br/>(active conditions,<br/>recent labs, etc.)"]
    BuildModel["🧠 Construct multi-system<br/>patient model"]

    PatientState["📊 Patient State Object:<br/>• Demographics<br/>• Active problems<br/>• Medication list<br/>• Lab trajectories<br/>• Vital trajectories<br/>• Care history"]

    End(["Return to caller<br/>(MCP tool response)"])

    Start --> Auth
    Auth --> QueryPatient
    QueryPatient --> QueryConditions
    QueryConditions --> QueryObservations
    QueryObservations --> QueryMeds
    QueryMeds --> QueryProcedures
    QueryProcedures --> QueryImmunizations
    QueryImmunizations --> QueryEncounters
    QueryEncounters --> QueryAllergies
    QueryAllergies --> Pagination
    Pagination -->|"yes"| NextPage
    NextPage --> Pagination
    Pagination -->|"no"| Normalize
    Normalize --> Filter
    Filter --> BuildModel
    BuildModel --> PatientState
    PatientState --> End

    style Start fill:#e1f5ff,stroke:#0288d1,stroke-width:2px
    style PatientState fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style End fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
```

**Why this pipeline matters:**

- **Pagination-aware:** Real patient charts can have hundreds of
  observations across many years. Phantom handles paginated bundles
  natively.
- **Type and unit normalization:** FHIR servers vary — Phantom converts
  everything to a consistent internal schema (e.g., glucose always in
  mg/dL, eGFR always in mL/min/1.73m²).
- **Clinical relevance filtering:** Not every resource matters for every
  decision. Phantom filters to active and clinically relevant data
  before model construction.
- **Reusable model:** Once built, the patient model is cached for
  subsequent tool calls in the same session — avoiding redundant FHIR
  queries.

---

## 5. Pre-Visit Agent Workflow

```mermaid
flowchart TD
    Trigger(["Clinician opens patient chart<br/>OR types prep request"])
    LoadContext["📥 Load SHARP context<br/>(patient, FHIR URL, JWT)"]
    BuildModel["🧠 Call build_patient_model"]

    Branch1{"Patient has<br/>complex multi-system<br/>disease?"}
    SimulateInaction["📉 Call simulate_scenario(inaction)"]
    DetectGaps["🔍 Call simulate_scenario(diagnostic_gap)"]
    QuickBriefing["📄 Generate brief snapshot"]

    NeedsComparison{"Multiple intervention<br/>options viable?"}
    CompareOptions["⚖️ Call compare_interventions"]
    SkipCompare["Skip comparison"]

    SynthesizeBriefing["📝 Synthesize Pre-Visit Briefing<br/>using briefing template"]

    QualityCheck["✅ Apply clinical interpretation guide<br/>(urgency, confidence, citations)"]

    DeliverBriefing["📋 Deliver to clinician<br/>(in-line in Po workspace)"]

    Trigger --> LoadContext
    LoadContext --> BuildModel
    BuildModel --> Branch1
    Branch1 -->|"yes"| SimulateInaction
    Branch1 -->|"no"| QuickBriefing
    SimulateInaction --> DetectGaps
    DetectGaps --> NeedsComparison
    NeedsComparison -->|"yes"| CompareOptions
    NeedsComparison -->|"no"| SkipCompare
    CompareOptions --> SynthesizeBriefing
    SkipCompare --> SynthesizeBriefing
    QuickBriefing --> SynthesizeBriefing
    SynthesizeBriefing --> QualityCheck
    QualityCheck --> DeliverBriefing

    style Trigger fill:#e1f5ff,stroke:#0288d1,stroke-width:2px
    style DeliverBriefing fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    style BuildModel fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style SimulateInaction fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style DetectGaps fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style CompareOptions fill:#fff3e0,stroke:#f57c00,stroke-width:2px
```

**Why this workflow matters:**

- **Conditional tool invocation:** The agent doesn't always call all
  3 tools — simple cases get a lightweight briefing, complex cases get
  the full pipeline. Saves time and tokens.
- **Decision points are explicit:** The branches in the workflow reflect
  real clinical reasoning patterns, not arbitrary rules.
- **Quality gating:** Before delivery, every briefing passes through the
  clinical interpretation guide for tone, urgency, and citation
  consistency.
- **Reproducible:** The same workflow runs the same way for every
  patient — no improvisation.

---

## 6. Multi-System Clinical Reasoning Pipeline

```mermaid
flowchart TB
    PatientData["📊 Raw FHIR data<br/>(96 resources)"]

    SystemFilter["🔀 System-aware filtering"]

    Renal["🫘 Renal System<br/>• eGFR trajectory<br/>• UACR<br/>• electrolytes<br/>• CKD staging"]
    Metabolic["🍬 Metabolic System<br/>• A1c trajectory<br/>• weight/BMI<br/>• lipid profile<br/>• glucose patterns"]
    Cardiovascular["❤️ Cardiovascular System<br/>• BP trajectory<br/>• ASCVD risk<br/>• arrhythmias<br/>• HF markers"]
    Hepatic["🟫 Hepatic System<br/>• ALT/AST<br/>• FIB-4<br/>• MASLD risk<br/>• imaging"]
    Preventive["🛡️ Preventive Care<br/>• vaccinations<br/>• cancer screens<br/>• age-based screenings"]
    Pharmacy["💊 Medication Profile<br/>• active meds<br/>• interactions<br/>• Beers Criteria<br/>• renal dosing"]

    CrossSystem["🔗 Cross-system reasoning<br/>(e.g., NSAID × CKD × HTN)"]

    EvidenceLayer["📚 Evidence Application<br/>• 14 trials referenced<br/>• 35 drugs analyzed<br/>• 5 risk equations computed<br/>• 70 care gap rules evaluated"]

    Synthesis["🧠 Multi-system synthesis<br/>• highest-leverage interventions<br/>• competing risks weighed<br/>• patient-specific NNT computed"]

    Output["📋 Unified clinical briefing<br/>NOT siloed by specialty"]

    PatientData --> SystemFilter
    SystemFilter --> Renal
    SystemFilter --> Metabolic
    SystemFilter --> Cardiovascular
    SystemFilter --> Hepatic
    SystemFilter --> Preventive
    SystemFilter --> Pharmacy

    Renal --> CrossSystem
    Metabolic --> CrossSystem
    Cardiovascular --> CrossSystem
    Hepatic --> CrossSystem
    Preventive --> CrossSystem
    Pharmacy --> CrossSystem

    CrossSystem --> EvidenceLayer
    EvidenceLayer --> Synthesis
    Synthesis --> Output

    style PatientData fill:#e1f5ff,stroke:#0288d1,stroke-width:2px
    style CrossSystem fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    style Output fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    style Renal fill:#ffebee,stroke:#c62828
    style Metabolic fill:#fff3e0,stroke:#ef6c00
    style Cardiovascular fill:#fce4ec,stroke:#ad1457
    style Hepatic fill:#efebe9,stroke:#5d4037
    style Preventive fill:#e8f5e9,stroke:#2e7d32
    style Pharmacy fill:#f3e5f5,stroke:#6a1b9a
```

**Why multi-system reasoning matters:**

- **Real patients have multimorbidity:** Maria Santos has 5 active
  conditions across 4 organ systems. Single-axis reasoning would miss
  the highest-leverage interventions.
- **Cross-system effects are common:** NSAID + CKD + HTN is one of the
  most clinically dangerous combinations, and is invisible to any system
  that reasons one organ at a time.
- **Single intervention, multi-system benefit:** SGLT2 inhibitors
  improve renal AND cardiovascular AND metabolic outcomes
  simultaneously. Phantom surfaces this multi-system leverage explicitly.
- **Specialty silos break down:** Cardiologists see hearts. Nephrologists
  see kidneys. Phantom sees patients.

---

## Interoperability Significance

The architecture above is built entirely on open standards:

| Standard | Role in Phantom | Why it matters |
|----------|----------------|----------------|
| **MCP** (Model Context Protocol) | Tool exposure to agents | Any MCP-compatible agent can equip Phantom |
| **A2A** (Agent-to-Agent) | Inter-agent composition | Phantom can be invoked by other agents in chains |
| **SHARP-on-MCP** | Healthcare context propagation | Patient/clinician identity flows securely through MCP |
| **FHIR R4** (HL7) | Patient data substrate | Vendor-neutral, used by every modern EHR |
| **SMART on FHIR** | OAuth + scoped access | Industry-standard healthcare auth |

**The architectural payoff:** Phantom is not a Po-specific tool. It is a
standards-native clinical reasoning service that can plug into any
agent platform that supports MCP, with any FHIR-compatible EHR backend,
authenticated by any SMART-on-FHIR identity provider.

This is the difference between building a hackathon demo and building
infrastructure.

---

## Diagram Maintenance Notes

- All diagrams use Mermaid syntax — render automatically on GitHub
- To preview locally, install the Mermaid VS Code extension
- Update diagrams when:
  - New MCP tools are added
  - SHARP integration evolves
  - Evidence base structure changes significantly
- Keep diagrams in sync with `docs/architecture.md` prose

---

*Phantom — Architecture Diagrams — `docs/architecture_diagrams.md`*
*Maintained alongside the system implementation.*