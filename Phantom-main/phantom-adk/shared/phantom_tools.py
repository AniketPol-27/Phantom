from google.adk.tools import ToolContext
from shared.mcp_client import phantom_mcp_client

from typing import Dict, Any, List


# ============================================================
# Helpers
# ============================================================

def _build_fhir_headers(
    tool_context: ToolContext,
) -> dict:
    """
    Build FHIR headers from ADK state.
    """

    try:

        state = tool_context.state

        headers = {
            "x-fhir-server-url":
                state.get("fhir_url", ""),

            "x-patient-id":
                state.get("patient_id", ""),
        }

        token = state.get("fhir_token")

        if token:

            headers[
                "x-fhir-access-token"
            ] = token

        return headers

    except Exception:

        return {}


def _has_fhir_context(headers: dict) -> bool:

    return bool(
        headers.get("x-fhir-server-url")
    )


# ============================================================
# build_patient_model_tool
# ============================================================

async def build_patient_model_tool(
    tool_context: ToolContext,
) -> str:

    headers = _build_fhir_headers(
        tool_context
    )

    # --------------------------------------------------------
    # NO FHIR CONTEXT
    # --------------------------------------------------------

    if not _has_fhir_context(headers):

        return (
            "FHIR context unavailable. "
            "No patient-scoped clinical data "
            "was provided to the agent."
        )

    # --------------------------------------------------------
    # MCP CALL
    # --------------------------------------------------------

    try:

        result = await phantom_mcp_client.call_tool(
            "build_patient_model",
            {},
            headers=headers,
        )

        if (
            hasattr(result, "content")
            and result.content
        ):

            for item in result.content:

                if hasattr(item, "text"):

                    return item.text[:1800]

        return str(result)

    except Exception as e:

        return (
            f"Unable to build patient model: {str(e)}"
        )


# ============================================================
# simulate_inaction_tool
# ============================================================

async def simulate_inaction_tool(
    tool_context: ToolContext,
    patient_model: Dict[str, Any],
    time_horizon_months: int = 12,
) -> str:

    headers = _build_fhir_headers(
        tool_context
    )

    if not _has_fhir_context(headers):

        return (
            "Simulation unavailable because "
            "FHIR patient context was not provided."
        )

    try:

        result = await phantom_mcp_client.call_tool(
            "simulate_scenario",
            {
                "patient_model": patient_model,
                "scenario_type": "inaction",
                "time_horizon_months":
                    time_horizon_months,
            },
            headers=headers,
        )

        if (
            hasattr(result, "content")
            and result.content
        ):

            for item in result.content:

                if hasattr(item, "text"):

                    return item.text

        return str(result)

    except Exception as e:

        return (
            f"Simulation failed: {str(e)}"
        )


# ============================================================
# compare_interventions_tool
# ============================================================

async def compare_interventions_tool(
    tool_context: ToolContext,
    patient_model: Dict[str, Any],
    clinical_question: str,
    interventions: List[str],
) -> str:

    headers = _build_fhir_headers(
        tool_context
    )

    if not _has_fhir_context(headers):

        return (
            "Intervention comparison unavailable "
            "because patient FHIR context "
            "was not provided."
        )

    try:

        result = await phantom_mcp_client.call_tool(
            "compare_interventions",
            {
                "patient_model": patient_model,
                "clinical_question":
                    clinical_question,

                "interventions":
                    interventions,
            },
            headers=headers,
        )

        if (
            hasattr(result, "content")
            and result.content
        ):

            for item in result.content:

                if hasattr(item, "text"):

                    return item.text

        return str(result)

    except Exception as e:

        return (
            f"Intervention comparison failed: "
            f"{str(e)}"
        )