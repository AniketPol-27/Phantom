import hashlib
import json


def safe_pretty_json(data) -> str:
    """
    Safely pretty-print JSON for logging.
    """

    try:
        return json.dumps(
            data,
            indent=2,
            default=str,
        )
    except Exception:
        return str(data)


def serialize_for_log(data):
    """
    Safely serialize arbitrary objects for logs.
    """

    try:
        return json.loads(
            json.dumps(data, default=str)
        )
    except Exception:
        return str(data)


def token_fingerprint(token: str | None) -> str:
    """
    Create a short non-reversible fingerprint for token logging.
    """

    if not token:
        return "none"

    digest = hashlib.sha256(
        token.encode()
    ).hexdigest()

    return digest[:12]
def redact_headers(headers: dict | None) -> dict:
    """
    Redact sensitive headers for safe logging.
    """

    if not headers:
        return {}

    redacted = {}

    sensitive_keys = {
        "authorization",
        "x-api-key",
        "x-fhir-access-token",
    }

    for key, value in headers.items():

        if key.lower() in sensitive_keys:
            redacted[key] = "***REDACTED***"
        else:
            redacted[key] = value

    return redacted    
