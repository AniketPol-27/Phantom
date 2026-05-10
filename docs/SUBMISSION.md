# Phantom — Clinical Simulation MCP Server

## Inspiration

Every day, clinicians face a version of the same impossible problem: they must make high-stakes decisions about medications, diagnoses, and treatment plans — in real time, under time pressure, with incomplete information — and there is no way to press "undo." A nephrologist adjusting a diuretic dose cannot simulate what happens to potassium levels before writing the order. A primary care physician adding an SGLT2 inhibitor cannot run a forward projection of eGFR trajectory before deciding. The "what-if" question — *what happens to this specific patient if I do this?* — has never had a computational answer at the point of care.

The emergence of the Model Context Protocol (MCP) and the SHARP-on-MCP healthcare context standard changes this. For the first time, AI agents operating inside clinical workflows have a standardized way to call structured, evidence-grounded tools — and receive back not just text, but structured clinical models that can be composed, simulated, and compared. Phantom was built to be exactly that: a clinical simulation layer that sits between the clinician's question and the EHR's raw data.

We chose the metaphor of a *patient digital twin* deliberately. A digital twin is not a summary — it is a computational model that can be run forward in time, stressed with interventions, and queried for projected outcomes. Phantom builds that twin from FHIR R4 patient data, runs it through validated clinical algorithms, and makes it available to any AI agent on the Prompt Opinion platform.

## What It Does

Phantom exposes three MCP tools that together form a complete clinical reasoning pipeline. The first tool, `build_patient_model`, ingests a patient's FHIR data — conditions, medications, labs, vitals, observations — and constructs a multi-system computational model. This model is not a text summary; it is a structured object containing eGFR trajectory with linear regression and 95% prediction intervals, ASCVD 10-year risk calculated via the ACC/AHA Pooled Cohort Equations, FIB-4 hepatic fibrosis index, active care gaps evaluated against 40+ guideline rules, and diagnostic gaps detected from longitudinal lab patterns.

The second tool, `simulate_scenario`, takes that patient model and runs a forward simulation. A clinician (or agent) can ask: *what happens if we add empagliflozin?* or *what is the projected trajectory if we do nothing for 12 months?* The simulation engine applies drug-specific effect modifiers drawn from a 21-drug knowledge base, adjusts eGFR slope based on trial-derived data (e.g., DAPA-CKD, EMPA-KIDNEY), and projects outcomes across renal, cardiovascular, metabolic, and hepatic systems simultaneously.

The third tool, `compare_interventions`, runs multiple simulations head-to-head and returns a ranked comparison table. This is designed for shared decision-making moments: the clinician wants to know whether empagliflozin or semaglutide is the better choice for *this specific patient*, given their eGFR of 49, rising HbA1c, and obesity. The comparison is personalized — it uses the patient's actual lab values, not population averages.

Clinicians experience Phantom through the Pre-Visit Intelligence Agent on the Prompt Opinion platform. The agent's workflow is simple: a clinician types "Prep me for my next patient" or "What should I focus on today?" The agent calls `build_patient_model` to construct the patient twin, calls `simulate_scenario` twice (once for inaction, once for the most urgent intervention), calls `compare_interventions` for the top decision point, and synthesizes everything into a structured Pre-Visit Briefing — a one-page clinical document with trajectory alerts, ranked visit priorities, a decision comparison table, diagnostic gaps, and a suggested visit agenda with time blocks.

## How We Built It

**Tech Stack:**
- Python 3.11 + FastAPI + FastMCP (MCP server framework)
- Streamable HTTP transport (MCP spec compliant)
- SHARP-on-MCP context propagation (X-FHIR-Server-URL, SMART on FHIR JWT)
- FHIR R4 client via httpx with pagination support
- Validated clinical algorithms: CKD-EPI 2021 (PMID 34554658), ACC/AHA Pooled Cohort Equations (PMID 24239921), FIB-4 (PMID 16729309), qSOFA (PMID 26903335)
- Clinical trial evidence database: 10 major trials encoded with structured outcome data (DAPA-CKD, CREDENCE, EMPA-REG OUTCOME, EMPA-KIDNEY, SUSTAIN-6, LEADER, REWIND, SPRINT, SURPASS-4, UKPDS-33)
- Drug knowledge base: 21 drugs across 11 therapeutic classes with multi-system effect profiles
- numpy + scipy for trajectory regression and statistical projections

**Architecture:**

The system follows a clean layered architecture. The MCP server mounts on FastAPI using the streamable HTTP transport pattern. When the Po platform invokes a tool, SHARP context (FHIR server URL, patient ID via SMART on FHIR JWT) arrives via HTTP headers and is extracted before tool execution begins. The FHIR client fetches patient data using that context, the patient model builder assembles the computational model, the simulation engine applies evidence-based modifiers, and the comparison engine ranks interventions. All clinical evidence lives in a pure-Python evidence base with no external database dependency — making the server deployable as a single container.

The agent configuration lives separately: a 257-line system prompt defines the agent's identity, 6-step workflow decision tree, prioritization rules, output formatting requirements, and guardrails. A 349-line briefing template with 10 required sections and clinically accurate examples ensures consistent, structured output.

## Challenges We Ran Into

**Discovering how SHARP context actually arrives.** The SHARP-on-MCP spec describes context propagation, but implementing it required understanding that patient context arrives via HTTP headers (`X-FHIR-Server-URL`, `X-FHIR-Context`), not as tool arguments. This meant patching FastMCP's capabilities declaration to advertise the Po FHIR context extension, and writing custom middleware to extract and validate the JWT before any tool execution.

