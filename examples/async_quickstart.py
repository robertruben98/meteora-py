"""Asynchronous quickstart for meteora-py.

Run with::

    python examples/async_quickstart.py
"""

import asyncio

from meteora import AsyncMeteoraClient


async def main() -> None:
    async with AsyncMeteoraClient() as client:
        # Fetch protocol metrics and the top pools page concurrently.
        stats, page = await asyncio.gather(
            client.get_protocol_metrics(),
            client.get_pools(page=1, page_size=5, sort_by="tvl:desc"),
        )
        print(f"TVL ${stats.total_tvl:,.0f} across {stats.total_pools:,} pools\n")
        print(f"Top {len(page.data)} pools by TVL:")
        for pool in page.data:
            print(f"  {pool.name:18} TVL ${pool.tvl:>14,.0f}  APY {pool.apy:8.0f}%")

        # OHLCV and volume history for the top pool, concurrently.
        top = page.data[0]
        candles, history = await asyncio.gather(
            client.get_pool_ohlcv(top.address),
            client.get_pool_volume_history(top.address),
        )
        print(f"\n{top.name}: {len(candles.data)} candles, {len(history.data)} volume buckets")


if __name__ == "__main__":
    asyncio.run(main())
