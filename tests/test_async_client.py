"""Tests for the asynchronous AsyncMeteoraClient using respx (no real network)."""

import httpx
import pytest
import respx

from meteora import AsyncMeteoraClient, MeteoraAPIError
from tests import fixtures

BASE = "https://dlmm.datapi.meteora.ag"
ADDR = "5rCf1DM8LjKTw4YqhnoLcngyZYeNnQqztScTogYHAS6"


@respx.mock
async def test_get_protocol_metrics() -> None:
    route = respx.get(f"{BASE}/stats/protocol_metrics").mock(
        return_value=httpx.Response(200, json=fixtures.PROTOCOL_METRICS)
    )
    async with AsyncMeteoraClient() as client:
        metrics = await client.get_protocol_metrics()
    assert route.called
    assert metrics.total_pools == 147951


@respx.mock
async def test_get_pools_sends_params() -> None:
    route = respx.get(f"{BASE}/pools").mock(
        return_value=httpx.Response(200, json=fixtures.POOLS_PAGE)
    )
    async with AsyncMeteoraClient() as client:
        page = await client.get_pools(page=1, page_size=2, sort_by="tvl")
    request = route.calls.last.request
    assert request.url.params["sort_by"] == "tvl"
    assert page.data[0].name == "SOL-USDC"


@respx.mock
async def test_get_pool_by_address() -> None:
    respx.get(f"{BASE}/pools/{ADDR}").mock(return_value=httpx.Response(200, json=fixtures.POOL))
    async with AsyncMeteoraClient() as client:
        pool = await client.get_pool(ADDR)
    assert pool.token_y.symbol == "USDC"


@respx.mock
async def test_get_pool_groups() -> None:
    respx.get(f"{BASE}/pools/groups").mock(
        return_value=httpx.Response(200, json=fixtures.POOL_GROUPS_PAGE)
    )
    async with AsyncMeteoraClient() as client:
        page = await client.get_pool_groups()
    assert page.data[0].group_name == "SOL-USDC"


@respx.mock
async def test_get_pool_ohlcv() -> None:
    route = respx.get(f"{BASE}/pools/{ADDR}/ohlcv").mock(
        return_value=httpx.Response(200, json=fixtures.OHLCV)
    )
    async with AsyncMeteoraClient() as client:
        resp = await client.get_pool_ohlcv(ADDR, from_=1, to=2, resolution="1h")
    request = route.calls.last.request
    assert request.url.params["resolution"] == "1h"
    assert resp.data[0].close == fixtures.OHLCV["data"][0]["close"]


@respx.mock
async def test_get_pool_volume_history() -> None:
    respx.get(f"{BASE}/pools/{ADDR}/volume/history").mock(
        return_value=httpx.Response(200, json=fixtures.VOLUME_HISTORY)
    )
    async with AsyncMeteoraClient() as client:
        resp = await client.get_pool_volume_history(ADDR)
    assert resp.data[0].protocol_fees == fixtures.VOLUME_HISTORY["data"][0]["protocol_fees"]


@respx.mock
async def test_api_error_is_raised_on_404() -> None:
    respx.get(f"{BASE}/pools/bad").mock(return_value=httpx.Response(404, text="nope"))
    async with AsyncMeteoraClient() as client:
        with pytest.raises(MeteoraAPIError) as exc_info:
            await client.get_pool("bad")
    assert exc_info.value.status_code == 404


async def test_injected_async_client_is_not_closed_by_aclose() -> None:
    external = httpx.AsyncClient()
    client = AsyncMeteoraClient(client=external)
    await client.aclose()
    assert not external.is_closed
    await external.aclose()
