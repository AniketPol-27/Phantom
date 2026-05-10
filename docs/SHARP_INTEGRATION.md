# SHARP-on-MCP Integration Guide

This document explains how Phantom integrates with the SHARP-on-MCP healthcare context propagation specification. SHARP (**S**ecure **H**ealthcare **A**gent **R**eference **P**rotocol) extends MCP to carry FHIR server URLs, SMART on FHIR identity, and patient context between AI agents and tool servers — without requiring tool schemas to know about session state.

---

## What Is SHARP?

In a standard MCP integration, every tool that needs context (which patient? which FHIR server? which user?) has to accept that context as an argument. This couples tool schemas to session state, breaks the principle of stateless tool design, and creates a security risk: any agent that can call the tool can pass any patient ID it wants.

**SHARP solves this by moving healthcare context into HTTP headers** that are propagated transparently from the EHR session through the agent platform to the MCP server. Tools never see patient IDs in their arguments; they extract identity from validated SHARP context provided by middleware. The agent passes nothing — it just makes the tool call. The infrastructure handles the rest.

The key SHARP-on-MCP headers are:

| Header | Purpose |
|--------|---------|
| `X-FHIR-Server-URL` | Base URL of the FHIR R4 server to query |
| `Authorization: Bearer <jwt>` | SMART on FHIR JWT containing the patient claim and access scopes |
| `X-FHIR-Context` | Optional additional FHIR context (encounter, location, etc.) |

The MCP server is expected to declare support for SHARP via a capability extension during the initialize handshake, allowing the platform (Prompt Opinion) to verify compatibility before sending real patient context.

---

## How Phantom Uses SHARP

### Extension Declaration

FastMCP's default capabilities object does not advertise SHARP support. Phantom patches the capabilities returned during the MCP `initialize` call to declare the `prompt-opinion-fhir-context` extension. This tells Po that Phantom understands and consumes SHARP headers.

```python
# In server.py — patching FastMCP capabilities to advertise SHARP

from fastmcp import FastMCP

mcp = FastMCP("phantom")

# Patch the server capabilities to advertise the Po FHIR context extension
@mcp.server.handle_initialize
async def patched_initialize(request):
    response = await default_initialize(request)
    response.capabilities.experimental = {
        **(response.capabilities.experimental or {}),
        "prompt-opinion-fhir-context": {
            "version": "1.0",
            "supported_scopes": [
                "patient/Patient.rs",
                "patient/Condition.rs",
                "patient/Observation.rs",
                "patient/MedicationRequest.rs",
                "patient/AllergyIntolerance.rs",
                "patient/Procedure.rs",
                "patient/Immunization.rs",
                "patient/Encounter.rs"
            ]
        }
    }
    return response
```

When Po calls `tools/list` or `initialize`, the response now includes the SHARP capability declaration, signaling that Po should propagate FHIR headers on subsequent tool calls.

### Header Extraction Middleware

Before any tool handler executes, middleware extracts and validates the SHARP context from the incoming request. This middleware runs at the FastAPI layer (before FastMCP dispatches the tool call).

```python
# In server.py — SHARP context extraction middleware

from fastapi import Request, HTTPException
from contextvars import ContextVar

# Per-request context store (async-safe)
_sharp_context: ContextVar[dict] = ContextVar("sharp_context", default={})

@app.middleware("http")
async def extract_sharp_context(request: Request, call_next):
    if not request.url.path.startswith("/mcp"):
        return await call_next(request)

    fhir_server_url = request.headers.get("X-FHIR-Server-URL")
    auth_header = request.headers.get("Authorization", "")

    if not fhir_server_url:
        # Tool calls without SHARP context will fail at execution time
        # with MissingPatientContextError. We don't reject here because
        # initialize and tools/list don't require context.
        return await call_next(request)

    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing SMART JWT")

    jwt_token = auth_header[7:]
    patient_id = _extract_patient_id_from_jwt(jwt_token)

    _sharp_context.set({
        "fhir_server_url": fhir_server_url,
        "jwt": jwt_token,
        "patient_id": patient_id
    })

    return await call_next(request)
```

