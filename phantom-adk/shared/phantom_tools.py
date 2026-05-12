from google.adk.tools import ToolContext
from shared.mcp_client import phantom_mcp_client
from typing import Dict, Any, List

def _build_fhir_headers(tool_context: ToolContext) -> dict:
    """Build FHIR headers from ADK tool context state."""
    
    # Try to get state from tool_context
    try:
        state = tool_context.state
        headers = {
            "x-fhir-server-url": state.get("fhir_url", ""),
            "x-patient-id": state.get("patient_id", ""),
        }
        token = state.get("fhir_token")
        if token:
            headers["x-fhir-access-token"] = token
        return headers
    except Exception:
        # No FHIR context available — return empty headers
        # MCP server will handle the missing context gracefully
        return {}


async def build_patient_model_tool(
    tool_context: ToolContext,
) -> str:
    """Build a computational patient model using Phantom MCP."""
    
    headers = _build_fhir_headers(tool_context)
    
    result = await phantom_mcp_client.call_tool(
        "build_patient_model",
        {},
        headers=headers,
    )
    print("TOOL RESULT:")
    print(result)
    # Extract text content from MCP result
    if hasattr(result, 'content') and result.content:
        for item in result.content:
            if hasattr(item, 'text'):
                return item.text[:4000]
    print("TEXT:")
    print(item.text)            
    print(type(item.text))
    print(len(item.text))
    return str(result)


async def simulate_inaction_tool(
    tool_context: ToolContext,
    patient_model: Dict[str, Any],
    time_horizon_months: int = 12,
) -> str:
    """Simulate inaction scenario using Phantom MCP."""
    
    headers = _build_fhir_headers(tool_context)
    
    result = await phantom_mcp_client.call_tool(
        "simulate_scenario",
        {
            "patient_model": patient_model,
            "scenario_type": "inaction",
            "time_horizon_months": time_horizon_months,
        },
        headers=headers,
    )
    
    if hasattr(result, 'content') and result.content:
        for item in result.content:
            if hasattr(item, 'text'):
                return item.text
    
    return str(result)


async def compare_interventions_tool(
    tool_context: ToolContext,
    patient_model: Dict[str, Any],
    clinical_question: str,
    interventions: List[str],
) -> str:
    """Compare clinical interventions using Phantom MCP."""
    
    headers = _build_fhir_headers(tool_context)
    
    result = await phantom_mcp_client.call_tool(
        "compare_interventions",
        {
            "patient_model": patient_model,
            "clinical_question": clinical_question,
            "interventions": interventions,
        },
        headers=headers,
    )
    
    if hasattr(result, 'content') and result.content:
        for item in result.content:
            if hasattr(item, 'text'):
                return item.text
    
    return str(result)