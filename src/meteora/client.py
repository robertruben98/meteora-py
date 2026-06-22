"""Synchronous and asynchronous clients for the Meteora DLMM Data API."""

from __future__ import annotations

from types import TracebackType
from typing import Any, Dict, Optional, Type

import httpx

from meteora._transport import build_pools_params, normalize_base_url, parse_response
from meteora.constants import DEFAULT_BASE_URL
from meteora.models import (
    OhlcvResponse,
    Pool,
    PoolGroupsPage,
    PoolsPage,
    ProtocolMetrics,
    VolumeHistoryResponse,
)


def _ohlcv_params(
    from_: Optional[int], to: Optional[int], resolution: Optional[str]
) -> Dict[str, Any]:
    """Build the optional range params for the OHLCV endpoint."""
    params: Dict[str, Any] = {}
    if from_ is not None:
        params["from"] = from_
    if to is not None:
        params["to"] = to
    if resolution is not None:
        params["resolution"] = resolution
    return params


class _BaseClient:
    """Shared configuration for the sync/async clients."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL) -> None:
        self.base_url = normalize_base_url(base_url)


class MeteoraClient(_BaseClient):
    """Synchronous client for the Meteora DLMM Data API.

    Wraps the public, read-only DLMM endpoints (protocol metrics, pools, pool
    groups, OHLCV, volume history) with typed requests and responses. Every
    method raises :class:`MeteoraAPIError` on a non-2xx response.

    Use it as a context manager so the underlying ``httpx`` connection pool is
    closed for you; otherwise call :meth:`close` when done.

    Example::

        from meteora import MeteoraClient

        with MeteoraClient() as client:
            stats = client.get_protocol_metrics()
            print(stats.total_pools)
            page = client.get_pools(page=1, page_size=10, sort_by="tvl")
            for pool in page.data:
                print(pool.name, pool.tvl, pool.apy)
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = 30.0,
        client: Optional[httpx.Client] = None,
    ) -> None:
        """Create a synchronous client.

        Args:
            base_url: DLMM Data API base URL. Defaults to the public endpoint
                (:data:`meteora.constants.DEFAULT_BASE_URL`); a trailing slash
                is tolerated. Point this at a compatible proxy if needed.
            timeout: Per-request timeout in seconds, applied when this client
                creates its own ``httpx.Client``. Ignored if ``client`` is given.
            client: An existing ``httpx.Client`` to reuse. When supplied, the
                caller owns its lifecycle and :meth:`close` will not close it.
        """
        super().__init__(base_url)
        self._client = client or httpx.Client(timeout=timeout)
        self._owns_client = client is None

    # -- lifecycle --

    def close(self) -> None:
        """Close the underlying HTTP client.

        No-op when an external ``httpx.Client`` was injected via the
        constructor (the caller owns that client's lifecycle).
        """
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> MeteoraClient:
        """Enter the runtime context and return this client."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Exit the runtime context, closing the client via :meth:`close`."""
        self.close()

    # -- internal --

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = self._client.get(f"{self.base_url}{path}", params=params)
        return parse_response(response)

    # -- endpoints --

    def get_protocol_metrics(self) -> ProtocolMetrics:
        """Fetch aggregated protocol-level metrics across all pools.

        Calls ``GET /stats/protocol_metrics``.

        Returns:
            A :class:`meteora.models.ProtocolMetrics` with total/24h TVL, volume
            and fees, plus the total pool count.

        Raises:
            MeteoraAPIError: If the API returns an error.
        """
        return ProtocolMetrics.model_validate(self._get("/stats/protocol_metrics"))

    def get_pools(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        query: Optional[str] = None,
        sort_by: Optional[str] = None,
        filter_by: Optional[str] = None,
    ) -> PoolsPage:
        """Fetch a page of DLMM pools.

        Calls ``GET /pools`` with offset pagination.

        Args:
            page: 1-based page number to fetch.
            page_size: Number of pools per page.
            query: Optional free-text filter (e.g. a token symbol or address).
            sort_by: Optional server-side sort in ``"<field>:<asc|desc>"`` form,
                e.g. ``"tvl:desc"`` or ``"volume:asc"``. A bare field name is
                rejected by the API with HTTP 400, so the direction is required.
            filter_by: Optional server-side filter expression in
                ``"<field>:<value>"`` form (e.g. ``"has_farm:true"``). Passed
                through verbatim; the accepted fields are defined by the API.

        Returns:
            A :class:`meteora.models.PoolsPage` envelope with ``total``,
            ``pages``, ``current_page``, ``page_size`` and the ``data`` list.

        Raises:
            MeteoraAPIError: If the API returns an error.
        """
        params = build_pools_params(
            page=page,
            page_size=page_size,
            query=query,
            sort_by=sort_by,
            filter_by=filter_by,
        )
        return PoolsPage.model_validate(self._get("/pools", params=params))

    def get_pool(self, address: str) -> Pool:
        """Fetch a single pool by its on-chain address.

        Calls ``GET /pools/{address}``.

        Args:
            address: The pool (LB pair) address, base58.

        Returns:
            A :class:`meteora.models.Pool` with full metrics and token metadata.

        Raises:
            MeteoraAPIError: If the pool is unknown or the address is malformed.
        """
        return Pool.model_validate(self._get(f"/pools/{address}"))

    def get_pool_groups(self, *, page: int = 1, page_size: int = 50) -> PoolGroupsPage:
        """Fetch a page of token-pair pool groups.

        Calls ``GET /pools/groups``. Each group aggregates every DLMM pool for a
        given token pair (combined TVL/volume, pool count, best fee/TVL ratio).

        Args:
            page: 1-based page number to fetch.
            page_size: Number of groups per page.

        Returns:
            A :class:`meteora.models.PoolGroupsPage` envelope.

        Raises:
            MeteoraAPIError: If the API returns an error.
        """
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        return PoolGroupsPage.model_validate(self._get("/pools/groups", params=params))

    def get_pool_ohlcv(
        self,
        address: str,
        *,
        from_: Optional[int] = None,
        to: Optional[int] = None,
        resolution: Optional[str] = None,
    ) -> OhlcvResponse:
        """Fetch OHLCV price candles for a pool.

        Calls ``GET /pools/{address}/ohlcv``. With no range arguments the API
        returns its default window.

        Args:
            address: The pool (LB pair) address, base58.
            from_: Optional range start as a Unix timestamp in seconds (sent as
                the ``from`` query param).
            to: Optional range end as a Unix timestamp in seconds.
            resolution: Optional candle timeframe, e.g. ``"1h"`` or ``"24h"``.

        Returns:
            An :class:`meteora.models.OhlcvResponse` with the candle list.

        Raises:
            MeteoraAPIError: If the pool is unknown or the address is malformed.
        """
        params = _ohlcv_params(from_, to, resolution)
        return OhlcvResponse.model_validate(self._get(f"/pools/{address}/ohlcv", params=params))

    def get_pool_volume_history(self, address: str) -> VolumeHistoryResponse:
        """Fetch historical volume and fees for a pool.

        Calls ``GET /pools/{address}/volume/history``.

        Args:
            address: The pool (LB pair) address, base58.

        Returns:
            A :class:`meteora.models.VolumeHistoryResponse` with per-bucket
            volume, fees, and protocol fees.

        Raises:
            MeteoraAPIError: If the pool is unknown or the address is malformed.
        """
        return VolumeHistoryResponse.model_validate(self._get(f"/pools/{address}/volume/history"))


