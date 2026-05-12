"""
Tests for FHIR resource parsers.
"""

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


# ============================================================
# Patient tests
# ============================================================

def test_parse_patient_basic():
    resource = {
        "resourceType": "Patient",
        "id": "abc-123",
        "active": True,
        "name": [{"given": ["Maria", "Elena"], "family": "Santos"}],
        "gender": "female",
        "birthDate": "1967-03-15",
    }
    result = parse_patient(resource)
    assert result["id"] == "abc-123"
    assert result["given_name"] == "Maria Elena"
    assert result["family_name"] == "Santos"
    assert result["full_name"] == "Maria Elena Santos"
    assert result["gender"] == "female"
    assert result["birth_date"] == "1967-03-15"
    assert result["age"] is not None and result["age"] > 50


def test_parse_patient_extracts_us_core_race():
    resource = {
        "resourceType": "Patient",
        "id": "p1",
        "extension": [
            {
                "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
                "extension": [
                    {
                        "url": "ombCategory",
                        "valueCoding": {
                            "system": "urn:oid:2.16.840.1.113883.6.238",
                            "code": "2054-5",
                            "display": "Black or African American",
                        },
                    }
                ],
            }
        ],
    }
    result = parse_patient(resource)
    assert result["race"] == "Black or African American"


def test_parse_patient_handles_missing_fields():
    resource = {"resourceType": "Patient", "id": "minimal"}
    result = parse_patient(resource)
    assert result["id"] == "minimal"
    assert result["given_name"] is None
    assert result["age"] is None


def test_parse_patient_returns_empty_for_wrong_type():
    assert parse_patient({"resourceType": "Condition"}) == {}
    assert parse_patient(None) == {}


# ============================================================
# Condition tests
# ============================================================

def test_parse_condition_extracts_icd10():
    resource = {
        "resourceType": "Condition",
        "id": "c1",
        "clinicalStatus": {
            "coding": [{"code": "active", "system": "http://terminology.hl7.org/CodeSystem/condition-clinical"}]
        },
        "code": {
            "coding": [
                {"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11.9", "display": "Type 2 diabetes mellitus"},
                {"system": "http://snomed.info/sct", "code": "44054006", "display": "Diabetes mellitus type 2"},
            ]
        },
        "onsetDateTime": "2017-06-15",
    }
    result = parse_condition(resource)
    assert result["code"] == "E11.9"
    assert result["code_system"] == "http://hl7.org/fhir/sid/icd-10-cm"
    assert result["display"] == "Type 2 diabetes mellitus"
    assert result["clinical_status"] == "active"
    assert result["is_active"] is True
    assert result["onset_date"] == "2017-06-15"


def test_parse_condition_marks_inactive():
    resource = {
        "resourceType": "Condition",
        "id": "c2",
        "clinicalStatus": {"coding": [{"code": "resolved"}]},
        "code": {"text": "Resolved infection"},
    }
    result = parse_condition(resource)
    assert result["is_active"] is False


# ============================================================
# Observation tests
# ============================================================

def test_parse_observation_lab_value():
    resource = {
        "resourceType": "Observation",
        "id": "obs-1",
        "status": "final",
        "code": {
            "coding": [{"system": "http://loinc.org", "code": "2160-0", "display": "Creatinine"}]
        },
        "valueQuantity": {"value": 1.3, "unit": "mg/dL", "code": "mg/dL"},
        "effectiveDateTime": "2025-08-15T10:00:00Z",
    }
    result = parse_observation(resource)
    assert result["code"] == "2160-0"
    assert result["display"] == "Creatinine"
    assert result["value"] == 1.3
    assert result["unit"] == "mg/dL"
    assert result["effective_datetime"] == "2025-08-15T10:00:00Z"


def test_parse_observation_blood_pressure_components():
    resource = {
        "resourceType": "Observation",
        "id": "bp-1",
        "status": "final",
        "code": {"coding": [{"system": "http://loinc.org", "code": "85354-9"}]},
        "component": [
            {
                "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic"}]},
                "valueQuantity": {"value": 148, "unit": "mm[Hg]"},
            },
            {
                "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic"}]},
                "valueQuantity": {"value": 88, "unit": "mm[Hg]"},
            },
        ],
        "effectiveDateTime": "2025-11-15",
    }
    result = parse_observation(resource)
    assert len(result["components"]) == 2
    systolic = next(c for c in result["components"] if c["code"] == "8480-6")
    assert systolic["value"] == 148
    diastolic = next(c for c in result["components"] if c["code"] == "8462-4")
    assert diastolic["value"] == 88


