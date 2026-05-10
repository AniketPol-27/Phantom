"""
Tool: build_patient_model

Round 3 Chunk 2: Fetches FHIR resources AND parses them into clean structures.
"""

import asyncio
import json
from typing import Annotated

import structlog
from mcp.server.fastmcp import Context
from pydantic import Field

from src.fhir import (
    FhirAuthError,
    FhirClient,
    FhirError,
    allergies_query,
    care_plans_query,
    conditions_query,
    encounters_query,
    immunizations_query,
    lab_observations_query,
    medication_requests_query,
    parse_allergy,
    parse_condition,
    parse_encounter,
    parse_immunization,
    parse_medication_request,
    parse_observation,
    parse_patient,
    procedures_query,
    parse_procedure,
    vital_observations_query,
)
from src.sharp import SharpContextError, extract_sharp_context
from src.model_builder.builder import assemble_patient_model

logger = structlog.get_logger(__name__)


async def _safe_fetch(label: str, coro):
    try:
        result = await coro
        return label, result
    except FhirAuthError as e:
        logger.error("build_patient_model.auth_error", label=label, error=str(e))
        return label, {"_error": "auth", "message": str(e)}
    except FhirError as e:
        logger.warning("build_patient_model.fetch_error", label=label, error=str(e))
        return label, {"_error": "fetch_failed", "message": str(e)}
    except Exception as e:
        logger.exception("build_patient_model.unexpected_error", label=label)
        return label, {"_error": "unexpected", "message": str(e)}


async def build_patient_model(
    ctx: Context,
    model_depth: Annotated[
        str,
        Field(description="comprehensive or focused", default="comprehensive"),
    ] = "comprehensive",
    lookback_months: Annotated[
        int,
        Field(description="Months of history", default=24, ge=6, le=60),
    ] = 24,
) -> str:
    """Build a parsed patient model from FHIR data."""

    try:
        sharp = extract_sharp_context(ctx)
    except SharpContextError as e:
        return json.dumps({"error": "FHIR context required", "message": str(e)}, indent=2)

    if not sharp.patient_id:
        return json.dumps({"error": "No patient in context"}, indent=2)

    patient_id = sharp.patient_id_only
    fhir = FhirClient(base_url=sharp.fhir_url, token=sharp.fhir_token)

    logger.info(
        "build_patient_model.starting",
        patient_id=patient_id,
        fhir_url=sharp.fhir_url,
        lookback_months=lookback_months,
    )

    try:
        patient_resource = await fhir.read("Patient", patient_id)
    except FhirAuthError as e:
        return json.dumps({"error": "FHIR authentication failed", "message": str(e)}, indent=2)
    except FhirError as e:
        return json.dumps({"error": "Failed to fetch Patient resource", "message": str(e)}, indent=2)

    if not patient_resource:
        return json.dumps(
            {"error": "Patient not found", "patient_id": patient_id, "fhir_url": sharp.fhir_url},
            indent=2,
        )

    fetches = [
        _safe_fetch("conditions", fhir.search("Condition", conditions_query(patient_id))),
        _safe_fetch("medication_requests", fhir.search("MedicationRequest", medication_requests_query(patient_id))),
        _safe_fetch("lab_observations", fhir.search("Observation", lab_observations_query(patient_id, months_back=lookback_months))),
        _safe_fetch("vital_observations", fhir.search("Observation", vital_observations_query(patient_id, months_back=lookback_months))),
        _safe_fetch("allergies", fhir.search("AllergyIntolerance", allergies_query(patient_id))),
        _safe_fetch("procedures", fhir.search("Procedure", procedures_query(patient_id, months_back=lookback_months))),
        _safe_fetch("immunizations", fhir.search("Immunization", immunizations_query(patient_id))),
        _safe_fetch("encounters", fhir.search("Encounter", encounters_query(patient_id, months_back=lookback_months))),
        _safe_fetch("care_plans", fhir.search("CarePlan", care_plans_query(patient_id))),
    ]

    results = await asyncio.gather(*fetches)
    fetch_dict = dict(results)

    def parse_section(label: str, parser, resource_type: str) -> dict:
        bundle = fetch_dict.get(label, {})
        if isinstance(bundle, dict) and "_error" in bundle:
            return {
                "status": "error",
                "error_type": bundle["_error"],
                "message": bundle.get("message", ""),
                "count": 0,
                "items": [],
            }
        if not bundle:
            return {"status": "ok", "count": 0, "items": []}
        raw_resources = FhirClient.extract_resources(bundle)
        parsed_items = []
        for r in raw_resources:
            if r.get("resourceType") == resource_type:
                item = parser(r)
                if item:
                    parsed_items.append(item)
        return {
            "status": "ok",
            "count": len(parsed_items),
            "total_reported": bundle.get("total", len(parsed_items)),
            "items": parsed_items,
        }

    patient = parse_patient(patient_resource)
    parsed_conditions = parse_section(
    "conditions",
    parse_condition,
    "Condition",
)

    parsed_medications = parse_section(
        "medication_requests",
        parse_medication_request,
        "MedicationRequest",
)

    parsed_labs = parse_section(
    "lab_observations",
    parse_observation,
    "Observation",
)

    parsed_vitals = parse_section(
    "vital_observations",
    parse_observation,
    "Observation",
)

    active_conditions = [
    c for c in parsed_conditions["items"]
    if c.get("is_active")
]

    active_medications = [
    m for m in parsed_medications["items"]
    if m.get("is_active")
]
    model = {
        "_round": "3.2",
        "_message": (
            "Round 3 Chunk 2 patient model: parsed and clean. "
            "Round 4 will add system models, trajectories, and risk scores."
        ),
        "patient": patient,
        "conditions": parse_section("conditions", parse_condition, "Condition"),
        "medications": parse_section("medication_requests", parse_medication_request, "MedicationRequest"),
        "lab_observations": parse_section("lab_observations", parse_observation, "Observation"),
        "vital_observations": parse_section("vital_observations", parse_observation, "Observation"),
        "allergies": parse_section("allergies", parse_allergy, "AllergyIntolerance"),
        "procedures": parse_section("procedures", parse_procedure, "Procedure"),
        "immunizations": parse_section("immunizations", parse_immunization, "Immunization"),
        "encounters": parse_section("encounters", parse_encounter, "Encounter"),
        "parameters": {
            "model_depth": model_depth,
            "lookback_months": lookback_months,
        },
    }

    logger.info(
        "build_patient_model.complete",
        patient_id=patient_id,
        active_conditions=len([c for c in model["conditions"]["items"] if c.get("is_active")]),
        active_medications=len([m for m in model["medications"]["items"] if m.get("is_active")]),
        lab_count=model["lab_observations"]["count"],
        vital_count=model["vital_observations"]["count"],
    )

    return json.dumps(model, indent=2, default=str)