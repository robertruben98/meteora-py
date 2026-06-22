"""Live integration tests against the real Meteora DLMM Data API.

Marked ``integration`` and deselected by default (see pyproject ``addopts``).
Run explicitly with::

    pytest -m integration
"""

import pytest

from meteora import MeteoraClient

pytestmark = pytest.mark.integration


def test_live_protocol_metrics() -> None:
    with MeteoraClient() as client:
        metrics = client.get_protocol_metrics()
    # The protocol has many thousands of indexed pools and a large TVL; these
    # bounds are loose enough to be stable while still proving a real response.
    assert metrics.total_pools > 1000
    assert metrics.total_tvl > 0
    assert metrics.volume_24h >= 0


def test_live_pools_page_round_trips() -> None:
    with MeteoraClient() as client:
        page = client.get_pools(page=1, page_size=5, sort_by="tvl:desc")
    assert page.current_page == 1
    assert page.page_size == 5
    assert len(page.data) == 5
    top = page.data[0]
    # Each pool has a token pair and a non-negative TVL.
    assert top.token_x.symbol
    assert top.token_y.symbol
    assert top.tvl >= 0

    # The single-pool endpoint returns the same pool by address.
    with MeteoraClient() as client:
        pool = client.get_pool(top.address)
    assert pool.address == top.address


def test_live_sort_by_requires_field_direction_form() -> None:
    # Contract discovered live: `sort_by` must be `<field>:<asc|desc>`. A bare
    # field name is rejected with HTTP 400, so callers must pass the direction.
    from meteora import MeteoraAPIError

    with MeteoraClient() as client, pytest.raises(MeteoraAPIError) as exc_info:
        client.get_pools(page=1, page_size=1, sort_by="tvl")
    assert exc_info.value.status_code == 400
