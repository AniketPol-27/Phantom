"""
Middleware for the Phantom Orchestrator.

Translates Prompt Opinion's gRPC-style A2A method names to the JSON-RPC
slash-style names that Google ADK / a2a-sdk expects, then logs the
result for debugging.
"""

import json
import logging
import os
import sys

from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# ============================================================
# Logging setup
# ============================================================

logger = logging.getLogger("phantom.middleware")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(name)s | %(message)s"))
    logger.addHandler(handler)


# ============================================================
# Translation tables
# ============================================================

A2A_METHOD_TRANSLATION = {
    "SendMessage": "message/send",
    "SendStreamingMessage": "message/stream",
    "GetTask": "tasks/get",
    "CancelTask": "tasks/cancel",
    "GetAgentCard": "agent/getCard",
    "ListTask": "tasks/list",
    "SetTaskPushNotificationConfig": "tasks/pushNotificationConfig/set",
    "GetTaskPushNotificationConfig": "tasks/pushNotificationConfig/get",
    "ResubscribeTask": "tasks/resubscribe",
}

ROLE_TRANSLATION = {
    "ROLE_USER": "user",
    "ROLE_AGENT": "agent",
    "ROLE_UNSPECIFIED": "user",
}


def _translate_payload(payload):
    """Recursively translate role values."""
    if isinstance(payload, dict):
        new = {}
        for k, v in payload.items():
            if k == "role" and isinstance(v, str) and v in ROLE_TRANSLATION:
                new[k] = ROLE_TRANSLATION[v]
            else:
                new[k] = _translate_payload(v)
        return new
    elif isinstance(payload, list):
        return [_translate_payload(item) for item in payload]
    else:
        return payload


# ============================================================
# ApiKeyMiddleware (used by app_factory.py)
# ============================================================

class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Optional API key authentication middleware."""

    def __init__(self, app, api_key: str | None = None):
        super().__init__(app)
        self.api_key = api_key or os.getenv("PHANTOM_API_KEY")

    async def dispatch(self, request: Request, call_next):
        if not self.api_key:
            return await call_next(request)

        if request.url.path in ("/.well-known/agent-card.json", "/health", "/"):
            if request.method == "GET":
                return await call_next(request)

        provided_key = request.headers.get("x-api-key")
        if provided_key != self.api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or missing API key"},
            )

        return await call_next(request)


# ============================================================
# Combined ASGI middleware (translation + logging)
# ============================================================
# We use raw ASGI middleware (not BaseHTTPMiddleware) because
# BaseHTTPMiddleware has known issues with body modification that
# don't propagate to downstream handlers.

class A2ATranslateMiddleware:
    """
    Pure ASGI middleware that:
    1. Reads the request body
    2. Translates Po method names to A2A v1 names
    3. Translates ROLE_USER -> user
    4. Logs everything
    5. Replaces the body so downstream handlers see the translated version
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Only intercept HTTP POST requests
        if scope["type"] != "http" or scope.get("method") != "POST":
            await self.app(scope, receive, send)
            return

        # Read the entire request body
        chunks = []
        more_body = True
        while more_body:
            message = await receive()
            chunks.append(message.get("body", b""))
            more_body = message.get("more_body", False)
        body = b"".join(chunks)

        path = scope.get("path", "")

        # Try to translate
        translated_body = body
        try:
            payload = json.loads(body.decode("utf-8"))

            original_method = payload.get("method")
            if original_method in A2A_METHOD_TRANSLATION:
                new_method = A2A_METHOD_TRANSLATION[original_method]
                payload["method"] = new_method
                logger.info(
                    f"METHOD TRANSLATED: {original_method} -> {new_method}"
                )

            payload = _translate_payload(payload)
            translated_body = json.dumps(payload).encode("utf-8")

            # Log
            logger.info("=" * 70)
            logger.info(f"INCOMING POST {path}")
            logger.info(f"Original body: {body.decode('utf-8')[:800]}")
            logger.info(f"Translated body: {translated_body.decode('utf-8')[:800]}")
            logger.info(
                f"Translated method: {payload.get('method', '<no method>')}"
            )
            logger.info("=" * 70)

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Could not parse/translate body: {e}")

        # Update content-length header to match translated body
        headers = MutableHeaders(scope=scope)
        headers["content-length"] = str(len(translated_body))

        # Replay the (possibly translated) body to downstream
        body_consumed = False

        async def replay_receive():
            nonlocal body_consumed
            if body_consumed:
                return {"type": "http.disconnect"}
            body_consumed = True
            return {
                "type": "http.request",
                "body": translated_body,
                "more_body": False,
            }

        await self.app(scope, replay_receive, send)


# ============================================================
# Backwards-compat wrappers
# ============================================================
# Keep the old function names exported in case something imports them.

async def log_a2a_requests(request, call_next):
    """Deprecated: use A2ATranslateMiddleware instead."""
    return await call_next(request)


async def translate_a2a_methods(request, call_next):
    """Deprecated: use A2ATranslateMiddleware instead."""
    return await call_next(request)