### JWT Patient ID Extraction (SMART on FHIR)

SMART on FHIR JWTs include a `patient` claim that carries the patient ID. Phantom decodes the JWT, validates the signature against the issuer's JWKS, and extracts the `patient` claim. Validation failure raises a 401.

```python
# In server.py — JWT decoding for SMART on FHIR

import jwt
from jwt import PyJWKClient

def _extract_patient_id_from_jwt(token: str) -> str:
    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
        issuer = unverified.get("iss")

        if not issuer:
            raise HTTPException(status_code=401, detail="JWT missing issuer")

        # Fetch issuer's JWKS to verify signature
        jwks_client = PyJWKClient(f"{issuer}/.well-known/jwks.json")
        signing_key = jwks_client.get_signing_key_from_jwt(token).key

        verified = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience="phantom-mcp-server"
        )

        patient_id = verified.get("patient")
        if not patient_id:
            raise HTTPException(status_code=401, detail="JWT missing patient claim")

        return patient_id

    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid JWT: {e}")
```

### Tool-Side Context Access

Once middleware has extracted SHARP context, tool handlers access it through the context store. Tools never touch the JWT or headers directly.

```python
# In a tool handler — accessing SHARP context

from .server import _sharp_context

@mcp.tool()
async def build_patient_model(
    include_trajectories: bool = True,
    include_care_gaps: bool = True,
    include_diagnostic_gaps: bool = True,
    lookback_months: int = 24
) -> dict:
    ctx = _sharp_context.get()
    if not ctx.get("patient_id"):
        raise MissingPatientContextError(
            "No SHARP context — verify Po has FHIR Context extension enabled"
        )

    fhir_client = FHIRClient(
        base_url=ctx["fhir_server_url"],
        jwt=ctx["jwt"]
    )

    patient_data = await fhir_client.fetch_patient_bundle(
        patient_id=ctx["patient_id"],
        lookback_months=lookback_months
    )

    return build_model(patient_data, include_trajectories, include_care_gaps, include_diagnostic_gaps)
```

### Error Handling

Phantom distinguishes three failure modes for SHARP context:

| Failure | HTTP Response | Tool Behavior |
|---------|---------------|---------------|
| No `X-FHIR-Server-URL` header | 200 (allowed at handshake time) | Tool raises `MissingPatientContextError` at execution |
| Malformed JWT | 401 Unauthorized | Tool never executes |
| Valid JWT, missing `patient` claim | 401 Unauthorized | Tool never executes |
| Valid JWT, patient claim present, but FHIR server returns 404 | 200 with structured error | Tool returns `FHIRConnectionError` payload |

This separation lets the agent distinguish "you're not authorized" (a configuration problem) from "the patient doesn't exist" (a clinical problem).

---

## Registering Phantom on Prompt Opinion

### Step 1: Deploy the MCP Server to a Public HTTPS URL

For development, ngrok works:

```bash
# Terminal 1 — start the server
cd mcp-server
uv run python -m src.server

# Terminal 2 — expose it publicly
ngrok http 8080
```

Copy the HTTPS forwarding URL (e.g., `https://abc123.ngrok.app`).

For production, deploy to Railway, Fly.io, Cloud Run, or any platform that supports a single ASGI app on HTTPS.

### Step 2: Add Phantom in Po Configuration

1. Sign into Prompt Opinion
2. Navigate to **Configuration → MCP Servers**
3. Click **Add MCP Server**
4. Fill in the form:
   - **Name:** Phantom Clinical Simulation
   - **URL:** `https://your-deployment-url/mcp`
   - **Transport:** Streamable HTTP
   - **Description:** Clinical simulation server with 3 tools

### Step 3: Enable the FHIR Context Extension

After adding the server, Po will perform an `initialize` handshake and discover Phantom's `prompt-opinion-fhir-context` capability. A new toggle will appear:

