"""Pydantic models for Meteora DLMM Data API payloads.

These models use ``extra="allow"`` so that fields the API adds over time (new
metrics, fee breakdowns, tags, etc.) do not break parsing. The API already
returns snake_case JSON, so no aliasing is needed; ``populate_by_name`` is kept
on for symmetry and so models can also be built from Python keyword arguments.

Rolling time-window maps (``volume``, ``fees``, ``protocol_fees``,
``fee_tvl_ratio``) are kept as plain ``Dict[str, float]`` keyed by window
(``"30m"``, ``"1h"``, ``"2h"``, ``"4h"``, ``"12h"``, ``"24h"``) rather than a
fixed model, because the set of windows is small and may evolve.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class _Model(BaseModel):
    """Base config shared by every model: name population + forward-compat.

    ``extra="allow"`` preserves any fields Meteora adds in the future instead of
    rejecting them; ``populate_by_name=True`` lets models be built from Python
    keyword arguments as well as the API's JSON keys.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")


# --- /stats/protocol_metrics ---


class ProtocolMetrics(_Model):
    """Aggregated protocol-level metrics from ``GET /stats/protocol_metrics``."""

    total_tvl: float = Field(description="Total value locked across all pools, in USD.")
    total_volume: float = Field(description="All-time cumulative swap volume, in USD.")
    total_fees: float = Field(description="All-time cumulative fees collected, in USD.")
    total_pools: int = Field(description="Total number of indexed DLMM pools.")
    volume_24h: float = Field(description="Swap volume over the trailing 24 hours, in USD.")
    fee_24h: float = Field(description="Fees collected over the trailing 24 hours, in USD.")


# --- shared building blocks ---


class TokenInfo(_Model):
    """Metadata for one side of a pool's token pair."""

    address: str = Field(description="Token mint address (base58).")
    name: str = Field(description="Full token name, e.g. 'USD Coin'.")
    symbol: str = Field(description="Ticker symbol, e.g. 'USDC'.")
    decimals: int = Field(description="Number of decimal places the token uses.")
    is_verified: Optional[bool] = Field(
        default=None, description="Whether Meteora has verified this token."
    )
    holders: Optional[int] = Field(default=None, description="Approximate number of holders.")
    freeze_authority_disabled: Optional[bool] = Field(
        default=None, description="True if the mint's freeze authority is disabled."
    )
    total_supply: Optional[float] = Field(
        default=None, description="Total token supply (UI units)."
    )
    price: Optional[float] = Field(default=None, description="Current token price in USD.")
    market_cap: Optional[float] = Field(
        default=None, description="Approximate market capitalization in USD."
    )


class PoolConfig(_Model):
    """A DLMM pool's static fee/bin configuration."""

    bin_step: int = Field(description="Bin step in basis points; controls price granularity.")
    base_fee_pct: float = Field(description="Base swap fee, as a percentage.")
    max_fee_pct: float = Field(description="Maximum swap fee (incl. dynamic fee), as a percentage.")
    protocol_fee_pct: float = Field(
        description="Share of the fee taken by the protocol, as a percentage."
    )
    collect_fee_mode: int = Field(description="Fee collection mode flag (0 = both tokens).")


class CumulativeMetrics(_Model):
    """All-time cumulative volume and fees for a single pool."""

    volume: float = Field(description="All-time cumulative swap volume, in USD.")
    fees: float = Field(description="All-time cumulative fees collected, in USD.")


# --- /pools and /pools/{address} ---


class Pool(_Model):
    """A single DLMM pool from ``GET /pools/{address}`` (and ``/pools`` items).

    Rolling metrics (:attr:`volume`, :attr:`fees`, :attr:`protocol_fees`,
    :attr:`fee_tvl_ratio`) are dicts keyed by time window (``"30m"`` … ``"24h"``).

    Example::

        pool = client.get_pool("5rCf1DM8LjKTw4YqhnoLcngyZYeNnQqztScTogYHAS6")
        print(pool.token_x.symbol, pool.token_y.symbol)  # 'SOL' 'USDC'
        print(pool.tvl, pool.apr, pool.apy)
        print(pool.volume["24h"], pool.fees["24h"])
    """

    address: str = Field(description="Pool (LB pair) address, base58.")
    name: str = Field(description="Human-readable pair name, e.g. 'SOL-USDC'.")
    token_x: TokenInfo = Field(description="The pool's base token (token X).")
    token_y: TokenInfo = Field(description="The pool's quote token (token Y).")
    reserve_x: str = Field(description="Address of the token-X reserve vault.")
    reserve_y: str = Field(description="Address of the token-Y reserve vault.")
    token_x_amount: float = Field(description="Token-X reserve balance (UI units).")
    token_y_amount: float = Field(description="Token-Y reserve balance (UI units).")
    created_at: int = Field(description="Pool creation time as a Unix timestamp in milliseconds.")
    reward_mint_x: Optional[str] = Field(
        default=None, description="Reward mint for token X (sentinel if none)."
    )
    reward_mint_y: Optional[str] = Field(
        default=None, description="Reward mint for token Y (sentinel if none)."
    )
    pool_config: PoolConfig = Field(description="Static fee/bin configuration for the pool.")
    dynamic_fee_pct: float = Field(description="Current dynamic (variable) fee, as a percentage.")
    tvl: float = Field(description="Current total value locked in the pool, in USD.")
    current_price: float = Field(description="Current price of token X in token Y.")
    apr: float = Field(description="Estimated annual percentage rate from fees (as a fraction).")
    apy: float = Field(description="Estimated annual percentage yield (as a percentage).")
    has_farm: bool = Field(description="Whether the pool has an active farm/rewards.")
    farm_apr: float = Field(description="Farm reward APR (as a fraction); 0 if no farm.")
    farm_apy: float = Field(description="Farm reward APY (as a percentage); 0 if no farm.")
    volume: Dict[str, float] = Field(
        default_factory=dict, description="Rolling swap volume (USD) keyed by time window."
    )
    fees: Dict[str, float] = Field(
        default_factory=dict, description="Rolling fees collected (USD) keyed by time window."
    )
    protocol_fees: Dict[str, float] = Field(
        default_factory=dict, description="Rolling protocol fees (USD) keyed by time window."
    )
    fee_tvl_ratio: Dict[str, float] = Field(
        default_factory=dict, description="Rolling fee/TVL ratio keyed by time window."
    )
    cumulative_metrics: CumulativeMetrics = Field(
        description="All-time cumulative volume and fees for the pool."
    )
    is_blacklisted: Optional[bool] = Field(
        default=None, description="Whether Meteora has blacklisted this pool."
    )
    launchpad: Optional[str] = Field(
        default=None, description="Originating launchpad, if the pool was launched via one."
    )
    tags: List[str] = Field(
        default_factory=list, description="Free-form classification tags from Meteora."
    )


