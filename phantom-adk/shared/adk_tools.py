from google.adk.tools import FunctionTool

from shared.phantom_tools import (
    build_patient_model_tool,
    simulate_inaction_tool,
    compare_interventions_tool,
)


build_patient_model_adk_tool = FunctionTool(
    func=build_patient_model_tool,
)

simulate_inaction_adk_tool = FunctionTool(
    func=simulate_inaction_tool,
)

compare_interventions_adk_tool = FunctionTool(
    func=compare_interventions_tool,
)
