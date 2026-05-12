"""
Middleware for the Phantom Orchestrator.

Translates Prompt Opinion's gRPC-style A2A method names to the JSON-RPC
slash-style names that Google ADK / a2a-sdk expects, then normalizes
responses into the hybrid A2A format that Prompt Opinion currently accepts.
"""

import json
import logging
import os
import sys
import uuid

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

    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(name)s | %(message)s"
        )
    )

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
    "SetTaskPushNotificationConfig":
        "tasks/pushNotificationConfig/set",
    "GetTaskPushNotificationConfig":
        "tasks/pushNotificationConfig/get",
    "ResubscribeTask": "tasks/resubscribe",
}

ROLE_TRANSLATION = {
    "ROLE_USER": "user",
    "ROLE_AGENT": "agent",
    "ROLE_UNSPECIFIED": "user",
}

# ============================================================
# Utility helpers
# ============================================================

def _translate_payload(payload):
    """
    Translate incoming PO enum roles into
    lowercase roles ADK understands internally.
    """

    if isinstance(payload, dict):

        new = {}

        for k, v in payload.items():

            if (
                k == "role"
                and isinstance(v, str)
                and v in ROLE_TRANSLATION
            ):

                new[k] = ROLE_TRANSLATION[v]

            else:

                new[k] = _translate_payload(v)

        return new

    elif isinstance(payload, list):

        return [
            _translate_payload(item)
            for item in payload
        ]

    return payload


def strip_kind(obj):
    """
    Recursively remove ALL `kind` fields.
    PO rejects v0.2 discriminators.
    """

    if isinstance(obj, dict):

        return {
            k: strip_kind(v)
            for k, v in obj.items()
            if k != "kind"
        }

    elif isinstance(obj, list):

        return [
            strip_kind(v)
            for v in obj
        ]

    return obj


def extract_text(parts):
    """
    Extract first text part safely.
    """

    if not isinstance(parts, list):
        return None

    for part in parts:

        if (
            isinstance(part, dict)
            and part.get("text")
        ):
            return part["text"]

    return None


# ============================================================
# ApiKeyMiddleware
# ============================================================

