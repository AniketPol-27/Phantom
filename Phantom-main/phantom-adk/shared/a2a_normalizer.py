import uuid
from copy import deepcopy


def _strip_kind(obj):
    """
    Recursively remove all `kind` fields from dicts/lists.
    """
    if isinstance(obj, dict):
        return {
            k: _strip_kind(v)
            for k, v in obj.items()
            if k != "kind"
        }

    if isinstance(obj, list):
        return [_strip_kind(v) for v in obj]

    return obj


def normalize_a2a_response(payload: dict) -> dict:
    """
    Convert ADK/a2a-sdk hybrid payload into strict A2A v1 payload.
    """

    payload = deepcopy(payload)

    result = payload.get("result", {})
    task = result.get("task", {})

    task_id = task.get("id", str(uuid.uuid4()))
    context_id = task.get("contextId", str(uuid.uuid4()))

    # -----------------------------
    # Extract best response text
    # -----------------------------
    response_text = "Task completed successfully."

    status = task.get("status", {})
    status_message = status.get("message", {})

    parts = status_message.get("parts", [])

    for part in parts:
        if isinstance(part, dict) and "text" in part:
            response_text = part["text"]
            break

    # -----------------------------
    # Extract user history safely
    # -----------------------------
    clean_history = []

    history = task.get("history", [])

    for item in history:
        if item.get("role") == "user":

            clean_parts = []

            for part in item.get("parts", []):
                if "text" in part:
                    clean_parts.append({
                        "text": part["text"]
                    })

            clean_history.append({
                "messageId": item.get(
                    "messageId",
                    str(uuid.uuid4())
                ),
                "role": "user",
                "parts": clean_parts
            })

    # -----------------------------
    # Build STRICT A2A v1 task
    # -----------------------------
    clean_task = {
        "id": task_id,
        "contextId": context_id,

        "status": {
            "state": "completed",
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "agent",
                "parts": [
                    {
                        "text": response_text
                    }
                ]
            }
        },

        "artifacts": [
            {
                "artifactId": str(uuid.uuid4()),
                "parts": [
                    {
                        "text": response_text
                    }
                ]
            }
        ],

        "history": clean_history
    }

    payload["result"] = {
        "task": clean_task
    }

    # FINAL SAFETY
    payload = _strip_kind(payload)

    return payload