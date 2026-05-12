"""
FHIR context hook — ADK before_model_callback.

Extracts FHIR credentials from A2A metadata and stores them
inside callback_context.state for MCP tool usage.
"""

import json
import logging
import os

from shared.logging_utils import (
    safe_pretty_json,
    serialize_for_log,
    token_fingerprint,
)

logger = logging.getLogger(__name__)

LOG_HOOK_RAW_OBJECTS = (
    os.getenv(
        "LOG_HOOK_RAW_OBJECTS",
        "false",
    ).lower() == "true"
)

FHIR_CONTEXT_KEY = "fhir-context"


# ============================================================
# Helpers
# ============================================================

def _first_non_empty(*values):

    for v in values:

        if v not in (None, ""):
            return v

    return None


def _safe_correlation_ids(
    callback_context,
    llm_request,
):

    return {

        "task_id":
        _first_non_empty(
            getattr(llm_request, "task_id", None),
            getattr(callback_context, "task_id", None),
        ),

        "context_id":
        _first_non_empty(
            getattr(llm_request, "context_id", None),
            getattr(callback_context, "context_id", None),
        ),

        "message_id":
        _first_non_empty(
            getattr(llm_request, "message_id", None),
            getattr(callback_context, "message_id", None),
        ),
    }


def _coerce_fhir_data(value):

    if isinstance(value, dict):
        return value

    if isinstance(value, str):

        try:

            parsed = json.loads(value)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            return None

    return None


def _extract_metadata_sources(
    callback_context,
    llm_request,
):
    """
    Collect all possible metadata locations.
    """

    callback_metadata = getattr(
        callback_context,
        "metadata",
        None,
    )

    run_config = getattr(
        callback_context,
        "run_config",
        None,
    )

    custom_metadata = (
        getattr(run_config, "custom_metadata", None)
        if run_config else None
    )

    a2a_metadata = (
        custom_metadata.get("a2a_metadata")
        if isinstance(custom_metadata, dict)
        else None
    )

    llm_payload = serialize_for_log(llm_request)

    contents = (
        llm_payload.get("contents", [])
        if isinstance(llm_payload, dict)
        else []
    )

    content_metadata = None

    if contents and isinstance(contents, list):

        last = contents[-1]

        if isinstance(last, dict):
            content_metadata = last.get("metadata")

    return [

        (
            "callback_context.metadata",
            callback_metadata,
        ),

        (
            "callback_context.run_config.custom_metadata.a2a_metadata",
            a2a_metadata,
        ),

        (
            "llm_request.contents[-1].metadata",
            content_metadata,
        ),
    ]


# ============================================================
# Main extraction helper
# ============================================================

def _find_fhir_data(metadata: dict):
    """
    Robustly extract FHIR context from multiple shapes.
    """

    if not isinstance(metadata, dict):
        return None

    # --------------------------------------------------------
    # CASE 1:
    # Direct flat metadata
    # --------------------------------------------------------

    if (
        "fhirUrl" in metadata
        or "fhirToken" in metadata
        or "patientId" in metadata
    ):

        logger.info(
            "FHIR metadata found in flat structure"
        )

        return {
            "fhirUrl":
            metadata.get("fhirUrl", ""),

            "fhirToken":
            metadata.get("fhirToken", ""),

            "patientId":
            metadata.get("patientId", ""),
        }

    # --------------------------------------------------------
    # CASE 2:
    # Nested under fhir-context URI key
    # --------------------------------------------------------

    for key, value in metadata.items():

        if FHIR_CONTEXT_KEY in str(key):

            logger.info(
                "FHIR metadata found under key=%s",
                key,
            )

            return _coerce_fhir_data(value)

    # --------------------------------------------------------
    # CASE 3:
    # Nested recursively
    # --------------------------------------------------------

    for key, value in metadata.items():

        if isinstance(value, dict):

            nested = _find_fhir_data(value)

            if nested:
                return nested

    return None


# ============================================================
# Public helper
# ============================================================

def extract_fhir_from_payload(payload: dict):

    if not isinstance(payload, dict):
        return None, None

    params = payload.get("params")

    if not isinstance(params, dict):
        return None, None

    metadata_candidates = [

        params.get("metadata"),

        (params.get("message") or {}).get(
            "metadata"
        ),
    ]

    for metadata in metadata_candidates:

        if not isinstance(metadata, dict):
            continue

        fhir_data = _find_fhir_data(metadata)

        if fhir_data:

            return (
                "fhir-context",
                fhir_data,
            )

    return None, None


# ============================================================
# ADK Hook
# ============================================================

def extract_fhir_context(
    callback_context,
    llm_request,
):
    """
    ADK before_model_callback.
    """

    correlation = _safe_correlation_ids(
        callback_context,
        llm_request,
    )

    metadata_sources = _extract_metadata_sources(
        callback_context,
        llm_request,
    )

    selected_source = "none"
    metadata = {}

    for source_name, candidate in metadata_sources:

        if (
            isinstance(candidate, dict)
            and candidate
        ):

            metadata = candidate
            selected_source = source_name
            break

    if LOG_HOOK_RAW_OBJECTS:

        logger.info(
            "hook_raw_metadata=\n%s",
            safe_pretty_json(metadata),
        )

    logger.info(
        "FHIR HOOK CALLED "
        "task_id=%s "
        "context_id=%s "
        "message_id=%s "
        "source=%s",
        correlation["task_id"],
        correlation["context_id"],
        correlation["message_id"],
        selected_source,
    )

    logger.info(
        "FHIR METADATA KEYS=%s",
        list(metadata.keys())
        if isinstance(metadata, dict)
        else [],
    )

    # --------------------------------------------------------
    # Extract FHIR context
    # --------------------------------------------------------

    fhir_data = _find_fhir_data(metadata)

    if not fhir_data:

        logger.warning(
            "FHIR CONTEXT NOT FOUND "
            "task_id=%s",
            correlation["task_id"],
        )

        return None

    # --------------------------------------------------------
    # Store in callback state
    # --------------------------------------------------------

    callback_context.state["fhir_url"] = (
        fhir_data.get("fhirUrl", "")
    )

    callback_context.state["fhir_token"] = (
        fhir_data.get("fhirToken", "")
    )

    callback_context.state["patient_id"] = (
        fhir_data.get("patientId", "")
    )

    logger.info(
        "FHIR_URL_FOUND=%s",
        callback_context.state["fhir_url"]
        or "[EMPTY]",
    )

    logger.info(
        "FHIR_TOKEN_FOUND=%s",
        token_fingerprint(
            callback_context.state["fhir_token"]
        ),
    )

    logger.info(
        "FHIR_PATIENT_FOUND=%s",
        callback_context.state["patient_id"]
        or "[EMPTY]",
    )

    logger.info(
        "FHIR CONTEXT SUCCESSFULLY STORED"
    )

    return None