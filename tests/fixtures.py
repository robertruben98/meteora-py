"""Captured real responses from the Meteora DLMM Data API (trimmed).

These are real payloads recorded live from ``https://dlmm.datapi.meteora.ag`` on
2026-06-22 and used both as model-parsing fixtures and as respx mock bodies, so
the models are validated against shapes the API actually returns.
"""

from typing import Any, Dict

PROTOCOL_METRICS: Dict[str, Any] = {
    "total_tvl": 209472305.73381257,
    "volume_24h": 146220201.57717612,
    "fee_24h": 363143.9242516719,
    "total_volume": 288290667660.7318,
    "total_fees": 1378823544.2878668,
    "total_pools": 147951,
}

_SOL_USDC_POOL: Dict[str, Any] = {
    "address": "5rCf1DM8LjKTw4YqhnoLcngyZYeNnQqztScTogYHAS6",
    "name": "SOL-USDC",
    "token_x": {
        "address": "So11111111111111111111111111111111111111112",
        "name": "Wrapped SOL",
        "symbol": "SOL",
        "decimals": 9,
        "is_verified": True,
        "holders": 3820662,
        "freeze_authority_disabled": True,
        "total_supply": 628949592.3543687,
        "price": 73.88272218322214,
        "market_cap": 42882141324.79753,
    },
    "token_y": {
        "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "name": "USD Coin",
        "symbol": "USDC",
        "decimals": 6,
        "is_verified": True,
        "holders": 5248202,
        "freeze_authority_disabled": False,
        "total_supply": 8199879969.623353,
        "price": 0.9995605671738208,
        "market_cap": 8196276673.193971,
    },
    "reserve_x": "EYj9xKw6ZszwpyNibHY7JD5o3QgTVrSdcBp1fMJhrR9o",
    "reserve_y": "CoaxzEh8p5YyGLcj36Eo3cUThVJxeKCs7qvLAGDYwBcz",
    "token_x_amount": 24946.917924742,
    "token_y_amount": 1454181.4536120002,
    "created_at": 1711766862000,
    "reward_mint_x": "11111111111111111111111111111111",
    "reward_mint_y": "11111111111111111111111111111111",
    "pool_config": {
        "bin_step": 4,
        "base_fee_pct": 0.04,
        "max_fee_pct": 0.0,
        "protocol_fee_pct": 5.0,
        "collect_fee_mode": 0,
    },
    "dynamic_fee_pct": 0.00005260000000000001,
    "tvl": 3296242.159947854,
    "current_price": 73.92685660103511,
    "apr": 0.34802392826643924,
    "apy": 255.4029397901615,
    "has_farm": False,
    "farm_apr": 0.0,
    "farm_apy": 0.0,
    "volume": {
        "30m": 529812.63,
        "1h": 840731.07,
        "2h": 1755731.24,
        "4h": 3637694.84,
        "12h": 17220277.93,
        "24h": 29584520.96,
    },
    "fees": {
        "30m": 194.83,
        "1h": 307.87,
        "2h": 648.33,
        "4h": 1356.34,
        "12h": 6860.35,
        "24h": 11471.71,
    },
    "protocol_fees": {
        "30m": 21.55,
        "1h": 33.97,
        "2h": 71.67,
        "4h": 150.0,
        "12h": 759.99,
        "24h": 1269.84,
    },
    "fee_tvl_ratio": {
        "30m": 0.0059,
        "1h": 0.0093,
        "2h": 0.0196,
        "4h": 0.0411,
        "12h": 0.2081,
        "24h": 0.3480,
    },
    "cumulative_metrics": {"volume": 22426869412.36, "fees": 9958047.82},
    "is_blacklisted": False,
    "launchpad": None,
    "tags": [],
}

POOL: Dict[str, Any] = _SOL_USDC_POOL

POOLS_PAGE: Dict[str, Any] = {
    "total": 114955,
    "pages": 57478,
    "current_page": 1,
    "page_size": 2,
    "data": [_SOL_USDC_POOL],
}

POOL_GROUPS_PAGE: Dict[str, Any] = {
    "total": 51194,
    "pages": 51194,
    "current_page": 1,
    "page_size": 1,
    "data": [
        {
            "lexical_order_mints": (
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v-"
                "So11111111111111111111111111111111111111112"
            ),
            "group_name": "SOL-USDC",
            "token_x": "So11111111111111111111111111111111111111112",
            "token_y": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "pool_count": 123,
            "total_tvl": 10742021.948,
            "total_volume": 46635477.686,
            "max_fee_tvl_ratio": 0.470780232795,
            "has_farm": False,
        }
    ],
}

OHLCV: Dict[str, Any] = {
    "start_time": 1781308800,
    "end_time": 1782086400,
    "timeframe": "24h",
    "data": [
        {
            "timestamp": 1781308800,
            "timestamp_str": "2026-06-13T00:00:00+00:00",
            "open": 66.78620148860574,
            "high": 69.51124213280988,
            "low": 66.59949896793648,
            "close": 68.90234803537834,
            "volume": 16438602.686150568,
        }
    ],
}

VOLUME_HISTORY: Dict[str, Any] = {
    "start_time": 1781308800,
    "end_time": 1782086400,
    "timeframe": "24h",
    "data": [
        {
            "timestamp": 1781308800,
            "timestamp_str": "2026-06-13T00:00:00+00:00",
            "volume": 16438602.686150584,
            "fees": 6211.48363399654,
            "protocol_fees": 724.5565340168054,
        }
    ],
}