class AsyncMeteoraClient(_BaseClient):
    """Asynchronous counterpart of :class:`MeteoraClient`.

    Exposes the same endpoints as coroutines, backed by ``httpx.AsyncClient``.
    Use it as an async context manager so the connection pool is closed for you;
    otherwise call :meth:`aclose`.

    Example::

        import asyncio
        from meteora import AsyncMeteoraClient

        async def main():
            async with AsyncMeteoraClient() as client:
                stats = await client.get_protocol_metrics()
                print(stats.total_pools)

        asyncio.run(main())
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = 30.0,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """Create an asynchronous client.

        Args:
            base_url: DLMM Data API base URL. Defaults to the public endpoint
                (:data:`meteora.constants.DEFAULT_BASE_URL`); a trailing slash
                is tolerated.
            timeout: Per-request timeout in seconds, applied when this client
                creates its own ``httpx.AsyncClient``. Ignored if ``client`` is
                given.
            client: An existing ``httpx.AsyncClient`` to reuse. When supplied,
                the caller owns its lifecycle and :meth:`aclose` will not close
                it.
        """
        super().__init__(base_url)
        self._client = client or httpx.AsyncClient(timeout=timeout)
        self._owns_client = client is None

    # -- lifecycle --

    async def aclose(self) -> None:
        """Close the underlying async HTTP client.

        No-op when an external ``httpx.AsyncClient`` was injected via the
        constructor (the caller owns that client's lifecycle).
        """
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncMeteoraClient:
        """Enter the async runtime context and return this client."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Exit the async runtime context, closing the client via :meth:`aclose`."""
        await self.aclose()

    # -- internal --

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = await self._client.get(f"{self.base_url}{path}", params=params)
        return parse_response(response)

    # -- endpoints --

    async def get_protocol_metrics(self) -> ProtocolMetrics:
        """Fetch aggregated protocol-level metrics across all pools.

        Calls ``GET /stats/protocol_metrics``.

        Returns:
            A :class:`meteora.models.ProtocolMetrics`.

        Raises:
            MeteoraAPIError: If the API returns an error.
        """
        return ProtocolMetrics.model_validate(await self._get("/stats/protocol_metrics"))

    async def get_pools(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        query: Optional[str] = None,
        sort_by: Optional[str] = None,
        filter_by: Optional[str] = None,
    ) -> PoolsPage:
        """Fetch a page of DLMM pools.

        Async equivalent of :meth:`MeteoraClient.get_pools`; see that method for
        full argument documentation.

        Args:
            page: 1-based page number to fetch.
            page_size: Number of pools per page.
            query: Optional free-text filter.
            sort_by: Optional server-side sort field.
            filter_by: Optional time window for window-scoped metrics.

        Returns:
            A :class:`meteora.models.PoolsPage` envelope.

        Raises:
            MeteoraAPIError: If the API returns an error.
        """
        params = build_pools_params(
            page=page,
            page_size=page_size,
            query=query,
            sort_by=sort_by,
            filter_by=filter_by,
        )
        return PoolsPage.model_validate(await self._get("/pools", params=params))

    async def get_pool(self, address: str) -> Pool:
        """Fetch a single pool by its on-chain address.

        Calls ``GET /pools/{address}``.

        Args:
            address: The pool (LB pair) address, base58.

        Returns:
            A :class:`meteora.models.Pool`.

        Raises:
            MeteoraAPIError: If the pool is unknown or the address is malformed.
        """
        return Pool.model_validate(await self._get(f"/pools/{address}"))

    async def get_pool_groups(self, *, page: int = 1, page_size: int = 50) -> PoolGroupsPage:
        """Fetch a page of token-pair pool groups.

        Calls ``GET /pools/groups``.

        Args:
            page: 1-based page number to fetch.
            page_size: Number of groups per page.

        Returns:
            A :class:`meteora.models.PoolGroupsPage` envelope.

        Raises:
            MeteoraAPIError: If the API returns an error.
        """
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        return PoolGroupsPage.model_validate(await self._get("/pools/groups", params=params))

    async def get_pool_ohlcv(
        self,
        address: str,
        *,
        from_: Optional[int] = None,
        to: Optional[int] = None,
        resolution: Optional[str] = None,
    ) -> OhlcvResponse:
        """Fetch OHLCV price candles for a pool.

        Async equivalent of :meth:`MeteoraClient.get_pool_ohlcv`.

        Args:
            address: The pool (LB pair) address, base58.
            from_: Optional range start (Unix seconds; sent as ``from``).
            to: Optional range end (Unix seconds).
            resolution: Optional candle timeframe, e.g. ``"1h"`` or ``"24h"``.

        Returns:
            An :class:`meteora.models.OhlcvResponse`.

        Raises:
            MeteoraAPIError: If the pool is unknown or the address is malformed.
        """
        params = _ohlcv_params(from_, to, resolution)
        return OhlcvResponse.model_validate(
            await self._get(f"/pools/{address}/ohlcv", params=params)
        )

    async def get_pool_volume_history(self, address: str) -> VolumeHistoryResponse:
        """Fetch historical volume and fees for a pool.

        Calls ``GET /pools/{address}/volume/history``.

        Args:
            address: The pool (LB pair) address, base58.

        Returns:
            A :class:`meteora.models.VolumeHistoryResponse`.

        Raises:
            MeteoraAPIError: If the pool is unknown or the address is malformed.
        """
        return VolumeHistoryResponse.model_validate(
            await self._get(f"/pools/{address}/volume/history")
        )
