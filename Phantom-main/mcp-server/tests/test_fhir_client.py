"""
Unit tests for the FHIR client.
"""

import httpx
import pytest
import respx

from src.fhir import FhirAuthError, FhirClient, FhirHttpError


@pytest.fixture
def base_url() -> str:
    return "https://fhir.example.com/r4"


@pytest.fixture
def token() -> str:
    return "test-token-abc123"


@pytest.fixture
def client(base_url, token) -> FhirClient:
    return FhirClient(base_url=base_url, token=token)


@respx.mock
async def test_read_returns_resource_when_found(client, base_url):
    respx.get(f"{base_url}/Patient/123").mock(
        return_value=httpx.Response(
            200,
            json={"resourceType": "Patient", "id": "123", "gender": "female"},
        )
    )
    result = await client.read("Patient", "123")
    assert result is not None
    assert result["resourceType"] == "Patient"
    assert result["id"] == "123"


@respx.mock
async def test_read_returns_none_on_404(client, base_url):
    respx.get(f"{base_url}/Patient/missing").mock(
        return_value=httpx.Response(404)
    )
    result = await client.read("Patient", "missing")
    assert result is None


@respx.mock
async def test_read_raises_on_401(client, base_url):
    respx.get(f"{base_url}/Patient/123").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    with pytest.raises(FhirAuthError):
        await client.read("Patient", "123")


@respx.mock
async def test_read_raises_on_403(client, base_url):
    respx.get(f"{base_url}/Patient/123").mock(
        return_value=httpx.Response(403, text="Forbidden")
    )
    with pytest.raises(FhirAuthError):
        await client.read("Patient", "123")


@respx.mock
async def test_read_raises_on_500(client, base_url):
    respx.get(f"{base_url}/Patient/123").mock(
        return_value=httpx.Response(500, text="Internal Error")
    )
    with pytest.raises(FhirHttpError) as exc_info:
        await client.read("Patient", "123")
    assert exc_info.value.status_code == 500


@respx.mock
async def test_search_returns_bundle(client, base_url):
    respx.get(f"{base_url}/Condition").mock(
        return_value=httpx.Response(
            200,
            json={
                "resourceType": "Bundle",
                "type": "searchset",
                "total": 2,
                "entry": [
                    {"resource": {"resourceType": "Condition", "id": "c1"}},
                    {"resource": {"resourceType": "Condition", "id": "c2"}},
                ],
            },
        )
    )
    result = await client.search("Condition", {"patient": "123"})
    assert result["resourceType"] == "Bundle"
    assert len(result["entry"]) == 2


@respx.mock
async def test_search_returns_empty_bundle_on_404(client, base_url):
    respx.get(f"{base_url}/Condition").mock(
        return_value=httpx.Response(404)
    )
    result = await client.search("Condition", {"patient": "missing"})
    assert result["resourceType"] == "Bundle"
    assert result["total"] == 0
    assert result["entry"] == []


@respx.mock
async def test_search_follows_pagination(client, base_url):
    """
    Test pagination: page 1 has a 'next' link, page 2 doesn't.
    Result should combine entries from both pages.
    """
    # Track which call we're on
    call_count = {"n": 0}

    def page_responder(request):
        call_count["n"] += 1
        if call_count["n"] == 1:
            # First call: return page 1 with a 'next' link
            return httpx.Response(
                200,
                json={
                    "resourceType": "Bundle",
                    "type": "searchset",
                    "total": 4,
                    "entry": [
                        {"resource": {"resourceType": "Observation", "id": "o1"}},
                        {"resource": {"resourceType": "Observation", "id": "o2"}},
                    ],
                    "link": [
                        {
                            "relation": "next",
                            "url": f"{base_url}/Observation?_page=2",
                        }
                    ],
                },
            )
        else:
            # Subsequent calls: return page 2 with NO 'next' link
            return httpx.Response(
                200,
                json={
                    "resourceType": "Bundle",
                    "type": "searchset",
                    "total": 4,
                    "entry": [
                        {"resource": {"resourceType": "Observation", "id": "o3"}},
                        {"resource": {"resourceType": "Observation", "id": "o4"}},
                    ],
                },
            )

    # Match any URL starting with the Observation endpoint
    respx.get(url__startswith=f"{base_url}/Observation").mock(side_effect=page_responder)

    result = await client.search("Observation", {"patient": "123"})
    assert len(result["entry"]) == 4
    assert call_count["n"] == 2  # Verify exactly 2 fetches happened

def test_extract_resources_filters_operation_outcome():
    bundle = {
        "entry": [
            {"resource": {"resourceType": "Patient", "id": "1"}},
            {"resource": {"resourceType": "OperationOutcome", "id": "warn"}},
            {"resource": {"resourceType": "Condition", "id": "c1"}},
        ]
    }
    resources = FhirClient.extract_resources(bundle)
    assert len(resources) == 2
    assert all(r["resourceType"] != "OperationOutcome" for r in resources)


def test_extract_resources_handles_empty_bundle():
    bundle = {"entry": []}
    assert FhirClient.extract_resources(bundle) == []


def test_token_normalization_strips_bearer_prefix(base_url):
    client = FhirClient(base_url=base_url, token="Bearer abc123")
    assert client.token == "abc123"


def test_token_normalization_keeps_raw_token(base_url):
    client = FhirClient(base_url=base_url, token="abc123")
    assert client.token == "abc123"


def test_build_url_with_relative_path(client, base_url):
    assert client._build_url("Patient/123") == f"{base_url}/Patient/123"


def test_build_url_with_absolute_url_passes_through(client):
    absolute = "https://other.fhir.com/r4/Observation?_page=2"
    assert client._build_url(absolute) == absolute