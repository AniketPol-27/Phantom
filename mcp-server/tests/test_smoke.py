"""
Smoke tests for the Phantom MCP server.

These tests verify the foundational plumbing:
- Configuration loads
- FastMCP instance is created
- Po extension is patched into capabilities
- Tools are registered
- SHARP context extraction works from headers
- JWT patient ID extraction works
"""

from unittest.mock import MagicMock

import jwt
import pytest

from src.config import get_settings
from src.mcp_constants import PHANTOM_FHIR_SCOPES, PO_FHIR_CONTEXT_EXTENSION
from src.sharp import SharpContextError, extract_sharp_context
from src.sharp.context import extract_patient_id


def _mock_context(headers: dict[str, str]) -> MagicMock:
    """Helper to create a mock FastMCP Context with given headers."""
    ctx = MagicMock()
    ctx.request_context.request.headers = headers
    return ctx


def test_config_loads():
    settings = get_settings()
    assert settings.host
    assert settings.port > 0


def test_mcp_instance_imports():
    """The FastMCP instance should be created with our extension patched in."""
    from src.mcp_instance import mcp
    assert mcp is not None
    assert mcp.name == "Phantom"


def test_po_extension_in_capabilities():
    """Calling get_capabilities should return our Po FHIR extension."""
    from src.mcp_instance import mcp

    caps = mcp._mcp_server.get_capabilities(
        notification_options=MagicMock(prompts_changed=False, resources_changed=False, tools_changed=False),
        experimental_capabilities={},
    )

    assert caps.model_extra is not None
    assert "extensions" in caps.model_extra
    assert PO_FHIR_CONTEXT_EXTENSION in caps.model_extra["extensions"]
    assert caps.model_extra["extensions"][PO_FHIR_CONTEXT_EXTENSION]["scopes"] == PHANTOM_FHIR_SCOPES


def test_sharp_context_extracts_from_headers():
    """SHARP context should extract from lowercase HTTP headers."""
    ctx = _mock_context({
        "x-fhir-server-url": "https://fhir.example.com/r4/",
        "x-fhir-access-token": "Bearer abc123",
        "x-patient-id": "Patient/789",
    })

    sharp = extract_sharp_context(ctx)
    assert sharp.fhir_url == "https://fhir.example.com/r4"  # trailing slash stripped
    assert sharp.fhir_token == "Bearer abc123"
    assert sharp.patient_id_only == "789"
    assert sharp.patient_reference == "Patient/789"


def test_sharp_context_extracts_patient_id_from_jwt():
    """When X-Patient-ID is missing, patient_id should come from JWT claims."""
    # Create a JWT with a 'patient' claim
    token = jwt.encode({"patient": "abc-jwt-456", "iss": "test"}, "secret", algorithm="HS256")

    ctx = _mock_context({
        "x-fhir-server-url": "https://fhir.example.com/r4",
        "x-fhir-access-token": token,
    })

    sharp = extract_sharp_context(ctx)
    assert sharp.patient_id_only == "abc-jwt-456"


def test_sharp_context_handles_bearer_prefix_in_jwt():
    """JWT extraction should handle 'Bearer ' prefix correctly."""
    token = jwt.encode({"patient": "xyz-789"}, "secret", algorithm="HS256")
    bearer_token = f"Bearer {token}"

    ctx = _mock_context({
        "x-fhir-server-url": "https://fhir.example.com/r4",
        "x-fhir-access-token": bearer_token,
    })

    sharp = extract_sharp_context(ctx)
    assert sharp.patient_id_only == "xyz-789"


def test_sharp_context_raises_when_fhir_url_missing():
    """Should raise SharpContextError when FHIR URL header is missing."""
    ctx = _mock_context({"x-fhir-access-token": "abc"})

    with pytest.raises(SharpContextError, match="x-fhir-server-url"):
        extract_sharp_context(ctx)


def test_sharp_context_raises_when_fhir_token_missing():
    """Should raise SharpContextError when FHIR token header is missing."""
    ctx = _mock_context({"x-fhir-server-url": "https://fhir.example.com/r4"})

    with pytest.raises(SharpContextError, match="x-fhir-access-token"):
        extract_sharp_context(ctx)


def test_sharp_context_includes_refresh_token_when_present():
    """Refresh token headers should be captured when present."""
    ctx = _mock_context({
        "x-fhir-server-url": "https://fhir.example.com/r4",
        "x-fhir-access-token": "abc",
        "x-fhir-refresh-token": "refresh-xyz",
        "x-fhir-refresh-url": "https://fhir.example.com/refresh",
    })

    sharp = extract_sharp_context(ctx)
    assert sharp.refresh_token == "refresh-xyz"
    assert sharp.refresh_url == "https://fhir.example.com/refresh"


def test_extract_patient_id_returns_none_when_no_token():
    """Patient ID extraction returns None when no headers or token are present."""
    assert extract_patient_id({}) is None


def test_extract_patient_id_handles_invalid_jwt():
    """Should gracefully handle malformed JWT and return None."""
    headers = {"x-fhir-access-token": "not-a-real-jwt"}
    assert extract_patient_id(headers) is None