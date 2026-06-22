"""Synchronous quickstart for meteora-py.

Run with::

    python examples/quickstart.py
"""

from meteora import MeteoraClient


def main() -> None:
    with MeteoraClient() as client:
        # Protocol-wide aggregates.
        stats = client.get_protocol_metrics()
        print(f"TVL ${stats.total_tvl:,.0f} across {stats.total_pools:,} pools")
        print(f"24h volume ${stats.volume_24h:,.0f}, 24h fees ${stats.fee_24h:,.0f}\n")

        # Top 5 pools by TVL. sort_by is a "<field>:<asc|desc>" expression.
        page = client.get_pools(page=1, page_size=5, sort_by="tvl:desc")
        print(f"Top {len(page.data)} of {page.total:,} pools by TVL:")
        for pool in page.data:
            print(
                f"  {pool.name:18} TVL ${pool.tvl:>14,.0f}  "
                f"APR {pool.apr:7.2%}  APY {pool.apy:8.0f}%"
            )

        # Drill into the first pool.
        top = page.data[0]
        pool = client.get_pool(top.address)
        print(f"\n{pool.name} @ {pool.address}")
        print(f"  {pool.token_x.symbol} price ${pool.token_x.price:,.4f}")
        print(f"  bin step {pool.pool_config.bin_step}, base fee {pool.pool_config.base_fee_pct}%")
        print(f"  24h volume ${pool.volume.get('24h', 0):,.0f}")

        # Recent OHLCV candles and volume history.
        candles = client.get_pool_ohlcv(pool.address)
        history = client.get_pool_volume_history(pool.address)
        if candles.data:
            last = candles.data[-1]
            print(f"\nLast candle ({last.timestamp_str}): close {last.close:,.4f}")
        if history.data:
            print(f"Latest volume bucket fees: ${history.data[-1].fees:,.2f}")


if __name__ == "__main__":
    main()