class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Optional API key authentication middleware."""

    def __init__(self, app, api_key: str | None = None):

        super().__init__(app)

        self.api_key = (
            api_key
            or os.getenv("PHANTOM_API_KEY")
        )

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):

        if not self.api_key:
            return await call_next(request)

        if request.url.path in (
            "/.well-known/agent-card.json",
            "/health",
            "/",
        ):

            if request.method == "GET":
                return await call_next(request)

        provided_key = request.headers.get("x-api-key")

        if provided_key != self.api_key:

            return JSONResponse(
                status_code=401,
                content={
                    "error":
                    "Invalid or missing API key"
                },
            )

        return await call_next(request)


# ============================================================
# Request translation middleware
# ============================================================

class A2ATranslateMiddleware:
    """
    Middleware that:
    1. Reads request body
    2. Translates PO method names
    3. Converts ROLE_USER -> user
    4. Logs request
    5. Replays translated body downstream
    """

    def __init__(self, app):
        self.app = app

    async def __call__(
        self,
        scope,
        receive,
        send,
    ):

        if (
            scope["type"] != "http"
            or scope.get("method") != "POST"
        ):
            await self.app(scope, receive, send)
            return

        # ----------------------------------------------------
        # Read request body
        # ----------------------------------------------------

        chunks = []
        more_body = True

        while more_body:

            message = await receive()

            chunks.append(
                message.get("body", b"")
            )

            more_body = message.get(
                "more_body",
                False,
            )

        body = b"".join(chunks)

        path = scope.get("path", "")

        translated_body = body

        # ----------------------------------------------------
        # Translate request
        # ----------------------------------------------------

        try:

            payload = json.loads(
                body.decode("utf-8")
            )

            original_method = payload.get(
                "method"
            )

            if (
                original_method
                in A2A_METHOD_TRANSLATION
            ):

                new_method = (
                    A2A_METHOD_TRANSLATION[
                        original_method
                    ]
                )

                payload["method"] = new_method

                logger.info(
                    f"METHOD TRANSLATED: "
                    f"{original_method} -> "
                    f"{new_method}"
                )

            payload = _translate_payload(
                payload
            )

            translated_body = json.dumps(
                payload
            ).encode("utf-8")

            logger.info("=" * 70)

            logger.info(
                f"INCOMING POST {path}"
            )

            logger.info(
                f"Original body: "
                f"{body.decode('utf-8')[:800]}"
            )

            logger.info(
                f"Translated body: "
                f"{translated_body.decode('utf-8')[:800]}"
            )

            logger.info(
                f"Translated method: "
                f"{payload.get('method')}"
            )

            logger.info("=" * 70)

        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ) as e:

            logger.warning(
                f"Could not parse/translate "
                f"body: {e}"
            )

        # ----------------------------------------------------
        # Fix content-length
        # ----------------------------------------------------

        headers = MutableHeaders(scope=scope)

        headers["content-length"] = str(
            len(translated_body)
        )

        body_consumed = False

        async def replay_receive():

            nonlocal body_consumed

            if body_consumed:

                return {
                    "type":
                    "http.disconnect"
                }

            body_consumed = True

            return {
                "type": "http.request",
                "body": translated_body,
                "more_body": False,
            }

        await self.app(
            scope,
            replay_receive,
            send,
        )

# ============================================================
# Response normalization middleware
# ============================================================

class A2AResponseFixMiddleware:
    """
    Converts ADK/a2a-sdk hybrid responses into the
    exact structure Prompt Opinion currently accepts.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(
        self,
        scope,
        receive,
        send,
    ):

        if scope["type"] != "http":

            await self.app(
                scope,
                receive,
                send,
            )

            return

        # ----------------------------------------------------
        # Capture downstream response
        # ----------------------------------------------------

        response_body = []

        original_headers = []
        original_status = 200

        async def capture_send(message):

            nonlocal original_headers
            nonlocal original_status

            if (
                message["type"]
                == "http.response.start"
            ):

                original_status = message[
                    "status"
                ]

                original_headers = list(
                    message.get(
                        "headers",
                        [],
                    )
                )

            elif (
                message["type"]
                == "http.response.body"
            ):

                response_body.append(
                    message.get(
                        "body",
                        b"",
                    )
                )

        await self.app(
            scope,
            receive,
            capture_send,
        )

        full_body = b"".join(
            response_body
        )

        # ----------------------------------------------------
        # Normalize response
        # ----------------------------------------------------

        try:

            data = json.loads(
                full_body.decode("utf-8")
            )

            result = data.get(
                "result",
                {},
            )

            # ------------------------------------------------
            # ADK sometimes returns raw task directly
            # ------------------------------------------------

            if (
                isinstance(result, dict)
                and result.get("kind")
                == "task"
            ):

                task = result

            else:

                task = result.get(
                    "task",
                    {},
                )

            if task:

                task_id = task.get(
                    "id",
                    str(uuid.uuid4())
                )

                context_id = task.get(
                    "contextId",
                    str(uuid.uuid4())
                )

                # ------------------------------------------------
                # Extract REAL response text
                # ------------------------------------------------

                response_text = None

                # --------------------------------------------
                # FIRST: Try artifacts
                # --------------------------------------------

                artifacts = task.get(
                    "artifacts",
                    [],
                )

                for artifact in artifacts:

                    for part in artifact.get(
                        "parts",
                        [],
                    ):

                        if (
                            isinstance(part, dict)
                            and part.get("text")
                        ):

                            response_text = (
                                part["text"]
                            )

                            break

                    if response_text:
                        break

                # --------------------------------------------
                # SECOND: fallback to status.message
                # --------------------------------------------

                if not response_text:

                    status = task.get(
                        "status",
                        {},
                    )

                    status_message = status.get(
                        "message",
                        {},
                    )

                    response_text = extract_text(
                        status_message.get(
                            "parts",
                            [],
                        )
                    )

                # --------------------------------------------
                # FINAL fallback
                # --------------------------------------------

                if not response_text:

                    response_text = (
                        "Task completed successfully."
                    )

                # ------------------------------------------------
                # Clean history
                # ------------------------------------------------

                clean_history = []

                seen_message_ids = set()

                for item in task.get(
                    "history",
                    [],
                ):

                    message_id = item.get(
                        "messageId",
                        str(uuid.uuid4())
                    )

                    if (
                        message_id
                        in seen_message_ids
                    ):
                        continue

                    seen_message_ids.add(
                        message_id
                    )

                    role = item.get(
                        "role",
                        "user",
                    )

                    # Convert back into PO enums

                    if role in [
                        "agent",
                        "ROLE_AGENT",
                    ]:

                        role = "ROLE_AGENT"

                    else:

                        role = "ROLE_USER"

                    clean_parts = []

                    for part in item.get(
                        "parts",
                        [],
                    ):

                        # Keep ONLY text parts

                        if "text" in part:

                            clean_parts.append(
                                {
                                    "text":
                                    part["text"]
                                }
                            )

                    clean_history.append(
                        {
                            "messageId":
                            message_id,

                            "role":
                            role,

                            "parts":
                            clean_parts,
                        }
                    )

                # ------------------------------------------------
                # Build final PO-compatible task
                # ------------------------------------------------

                clean_task = {

                    "id":
                    task_id,

                    "contextId":
                    context_id,

                    "status": {

                        "state":
                        "TASK_STATE_COMPLETED",

                        "message": {

                            "messageId":
                            str(
                                uuid.uuid4()
                            ),

                            "role":
                            "ROLE_AGENT",

                            "parts": [
                                {
                                    "text":
                                    response_text
                                }
                            ],
                        },
                    },

                    "artifacts": [
                        {

                            "artifactId":
                            str(
                                uuid.uuid4()
                            ),

                            "parts": [
                                {
                                    "text":
                                    response_text
                                }
                            ],
                        }
                    ],

                    "history":
                    clean_history,
                }

                # ------------------------------------------------
                # Replace result
                # ------------------------------------------------

                data["result"] = {
                    "task":
                    clean_task
                }

                # ------------------------------------------------
                # Remove ALL kind fields
                # ------------------------------------------------

                data = strip_kind(data)

                logger.info(
                    "RESPONSE NORMALIZED "
                    "TO PO-COMPATIBLE A2A"
                )

            full_body = json.dumps(
                data
            ).encode("utf-8")

        except Exception as e:

            logger.warning(
                f"Response normalization "
                f"failed: {e}"
            )

        # ----------------------------------------------------
        # Send normalized response
        # ----------------------------------------------------

        await send({

            "type":
            "http.response.start",

            "status":
            original_status,

            "headers": [

                (k, v)

                for k, v
                in original_headers

                if k.lower()
                != b"content-length"

            ] + [

                (
                    b"content-length",

                    str(
                        len(full_body)
                    ).encode()
                )
            ],
        })

        await send({

            "type":
            "http.response.body",

            "body":
            full_body,

            "more_body":
            False,
        })


# ============================================================
# Backwards compatibility wrappers
# ============================================================

async def log_a2a_requests(
    request,
    call_next,
):
    """Deprecated."""
    return await call_next(request)


async def translate_a2a_methods(
    request,
    call_next,
):
    """Deprecated."""
    return await call_next(request)