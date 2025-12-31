"""Orderbook models for the Oraclyst SDK."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class OrderbookLevel(BaseModel):
    """A single level in the orderbook."""
    
    price: float = Field(description="Price level")
    size: float = Field(description="Size at this price level")
    
    @property
    def price_percent(self) -> float:
        """Get price as percentage (0-100)."""
        return self.price * 100
    
    @property
    def value(self) -> float:
        """Get the total value at this level (price * size)."""
        return self.price * self.size


class Orderbook(BaseModel):
    """Orderbook data for a market token."""
    
    bids: list[OrderbookLevel] = Field(description="Buy orders (bids)")
    asks: list[OrderbookLevel] = Field(description="Sell orders (asks)")
    spread: Optional[float] = Field(default=None, description="Bid-ask spread")
    mid_price: Optional[float] = Field(alias="midPrice", default=None, description="Mid price")
    timestamp: Optional[str] = Field(default=None, description="Data timestamp")
    
    model_config = {"populate_by_name": True}
    
    @property
    def best_bid(self) -> Optional[OrderbookLevel]:
        """Get the highest bid."""
        return self.bids[0] if self.bids else None
    
    @property
    def best_ask(self) -> Optional[OrderbookLevel]:
        """Get the lowest ask."""
        return self.asks[0] if self.asks else None
    
    @property
    def total_bid_size(self) -> float:
        """Calculate total size of all bids."""
        return sum(level.size for level in self.bids)
    
    @property
    def total_ask_size(self) -> float:
        """Calculate total size of all asks."""
        return sum(level.size for level in self.asks)
    
    @property
    def calculated_spread(self) -> Optional[float]:
        """Calculate spread from best bid/ask if not provided."""
        if self.spread is not None:
            return self.spread
        if self.best_bid and self.best_ask:
            return self.best_ask.price - self.best_bid.price
        return None