def test_parse_observation_with_reference_range():
    resource = {
        "resourceType": "Observation",
        "id": "obs-rr",
        "status": "final",
        "code": {"coding": [{"system": "http://loinc.org", "code": "2160-0"}]},
        "valueQuantity": {"value": 1.3, "unit": "mg/dL"},
        "referenceRange": [
            {
                "low": {"value": 0.6, "unit": "mg/dL"},
                "high": {"value": 1.2, "unit": "mg/dL"},
            }
        ],
    }
    result = parse_observation(resource)
    assert result["reference_range"]["low"] == 0.6
    assert result["reference_range"]["high"] == 1.2


# ============================================================
# MedicationRequest tests
# ============================================================

def test_parse_medication_request_extracts_rxcui():
    resource = {
        "resourceType": "MedicationRequest",
        "id": "med-1",
        "status": "active",
        "intent": "order",
        "medicationCodeableConcept": {
            "coding": [
                {
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": "860974",
                    "display": "Metformin 1000 MG Oral Tablet",
                }
            ]
        },
        "authoredOn": "2025-01-15",
        "dosageInstruction": [
            {
                "text": "Take 1 tablet by mouth twice daily",
                "doseAndRate": [{"doseQuantity": {"value": 1000, "unit": "mg"}}],
                "timing": {"repeat": {"frequency": 2, "period": 1, "periodUnit": "d"}},
            }
        ],
    }
    result = parse_medication_request(resource)
    assert result["rxcui"] == "860974"
    assert result["drug_name"] == "Metformin 1000 MG Oral Tablet"
    assert result["status"] == "active"
    assert result["is_active"] is True
    assert result["dose_quantity"] == 1000
    assert result["frequency"] == 2


def test_parse_medication_request_prn():
    resource = {
        "resourceType": "MedicationRequest",
        "id": "med-prn",
        "status": "active",
        "medicationCodeableConcept": {
            "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "310965"}]
        },
        "dosageInstruction": [{"text": "As needed for pain", "asNeededBoolean": True}],
    }
    result = parse_medication_request(resource)
    assert result["as_needed"] is True


# ============================================================
# Allergy tests
# ============================================================

def test_parse_allergy_basic():
    resource = {
        "resourceType": "AllergyIntolerance",
        "id": "all-1",
        "clinicalStatus": {"coding": [{"code": "active"}]},
        "code": {
            "coding": [{"system": "http://snomed.info/sct", "code": "387406002", "display": "Sulfonamide"}]
        },
        "criticality": "low",
        "reaction": [
            {
                "manifestation": [
                    {"coding": [{"system": "http://snomed.info/sct", "code": "271807003", "display": "Rash"}]}
                ],
                "severity": "mild",
            }
        ],
    }
    result = parse_allergy(resource)
    assert result["display"] == "Sulfonamide"
    assert result["criticality"] == "low"
    assert result["is_active"] is True
    assert "Rash" in result["reactions"][0]["manifestations"]


# ============================================================
# Procedure / Immunization / Encounter tests
# ============================================================

def test_parse_procedure_basic():
    resource = {
        "resourceType": "Procedure",
        "id": "proc-1",
        "status": "completed",
        "code": {
            "coding": [{"system": "http://snomed.info/sct", "code": "415300000", "display": "Annual physical examination"}]
        },
        "performedDateTime": "2025-08-15",
    }
    result = parse_procedure(resource)
    assert result["display"] == "Annual physical examination"
    assert result["performed_datetime"] == "2025-08-15"


def test_parse_immunization_basic():
    resource = {
        "resourceType": "Immunization",
        "id": "imm-1",
        "status": "completed",
        "vaccineCode": {
            "coding": [{"system": "http://hl7.org/fhir/sid/cvx", "code": "158", "display": "Influenza"}]
        },
        "occurrenceDateTime": "2025-10-12",
    }
    result = parse_immunization(resource)
    assert result["cvx_code"] == "158"
    assert result["vaccine_name"] == "Influenza"


def test_parse_encounter_basic():
    resource = {
        "resourceType": "Encounter",
        "id": "enc-1",
        "status": "finished",
        "class": {"code": "AMB", "display": "ambulatory"},
        "type": [{"coding": [{"display": "Diabetes follow-up"}]}],
        "period": {"start": "2025-08-15T10:00:00Z", "end": "2025-08-15T10:30:00Z"},
    }
    result = parse_encounter(resource)
    assert result["class_code"] == "AMB"
    assert "Diabetes follow-up" in result["types"]
    assert result["period_start"] == "2025-08-15T10:00:00Z"


# ============================================================
# Bulk parser test
# ============================================================

def test_parse_resources_filters_wrong_type():
    resources = [
        {"resourceType": "Patient", "id": "p1", "name": [{"family": "Test"}]},
        {"resourceType": "Condition", "id": "c1", "code": {"text": "Diabetes"}, "clinicalStatus": {"coding": [{"code": "active"}]}},
        {"resourceType": "Patient", "id": "p2", "name": [{"family": "Other"}]},
    ]
    patients = parse_resources(resources, "Patient")
    conditions = parse_resources(resources, "Condition")
    assert len(patients) == 2
    assert len(conditions) == 1