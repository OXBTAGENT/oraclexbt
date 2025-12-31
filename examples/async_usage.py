#!/usr/bin/env python3
"""
Async usage example for the Oraclyst Python SDK.

This example demonstrates how to use the asynchronous client to:
- Fetch multiple markets concurrently
- Use async iteration for pagination
"""

import asyncio
from oraclyst_sdk import AsyncOraclystClient


async def main():
    print("=" * 60)
    print("Oraclyst Python SDK - Async Usage Example")
    print("=" * 60)
    
    async with AsyncOraclystClient() as client:
        print("\n1. Fetching first 10 markets...")
        print("-" * 40)
        
        markets = await client.list_markets(limit=10)
        
        print(f"Fetched {len(markets.data)} markets")
        
        print("\n2. Fetching market details concurrently...")
        print("-" * 40)
        
        market_ids = [m.id for m in markets.data[:3]]
        
        tasks = [client.get_market(mid) for mid in market_ids]
        detailed_markets = await asyncio.gather(*tasks)
        
        for market in detailed_markets:
            print(f"  - {market.title[:50]}...")
            print(f"    Volume: {market.volume}")
        
        print("\n3. Fetching price history for multiple markets concurrently...")
        print("-" * 40)
        
        history_tasks = [client.get_price_history(mid, range="1h") for mid in market_ids]
        histories = await asyncio.gather(*history_tasks)
        
        for market_id, history in zip(market_ids, histories):
            points_count = len(history.points)
            print(f"  - {market_id}: {points_count} data points")
        
        print("\n4. Async iteration through markets (first 20)...")
        print("-" * 40)
        
        count = 0
        async for market in client.iter_all_markets(page_size=10):
            print(f"  [{count+1}] {market.title[:40]}...")
            count += 1
            if count >= 20:
                break
    
    print("\n" + "=" * 60)
    print("Async example complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
