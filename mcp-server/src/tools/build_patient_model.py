"""
Tool: build_patient_model

Round 2.7 (Reconnaissance): Fetches real FHIR data to discover what's
available at Po's FHIR endpoint. This is a TEMPORARY exploratory version
to inform Round 3's full implementation.
"""

import json
from typing import Annotated

import httpx
import structlog
from mcp.server.fastmcp import Context
from pydantic import Field

from src.sharp import SharpContextError, extract_sharp_context

logger = structlog.get_logger(__name__)


async def _fetch_fhir(url: str, token: str) -> dict | None:
    """Fetch a FHIR resource. Returns None on 404, raises on other errors."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/fhir+json"},
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "_error": f"HTTP {e.response.status_code}",
                "_body": e.response.text[:500],
            }
        except Exception as e:
            return {"_error": str(e)}


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
    """
    Reconnaissance round: Fetch and report what FHIR data exists for the
    patient in context.
    """
    try:
        sharp = extract_sharp_context(ctx)
    except SharpContextError as e:
        return json.dumps({"error": "FHIR context required", "message": str(e)})

    if not sharp.patient_id:
        return json.dumps({"error": "No patient in context"})

    patient_id = sharp.patient_id_only
    base_url = sharp.fhir_url
    token = sharp.fhir_token

    # Strip "Bearer " prefix if present (we add it ourselves)
    if token.lower().startswith("bearer "):
        token = token[7:]

    logger.info(
        "build_patient_model.recon_starting",
        patient_id=patient_id,
        fhir_url=base_url,
    )

    # Fetch all relevant FHIR resources for this patient
    resources_to_check = {
        "Patient": f"{base_url}/Patient/{patient_id}",
        "Conditions": f"{base_url}/Condition?patient={patient_id}",
        "MedicationRequests": f"{base_url}/MedicationRequest?patient={patient_id}",
        "MedicationStatements": f"{base_url}/MedicationStatement?patient={patient_id}",
        "Observations_Labs": f"{base_url}/Observation?patient={patient_id}&category=laboratory",
        "Observations_Vitals": f"{base_url}/Observation?patient={patient_id}&category=vital-signs",
        "Observations_All": f"{base_url}/Observation?patient={patient_id}&_count=20",
        "AllergyIntolerances": f"{base_url}/AllergyIntolerance?patient={patient_id}",
        "Procedures": f"{base_url}/Procedure?patient={patient_id}",
        "Immunizations": f"{base_url}/Immunization?patient={patient_id}",
        "Encounters": f"{base_url}/Encounter?patient={patient_id}",
        "CarePlans": f"{base_url}/CarePlan?patient={patient_id}",
    }

    recon_results = {}
    for label, url in resources_to_check.items():
        result = await _fetch_fhir(url, token)
        if result is None:
            recon_results[label] = {"status": "not_found"}
        elif "_error" in result:
            recon_results[label] = {"status": "error", "details": result}
        elif result.get("resourceType") == "Bundle":
            entries = result.get("entry", [])
            sample = entries[0] if entries else None
            recon_results[label] = {
                "status": "ok",
                "total_count": result.get("total", len(entries)),
                "returned_count": len(entries),
                "sample_entry": sample,
            }
        else:
            recon_results[label] = {
                "status": "ok",
                "resource_type": result.get("resourceType"),
                "data": result,
            }

    logger.info("build_patient_model.recon_complete", resource_count=len(recon_results))

    return json.dumps(
        {
            "_recon_mode": True,
            "_message": (
                "This is a temporary reconnaissance response showing what "
                "FHIR data exists for the patient in context. Use this to "
                "design the real patient model in Round 3."
            ),
            "patient_id": patient_id,
            "fhir_url": base_url,
            "resources_discovered": recon_results,
        },
        indent=2,
        default=str,
    )