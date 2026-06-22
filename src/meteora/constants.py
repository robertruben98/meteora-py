"""Constants for the Meteora DLMM Data API: base URL and time-window windows."""

from __future__ import annotations

from typing import FrozenSet

#: Default DLMM Data API base URL. Override via ``MeteoraClient(base_url=...)``.
#: The legacy ``dlmm-api.meteora.ag`` host has been retired; this is the current
#: public endpoint (keyless, rate-limited to 30 requests/second).
DEFAULT_BASE_URL = "https://dlmm.datapi.meteora.ag"

#: Development/staging base URL, documented by Meteora alongside production.
DEV_BASE_URL = "https://dlmm.dev.metdev.io"

#: Time windows present as keys in a pool's rolling ``volume``/``fees``/
#: ``protocol_fees``/``fee_tvl_ratio`` maps. Use these to index those dicts,
#: e.g. ``pool.volume["24h"]``.
TIME_WINDOWS: FrozenSet[str] = frozenset({"30m", "1h", "2h", "4h", "12h", "24h"})
