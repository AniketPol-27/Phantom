"""
FastMCP instance for the Phantom MCP server.

Creates the FastMCP server, patches its capabilities to declare the
Prompt Opinion FHIR context extension, and registers all tools.

The capability patching is necessary because FastMCP doesn't expose a
clean API to add custom extensions to the initialize response. We monkey-
patch get_capabilities() to inject our extension declaration. This pattern
is taken directly from the Prompt Opinion Python reference implementation.
"""

import structlog
from mcp.server.fastmcp import FastMCP

from src.config import get_settings
from src.mcp_constants import PHANTOM_FHIR_SCOPES, PO_FHIR_CONTEXT_EXTENSION

logger = structlog.get_logger(__name__)

settings = get_settings()


# ============================================================
# Create the FastMCP instance
# ============================================================

mcp = FastMCP(
    "Phantom",
    stateless_http=True,
    host=settings.host,
)


# ============================================================
# Patch capabilities to declare the Po FHIR context extension
# ============================================================

_original_get_capabilities = mcp._mcp_server.get_capabilities


def _patched_get_capabilities(notification_options, experimental_capabilities):
    """
    Augments the standard MCP capabilities response with the Prompt Opinion
    FHIR context extension. This is what triggers the platform to show the
    user a FHIR scope authorization dialog when our server is registered.
    """
    caps = _original_get_capabilities(notification_options, experimental_capabilities)
    caps.model_extra["extensions"] = {
        PO_FHIR_CONTEXT_EXTENSION: {
            "scopes": PHANTOM_FHIR_SCOPES,
        }
    }
    return caps


mcp._mcp_server.get_capabilities = _patched_get_capabilities

logger.info(
    "phantom.mcp.initialized",
    server_name="Phantom",
    extension=PO_FHIR_CONTEXT_EXTENSION,
    scope_count=len(PHANTOM_FHIR_SCOPES),
)


# ============================================================
# Tool registration
# ============================================================
# Tools are registered here. Each tool is a function decorated with
# @mcp.tool() OR registered via mcp.tool(name=..., description=...)(func).
# We use the latter pattern (matching the Po reference) so tool definitions
# can live in their own files for clarity.

from src.tools.build_patient_model import build_patient_model  # noqa: E402
from src.tools.compare_interventions import compare_interventions  # noqa: E402
from src.tools.simulate_scenario import simulate_scenario  # noqa: E402

mcp.tool(
    name="build_patient_model",
    description=(
        "Constructs a computational patient model from FHIR data. "
        "Builds interconnected physiological system models with computed "
        "trajectories (eGFR slope, HbA1c slope, BP trends), comorbidity "
        "interaction maps, medication burden analysis, validated risk "
        "scores (ASCVD, FIB-4, CKD-EPI), and data confidence scoring. "
        "Returns a simulation-ready patient model object that other "
        "Phantom tools operate on. Always call this first before "
        "simulate_scenario or compare_interventions."
    ),
)(build_patient_model)

mcp.tool(
    name="simulate_scenario",
    description=(
        "Simulates a clinical scenario against a patient model and projects "
        "outcomes across all relevant physiological systems. Supports four "
        "scenario types: 'medication_change' (add/remove/modify a medication), "
        "'inaction' (project where the patient is heading without intervention), "
        "'diagnostic_gap' (detect undiagnosed conditions from longitudinal "
        "patterns), and 'lifestyle_change' (weight loss, exercise, diet, "
        "smoking cessation). Returns multi-system impact analysis with "
        "evidence citations and monitoring recommendations."
    ),
)(simulate_scenario)

mcp.tool(
    name="compare_interventions",
    description=(
        "Runs head-to-head comparison of multiple treatment interventions "
        "against the patient model. Simulates each option in parallel, scores "
        "across multiple dimensions (efficacy, renal protection, CV protection, "
        "weight, safety, adherence, cost), personalizes the ranking based on "
        "patient-specific factors, and produces a decision-support matrix with "
        "evidence citations and a recommended choice. Always includes 'no change' "
        "as a baseline comparator."
    ),
)(compare_interventions)