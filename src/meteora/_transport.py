"""Shared request-building and response/error-handling helpers.

These are VM-agnostic and used by both the sync and async clients so the
behaviour (query construction, error detection) is identical.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from meteora._errors import MeteoraAPIError


def normalize_base_url(base_url: str) -> str:
    """Strip a single trailing slash so path joins are predictable."""
    return base_url.rstrip("/")


def build_pools_params(
    *,
    page: int,
    page_size: int,
    query: Optional[str],
    sort_by: Optional[str],
    filter_by: Optional[str],
) -> Dict[str, Any]:
    """Build query params for ``GET /pools``, omitting unset optional filters."""
    params: Dict[str, Any] = {"page": page, "page_size": page_size}
    if query is not None:
        params["query"] = query
    if sort_by is not None:
        params["sort_by"] = sort_by
    if filter_by is not None:
        params["filter_by"] = filter_by
    return params


def parse_response(response: httpx.Response) -> Dict[str, Any]:
    """Return the JSON body, raising ``MeteoraAPIError`` on any error.

    The Meteora API signals errors with a non-2xx HTTP status. When the body is
    JSON, its ``message`` (or ``error``) field is surfaced; otherwise the raw
    text, falling back to ``"HTTP <status>"``. A 2xx body that is not a JSON
    object is also treated as an error, since every endpoint returns an object.
    """
    try:
        data: Any = response.json()
    except ValueError:
        if response.is_error:
            raise MeteoraAPIError(
                message=response.text or f"HTTP {response.status_code}",
                status_code=response.status_code,
            ) from None
        raise MeteoraAPIError(
            message="Response body was not valid JSON",
            status_code=response.status_code,
        ) from None

    if response.is_error:
        message: str
        if isinstance(data, dict):
            message = str(data.get("message") or data.get("error") or "") or (
                f"HTTP {response.status_code}"
            )
        else:
            message = response.text or f"HTTP {response.status_code}"
        raise MeteoraAPIError(message=message, status_code=response.status_code)

    if not isinstance(data, dict):
        raise MeteoraAPIError(
            message="Expected a JSON object response",
            status_code=response.status_code,
        )
    return data
