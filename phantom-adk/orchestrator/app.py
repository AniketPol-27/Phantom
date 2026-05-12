import os
from dotenv import load_dotenv

# MUST be absolutely first — before any other imports
load_dotenv(override=True)
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

print(f">>> GEMINI KEY LOADED: {os.environ.get('GOOGLE_API_KEY', 'MISSING')[:15]}...")

from a2a.types import AgentSkill
from shared.app_factory import create_a2a_app
from shared.middleware import A2ATranslateMiddleware
from .agent import root_agent

a2a_app = create_a2a_app(
    agent=root_agent,
    name="phantom_previsit_orchestrator",
    description=(
        "An advanced longitudinal clinical intelligence system that "
        "builds computational patient models, forecasts disease "
        "trajectories, compares interventions, and generates "
        "high-signal pre-visit clinician briefings."
    ),
    url=os.getenv(
        "PHANTOM_ORCHESTRATOR_URL",
        os.getenv("BASE_URL", "http://localhost:8005"),
    ),
    port=8005,
    fhir_extension_uri=(
        f"{os.getenv('PO_PLATFORM_BASE_URL', 'http://localhost:5139')}"
        "/schemas/a2a/v1/fhir-context"
    ),
    fhir_scopes=[
        {"name": "patient/Patient.rs", "required": True},
        {"name": "patient/Condition.rs", "required": True},
        {"name": "patient/MedicationRequest.rs", "required": True},
        {"name": "patient/Observation.rs", "required": True},
        {"name": "patient/Procedure.rs", "required": True},
        {"name": "patient/AllergyIntolerance.rs", "required": True},
        {"name": "patient/Encounter.rs", "required": True},
        {"name": "patient/Immunization.rs", "required": True},
    ],
    require_api_key=False,
    skills=[
        AgentSkill(
            id="previsit-intelligence",
            name="previsit-intelligence",
            description=(
                "Build computational patient models, identify longitudinal "
                "clinical priorities, forecast disease progression, compare "
                "interventions, and generate clinician pre-visit briefings."
            ),
            tags=[
                "clinical",
                "longitudinal",
                "simulation",
                "trajectory",
                "previsit",
                "orchestrator",
                "fhir",
            ],
        ),
    ],
)

a2a_app = A2ATranslateMiddleware(a2a_app)
