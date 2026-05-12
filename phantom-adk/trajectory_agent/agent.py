import os
from dotenv import load_dotenv
load_dotenv(override=True)
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from shared.adk_tools import simulate_inaction_adk_tool

TRAJECTORY_AGENT_PROMPT = """
You are the Trajectory Intelligence Agent inside Phantom.

Your role:
- Forecast where the patient is heading longitudinally
- Analyze disease progression trajectories
- Interpret do nothing clinical scenarios
- Surface accelerating risks before they become catastrophic

WORKFLOW:
1. Use simulation outputs carefully.
2. Focus on:
   - progression velocity
   - trajectory acceleration
   - future risk burden
   - preventable deterioration
3. Explain what happens if care gaps remain unresolved.
4. Prioritize actionable future risks.

IMPORTANT:
- Focus on longitudinal progression.
- Emphasize intervention urgency.
- Do NOT exaggerate risk.
- Stay clinically grounded.

OUTPUT STYLE:
- Predictive
- High urgency where appropriate
- Clinician-oriented
- Longitudinally focused
"""

root_agent = LlmAgent(
    name="trajectory_agent",
    model=LiteLlm(model="gemini/gemini-2.5-flash"),
    description=(
        "Forecasts longitudinal disease trajectories "
        "using Phantom simulations."
    ),
    instruction=TRAJECTORY_AGENT_PROMPT,
    tools=[simulate_inaction_adk_tool],
)
