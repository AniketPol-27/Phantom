from shared.mcp_client import phantom_mcp_client


def _build_fhir_headers(callback_context):

    state = callback_context.state

    headers = {
        "x-fhir-server-url": state.get("fhir_url", ""),
        "x-patient-id": state.get("patient_id", ""),
    }

    token = state.get("fhir_token")

    if token:
        headers["x-fhir-access-token"] = token

    return headers


async def build_patient_model_tool(
    callback_context,
):

    headers = _build_fhir_headers(callback_context)

    return await phantom_mcp_client.call_tool(
        "build_patient_model",
        {},
        headers=headers,
    )


async def simulate_inaction_tool(
    callback_context,
    patient_model: dict,
    time_horizon_months: int = 12,
):

    headers = _build_fhir_headers(callback_context)

    return await phantom_mcp_client.call_tool(
        "simulate_scenario",
        {
            "patient_model": patient_model,
            "scenario_type": "inaction",
            "time_horizon_months": time_horizon_months,
        },
        headers=headers,
    )


async def compare_interventions_tool(
    callback_context,
    patient_model: dict,
    clinical_question: str,
    interventions: list[dict],
):

    headers = _build_fhir_headers(callback_context)

    return await phantom_mcp_client.call_tool(
        "compare_interventions",
        {
            "patient_model": patient_model,
            "clinical_question": clinical_question,
            "interventions": interventions,
        },
        headers=headers,
    )
