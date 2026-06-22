"""Tests for the pydantic models, validated against real captured payloads."""

from meteora.models import (
    OhlcvResponse,
    Pool,
    PoolGroupsPage,
    PoolsPage,
    ProtocolMetrics,
    VolumeHistoryResponse,
)
from tests import fixtures


def test_protocol_metrics_parses_real_payload() -> None:
    metrics = ProtocolMetrics.model_validate(fixtures.PROTOCOL_METRICS)
    assert metrics.total_pools == 147951
    assert metrics.total_tvl == fixtures.PROTOCOL_METRICS["total_tvl"]
    assert metrics.volume_24h == fixtures.PROTOCOL_METRICS["volume_24h"]


def test_pool_parses_real_payload_with_nested_tokens() -> None:
    pool = Pool.model_validate(fixtures.POOL)
    assert pool.address == "5rCf1DM8LjKTw4YqhnoLcngyZYeNnQqztScTogYHAS6"
    assert pool.name == "SOL-USDC"
    assert pool.token_x.symbol == "SOL"
    assert pool.token_y.symbol == "USDC"
    assert pool.token_x.decimals == 9
    assert pool.apr == fixtures.POOL["apr"]
    assert pool.apy == fixtures.POOL["apy"]
    assert pool.has_farm is False


def test_pool_parses_nested_config_and_rolling_windows() -> None:
    pool = Pool.model_validate(fixtures.POOL)
    assert pool.pool_config.bin_step == 4
    assert pool.pool_config.base_fee_pct == 0.04
    # Rolling time-window maps are kept as plain dicts keyed by window.
    assert pool.volume["24h"] == fixtures.POOL["volume"]["24h"]
    assert pool.fees["1h"] == fixtures.POOL["fees"]["1h"]
    assert pool.cumulative_metrics.volume == fixtures.POOL["cumulative_metrics"]["volume"]


def test_pools_page_parses_pagination_envelope() -> None:
    page = PoolsPage.model_validate(fixtures.POOLS_PAGE)
    assert page.total == 114955
    assert page.pages == 57478
    assert page.current_page == 1
    assert page.page_size == 2
    assert len(page.data) == 1
    assert page.data[0].name == "SOL-USDC"


def test_pool_groups_page_parses_real_payload() -> None:
    page = PoolGroupsPage.model_validate(fixtures.POOL_GROUPS_PAGE)
    assert page.total == 51194
    group = page.data[0]
    assert group.group_name == "SOL-USDC"
    assert group.pool_count == 123
    assert group.max_fee_tvl_ratio == fixtures.POOL_GROUPS_PAGE["data"][0]["max_fee_tvl_ratio"]


def test_ohlcv_response_parses_candles() -> None:
    resp = OhlcvResponse.model_validate(fixtures.OHLCV)
    assert resp.timeframe == "24h"
    assert resp.start_time == 1781308800
    candle = resp.data[0]
    assert candle.open == fixtures.OHLCV["data"][0]["open"]
    assert candle.close == fixtures.OHLCV["data"][0]["close"]
    assert candle.volume == fixtures.OHLCV["data"][0]["volume"]
    assert candle.timestamp_str == "2026-06-13T00:00:00+00:00"


def test_volume_history_response_parses_points() -> None:
    resp = VolumeHistoryResponse.model_validate(fixtures.VOLUME_HISTORY)
    point = resp.data[0]
    assert point.volume == fixtures.VOLUME_HISTORY["data"][0]["volume"]
    assert point.fees == fixtures.VOLUME_HISTORY["data"][0]["fees"]
    assert point.protocol_fees == fixtures.VOLUME_HISTORY["data"][0]["protocol_fees"]


def test_models_preserve_unknown_fields() -> None:
    # extra="allow" keeps forward-compatibility: a field the API adds later is
    # retained on the model rather than dropped or rejected.
    payload = dict(fixtures.PROTOCOL_METRICS, brand_new_field="kept")
    metrics = ProtocolMetrics.model_validate(payload)
    assert metrics.brand_new_field == "kept"  # type: ignore[attr-defined]
