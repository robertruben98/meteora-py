# meteora-py

[![CI](https://github.com/robertruben98/meteora-py/actions/workflows/ci.yml/badge.svg)](https://github.com/robertruben98/meteora-py/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/meteora-py.svg)](https://pypi.org/project/meteora-py/)
[![Docs](https://img.shields.io/badge/docs-online-blue)](https://robertruben98.github.io/meteora-py/)
[![Python](https://img.shields.io/pypi/pyversions/meteora-py.svg)](https://pypi.org/project/meteora-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Typed, read-only Python client for the **[Meteora](https://www.meteora.ag) DLMM Data API** on
Solana — list liquidity pools, read per-pool metrics (TVL, volume, fees, APR/APY), browse
token-pair pool groups, and pull OHLCV candles and historical volume. Sync **and** async,
backed by [`httpx`](https://www.python-httpx.org/) with [`pydantic`](https://docs.pydantic.dev/)
v2 models.

The Meteora DLMM Data API is **public and keyless** (rate-limited to 30 requests/second). This
library covers the read endpoints; it does **not** build or sign transactions.

## Install

```bash
pip install meteora-py
```

## Quickstart

```python
from meteora import MeteoraClient

with MeteoraClient() as client:
    # Protocol-wide aggregates
    stats = client.get_protocol_metrics()
    print(f"TVL ${stats.total_tvl:,.0f} across {stats.total_pools:,} pools")

    # Page through pools (sorted server-side; sort_by is "<field>:<asc|desc>")
    page = client.get_pools(page=1, page_size=10, sort_by="tvl:desc")
    for pool in page.data:
        print(f"{pool.name:16} TVL ${pool.tvl:,.0f}  APR {pool.apr:.2%}  APY {pool.apy:.0%}")

    # A single pool by its on-chain address
    sol_usdc = client.get_pool("5rCf1DM8LjKTw4YqhnoLcngyZYeNnQqztScTogYHAS6")
    print(sol_usdc.token_x.symbol, sol_usdc.token_y.symbol, sol_usdc.current_price)

    # OHLCV candles and historical volume
    candles = client.get_pool_ohlcv(sol_usdc.address)
    history = client.get_pool_volume_history(sol_usdc.address)
    print(candles.data[-1].close, history.data[-1].fees)
```

### Async

```python
import asyncio
from meteora import AsyncMeteoraClient

async def main() -> None:
    async with AsyncMeteoraClient() as client:
        stats = await client.get_protocol_metrics()
        print(stats.total_pools)

asyncio.run(main())
```

See [`examples/`](examples/) for runnable scripts.

## Covered endpoints

Base URL: `https://dlmm.datapi.meteora.ag` (override via `MeteoraClient(base_url=...)`).

| Method | Endpoint | Client method |
|--------|----------|---------------|
| `GET` | `/stats/protocol_metrics` | `get_protocol_metrics()` |
| `GET` | `/pools` | `get_pools(page, page_size, query, sort_by, filter_by)`* |
| `GET` | `/pools/{address}` | `get_pool(address)` |
| `GET` | `/pools/groups` | `get_pool_groups(page, page_size)` |
| `GET` | `/pools/{address}/ohlcv` | `get_pool_ohlcv(address, from_, to, resolution)` |
| `GET` | `/pools/{address}/volume/history` | `get_pool_volume_history(address)` |

*`sort_by` is a `"<field>:<asc|desc>"` expression (e.g. `"tvl:desc"`); a bare field name is
rejected with HTTP 400. `filter_by` is a `"<field>:<value>"` filter expression passed through
verbatim. Both were confirmed against the live API.

All endpoints were discovered and verified live against the public API. The Meteora docs also
expose `/portfolio`, `/positions`, `/wallets`, and limit-order endpoints, plus separate DAMM v1/v2
APIs — these are out of scope for v1 and may follow in a later release.

## Error handling

Every method raises `MeteoraAPIError` (a subclass of `MeteoraError`) on a non-2xx response.
Network-level failures propagate as the underlying `httpx` exceptions.

```python
from meteora import MeteoraClient, MeteoraAPIError

with MeteoraClient() as client:
    try:
        client.get_pool("not-a-real-address")
    except MeteoraAPIError as exc:
        print(exc.status_code, exc.message)
```

Models are configured with `extra="allow"`, so fields Meteora adds over time are preserved
rather than rejected.

## Development

```bash
pip install -e ".[dev]"
ruff check . && ruff format --check .
mypy
pytest -q              # unit tests (respx-mocked, no network)
pytest -m integration  # one live test against the real API
```

## License

[MIT](LICENSE)
