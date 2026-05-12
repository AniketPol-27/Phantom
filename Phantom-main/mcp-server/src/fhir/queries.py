"""
FHIR query builders for patient-scoped resource fetching.
"""

from datetime import datetime, timedelta


def _date_n_months_ago(months: int) -> str:
    """Return ISO date string for N months ago."""
    target = datetime.utcnow() - timedelta(days=months * 30)
    return target.strftime("%Y-%m-%d")


def patient_query(patient_id: str) -> dict[str, str]:
    return {"_id": patient_id}


def conditions_query(patient_id: str, active_only: bool = False) -> dict[str, str]:
    """Search for Condition resources for a patient."""
    params = {"patient": patient_id}
    if active_only:
        params["clinical-status"] = "active"
    return params


def medication_requests_query(
    patient_id: str,
    active_only: bool = True,
) -> dict[str, str]:
    """Search for MedicationRequest resources."""
    params = {"patient": patient_id}
    if active_only:
        params["status"] = "active"
    return params


def medication_statements_query(patient_id: str) -> dict[str, str]:
    """Search for MedicationStatement resources."""
    return {"patient": patient_id}


def observations_query(
    patient_id: str,
    category: str | None = None,
    code: str | None = None,
    months_back: int | None = 24,
    count: int = 100,
) -> dict[str, str]:
    """Search for Observation resources."""
    params: dict[str, str] = {
        "patient": patient_id,
        "_sort": "-date",
        "_count": str(count),
    }
    if category:
        params["category"] = category
    if code:
        params["code"] = code
    if months_back is not None:
        params["date"] = f"ge{_date_n_months_ago(months_back)}"
    return params


def lab_observations_query(
    patient_id: str,
    months_back: int = 24,
) -> dict[str, str]:
    """Convenience: laboratory observations within time window."""
    return observations_query(
        patient_id=patient_id,
        category="laboratory",
        months_back=months_back,
    )


def vital_observations_query(
    patient_id: str,
    months_back: int = 24,
) -> dict[str, str]:
    """Convenience: vital signs observations within time window."""
    return observations_query(
        patient_id=patient_id,
        category="vital-signs",
        months_back=months_back,
    )


def allergies_query(patient_id: str) -> dict[str, str]:
    """Search for AllergyIntolerance resources."""
    return {"patient": patient_id}


def procedures_query(
    patient_id: str,
    months_back: int | None = 24,
) -> dict[str, str]:
    """Search for Procedure resources."""
    params = {"patient": patient_id, "_sort": "-date"}
    if months_back is not None:
        params["date"] = f"ge{_date_n_months_ago(months_back)}"
    return params


def immunizations_query(patient_id: str) -> dict[str, str]:
    """Search for Immunization resources."""
    return {"patient": patient_id, "_sort": "-date"}


def encounters_query(
    patient_id: str,
    months_back: int = 24,
) -> dict[str, str]:
    """Search for Encounter resources within time window."""
    return {
        "patient": patient_id,
        "date": f"ge{_date_n_months_ago(months_back)}",
        "_sort": "-date",
    }


def care_plans_query(
    patient_id: str,
    active_only: bool = True,
) -> dict[str, str]:
    """Search for CarePlan resources."""
    params = {"patient": patient_id}
    if active_only:
        params["status"] = "active"
    return params