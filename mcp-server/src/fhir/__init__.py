"""FHIR client and queries for the Phantom MCP server."""

from src.fhir.client import (
    FhirAuthError,
    FhirClient,
    FhirError,
    FhirHttpError,
)
from src.fhir.queries import (
    allergies_query,
    care_plans_query,
    conditions_query,
    encounters_query,
    immunizations_query,
    lab_observations_query,
    medication_requests_query,
    medication_statements_query,
    observations_query,
    procedures_query,
    vital_observations_query,
)

__all__ = [
    "FhirClient",
    "FhirError",
    "FhirAuthError",
    "FhirHttpError",
    "conditions_query",
    "medication_requests_query",
    "medication_statements_query",
    "observations_query",
    "lab_observations_query",
    "vital_observations_query",
    "allergies_query",
    "procedures_query",
    "immunizations_query",
    "encounters_query",
    "care_plans_query",
]