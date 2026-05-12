"""
FHIR resource parsers.

Each parser takes a raw FHIR resource dict and returns a clean,
flattened dict containing only the fields we care about for clinical
reasoning.

Design principles:
- Never raise on missing fields — return None or empty defaults
- Always return JSON-serializable types
- Strip nested complexity (extensions, codings, etc.) into simple values
- Preserve dates as ISO 8601 strings
"""

from datetime import datetime
from typing import Any


# ============================================================
# Coding system constants (used across parsers)
# ============================================================

CODING_SYSTEMS = {
    "loinc": "http://loinc.org",
    "snomed": "http://snomed.info/sct",
    "icd10": "http://hl7.org/fhir/sid/icd-10-cm",
    "icd10_alt": "http://hl7.org/fhir/sid/icd-10",
    "rxnorm": "http://www.nlm.nih.gov/research/umls/rxnorm",
    "cvx": "http://hl7.org/fhir/sid/cvx",
    "ucum": "http://unitsofmeasure.org",
    "us_core_race": "urn:oid:2.16.840.1.113883.6.238",
    "us_core_ethnicity": "urn:oid:2.16.840.1.113883.6.238",
}


# ============================================================
# Helpers
# ============================================================

def _safe_get(obj: dict | None, *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dicts. Returns default if any key is missing."""
    if obj is None:
        return default
    current = obj
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def _extract_coding(
    codeable_concept: dict | None,
    preferred_systems: list[str] | None = None,
) -> dict[str, str | None]:
    """
    Extract code, system, and display from a CodeableConcept.

    If preferred_systems is provided, prefers codings from those systems
    (in order). Otherwise returns the first coding found.

    Returns: {"code": str, "system": str, "display": str, "text": str}
    """
    if not codeable_concept:
        return {"code": None, "system": None, "display": None, "text": None}

    text = codeable_concept.get("text")
    codings = codeable_concept.get("coding", [])

    if not codings:
        return {"code": None, "system": None, "display": None, "text": text}

    # Try preferred systems in order
    if preferred_systems:
        for preferred in preferred_systems:
            for coding in codings:
                if coding.get("system") == preferred:
                    return {
                        "code": coding.get("code"),
                        "system": coding.get("system"),
                        "display": coding.get("display"),
                        "text": text,
                    }

    # Fall back to first coding
    first = codings[0]
    return {
        "code": first.get("code"),
        "system": first.get("system"),
        "display": first.get("display"),
        "text": text,
    }


def _extract_all_codings(codeable_concept: dict | None) -> list[dict]:
    """Extract all codings from a CodeableConcept (useful when multiple systems exist)."""
    if not codeable_concept:
        return []
    return [
        {
            "code": c.get("code"),
            "system": c.get("system"),
            "display": c.get("display"),
        }
        for c in codeable_concept.get("coding", [])
    ]


def _calculate_age(birth_date: str | None, as_of: datetime | None = None) -> int | None:
    """Calculate age in years from a birth date string."""
    if not birth_date:
        return None
    try:
        # Handle both YYYY-MM-DD and YYYY-MM-DDTHH:MM:SS formats
        birth = datetime.fromisoformat(birth_date.split("T")[0])
        ref = as_of or datetime.utcnow()
        age = ref.year - birth.year
        # Adjust if birthday hasn't occurred yet this year
        if (ref.month, ref.day) < (birth.month, birth.day):
            age -= 1
        return age
    except (ValueError, AttributeError):
        return None


def _extract_us_core_race(patient: dict) -> str | None:
    """Extract race from US Core Race extension."""
    extensions = patient.get("extension", [])
    for ext in extensions:
        if ext.get("url") == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race":
            for sub_ext in ext.get("extension", []):
                if sub_ext.get("url") == "ombCategory":
                    coding = sub_ext.get("valueCoding", {})
                    return coding.get("display")
                if sub_ext.get("url") == "text":
                    return sub_ext.get("valueString")
    return None


def _extract_us_core_ethnicity(patient: dict) -> str | None:
    """Extract ethnicity from US Core Ethnicity extension."""
    extensions = patient.get("extension", [])
    for ext in extensions:
        if ext.get("url") == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity":
            for sub_ext in ext.get("extension", []):
                if sub_ext.get("url") == "ombCategory":
                    coding = sub_ext.get("valueCoding", {})
                    return coding.get("display")
                if sub_ext.get("url") == "text":
                    return sub_ext.get("valueString")
    return None


# ============================================================
# Patient parser
# ============================================================

def parse_patient(resource: dict) -> dict:
    """
    Parse a FHIR Patient resource into a clean dict.

    Returns demographics ready for clinical reasoning.
    """
    if not resource or resource.get("resourceType") != "Patient":
        return {}

    names = resource.get("name", [])
    primary_name = names[0] if names else {}
    given_names = primary_name.get("given", [])

    return {
        "id": resource.get("id"),
        "active": resource.get("active", True),
        "given_name": " ".join(given_names) if given_names else None,
        "family_name": primary_name.get("family"),
        "full_name": _format_full_name(primary_name),
        "gender": resource.get("gender"),
        "birth_date": resource.get("birthDate"),
        "age": _calculate_age(resource.get("birthDate")),
        "race": _extract_us_core_race(resource),
        "ethnicity": _extract_us_core_ethnicity(resource),
        "deceased": resource.get("deceasedBoolean", False),
    }


def _format_full_name(name_dict: dict) -> str | None:
    """Format a HumanName into a single string."""
    if not name_dict:
        return None
    given = " ".join(name_dict.get("given", []))
    family = name_dict.get("family", "")
    full = f"{given} {family}".strip()
    return full or None


# ============================================================
# Condition parser
# ============================================================

def parse_condition(resource: dict) -> dict:
    """
    Parse a FHIR Condition resource into a clean dict.

    Extracts ICD-10 code (preferred) or SNOMED code, plus clinical status.
    """
    if not resource or resource.get("resourceType") != "Condition":
        return {}

    code_info = _extract_coding(
        resource.get("code"),
        preferred_systems=[CODING_SYSTEMS["icd10"], CODING_SYSTEMS["icd10_alt"], CODING_SYSTEMS["snomed"]],
    )

    clinical_status = _extract_coding(resource.get("clinicalStatus"))
    verification_status = _extract_coding(resource.get("verificationStatus"))

    category_codings = []
    for cat in resource.get("category", []):
        category_codings.append(_extract_coding(cat))

    return {
        "id": resource.get("id"),
        "code": code_info["code"],
        "code_system": code_info["system"],
        "display": code_info["display"] or code_info["text"],
        "all_codings": _extract_all_codings(resource.get("code")),
        "clinical_status": clinical_status["code"] or "unknown",
        "verification_status": verification_status["code"],
        "categories": [c["code"] for c in category_codings if c["code"]],
        "onset_date": resource.get("onsetDateTime") or resource.get("onsetPeriod", {}).get("start"),
        "recorded_date": resource.get("recordedDate"),
        "is_active": clinical_status["code"] in ("active", "recurrence", "relapse"),
    }


# ============================================================
# Observation parser
# ============================================================

def parse_observation(resource: dict) -> dict:
    """
    Parse a FHIR Observation resource into a clean dict.

    Handles both single-value observations (lab results) and
    component-based observations (e.g., blood pressure with systolic/diastolic).
    """
    if not resource or resource.get("resourceType") != "Observation":
        return {}

    code_info = _extract_coding(
        resource.get("code"),
        preferred_systems=[CODING_SYSTEMS["loinc"], CODING_SYSTEMS["snomed"]],
    )

    category_codings = []
    for cat in resource.get("category", []):
        category_codings.append(_extract_coding(cat))

    parsed = {
        "id": resource.get("id"),
        "status": resource.get("status"),
        "code": code_info["code"],
        "code_system": code_info["system"],
        "display": code_info["display"] or code_info["text"],
        "all_codings": _extract_all_codings(resource.get("code")),
        "categories": [c["code"] for c in category_codings if c["code"]],
        "effective_datetime": resource.get("effectiveDateTime"),
        "issued": resource.get("issued"),
        "value": None,
        "unit": None,
        "components": [],
        "interpretation": None,
        "reference_range": None,
    }

    # Single value
    if "valueQuantity" in resource:
        vq = resource["valueQuantity"]
        parsed["value"] = vq.get("value")
        parsed["unit"] = vq.get("unit") or vq.get("code")

    elif "valueString" in resource:
        parsed["value"] = resource["valueString"]

    elif "valueCodeableConcept" in resource:
        coding = _extract_coding(resource["valueCodeableConcept"])
        parsed["value"] = coding["display"] or coding["code"]

    elif "valueBoolean" in resource:
        parsed["value"] = resource["valueBoolean"]

    elif "valueInteger" in resource:
        parsed["value"] = resource["valueInteger"]

    # Component-based (e.g., blood pressure)
    components = resource.get("component", [])
    for comp in components:
        comp_code = _extract_coding(
            comp.get("code"),
            preferred_systems=[CODING_SYSTEMS["loinc"]],
        )
        comp_value = None
        comp_unit = None
        if "valueQuantity" in comp:
            cvq = comp["valueQuantity"]
            comp_value = cvq.get("value")
            comp_unit = cvq.get("unit") or cvq.get("code")

        parsed["components"].append({
            "code": comp_code["code"],
            "display": comp_code["display"],
            "value": comp_value,
            "unit": comp_unit,
        })

    # Interpretation (e.g., H, L, N for high/low/normal)
    interpretations = resource.get("interpretation", [])
    if interpretations:
        interp_coding = _extract_coding(interpretations[0])
        parsed["interpretation"] = interp_coding["code"]

    # Reference range
    ref_ranges = resource.get("referenceRange", [])
    if ref_ranges:
        rr = ref_ranges[0]
        parsed["reference_range"] = {
            "low": _safe_get(rr, "low", "value"),
            "high": _safe_get(rr, "high", "value"),
            "unit": _safe_get(rr, "low", "unit") or _safe_get(rr, "high", "unit"),
        }

    return parsed


# ============================================================
# MedicationRequest parser
# ============================================================

def parse_medication_request(resource: dict) -> dict:
    """
    Parse a FHIR MedicationRequest resource into a clean dict.

    Extracts drug RxCUI, name, dosage, frequency, status.
    """
    if not resource or resource.get("resourceType") != "MedicationRequest":
        return {}

    # Medication can be either inline (medicationCodeableConcept) or referenced
    med_concept = resource.get("medicationCodeableConcept")
    med_info = _extract_coding(
        med_concept,
        preferred_systems=[CODING_SYSTEMS["rxnorm"]],
    )

    dosage_instructions = resource.get("dosageInstruction", [])
    dosage_text = None
    dose_quantity = None
    dose_unit = None
    frequency = None
    period_unit = None
    as_needed = False
    route = None

    if dosage_instructions:
        di = dosage_instructions[0]
        dosage_text = di.get("text")
        as_needed = di.get("asNeededBoolean", False)

        # Route
        route_info = _extract_coding(di.get("route"))
        route = route_info["display"] or route_info["code"]

        # Dose
        dose_and_rate = di.get("doseAndRate", [])
        if dose_and_rate:
            dose_q = dose_and_rate[0].get("doseQuantity", {})
            dose_quantity = dose_q.get("value")
            dose_unit = dose_q.get("unit") or dose_q.get("code")

        # Frequency from timing
        timing = di.get("timing", {})
        repeat = timing.get("repeat", {})
        frequency = repeat.get("frequency")
        period = repeat.get("period")
        period_unit = repeat.get("periodUnit")

    return {
        "id": resource.get("id"),
        "status": resource.get("status"),
        "intent": resource.get("intent"),
        "rxcui": med_info["code"] if med_info["system"] == CODING_SYSTEMS["rxnorm"] else None,
        "drug_name": med_info["display"] or med_info["text"],
        "all_medication_codings": _extract_all_codings(med_concept),
        "dosage_text": dosage_text,
        "dose_quantity": dose_quantity,
        "dose_unit": dose_unit,
        "frequency": frequency,
        "period_unit": period_unit,
        "as_needed": as_needed,
        "route": route,
        "authored_on": resource.get("authoredOn"),
        "is_active": resource.get("status") == "active",
    }


# ============================================================
# AllergyIntolerance parser
# ============================================================

def parse_allergy(resource: dict) -> dict:
    """Parse a FHIR AllergyIntolerance resource into a clean dict."""
    if not resource or resource.get("resourceType") != "AllergyIntolerance":
        return {}

    code_info = _extract_coding(
        resource.get("code"),
        preferred_systems=[CODING_SYSTEMS["snomed"], CODING_SYSTEMS["rxnorm"]],
    )

    clinical_status = _extract_coding(resource.get("clinicalStatus"))
    verification_status = _extract_coding(resource.get("verificationStatus"))

    reactions = []
    for rxn in resource.get("reaction", []):
        manifestations = []
        for m in rxn.get("manifestation", []):
            m_info = _extract_coding(m)
            if m_info["display"] or m_info["code"]:
                manifestations.append(m_info["display"] or m_info["code"])

        reactions.append({
            "manifestations": manifestations,
            "severity": rxn.get("severity"),
        })

    return {
        "id": resource.get("id"),
        "code": code_info["code"],
        "display": code_info["display"] or code_info["text"],
        "type": resource.get("type"),
        "category": resource.get("category", []),
        "criticality": resource.get("criticality"),
        "clinical_status": clinical_status["code"],
        "verification_status": verification_status["code"],
        "reactions": reactions,
        "is_active": clinical_status["code"] == "active",
    }


# ============================================================
# Procedure parser
# ============================================================

def parse_procedure(resource: dict) -> dict:
    """Parse a FHIR Procedure resource into a clean dict."""
    if not resource or resource.get("resourceType") != "Procedure":
        return {}

    code_info = _extract_coding(
        resource.get("code"),
        preferred_systems=[CODING_SYSTEMS["snomed"], CODING_SYSTEMS["icd10"]],
    )

    return {
        "id": resource.get("id"),
        "status": resource.get("status"),
        "code": code_info["code"],
        "display": code_info["display"] or code_info["text"],
        "performed_datetime": (
            resource.get("performedDateTime")
            or _safe_get(resource, "performedPeriod", "start")
        ),
    }


# ============================================================
# Immunization parser
# ============================================================

def parse_immunization(resource: dict) -> dict:
    """Parse a FHIR Immunization resource into a clean dict."""
    if not resource or resource.get("resourceType") != "Immunization":
        return {}

    vaccine_info = _extract_coding(
        resource.get("vaccineCode"),
        preferred_systems=[CODING_SYSTEMS["cvx"]],
    )

    return {
        "id": resource.get("id"),
        "status": resource.get("status"),
        "cvx_code": vaccine_info["code"] if vaccine_info["system"] == CODING_SYSTEMS["cvx"] else None,
        "vaccine_name": vaccine_info["display"] or vaccine_info["text"],
        "occurrence_datetime": resource.get("occurrenceDateTime"),
    }


# ============================================================
# Encounter parser
# ============================================================

def parse_encounter(resource: dict) -> dict:
    """Parse a FHIR Encounter resource into a clean dict."""
    if not resource or resource.get("resourceType") != "Encounter":
        return {}

    types = []
    for t in resource.get("type", []):
        t_info = _extract_coding(t)
        if t_info["display"] or t_info["code"]:
            types.append(t_info["display"] or t_info["code"])

    class_info = resource.get("class", {})

    period = resource.get("period", {})

    return {
        "id": resource.get("id"),
        "status": resource.get("status"),
        "class_code": class_info.get("code") if isinstance(class_info, dict) else None,
        "class_display": class_info.get("display") if isinstance(class_info, dict) else None,
        "types": types,
        "period_start": period.get("start"),
        "period_end": period.get("end"),
    }


# ============================================================
# Bulk parsing helpers
# ============================================================

def parse_resources(resources: list[dict], resource_type: str) -> list[dict]:
    """
    Parse a list of resources using the appropriate parser.

    Filters out resources of the wrong type.
    """
    parsers = {
        "Patient": parse_patient,
        "Condition": parse_condition,
        "Observation": parse_observation,
        "MedicationRequest": parse_medication_request,
        "AllergyIntolerance": parse_allergy,
        "Procedure": parse_procedure,
        "Immunization": parse_immunization,
        "Encounter": parse_encounter,
    }

    parser = parsers.get(resource_type)
    if not parser:
        return []

    parsed = []
    for r in resources:
        if r.get("resourceType") == resource_type:
            result = parser(r)
            if result:
                parsed.append(result)

    return parsed