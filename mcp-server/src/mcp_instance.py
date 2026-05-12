"""
Phantom FastMCP Runtime

Initializes the Phantom clinical intelligence runtime,
declares Prompt Opinion FHIR context capabilities,
and registers all computational clinical simulation tools.

Phantom is designed as:
- a longitudinal computational patient modeling engine,
- a disease trajectory forecasting system,
- and a simulation-first clinical intelligence platform.

The MCP runtime exposes:
1. build_patient_model
2. simulate_scenario
3. compare_interventions

These tools operate together as a unified longitudinal
clinical reasoning pipeline.
"""

import structlog
from mcp.server.fastmcp import FastMCP

from src.config import get_settings
from src.mcp_constants import (
    PHANTOM_FHIR_SCOPES,
    PO_FHIR_CONTEXT_EXTENSION,
)

logger = structlog.get_logger(__name__)

settings = get_settings()

# ============================================================
# FastMCP Runtime
# ============================================================

mcp = FastMCP(

    "Phantom Clinical Intelligence Platform",

    stateless_http=True,

    host=settings.host,
)

# ============================================================
# Prompt Opinion FHIR Context Extension
# ============================================================

# FastMCP currently does not expose a public API
# for custom MCP capability extensions.
#
# We patch get_capabilities() directly to declare:
#
# ai.promptopinion/fhir-context
#
# This enables:
# - SMART/SHARP-on-FHIR authorization
# - patient-scoped access tokens
# - secure longitudinal FHIR retrieval
# - automatic scope consent dialogs in Prompt Opinion

_original_get_capabilities = (
    mcp._mcp_server.get_capabilities
)

def _patched_get_capabilities(
    notification_options,
    experimental_capabilities,
):
    """
    Inject Prompt Opinion FHIR capability extension.
    """

    caps = _original_get_capabilities(
        notification_options,
        experimental_capabilities,
    )

    caps.model_extra["extensions"] = {

        PO_FHIR_CONTEXT_EXTENSION: {

            "scopes": PHANTOM_FHIR_SCOPES,
        }
    }

    return caps

mcp._mcp_server.get_capabilities = (
    _patched_get_capabilities
)

logger.info(

    "phantom.mcp.initialized",

    runtime="clinical_intelligence_platform",

    extension=PO_FHIR_CONTEXT_EXTENSION,

    scope_count=len(PHANTOM_FHIR_SCOPES),
)

# ============================================================
# Tool Imports
# ============================================================

from src.tools.build_patient_model import (  # noqa: E402
    build_patient_model,
)

from src.tools.simulate_scenario import (  # noqa: E402
    simulate_scenario,
)

from src.tools.compare_interventions import (  # noqa: E402
    compare_interventions,
)

# ============================================================
# build_patient_model
# ============================================================

mcp.tool(

    name="build_patient_model",

    description=(
        "Builds a simulation-ready computational patient model "
        "from longitudinal FHIR records.\n\n"

        "The engine synthesizes multi-system physiological "
        "state across renal, metabolic, cardiovascular, and "
        "hepatic domains using validated clinical equations, "
        "trajectory analysis, risk stratification, medication "
        "burden analysis, and comorbidity interaction mapping.\n\n"

        "Outputs include:\n"
        "- longitudinal disease trajectories\n"
        "- CKD progression modeling\n"
        "- ASCVD risk synthesis\n"
        "- metabolic control assessment\n"
        "- hidden deterioration risks\n"
        "- intervention opportunity detection\n"
        "- confidence scoring\n"
        "- cross-system cascade analysis\n"
        "- simulation-ready digital patient representation\n\n"

        "This tool should ALWAYS be invoked before "
        "simulate_scenario or compare_interventions."
    ),
)(
    build_patient_model
)

# ============================================================
# simulate_scenario
# ============================================================

mcp.tool(

    name="simulate_scenario",

    description=(
        "Runs longitudinal disease progression simulations "
        "against a computational patient model.\n\n"

        "Supports:\n"
        "- inaction forecasting\n"
        "- medication intervention simulation\n"
        "- lifestyle modification simulation\n"
        "- future risk projection\n"
        "- trajectory acceleration analysis\n\n"

        "The simulation engine models projected future "
        "multi-system physiological behavior over time horizons "
        "ranging from months to years.\n\n"

        "Outputs include:\n"
        "- projected disease progression\n"
        "- deterioration risk trajectories\n"
        "- intervention impact analysis\n"
        "- future cardiovascular burden\n"
        "- renal progression forecasts\n"
        "- metabolic stability projections\n"
        "- longitudinal monitoring recommendations\n"
        "- clinically actionable trajectory alerts\n\n"

        "Designed for clinician-oriented pre-visit "
        "intelligence and longitudinal decision support."
    ),
)(
    simulate_scenario
)

# ============================================================
# compare_interventions
# ============================================================

mcp.tool(

    name="compare_interventions",

    description=(
        "Performs comparative longitudinal analysis of "
        "multiple treatment strategies using the Phantom "
        "computational patient model.\n\n"

        "The engine dynamically evaluates interventions "
        "across multiple competing dimensions:\n"
        "- renal protection\n"
        "- cardiovascular benefit\n"
        "- metabolic improvement\n"
        "- safety profile\n"
        "- adherence burden\n"
        "- longitudinal stability impact\n\n"

        "Interventions are ranked using patient-specific "
        "risk weighting and multi-system trajectory modeling.\n\n"

        "Outputs include:\n"
        "- intervention ranking\n"
        "- comparative tradeoff analysis\n"
        "- projected longitudinal benefit\n"
        "- strategy optimization insights\n"
        "- evidence-grounded rationale\n"
        "- clinician-oriented treatment recommendations\n\n"

        "Designed for advanced clinical decision support "
        "and future-risk-aware therapeutic planning."
    ),
)(
    compare_interventions
)

# ============================================================
# Runtime Ready
# ============================================================

logger.info(

    "phantom.mcp.tools_registered",

    tool_count=3,

    tools=[

        "build_patient_model",

        "simulate_scenario",

        "compare_interventions",
    ],
)