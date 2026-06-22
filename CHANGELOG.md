# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-22

### Added

- Initial release: typed, read-only client for the Meteora DLMM Data API
  (`https://dlmm.datapi.meteora.ag`), keyless.
- Synchronous `MeteoraClient` and asynchronous `AsyncMeteoraClient`, both
  backed by `httpx` with pydantic v2 models (`extra="allow"` for
  forward-compatibility) and shipped `py.typed`.
- Endpoints covered:
  - `get_protocol_metrics()` — `GET /stats/protocol_metrics`
  - `get_pools()` — `GET /pools` (offset pagination; `sort_by`/`filter_by`)
  - `get_pool()` — `GET /pools/{address}`
  - `get_pool_groups()` — `GET /pools/groups`
  - `get_pool_ohlcv()` — `GET /pools/{address}/ohlcv`
  - `get_pool_volume_history()` — `GET /pools/{address}/volume/history`
- `MeteoraError` / `MeteoraAPIError` exception hierarchy.
- respx-mocked unit tests plus one live, opt-in integration test
  (`pytest -m integration`).

[0.1.0]: https://github.com/robertruben98/meteora-py/releases/tag/v0.1.0
