"""FHIR client, queries, and parsers for the Phantom MCP server."""

from src.fhir.client import (
    FhirAuthError,
    FhirClient,
    FhirError,
    FhirHttpError,
)
from src.fhir.parsers import (
    parse_allergy,
    parse_condition,
    parse_encounter,
    parse_immunization,
    parse_medication_request,
    parse_observation,
    parse_patient,
    parse_procedure,
    parse_resources,
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
    # Client
    "FhirClient",
    "FhirError",
    "FhirAuthError",
    "FhirHttpError",
    # Queries
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
    # Parsers
    "parse_patient",
    "parse_condition",
    "parse_observation",
    "parse_medication_request",
    "parse_allergy",
    "parse_procedure",
    "parse_immunization",
    "parse_encounter",
    "parse_resources",
]