"""Tests for the synchronous MeteoraClient using respx (no real network)."""

from typing import Iterator

import httpx
import pytest
import respx

from meteora import MeteoraAPIError, MeteoraClient
from tests import fixtures

BASE = "https://dlmm.datapi.meteora.ag"
ADDR = "5rCf1DM8LjKTw4YqhnoLcngyZYeNnQqztScTogYHAS6"


@pytest.fixture
def client() -> Iterator[MeteoraClient]:
    c = MeteoraClient()
    yield c
    c.close()


@respx.mock
def test_get_protocol_metrics(client: MeteoraClient) -> None:
    route = respx.get(f"{BASE}/stats/protocol_metrics").mock(
        return_value=httpx.Response(200, json=fixtures.PROTOCOL_METRICS)
    )
    metrics = client.get_protocol_metrics()
    assert route.called
    assert metrics.total_pools == 147951


@respx.mock
def test_get_pools_sends_pagination_params(client: MeteoraClient) -> None:
    route = respx.get(f"{BASE}/pools").mock(
        return_value=httpx.Response(200, json=fixtures.POOLS_PAGE)
    )
    page = client.get_pools(page=1, page_size=2, sort_by="tvl:desc", filter_by="has_farm:true")
    assert route.called
    request = route.calls.last.request
    assert request.url.params["page"] == "1"
    assert request.url.params["page_size"] == "2"
    assert request.url.params["sort_by"] == "tvl:desc"
    assert request.url.params["filter_by"] == "has_farm:true"
    assert page.data[0].name == "SOL-USDC"


@respx.mock
def test_get_pools_omits_unset_optional_params(client: MeteoraClient) -> None:
    route = respx.get(f"{BASE}/pools").mock(
        return_value=httpx.Response(200, json=fixtures.POOLS_PAGE)
    )
    client.get_pools()
    request = route.calls.last.request
    assert "query" not in request.url.params
    assert "sort_by" not in request.url.params


@respx.mock
def test_get_pool_by_address(client: MeteoraClient) -> None:
    route = respx.get(f"{BASE}/pools/{ADDR}").mock(
        return_value=httpx.Response(200, json=fixtures.POOL)
    )
    pool = client.get_pool(ADDR)
    assert route.called
    assert pool.address == ADDR
    assert pool.token_x.symbol == "SOL"


@respx.mock
def test_get_pool_groups(client: MeteoraClient) -> None:
    route = respx.get(f"{BASE}/pools/groups").mock(
        return_value=httpx.Response(200, json=fixtures.POOL_GROUPS_PAGE)
    )
    page = client.get_pool_groups(page=1, page_size=1)
    assert route.called
    assert page.data[0].group_name == "SOL-USDC"


@respx.mock
def test_get_pool_ohlcv_sends_range_params(client: MeteoraClient) -> None:
    route = respx.get(f"{BASE}/pools/{ADDR}/ohlcv").mock(
        return_value=httpx.Response(200, json=fixtures.OHLCV)
    )
    resp = client.get_pool_ohlcv(ADDR, from_=1781308800, to=1782086400, resolution="24h")
    assert route.called
    request = route.calls.last.request
    assert request.url.params["from"] == "1781308800"
    assert request.url.params["to"] == "1782086400"
    assert request.url.params["resolution"] == "24h"
    assert resp.data[0].close == fixtures.OHLCV["data"][0]["close"]


@respx.mock
def test_get_pool_ohlcv_omits_unset_params(client: MeteoraClient) -> None:
    route = respx.get(f"{BASE}/pools/{ADDR}/ohlcv").mock(
        return_value=httpx.Response(200, json=fixtures.OHLCV)
    )
    client.get_pool_ohlcv(ADDR)
    request = route.calls.last.request
    assert "from" not in request.url.params
    assert "resolution" not in request.url.params


@respx.mock
def test_get_pool_volume_history(client: MeteoraClient) -> None:
    route = respx.get(f"{BASE}/pools/{ADDR}/volume/history").mock(
        return_value=httpx.Response(200, json=fixtures.VOLUME_HISTORY)
    )
    resp = client.get_pool_volume_history(ADDR)
    assert route.called
    assert resp.data[0].fees == fixtures.VOLUME_HISTORY["data"][0]["fees"]


@respx.mock
def test_api_error_is_raised_on_404(client: MeteoraClient) -> None:
    respx.get(f"{BASE}/pools/bad").mock(return_value=httpx.Response(404, text="pool not found"))
    with pytest.raises(MeteoraAPIError) as exc_info:
        client.get_pool("bad")
    assert exc_info.value.status_code == 404


def test_client_accepts_custom_base_url() -> None:
    c = MeteoraClient(base_url="https://proxy.test/")
    assert c.base_url == "https://proxy.test"
    c.close()


def test_injected_httpx_client_is_not_closed_by_close() -> None:
    external = httpx.Client()
    c = MeteoraClient(client=external)
    c.close()
    assert not external.is_closed
    external.close()
