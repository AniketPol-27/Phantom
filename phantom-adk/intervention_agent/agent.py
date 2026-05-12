import os
from dotenv import load_dotenv
load_dotenv(override=True)
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from shared.adk_tools import compare_interventions_adk_tool

INTERVENTION_AGENT_PROMPT = """
You are the Intervention Intelligence Agent inside Phantom.

Your role:
- Compare clinical interventions
- Rank treatment options by longitudinal impact
- Evaluate trade-offs between therapy options
- Identify the highest-value clinical actions

WORKFLOW:
1. Use comparison tool outputs carefully.
2. Focus on:
   - longitudinal benefit
   - risk/benefit ratio
   - urgency of intervention
   - patient-specific factors
3. Rank interventions by clinical impact.
4. Explain WHY certain interventions are prioritized.

IMPORTANT:
- Stay evidence-based.
- Do NOT invent clinical data.
- Focus on actionable recommendations.

OUTPUT STYLE:
- Ranked and prioritized
- Evidence-referenced
- Clinician-oriented
- Actionable
"""

root_agent = LlmAgent(
    name="intervention_agent",
    model=LiteLlm(model="gemini/gemini-2.5-flash"),
    description=(
        "Compares and ranks clinical interventions "
        "using Phantom MCP."
    ),
    instruction=INTERVENTION_AGENT_PROMPT,
    tools=[compare_interventions_adk_tool],
)
