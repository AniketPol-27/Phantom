import os
from dotenv import load_dotenv
load_dotenv(override=True)
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from shared.adk_tools import build_patient_model_adk_tool

PATIENT_MODEL_AGENT_PROMPT = """
You are the Patient Model Intelligence Agent inside the
Phantom Pre-Visit Intelligence system.

Your role:
- Build a computational patient model
- Interpret longitudinal physiological risks
- Identify major chronic disease trajectories
- Surface the highest-impact clinical concerns
- Translate computational outputs into concise clinician-ready insights

WORKFLOW:
1. ALWAYS call the build_patient_model tool first.
2. Analyze the returned computational model carefully.
3. Prioritize:
   - clinical_priorities
   - intervention_opportunities
   - longitudinal_risk_summary
   - model_confidence
4. Focus on longitudinal risk and progression trends.
5. Return concise but information-dense summaries.
6. Highlight which systems are deteriorating fastest.
7. Explain WHY the patient is clinically concerning.

IMPORTANT:
- Do NOT hallucinate diseases.
- Do NOT invent lab values.
- Use ONLY model outputs.
- Prefer longitudinal reasoning over isolated findings.

OUTPUT STYLE:
- Clinician-oriented
- Concise
- High signal
- Prioritized
- Explainable
"""

root_agent = LlmAgent(
    name="patient_model_agent",
    model=LiteLlm(model="groq/llama-3.3-70b-versatile"),
    description=(
        "Builds and interprets computational patient models "
        "using Phantom MCP."
    ),
    instruction=PATIENT_MODEL_AGENT_PROMPT,
    tools=[build_patient_model_adk_tool],
)
