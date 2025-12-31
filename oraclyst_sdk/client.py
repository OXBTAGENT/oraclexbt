"""Main client classes for the Oraclyst SDK."""

from __future__ import annotations

import os
import logging
from typing import Any, AsyncIterator, Iterator, Optional

from oraclyst_sdk.config import OraclystConfig
from oraclyst_sdk.exceptions import ConfigError, ResponseValidationError
from oraclyst_sdk.http.sync_client import SyncTransport
from oraclyst_sdk.http.async_client import AsyncTransport
from oraclyst_sdk.models import (
    ApiResponse,
    Market,
    MarketFilters,
    Orderbook,
    PaginatedResponse,
    PriceHistory,
    TickerItem,
)
from oraclyst_sdk.models.history import TimeRange

logger = logging.getLogger("oraclyst_sdk")


class OraclystClient:
    """
    Synchronous client for the Oraclyst API.
    
    Provides methods for accessing prediction markets, price history,
    ticker data, and orderbooks across Polymarket, Kalshi, and Limitless.
    
    Example:
        # Using default configuration
        client = OraclystClient()
        
        # List markets with filters
        markets = client.list_markets(
            limit=20,
            provider="polymarket",
            category="Politics"
        )
        
        # Get market details
        market = client.get_market("pm-123456")
        
        # Get price history
        history = client.get_price_history("pm-123456", range="1h")
        
        # Always close when done
        client.close()
        
        # Or use as context manager
        with OraclystClient() as client:
            markets = client.list_markets()
    
    Security Note:
        API keys should be provided via environment variables (ORACLYST_API_KEY)
        rather than hardcoded in your application code.
    """
    
    def __init__(
        self,
        config: Optional[OraclystConfig] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the Oraclyst client.
        
        Args:
            config: Optional configuration object. If not provided,
                    uses default config with environment variable overrides.
            base_url: Optional base URL override.
        """
        if config is None:
            config = OraclystConfig.from_env()
        
        if base_url:
            config = config.with_base_url(base_url)
        
        self.config = config
        self._transport = SyncTransport(config)
    
    def list_markets(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[MarketFilters] = None,
        **kwargs: Any,
    ) -> PaginatedResponse[Market]:
        """
        List markets with optional filtering and pagination.
        
        Args:
            limit: Maximum number of markets to return (default 100).
            offset: Number of markets to skip (for pagination).
            filters: Optional MarketFilters object.
            **kwargs: Additional filter parameters (provider, category, search, etc.)
        
        Returns:
            PaginatedResponse containing list of Market objects.
        
        Example:
            # Get first page of markets
            result = client.list_markets(limit=20)
            
            # Filter by provider
            result = client.list_markets(provider="kalshi")
            
            # Search with filters
            result = client.list_markets(
                search="bitcoin",
                category="Crypto",
                sort_by="volume"
            )
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        
        if filters:
            params.update(filters.to_query_params())
        
        for key, value in kwargs.items():
            if key == "sort_by":
                params["sortBy"] = value
            elif key == "sort_order":
                params["sortOrder"] = value
            elif value is not None:
                params[key] = value
        
        data = self._transport.get("/api/v1/markets", params)
        
        try:
            markets = [Market.model_validate(m) for m in data.get("data", [])]
            return PaginatedResponse(
                success=data.get("success", True),
                data=markets,
                meta=data.get("meta", {}),
                timestamp=data.get("timestamp"),
            )
        except Exception as e:
            raise ResponseValidationError(
                f"Failed to parse markets response: {e}",
                raw_data=data,
            ) from e
    
    def iter_all_markets(
        self,
        page_size: int = 100,
        filters: Optional[MarketFilters] = None,
        **kwargs: Any,
    ) -> Iterator[Market]:
        """
        Iterate through all markets with automatic pagination.
        
        Args:
            page_size: Number of markets per page (default 100).
            filters: Optional MarketFilters object.
            **kwargs: Additional filter parameters.
        
        Yields:
            Market objects one at a time.
        
        Example:
            for market in client.iter_all_markets(page_size=50):
                print(f"{market.title}: {market.yes_price}")
        """
        offset = 0
        while True:
            result = self.list_markets(
                limit=page_size,
                offset=offset,
                filters=filters,
                **kwargs,
            )
            
            for market in result.data:
                yield market
            
            if not result.meta.has_more:
                break
            
            offset += page_size
    
    def get_market(self, market_id: str) -> Market:
        """
        Get details for a specific market.
        
        Args:
            market_id: The market ID (e.g., "pm-123456", "ks-ABCD").
        
        Returns:
            Market object with full details.
        
        Raises:
            NotFoundError: If the market doesn't exist.
        
        Example:
            market = client.get_market("pm-551963")
            print(f"Title: {market.title}")
            print(f"Yes Price: {market.yes_price}")
        """
        data = self._transport.get(f"/api/v1/markets/{market_id}")
        
        try:
            return Market.model_validate(data.get("data", {}))
        except Exception as e:
            raise ResponseValidationError(
                f"Failed to parse market response: {e}",
                raw_data=data,
            ) from e
    
    def get_price_history(
        self,
        market_id: str,
        range: TimeRange = "1h",
    ) -> PriceHistory:
        """
        Get price history for a market.
        
        Args:
            market_id: The market ID.
            range: Time range - "1m", "5m", "1h", "4h", or "1d".
        
        Returns:
            PriceHistory object with price points.
        
        Example:
            history = client.get_price_history("pm-551963", range="4h")
            if not history.is_empty:
                change = history.price_change()
                print(f"Yes price changed by {change[0]}")
        """
        data = self._transport.get(
            f"/api/v1/markets/{market_id}/history",
            params={"range": range},
        )
        
        try:
            return PriceHistory.model_validate(data.get("data", {}))
        except Exception as e:
            raise ResponseValidationError(
                f"Failed to parse price history response: {e}",
                raw_data=data,
            ) from e
    
    def get_ticker(self) -> list[TickerItem]:
        """
        Get live ticker data for top markets.
        
        Returns:
            List of TickerItem objects.
        
        Example:
            ticker = client.get_ticker()
            for item in ticker:
                print(f"{item.event}: {item.spread}% spread")
        """
        data = self._transport.get("/api/v1/ticker")
        
        try:
            return [TickerItem.model_validate(t) for t in data.get("data", [])]
        except Exception as e:
            raise ResponseValidationError(
                f"Failed to parse ticker response: {e}",
                raw_data=data,
            ) from e
    
    def get_arb_scanner(self) -> list[TickerItem]:
        """
        Get arbitrage scanner data showing spread opportunities.
        
        Returns:
            List of TickerItem objects sorted by spread.
        
        Example:
            opportunities = client.get_arb_scanner()
            for item in opportunities[:5]:
                print(f"{item.event}: {item.spread}% spread")
        """
        data = self._transport.get("/api/v1/arb-scanner")
        
        try:
            return [TickerItem.model_validate(t) for t in data.get("data", [])]
        except Exception as e:
            raise ResponseValidationError(
                f"Failed to parse arb scanner response: {e}",
                raw_data=data,
            ) from e
    
    def get_orderbook(self, venue: str, token_id: str) -> Orderbook:
        """
        Get orderbook data for a specific token.
        
        Args:
            venue: The venue (e.g., "polymarket").
            token_id: The CLOB token ID.
        
        Returns:
            Orderbook object with bids and asks.
        
        Example:
            market = client.get_market("pm-551963")
            if market.clob_token_ids:
                orderbook = client.get_orderbook("polymarket", market.clob_token_ids[0])
                print(f"Best bid: {orderbook.best_bid.price}")
        """
        data = self._transport.get(f"/api/v1/orderbook/{venue}/{token_id}")
        
        try:
            return Orderbook.model_validate(data.get("data", {}))
        except Exception as e:
            raise ResponseValidationError(
                f"Failed to parse orderbook response: {e}",
                raw_data=data,
            ) from e
    
    def close(self) -> None:
        """Close the client and release resources."""
        self._transport.close()
    
    def __enter__(self) -> OraclystClient:
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncOraclystClient:
    """
    Asynchronous client for the Oraclyst API.
    
    Provides async/await methods for accessing prediction markets.
    Use this client in async applications for better performance.
    
    Example:
        async with AsyncOraclystClient() as client:
            markets = await client.list_markets(limit=20)
            
            # Concurrent requests
            import asyncio
            market1, market2 = await asyncio.gather(
                client.get_market("pm-123"),
                client.get_market("pm-456"),
            )
    
    Security Note:
        API keys should be provided via environment variables (ORACLYST_API_KEY)
        rather than hardcoded in your application code.
    """
    
    def __init__(
        self,
        config: Optional[OraclystConfig] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the async Oraclyst client.
        
        Args:
            config: Optional configuration object.
            base_url: Optional base URL override.
        """
        if config is None:
            config = OraclystConfig.from_env()
        
        if base_url:
            config = config.with_base_url(base_url)
        
        self.config = config
        self._transport = AsyncTransport(config)
    
    async def list_markets(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[MarketFilters] = None,
        **kwargs: Any,
    ) -> PaginatedResponse[Market]:
        """List markets with optional filtering and pagination."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        
        if filters:
            params.update(filters.to_query_params())
        
        for key, value in kwargs.items():
            if key == "sort_by":
                params["sortBy"] = value
            elif key == "sort_order":
                params["sortOrder"] = value
            elif value is not None:
                params[key] = value
        
        data = await self._transport.get("/api/v1/markets", params)
        
        try:
            markets = [Market.model_validate(m) for m in data.get("data", [])]
            return PaginatedResponse(
                success=data.get("success", True),
                data=markets,
                meta=data.get("meta", {}),
                timestamp=data.get("timestamp"),
            )
        except Exception as e:
            raise ResponseValidationError(
                f"Failed to parse markets response: {e}",
                raw_data=data,
            ) from e
    
    async def iter_all_markets(
        self,
        page_size: int = 100,
        filters: Optional[MarketFilters] = None,
        **kwargs: Any,
    ) -> AsyncIterator[Market]:
        """Iterate through all markets with automatic pagination."""
        offset = 0
        while True:
            result = await self.list_markets(
                limit=page_size,
                offset=offset,
                filters=filters,
                **kwargs,
            )
            
            for market in result.data:
                yield market
            
            if not result.meta.has_more:
                break
            
            offset += page_size
    
    async def get_market(self, market_id: str) -> Market:
        """Get details for a specific market."""
        data = await self._transport.get(f"/api/v1/markets/{market_id}")
        
        try:
            return Market.model_validate(data.get("data", {}))
        except Exception as e:
            raise ResponseValidationError(
                f"Failed to parse market response: {e}",
                raw_data=data,
            ) from e
    
    async def get_price_history(
        self,
        market_id: str,
        range: TimeRange = "1h",
    ) -> PriceHistory:
        """Get price history for a market."""
        data = await self._transport.get(
            f"/api/v1/markets/{market_id}/history",
            params={"range": range},
        )
        
        try:
            return PriceHistory.model_validate(data.get("data", {}))
        except Exception as e:
            raise ResponseValidationError(
                f"Failed to parse price history response: {e}",
                raw_data=data,
            ) from e
    
    async def get_ticker(self) -> list[TickerItem]:
        """Get live ticker data for top markets."""
        data = await self._transport.get("/api/v1/ticker")
        
        try:
            return [TickerItem.model_validate(t) for t in data.get("data", [])]
        except Exception as e:
            raise ResponseValidationError(
                f"Failed to parse ticker response: {e}",
                raw_data=data,
            ) from e
    
    async def get_arb_scanner(self) -> list[TickerItem]:
        """Get arbitrage scanner data showing spread opportunities."""
        data = await self._transport.get("/api/v1/arb-scanner")
        
        try:
            return [TickerItem.model_validate(t) for t in data.get("data", [])]
        except Exception as e:
            raise ResponseValidationError(
                f"Failed to parse arb scanner response: {e}",
                raw_data=data,
            ) from e
    
    async def get_orderbook(self, venue: str, token_id: str) -> Orderbook:
        """Get orderbook data for a specific token."""
        data = await self._transport.get(f"/api/v1/orderbook/{venue}/{token_id}")
        
        try:
            return Orderbook.model_validate(data.get("data", {}))
        except Exception as e:
            raise ResponseValidationError(
                f"Failed to parse orderbook response: {e}",
                raw_data=data,
            ) from e
    
    async def close(self) -> None:
        """Close the client and release resources."""
        await self._transport.close()
    
    async def __aenter__(self) -> AsyncOraclystClient:
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        await self.close()
