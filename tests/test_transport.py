"""Tests for the shared transport helpers (URL/param building, parsing)."""

import httpx
import pytest

from meteora._errors import MeteoraAPIError
from meteora._transport import build_pools_params, normalize_base_url, parse_response


def test_normalize_base_url_strips_trailing_slash() -> None:
    assert normalize_base_url("https://x.test/") == "https://x.test"
    assert normalize_base_url("https://x.test") == "https://x.test"


def test_build_pools_params_includes_only_set_values() -> None:
    params = build_pools_params(page=2, page_size=50, query=None, sort_by=None, filter_by=None)
    assert params == {"page": 2, "page_size": 50}


def test_build_pools_params_includes_optional_filters() -> None:
    params = build_pools_params(page=1, page_size=10, query="SOL", sort_by="tvl", filter_by="24h")
    assert params == {
        "page": 1,
        "page_size": 10,
        "query": "SOL",
        "sort_by": "tvl",
        "filter_by": "24h",
    }


def test_parse_response_returns_json_object() -> None:
    resp = httpx.Response(200, json={"total_pools": 5})
    assert parse_response(resp) == {"total_pools": 5}


def test_parse_response_raises_on_non_2xx_with_text_body() -> None:
    resp = httpx.Response(404, text="pool not found")
    with pytest.raises(MeteoraAPIError) as exc_info:
        parse_response(resp)
    assert exc_info.value.status_code == 404
    assert "pool not found" in exc_info.value.message


def test_parse_response_raises_on_non_2xx_with_json_message() -> None:
    resp = httpx.Response(400, json={"message": "bad address"})
    with pytest.raises(MeteoraAPIError) as exc_info:
        parse_response(resp)
    assert exc_info.value.status_code == 400
    assert "bad address" in exc_info.value.message


def test_parse_response_falls_back_to_http_status_when_no_body() -> None:
    resp = httpx.Response(500)
    with pytest.raises(MeteoraAPIError) as exc_info:
        parse_response(resp)
    assert "500" in exc_info.value.message


def test_parse_response_rejects_non_object_json() -> None:
    resp = httpx.Response(200, json=[1, 2, 3])
    with pytest.raises(MeteoraAPIError):
        parse_response(resp)
