#!/usr/bin/env python3
"""
Basic usage example for the Oraclyst Python SDK.

This example demonstrates how to use the synchronous client to:
- List markets with filtering
- Get market details
- Fetch price history
- Access ticker data
"""

from oraclyst_sdk import OraclystClient, MarketProvider


def main():
    print("=" * 60)
    print("Oraclyst Python SDK - Basic Usage Example")
    print("=" * 60)
    
    with OraclystClient() as client:
        print("\n1. Listing top 5 markets by volume...")
        print("-" * 40)
        
        markets = client.list_markets(limit=5, sort_by="volume", sort_order="desc")
        
        print(f"Total markets available: {markets.meta.total}")
        print(f"Showing first {len(markets.data)} markets:\n")
        
        for market in markets.data:
            yes_price = market.yes_price or 0
            print(f"  [{market.source.value.upper()[:2]}] {market.title[:50]}...")
            print(f"      Yes: {yes_price:.1%} | Volume: {market.volume}")
            print()
        
        if markets.data:
            market_id = markets.data[0].id
            print(f"\n2. Getting details for market: {market_id}")
            print("-" * 40)
            
            market = client.get_market(market_id)
            print(f"  Title: {market.title}")
            print(f"  Source: {market.source.value}")
            print(f"  Status: {market.status.value}")
            print(f"  Expiry: {market.expiry_date}")
            print(f"  Volume: {market.volume}")
            print(f"  Categories: {', '.join(market.categories)}")
            print("\n  Outcomes:")
            for outcome in market.outcomes:
                print(f"    - {outcome.name}: {outcome.price:.1%}")
            
            print(f"\n3. Getting 1-hour price history for: {market_id}")
            print("-" * 40)
            
            history = client.get_price_history(market_id, range="1h")
            
            if history.is_empty:
                print("  No price history available yet.")
            else:
                print(f"  Data points: {len(history.points)}")
                if history.latest:
                    print(f"  Latest: Yes {history.latest.yes_percent:.1f}%, No {history.latest.no_percent:.1f}%")
                
                change = history.price_change()
                if change:
                    yes_change, no_change = change
                    print(f"  Change: Yes {yes_change:+.2%}, No {no_change:+.2%}")
        
        print("\n4. Getting arbitrage scanner data...")
        print("-" * 40)
        
        arb_data = client.get_arb_scanner()
        print(f"  Found {len(arb_data)} markets with spread data:\n")
        
        for item in arb_data[:5]:
            trend_symbol = {"up": "^", "down": "v", "neutral": "-"}[item.trend.value]
            print(f"  [{trend_symbol}] {item.event}")
            print(f"      Spread: {item.spread}% | Volume: {item.volume}")
            print()
    
    print("=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
