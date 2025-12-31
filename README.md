# Oraclyst Python SDK

Production-grade Python SDK for the Oraclyst prediction market aggregation platform. Access markets across Polymarket, Kalshi, and Limitless through a unified interface.

## Features

- **Unified API**: Single interface for multiple prediction market platforms
- **Type Safety**: Full Pydantic models with type hints
- **Async Support**: Both synchronous and asynchronous clients
- **Production Ready**: Automatic retries, rate limiting, and error handling
- **Pagination Helpers**: Easy iteration through large result sets

## Installation

```bash
pip install oraclyst-sdk
```

Or install from source:

```bash
cd sdk
pip install -e .
```

## Quick Start

### Synchronous Usage

```python
from oraclyst_sdk import OraclystClient

# Create client (uses environment variables for configuration)
client = OraclystClient()

# List markets
markets = client.list_markets(limit=10)
for market in markets.data:
    print(f"{market.title}: Yes {market.yes_price:.1%}")

# Get specific market
market = client.get_market("pm-551963")
print(f"Title: {market.title}")
print(f"Volume: {market.volume}")

# Get price history
history = client.get_price_history("pm-551963", range="1h")
if history.points:
    latest = history.latest
    print(f"Current: Yes {latest.yes_percent:.1f}%, No {latest.no_percent:.1f}%")

# Get ticker/arbitrage opportunities
ticker = client.get_arb_scanner()
for item in ticker[:5]:
    print(f"{item.event}: {item.spread}% spread")

# Always close when done
client.close()
```

### Context Manager (Recommended)

```python
from oraclyst_sdk import OraclystClient

with OraclystClient() as client:
    markets = client.list_markets(category="Politics", limit=20)
    for market in markets.data:
        print(market.title)
```

### Async Usage

```python
import asyncio
from oraclyst_sdk import AsyncOraclystClient

async def main():
    async with AsyncOraclystClient() as client:
        # Fetch multiple markets concurrently
        markets = await client.list_markets(limit=10)
        
        # Parallel requests
        import asyncio
        tasks = [client.get_market(m.id) for m in markets.data[:5]]
        detailed_markets = await asyncio.gather(*tasks)
        
        for market in detailed_markets:
            print(f"{market.title}: {market.volume}")

asyncio.run(main())
```

### Iterate All Markets

```python
from oraclyst_sdk import OraclystClient

with OraclystClient() as client:
    # Automatically handles pagination
    for market in client.iter_all_markets(page_size=50):
        if market.source == "polymarket":
            print(f"[PM] {market.title}")
```

## Configuration

### Environment Variables

```bash
export ORACLYST_BASE_URL="https://oraclyst.app"
export ORACLYST_TIMEOUT="30"
export ORACLYST_MAX_RETRIES="3"
export ORACLYST_API_KEY="your-api-key"  # Optional, for authenticated endpoints
```

### Programmatic Configuration

```python
from oraclyst_sdk import OraclystClient, OraclystConfig

# Custom configuration
config = OraclystConfig(
    base_url="https://oraclyst.app",
    timeout=60.0,
    max_retries=5,
)

client = OraclystClient(config=config)
```

### From Environment

```python
from oraclyst_sdk import OraclystClient, OraclystConfig

# Load from environment variables with custom prefix
config = OraclystConfig.from_env(prefix="MYAPP_ORACLYST_")
client = OraclystClient(config=config)
```

## Filtering Markets

```python
from oraclyst_sdk import OraclystClient, MarketFilters, MarketProvider

with OraclystClient() as client:
    # Using filter object
    filters = MarketFilters(
        provider=MarketProvider.POLYMARKET,
        category="Crypto",
        sort_by="volume",
        sort_order="desc",
    )
    markets = client.list_markets(filters=filters)
    
    # Or using keyword arguments
    markets = client.list_markets(
        provider="kalshi",
        search="bitcoin",
        sort_by="volume",
    )
```

## Error Handling

```python
from oraclyst_sdk import (
    OraclystClient,
    OraclystError,
    NotFoundError,
    RateLimitExceededError,
    TransportError,
)

with OraclystClient() as client:
    try:
        market = client.get_market("invalid-id")
    except NotFoundError:
        print("Market not found")
    except RateLimitExceededError as e:
        print(f"Rate limited. Retry after {e.retry_after}s")
    except TransportError as e:
        print(f"Network error: {e}")
    except OraclystError as e:
        print(f"API error: {e}")
```

## Models

### Market

```python
market = client.get_market("pm-123456")

print(market.id)           # "pm-123456"
print(market.title)        # "Will X happen?"
print(market.source)       # MarketProvider.POLYMARKET
print(market.volume)       # "$1.2M"
print(market.volume_decimal)  # Decimal("1200000")
print(market.yes_price)    # 0.65
print(market.no_price)     # 0.35
print(market.outcomes)     # [MarketOutcome(name="Yes", price=0.65), ...]
print(market.expiry_date)  # "Dec 31, 2025"
print(market.categories)   # ["Politics", "US"]
```

### PriceHistory

```python
history = client.get_price_history("pm-123456", range="4h")

print(history.range)       # "4h"
print(history.is_empty)    # False
print(history.latest)      # PricePoint(timestamp=..., yes_price=0.65, no_price=0.35)
print(history.oldest)      # PricePoint(...)

# Calculate price change
change = history.price_change()
if change:
    yes_change, no_change = change
    print(f"Yes moved {yes_change:+.1%}")
```

### Orderbook

```python
market = client.get_market("pm-123456")
if market.clob_token_ids:
    orderbook = client.get_orderbook("polymarket", market.clob_token_ids[0])
    
    print(orderbook.best_bid)      # OrderbookLevel(price=0.64, size=100)
    print(orderbook.best_ask)      # OrderbookLevel(price=0.66, size=50)
    print(orderbook.spread)        # 0.02
    print(orderbook.total_bid_size)  # 500.0
```

## API Reference

### OraclystClient / AsyncOraclystClient

| Method | Description |
|--------|-------------|
| `list_markets(limit, offset, filters, **kwargs)` | List markets with filtering |
| `iter_all_markets(page_size, filters)` | Iterate all markets (auto-pagination) |
| `get_market(market_id)` | Get single market details |
| `get_price_history(market_id, range)` | Get price history |
| `get_ticker()` | Get live ticker data |
| `get_arb_scanner()` | Get arbitrage opportunities |
| `get_orderbook(venue, token_id)` | Get orderbook data |

### Time Ranges

- `"1m"` - 1 minute
- `"5m"` - 5 minutes
- `"1h"` - 1 hour (default)
- `"4h"` - 4 hours
- `"1d"` - 1 day

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy oraclyst_sdk

# Linting
ruff check oraclyst_sdk
```

## License

MIT License - see LICENSE file for details.

## Links

- [Oraclyst Platform](https://oraclyst.app)
- [API Documentation](https://docs.oraclyst.app)