**Making clinical simulations evidence-grounded.** The core risk in healthcare AI is hallucination — an LLM confidently generating a drug recommendation with no grounding in trial evidence. We solved this by encoding the actual trial data (eGFR slopes, hazard ratios, NNTs) as structured Python objects, so every simulation output cites a specific trial and PMID. The simulation engine never asks an LLM what empagliflozin does to eGFR — it looks it up in the structured drug knowledge base and applies the DAPA-CKD/EMPA-KIDNEY derived slope modifier.

**Designing the patient model schema.** The patient model needs to be rich enough to power simulations but compact enough to fit in an agent's context window. We went through several iterations before settling on a multi-system state object with explicit trajectory objects (slope, direction, projections at 6/12/24 months) rather than raw lab series.

**Handling FHIR observation pagination.** Real FHIR servers paginate observation bundles. A patient with 2 years of quarterly labs easily exceeds a single page. The FHIR client needed robust pagination handling with timeout and retry logic.

**Balancing clinical accuracy with hackathon scope.** Clinical medicine is enormously complex. We had to make principled decisions about scope — 21 drugs instead of 200, 10 trials instead of 100, 40 care gap rules instead of 400 — while ensuring that every encoded piece of data is clinically accurate and citable.

## Accomplishments We're Proud Of

- **Validated clinical risk equations** — CKD-EPI 2021 (race-free), ACC/AHA Pooled Cohort Equations with all 4 sex/race coefficient sets, FIB-4, qSOFA, KDIGO 2024 risk matrix — all with PMID citations and tested against known clinical inputs
- **10 major clinical trials encoded** with structured outcome data including eGFR slope comparisons, hazard ratios, NNTs, subgroup analyses, and safety profiles
- **21 drugs across 11 therapeutic classes** with multi-system effect profiles covering renal, cardiovascular, metabolic, hepatic, and weight effects — plus contraindications, interactions, dosing adjustments, and monitoring requirements
- **Diagnostic gap detection from longitudinal patterns** — the system detects CKD-associated anemia from trending hemoglobin, MASLD from persistently elevated ALT, triple whammy nephrotoxicity from drug combinations, and 8 other diagnostic gaps
- **Comorbidity cascade modeling** — T2DM + CKD triggers bidirectional acceleration cascades that modify progression projections across both systems simultaneously
- **Full standards compliance** — MCP, A2A, SHARP-on-MCP, FHIR R4, LOINC, SNOMED CT, ICD-10, RxNorm, CVX, UCUM
- **Composable architecture** — any agent on the Po platform can equip Phantom, multiplying the value of the evidence base across every clinical use case

## What We Learned

MCP is more than tool calling — it is the connective tissue for AI agents operating in structured domains. Before MCP, every healthcare AI system had to solve the same integration problems from scratch: how does the agent get patient context? How does it call clinical logic? How does it return structured results? MCP standardizes all of this, and SHARP extends it specifically for healthcare. Building Phantom taught us that the protocol layer is what makes clinical AI composable and trustworthy at scale.

Healthcare AI must be evidence-grounded to be clinically useful. An LLM that generates a medication recommendation without citing a trial is not clinical decision support — it is a liability. The architecture of Phantom — where every simulation output traces back to a specific trial and PMID — is the right model for healthcare AI. The LLM handles reasoning and communication; the evidence base handles facts.

The SHARP specification is well-designed. The decision to propagate patient context via HTTP headers (rather than tool arguments) keeps tool schemas clean and context-agnostic. The JWT-based patient ID extraction integrates naturally with SMART on FHIR, the existing healthcare auth standard. Building against SHARP felt like building with the grain of the existing healthcare ecosystem.

Composable tools have a multiplier effect. A single Phantom MCP server, once deployed, is accessible to every agent on the Po platform. A cardiology agent, a nephrology agent, a pharmacy agent, and a care coordination agent can all equip Phantom — each getting the full benefit of the evidence base without rebuilding it. This is the network effect of standards-based composability.

## What's Next for Phantom

**Expanded drug knowledge base** — scaling from 21 to 100+ drugs, with particular focus on oncology supportive care, psychiatry, and rheumatology where drug interactions are most complex.

**Specialty-specific tool packs** — a Cardiology Pack (HFrEF management, arrhythmia risk, anticoagulation decisions), a Nephrology Pack (dialysis timing, transplant candidacy, mineral metabolism), and an Oncology Pack (chemotherapy toxicity prediction, supportive care gaps).

**Real-time trajectory alert system** — proactive notifications when a patient's monitored values cross a threshold defined by their care plan, triggering an automatic briefing without waiting for a scheduled visit.

**Population-level analytics** — extending the patient model to a panel model, enabling care managers to identify the highest-risk patients across a panel using the same validated algorithms.

**EHR integration beyond FHIR** — direct Epic/Cerner integrations for health systems that have not yet fully implemented FHIR R4, using vendor-specific APIs where needed.

## Built With

- Python 3.11
- FastAPI
- FastMCP
- Model Context Protocol (MCP)
- Agent-to-Agent Protocol (A2A)
- SHARP-on-MCP
- FHIR R4 (HL7)
- Prompt Opinion Platform
- HAPI FHIR
- Pydantic
- httpx
- structlog
- numpy
- scipy
- pytest
- uv