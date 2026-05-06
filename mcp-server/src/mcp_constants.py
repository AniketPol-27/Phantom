"""
Constants used by the Phantom MCP server.

Header names match the SHARP-on-MCP specification and the Prompt Opinion
platform's conventions exactly. HTTP headers are case-insensitive but we
store them lowercase to match the reference implementation.
"""

# SHARP-on-MCP Headers (sent by Prompt Opinion on every tool call)
FHIR_SERVER_URL_HEADER = "x-fhir-server-url"
FHIR_ACCESS_TOKEN_HEADER = "x-fhir-access-token"
PATIENT_ID_HEADER = "x-patient-id"

# Optional headers when offline_access scope is requested
FHIR_REFRESH_TOKEN_HEADER = "x-fhir-refresh-token"
FHIR_REFRESH_URL_HEADER = "x-fhir-refresh-url"

# Prompt Opinion MCP extension key (used in initialize response capabilities)
PO_FHIR_CONTEXT_EXTENSION = "ai.promptopinion/fhir-context"

# SMART on FHIR scopes that Phantom requires.
# These determine which FHIR resources Po will request access to from the user.
PHANTOM_FHIR_SCOPES = [
    {"name": "patient/Patient.rs", "required": True},
    {"name": "patient/Condition.rs", "required": True},
    {"name": "patient/MedicationRequest.rs", "required": True},
    {"name": "patient/MedicationStatement.rs"},
    {"name": "patient/Observation.rs", "required": True},
    {"name": "patient/AllergyIntolerance.rs"},
    {"name": "patient/Procedure.rs"},
    {"name": "patient/Immunization.rs"},
    {"name": "patient/Encounter.rs"},
    {"name": "patient/CarePlan.rs"},
]