5. Toggle **"Prompt Opinion FHIR Context"** to **ON**
6. Approve the requested FHIR scopes (the 8 scopes listed in the marketplace listing)
7. Click **Save**

### Step 4: Verify the Integration

1. Open the Pre-Visit Intelligence Agent in Po
2. Load a patient session (Po will inject the SHARP headers automatically)
3. Send: *"Prep me for my next patient"*
4. Watch the tool calls in the agent trace — `build_patient_model` should succeed and return a populated patient model

If the tool returns `MissingPatientContextError`, the FHIR Context extension is not enabled. Re-check Step 3.

---

## Testing the Integration Manually

Use these `curl` commands to verify the SHARP integration outside of Po.

### Test 1: Initialize Handshake (no SHARP context required)

```bash
curl -X POST https://your-deployment-url/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": { "name": "test-client", "version": "1.0" }
    }
  }'
```

**Expected:** Response includes `capabilities.experimental.prompt-opinion-fhir-context`.

### Test 2: List Tools (no SHARP context required)

```bash
curl -X POST https://your-deployment-url/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

**Expected:** Returns 3 tools: `build_patient_model`, `simulate_scenario`, `compare_interventions`.

### Test 3: Call a Tool with SHARP Context

```bash
curl -X POST https://your-deployment-url/mcp \
  -H "Content-Type: application/json" \
  -H "X-FHIR-Server-URL: https://hapi.fhir.org/baseR4" \
  -H "Authorization: Bearer <test-smart-jwt>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "build_patient_model",
      "arguments": { "include_trajectories": true }
    }
  }'
```

**Expected:** Returns a structured patient model (or a structured error if the patient does not exist).

### Test 4: Call a Tool Without SHARP Context

```bash
curl -X POST https://your-deployment-url/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "build_patient_model",
      "arguments": {}
    }
  }'
```

**Expected:** Returns a structured `MissingPatientContextError` payload.

---

## Common Integration Issues

### "FHIR Context extension toggle not appearing in Po"

The capabilities patch did not take effect. Verify:
1. The server is actually responding to `initialize` (run Test 1 above)
2. The response contains `experimental.prompt-opinion-fhir-context`
3. Po is using the URL you registered (not a stale one)

### "Tool returns MissingPatientContextError every time"

SHARP headers are not arriving. Verify:
1. The FHIR Context extension toggle is **ON** in Po
2. The patient session is loaded before invoking the agent
3. Inspect the request headers in your server logs — `X-FHIR-Server-URL` should be present

### "Tool returns 401 Invalid JWT"

JWT validation is failing. Verify:
1. The issuer's JWKS endpoint is reachable from your deployment
2. The JWT audience matches what your code expects (`phantom-mcp-server`)
3. The JWT has not expired

### "FHIR fetch succeeds in dev but fails in production"

Production FHIR servers often require additional headers (e.g., `Accept: application/fhir+json`) or specific TLS configuration. Check the FHIR server's documentation and your httpx client configuration.

---

## Why SHARP Matters for Healthcare AI

SHARP is not just a header convention — it is a security and architecture posture. Three principles drive its design:

1. **Tools are stateless.** A tool's schema describes what it does, not which patient it operates on. This makes tool catalogs cleaner and tool discovery more useful.

2. **Identity flows from the EHR.** The patient's identity, the clinician's identity, and the FHIR access scopes are all bound at the EHR session boundary — not invented by the agent. This eliminates an entire class of attacks where a malicious agent could query data for patients it shouldn't access.

3. **Audit trails are coherent.** Every FHIR access can be traced back through the SHARP context to the EHR session that initiated it. This is what makes healthcare AI auditable in a way that ad hoc tool integrations are not.

Phantom's adoption of SHARP is a deliberate bet that healthcare AI infrastructure will converge on these principles. Building on SHARP today means Phantom is ready for the ecosystem that the Prompt Opinion platform is creating.