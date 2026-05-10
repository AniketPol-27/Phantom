"""
Phantom MCP Server - HTTP Application Entry Point

Wires together:
- The FastMCP server (with all tools registered) from src.mcp_instance
- A FastAPI application that mounts the MCP streamable HTTP app
- CORS middleware (required for Po platform browser-based connections)
- A health check endpoint
- The lifespan context manager for the MCP session

This module mirrors the structure of the Prompt Opinion Python reference
implementation, with our novel clinical tooling layered on top.
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
# Logging Setup
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
        structlog.dev.ConsoleRenderer() if settings.dev_mode
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
# FastAPI Application with MCP Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the FastMCP session lifecycle alongside the FastAPI app.
    The MCP session manager must be running for the streamable HTTP
    transport to function.
    """
    logger.info("phantom.lifespan.starting")
    async with mcp.session_manager.run():
        logger.info("phantom.lifespan.mcp_ready")
        yield
    logger.info("phantom.lifespan.stopped")


app = FastAPI(
    title="Phantom MCP Server",
    description="Clinical simulation engine - patient digital twin for clinical reasoning",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS - required for Prompt Opinion to connect from browser context
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Health and Info Endpoints
# ============================================================

@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint for monitoring and Docker health checks."""
    return JSONResponse({
        "status": "healthy",
        "service": "phantom-mcp-server",
        "version": "0.1.0",
    })


@app.get("/info")
async def info() -> JSONResponse:
    """Server info endpoint (the root path is reserved for the MCP app)."""
    return JSONResponse({
        "service": "Phantom MCP Server",
        "version": "0.1.0",
        "description": "Clinical simulation engine - patient digital twin",
        "tools": [
            "build_patient_model",
            "simulate_scenario",
            "compare_interventions",
        ],
        "extensions": {
            "fhir_context": "ai.promptopinion/fhir-context",
        },
    })


# ============================================================
# Mount the MCP Streamable HTTP App
# ============================================================
# This must be mounted LAST, at the root path. The MCP server lives at "/".
# Prompt Opinion will register the URL of this server (e.g., https://your-host/)
# and the MCP protocol communication happens at the root.

app.mount("/", mcp.streamable_http_app())


# ============================================================
# Entry Point
# ============================================================

def main() -> None:
    """Start the Phantom MCP server."""
    logger.info(
        "phantom.server.starting",
        host=settings.host,
        port=settings.port,
        dev_mode=settings.dev_mode,
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