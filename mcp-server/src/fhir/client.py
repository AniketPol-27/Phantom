"""
Authenticated FHIR R4 client for the Phantom MCP server.

Wraps httpx with FHIR-specific behaviors:
- Bearer token authentication (from SHARP context)
- Retry logic for transient failures
- 404 returns None (not an error — resource doesn't exist)
- 401/403 raises FhirAuthError (token expired or scope missing)
- Other HTTP errors raise FhirHttpError with response body
- Bundle pagination handling (auto-follows 'next' links up to a limit)
- Timeout handling
"""

import asyncio
from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)


class FhirError(Exception):
    """Base class for FHIR client errors."""

    pass


class FhirAuthError(FhirError):
    """Raised on 401/403 — token expired or insufficient scope."""

    pass


class FhirHttpError(FhirError):
    """Raised on other HTTP errors with response body for debugging."""

    def __init__(self, status_code: int, message: str, body: str = "") -> None:
        super().__init__(f"FHIR HTTP {status_code}: {message}")
        self.status_code = status_code
        self.body = body


class FhirClient:
    """
    FHIR R4 client with SHARP-aware authentication.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: float = 30.0,
        max_retries: int = 2,
        max_pages: int = 10,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = self._normalize_token(token)
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_pages = max_pages

    @staticmethod
    def _normalize_token(token: str) -> str:
        """Strip 'Bearer ' prefix if present so we always store the raw token."""
        if token.lower().startswith("bearer "):
            return token[7:]
        return token

    @property
    def _headers(self) -> dict[str, str]:
        """Standard headers for FHIR requests."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/fhir+json",
        }

    def _build_url(self, path: str) -> str:
        """
        Build a full URL from a relative path or pass through if absolute.
        """
        if path.startswith("http://") or path.startswith("https://"):
            return path
        path = path.lstrip("/")
        return f"{self.base_url}/{path}"

    async def _request(
        self,
        url: str,
        params: dict[str, str] | None = None,
        attempt: int = 0,
    ) -> dict[str, Any] | None:
        """
        Perform a single GET request with retry logic.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug("fhir.request", url=url, params=params, attempt=attempt)
                response = await client.get(url, headers=self._headers, params=params)

                if response.status_code == 404:
                    logger.debug("fhir.response.not_found", url=url)
                    return None

                if response.status_code in (401, 403):
                    logger.error(
                        "fhir.response.auth_error",
                        status=response.status_code,
                        url=url,
                    )
                    raise FhirAuthError(
                        f"FHIR auth error {response.status_code}: "
                        f"token expired or insufficient scope for {url}"
                    )

                if response.status_code >= 400:
                    body_preview = response.text[:500]
                    logger.error(
                        "fhir.response.http_error",
                        status=response.status_code,
                        url=url,
                        body_preview=body_preview,
                    )
                    raise FhirHttpError(
                        status_code=response.status_code,
                        message=f"Failed to fetch {url}",
                        body=body_preview,
                    )

                logger.debug("fhir.response.ok", url=url, status=response.status_code)
                return response.json()

        except httpx.TimeoutException as e:
            if attempt < self.max_retries:
                wait_seconds = 2**attempt
                logger.warning(
                    "fhir.timeout.retrying",
                    url=url,
                    attempt=attempt,
                    wait_seconds=wait_seconds,
                )
                await asyncio.sleep(wait_seconds)
                return await self._request(url, params, attempt + 1)
            raise FhirError(f"Timeout after {self.max_retries} retries: {url}") from e

        except httpx.RequestError as e:
            if attempt < self.max_retries:
                wait_seconds = 2**attempt
                logger.warning(
                    "fhir.transport_error.retrying",
                    url=url,
                    error=str(e),
                    attempt=attempt,
                )
                await asyncio.sleep(wait_seconds)
                return await self._request(url, params, attempt + 1)
            raise FhirError(f"Transport error for {url}: {e}") from e

    async def read(
        self,
        resource_type: str,
        resource_id: str,
    ) -> dict[str, Any] | None:
        """
        Read a single FHIR resource by type and ID.
        """
        url = self._build_url(f"{resource_type}/{resource_id}")
        return await self._request(url)

    async def search(
        self,
        resource_type: str,
        params: dict[str, str] | None = None,
        follow_pagination: bool = True,
    ) -> dict[str, Any]:
        """
        Search for FHIR resources, optionally following pagination.
        """
        url = self._build_url(resource_type)
        result = await self._request(url, params=params)

        if result is None:
            return self._empty_bundle()

        all_entries = list(result.get("entry", []))

        if follow_pagination:
            current_bundle = result
            pages_fetched = 1

            while pages_fetched < self.max_pages:
                next_link = self._get_next_link(current_bundle)
                if not next_link:
                    break

                logger.debug("fhir.pagination.fetching_next", page=pages_fetched + 1)
                next_bundle = await self._request(next_link)
                if next_bundle is None:
                    break

                all_entries.extend(next_bundle.get("entry", []))
                current_bundle = next_bundle
                pages_fetched += 1

            if pages_fetched >= self.max_pages:
                logger.warning(
                    "fhir.pagination.limit_reached",
                    max_pages=self.max_pages,
                    resource_type=resource_type,
                )

        return {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": result.get("total", len(all_entries)),
            "entry": all_entries,
        }

    @staticmethod
    def _get_next_link(bundle: dict[str, Any]) -> str | None:
        """Extract the 'next' pagination URL from a Bundle."""
        for link in bundle.get("link", []):
            if link.get("relation") == "next":
                return link.get("url")
        return None

    @staticmethod
    def _empty_bundle() -> dict[str, Any]:
        """Return an empty Bundle for cases where no resources exist."""
        return {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": 0,
            "entry": [],
        }

    @staticmethod
    def extract_resources(bundle: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract resource dicts from a Bundle's entry list.
        """
        resources = []
        for entry in bundle.get("entry", []):
            resource = entry.get("resource")
            if resource and resource.get("resourceType") != "OperationOutcome":
                resources.append(resource)
        return resources