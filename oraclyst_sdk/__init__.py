"""
Oraclyst Python SDK

Production-grade SDK for the Oraclyst prediction market aggregation platform.
Provides both synchronous and asynchronous clients for accessing markets across
Polymarket, Kalshi, and Limitless.

Example usage:
    # Synchronous
    from oraclyst_sdk import OraclystClient
    
    client = OraclystClient()
    markets = client.list_markets(limit=10)
    for market in markets.data:
        print(f"{market.title}: {market.outcomes[0].price}")
    
    # Asynchronous
    from oraclyst_sdk import AsyncOraclystClient
    
    async with AsyncOraclystClient() as client:
        markets = await client.list_markets(limit=10)
        market = await client.get_market("pm-123456")
"""

from oraclyst_sdk.version import __version__
from oraclyst_sdk.config import OraclystConfig
from oraclyst_sdk.exceptions import (
    OraclystError,
    ConfigError,
    TransportError,
    ApiError,
    NotFoundError,
    RateLimitExceededError,
    ResponseValidationError,
)
from oraclyst_sdk.models import (
    Market,
    MarketOutcome,
    PricePoint,
    PriceHistory,
    TickerItem,
    OrderbookLevel,
    Orderbook,
    ApiResponse,
    PaginatedResponse,
    MarketFilters,
    MarketProvider,
    MarketStatus,
)
from oraclyst_sdk.client import OraclystClient, AsyncOraclystClient

__all__ = [
    "__version__",
    "OraclystConfig",
    "OraclystClient",
    "AsyncOraclystClient",
    "OraclystError",
    "ConfigError",
    "TransportError",
    "ApiError",
    "NotFoundError",
    "RateLimitExceededError",
    "ResponseValidationError",
    "Market",
    "MarketOutcome",
    "PricePoint",
    "PriceHistory",
    "TickerItem",
    "OrderbookLevel",
    "Orderbook",
    "ApiResponse",
    "PaginatedResponse",
    "MarketFilters",
    "MarketProvider",
    "MarketStatus",
]