class PoolsPage(_Model):
    """A page of pools from ``GET /pools`` (offset pagination envelope)."""

    total: int = Field(description="Total number of pools matching the query.")
    pages: int = Field(description="Total number of pages at the current page size.")
    current_page: int = Field(description="The page number returned (1-based).")
    page_size: int = Field(description="Number of items per page.")
    data: List[Pool] = Field(default_factory=list, description="The pools on this page.")


# --- /pools/groups ---


class PoolGroup(_Model):
    """A token-pair pool group: aggregated stats across all pools for one pair."""

    lexical_order_mints: str = Field(
        description="The pair's two mints joined in lexical order (stable group key)."
    )
    group_name: str = Field(description="Human-readable pair name, e.g. 'SOL-USDC'.")
    token_x: str = Field(description="Token-X mint address.")
    token_y: str = Field(description="Token-Y mint address.")
    pool_count: int = Field(description="Number of DLMM pools for this token pair.")
    total_tvl: float = Field(description="Combined TVL across the group's pools, in USD.")
    total_volume: float = Field(description="Combined volume across the group's pools, in USD.")
    max_fee_tvl_ratio: float = Field(description="Highest fee/TVL ratio among the group's pools.")
    has_farm: bool = Field(description="Whether any pool in the group has an active farm.")


class PoolGroupsPage(_Model):
    """A page of pool groups from ``GET /pools/groups``."""

    total: int = Field(description="Total number of groups matching the query.")
    pages: int = Field(description="Total number of pages at the current page size.")
    current_page: int = Field(description="The page number returned (1-based).")
    page_size: int = Field(description="Number of items per page.")
    data: List[PoolGroup] = Field(default_factory=list, description="The groups on this page.")


# --- /pools/{address}/ohlcv ---


class OhlcvCandle(_Model):
    """A single OHLCV candle for a pool's price over one timeframe bucket."""

    timestamp: int = Field(description="Bucket start time as a Unix timestamp in seconds.")
    timestamp_str: str = Field(description="Bucket start time as an ISO-8601 string.")
    open: float = Field(description="Opening price in the bucket.")
    high: float = Field(description="Highest price in the bucket.")
    low: float = Field(description="Lowest price in the bucket.")
    close: float = Field(description="Closing price in the bucket.")
    volume: float = Field(description="Swap volume during the bucket, in USD.")


class OhlcvResponse(_Model):
    """Response of ``GET /pools/{address}/ohlcv`` — candles over a time range."""

    start_time: int = Field(description="Range start as a Unix timestamp in seconds.")
    end_time: int = Field(description="Range end as a Unix timestamp in seconds.")
    timeframe: str = Field(description="Resolution/timeframe of each candle, e.g. '24h'.")
    data: List[OhlcvCandle] = Field(default_factory=list, description="The candles in the range.")


# --- /pools/{address}/volume/history ---


class VolumeHistoryPoint(_Model):
    """A single historical bucket of volume and fees for a pool."""

    timestamp: int = Field(description="Bucket start time as a Unix timestamp in seconds.")
    timestamp_str: str = Field(description="Bucket start time as an ISO-8601 string.")
    volume: float = Field(description="Swap volume during the bucket, in USD.")
    fees: float = Field(description="Fees collected during the bucket, in USD.")
    protocol_fees: float = Field(description="Protocol fees collected during the bucket, in USD.")


class VolumeHistoryResponse(_Model):
    """Response of ``GET /pools/{address}/volume/history`` — volume/fees over time."""

    start_time: int = Field(description="Range start as a Unix timestamp in seconds.")
    end_time: int = Field(description="Range end as a Unix timestamp in seconds.")
    timeframe: str = Field(description="Resolution/timeframe of each point, e.g. '24h'.")
    data: List[VolumeHistoryPoint] = Field(
        default_factory=list, description="The volume/fee points in the range."
    )
