"""
Phantom MCP Server — Clinical Intelligence Runtime

Phantom is an advanced computational clinical intelligence platform
that transforms longitudinal FHIR patient records into simulation-ready
digital patient models.

Core capabilities:
- Computational patient modeling
- Longitudinal disease trajectory analysis
- Future risk simulation
- Intervention comparison and optimization
- Cross-system physiological reasoning
- Clinician-oriented pre-visit intelligence

The server exposes a FastMCP interface compatible with:
- Prompt Opinion
- MCP-compatible orchestration systems
- Clinical AI copilots
- Longitudinal simulation workflows

Architecture:
- FastMCP over Streamable HTTP
- FastAPI application runtime
- SMART/SHARP-on-FHIR context support
- Evidence-grounded simulation engines
- Multi-system physiological modeling
"""

import logging
import sys
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.mcp_instance import mcp

# ============================================================
# Logging Configuration
# ============================================================

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(message)s",
    stream=sys.stdout,
)

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),

        structlog.dev.ConsoleRenderer()
        if settings.dev_mode
        else structlog.processors.JSONRenderer(),
    ],

    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(logging, settings.log_level.upper())
    ),

    context_class=dict,

    logger_factory=structlog.PrintLoggerFactory(),

    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# ============================================================
# FastAPI Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Coordinates the FastMCP session lifecycle.

    The MCP session manager powers:
    - Streamable HTTP transport
    - MCP tool execution
    - SHARP context propagation
    - Clinical simulation runtime state
    """

    logger.info(
        "phantom.runtime.starting",
        version="1.0",
        dev_mode=settings.dev_mode,
    )

    async with mcp.session_manager.run():

        logger.info(
            "phantom.runtime.ready",
            transport="streamable_http",
            clinical_engine="active",
        )

        yield

    logger.info(
        "phantom.runtime.stopped",
    )

# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(

    title="Phantom Clinical Intelligence Platform",

    description=(
        "Advanced longitudinal clinical intelligence engine "
        "for computational patient modeling, disease trajectory "
        "simulation, and intervention optimization."
    ),

    version="1.0.0",

    lifespan=lifespan,
)

# ============================================================
# CORS Configuration
# ============================================================

# Required for:
# - Prompt Opinion browser-based connections
# - MCP-compatible orchestration systems
# - Local development
# - Cross-origin simulation clients

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_methods=["*"],

    allow_headers=["*"],
)

# ============================================================
# Health Endpoint
# ============================================================

@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Runtime health endpoint.

    Used for:
    - Deployment validation
    - Docker/container health checks
    - Infrastructure monitoring
    """

    return JSONResponse({

        "status": "healthy",

        "service": "phantom-clinical-intelligence-platform",

        "version": "1.0.0",

        "runtime": "active",

        "simulation_engine": "ready",

        "capabilities": [

            "computational_patient_modeling",

            "trajectory_forecasting",

            "intervention_simulation",

            "longitudinal_risk_analysis",

            "clinical_intelligence_generation",
        ],
    })

# ============================================================
# Info Endpoint
# ============================================================

@app.get("/info")
async def info() -> JSONResponse:
    """
    Public runtime metadata endpoint.

    Provides:
    - server metadata
    - available clinical tools
    - supported extensions
    - capability overview
    """

    return JSONResponse({

        "service": "Phantom Clinical Intelligence Platform",

        "version": "1.0.0",

        "description": (
            "Computational clinical intelligence engine "
            "for longitudinal physiological modeling and "
            "future risk simulation."
        ),

        "core_capabilities": [

            "Computational patient modeling",

            "Disease trajectory forecasting",

            "Intervention impact simulation",

            "Longitudinal multi-system risk analysis",

            "Clinical decision support synthesis",
        ],

        "tools": [

            {
                "name": "build_patient_model",

                "description": (
                    "Builds a simulation-ready computational "
                    "patient model from longitudinal FHIR data."
                ),
            },

            {
                "name": "simulate_scenario",

                "description": (
                    "Simulates future disease trajectories "
                    "under intervention or inaction scenarios."
                ),
            },

            {
                "name": "compare_interventions",

                "description": (
                    "Compares competing treatment strategies "
                    "using longitudinal multi-system modeling."
                ),
            },
        ],

        "supported_context_extensions": {

            "fhir_context": "ai.promptopinion/fhir-context",
        },

        "transport": {

            "protocol": "MCP",

            "mode": "streamable_http",
        },
    })

# ============================================================
# Mount MCP Application
# ============================================================

# IMPORTANT:
#
# MCP must be mounted at the root path.
#
# Prompt Opinion registers the root server URL:
#   https://your-server/
#
# MCP protocol communication occurs directly at "/"

app.mount("/", mcp.streamable_http_app())

# ============================================================
# Entry Point
# ============================================================

def main() -> None:
    """
    Start the Phantom Clinical Intelligence runtime.
    """

    logger.info(

        "phantom.server.launch",

        host=settings.host,

        port=settings.port,

        dev_mode=settings.dev_mode,

        log_level=settings.log_level,
    )

    uvicorn.run(

        "src.server:app",

        host=settings.host,

        port=settings.port,

        log_level=settings.log_level.lower(),

        reload=settings.dev_mode,
    )

if __name__ == "__main__":
    main()