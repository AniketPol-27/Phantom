"""
SHARP context extraction.

The Prompt Opinion platform sends FHIR context via HTTP headers on every
MCP tool call (per the SHARP-on-MCP specification). This module extracts
that context from the FastMCP Context object.

SHARP Headers:
- X-FHIR-Server-URL: Base URL of the FHIR server
- X-FHIR-Access-Token: Bearer token for the FHIR server
- X-Patient-ID: Patient ID for patient-scoped calls (optional, may be in JWT)

The patient ID can also be embedded in the access token's JWT claims
(SMART on FHIR convention). We check both sources.
"""

from dataclasses import dataclass

import jwt
import structlog
from mcp.server.fastmcp import Context

from src.mcp_constants import (
    FHIR_ACCESS_TOKEN_HEADER,
    FHIR_REFRESH_TOKEN_HEADER,
    FHIR_REFRESH_URL_HEADER,
    FHIR_SERVER_URL_HEADER,
    PATIENT_ID_HEADER,
)

logger = structlog.get_logger(__name__)


@dataclass
class SharpContext:
    """
    Validated SHARP context extracted from an MCP tool call.

    Created by extract_sharp_context() from the request headers and JWT claims.
    """

    fhir_url: str
    fhir_token: str
    patient_id: str | None = None
    refresh_token: str | None = None
    refresh_url: str | None = None

    @property
    def patient_reference(self) -> str | None:
        """Returns the patient reference in FHIR format (e.g., 'Patient/12345')."""
        if not self.patient_id:
            return None
        if self.patient_id.startswith("Patient/"):
            return self.patient_id
        return f"Patient/{self.patient_id}"

    @property
    def patient_id_only(self) -> str | None:
        """Returns just the patient ID without the 'Patient/' prefix."""
        if not self.patient_id:
            return None
        if self.patient_id.startswith("Patient/"):
            return self.patient_id.replace("Patient/", "")
        return self.patient_id


class SharpContextError(Exception):
    """Raised when required SHARP context is missing."""

    pass


def get_request_headers(ctx: Context) -> dict[str, str]:
    """
    Extracts headers from the FastMCP request context.

    FastMCP wraps the Starlette Request object inside ctx.request_context.request.
    Headers are accessed via the headers attribute (case-insensitive).
    """
    try:
        req = ctx.request_context.request
        # Convert headers to a plain dict with lowercase keys
        return {k.lower(): v for k, v in req.headers.items()}
    except AttributeError as e:
        logger.error("sharp.context.no_request", error=str(e))
        return {}


def extract_patient_id(headers: dict[str, str]) -> str | None:
    """
    Extracts the patient ID from headers or JWT token claims.

    Priority:
    1. X-Patient-ID header (if present)
    2. 'patient' claim from the FHIR access token JWT (SMART on FHIR convention)

    The JWT is decoded WITHOUT signature verification because we are only
    extracting claims for context. The token has already been validated
    by the Prompt Opinion platform before being passed to us.
    """
    # Try header first
    patient_id = headers.get(PATIENT_ID_HEADER)
    if patient_id:
        logger.debug("sharp.patient_id.from_header", patient_id=patient_id)
        return patient_id

    # Try JWT claims
    fhir_token = headers.get(FHIR_ACCESS_TOKEN_HEADER)
    if not fhir_token:
        return None

    try:
        # Strip "Bearer " prefix if present
        if fhir_token.lower().startswith("bearer "):
            fhir_token = fhir_token[7:]

        claims = jwt.decode(fhir_token, options={"verify_signature": False})
        patient = claims.get("patient")
        if patient:
            logger.debug("sharp.patient_id.from_jwt", patient_id=patient)
            return str(patient)
    except jwt.PyJWTError as e:
        logger.warning("sharp.jwt_decode_failed", error=str(e))
    except Exception as e:
        logger.warning("sharp.jwt_unexpected_error", error=str(e))

    return None


def extract_sharp_context(ctx: Context) -> SharpContext:
    """
    Extracts and validates SHARP context from a FastMCP tool call.

    Args:
        ctx: The FastMCP Context object passed to tool handlers

    Returns:
        Validated SharpContext object

    Raises:
        SharpContextError: If required context (FHIR URL or token) is missing
    """
    headers = get_request_headers(ctx)

    fhir_url = headers.get(FHIR_SERVER_URL_HEADER)
    fhir_token = headers.get(FHIR_ACCESS_TOKEN_HEADER)

    if not fhir_url:
        logger.error("sharp.context.missing_fhir_url", headers_present=list(headers.keys()))
        raise SharpContextError(
            f"Missing required header: {FHIR_SERVER_URL_HEADER}. "
            "FHIR context is required for this tool."
        )

    if not fhir_token:
        logger.error("sharp.context.missing_fhir_token")
        raise SharpContextError(
            f"Missing required header: {FHIR_ACCESS_TOKEN_HEADER}. "
            "FHIR access token is required for this tool."
        )

    patient_id = extract_patient_id(headers)

    context = SharpContext(
        fhir_url=fhir_url.rstrip("/"),
        fhir_token=fhir_token,
        patient_id=patient_id,
        refresh_token=headers.get(FHIR_REFRESH_TOKEN_HEADER),
        refresh_url=headers.get(FHIR_REFRESH_URL_HEADER),
    )

    logger.info(
        "sharp.context.extracted",
        patient_id=context.patient_id_only,
        fhir_url=context.fhir_url,
        has_refresh=bool(context.refresh_token),
    )

    return context