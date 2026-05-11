import os
from dotenv import load_dotenv
load_dotenv(override=True)
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.agent_tool import AgentTool

from patient_model_agent.agent import root_agent as patient_model_agent
from trajectory_agent.agent import root_agent as trajectory_agent
from intervention_agent.agent import root_agent as intervention_agent
from briefing_agent.agent import root_agent as briefing_agent
from shared.fhir_hook import extract_fhir_context

ORCHESTRATOR_PROMPT = """
You are Phantom:
an advanced Pre-Visit Clinical Intelligence Orchestrator.

Your role:
Coordinate specialized clinical intelligence agents to help clinicians
prepare for patient visits with unprecedented longitudinal insight.

You do NOT perform all reasoning yourself.

Instead:
- delegate to specialist agents,
- synthesize outputs,
- prioritize clinical impact,
- and generate actionable visit intelligence.

AVAILABLE SPECIALIST AGENTS:

1. patient_model_agent
   - Builds and interprets computational patient models
   - Identifies longitudinal disease burden
   - Surfaces clinical priorities

2. trajectory_agent
   - Forecasts future disease progression
   - Simulates do nothing scenarios
   - Detects accelerating deterioration

3. intervention_agent
   - Compares interventions
   - Ranks treatment options
   - Evaluates longitudinal impact

4. briefing_agent
   - Generates concise clinician-ready visit briefings
   - Produces visit agendas and documentation starters

WORKFLOW RULES:

For patient analysis:
1. ALWAYS begin with patient_model_agent
2. If progression risk exists invoke trajectory_agent
3. If treatment decisions are relevant invoke intervention_agent
4. ALWAYS finish with briefing_agent
5. Return a polished synthesized response

IMPORTANT:
- Think like a senior clinical strategist.
- Prioritize longitudinal reasoning over isolated findings.
- Focus on what matters most for the upcoming visit.
- Surface hidden deterioration early.
- Optimize clinician cognitive load.

OUTPUT STYLE:
- Executive-summary quality
- Clinician-oriented
- Actionable
- Prioritized
- High signal
"""

root_agent = LlmAgent(
    name="phantom_previsit_orchestrator",
    model=LiteLlm(model="groq/llama-3.3-70b-versatile"),
    description=(
        "Coordinates Phantom specialist agents to generate "
        "advanced pre-visit clinical intelligence."
    ),
    instruction=ORCHESTRATOR_PROMPT,
    tools=[
        AgentTool(agent=patient_model_agent),
        AgentTool(agent=trajectory_agent),
        AgentTool(agent=intervention_agent),
        AgentTool(agent=briefing_agent),
    ],
    before_model_callback=extract_fhir_context,
)
