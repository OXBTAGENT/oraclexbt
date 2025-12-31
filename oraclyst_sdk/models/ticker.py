"""Ticker models for the Oraclyst SDK."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from oraclyst_sdk.models.common import MarketProvider


class TickerTrend(str, Enum):
    """Ticker trend direction."""
    
    UP = "up"
    DOWN = "down"
    NEUTRAL = "neutral"


class TickerItem(BaseModel):
    """A single item in the live ticker."""
    
    id: str = Field(description="Market ID")
    event: str = Field(description="Shortened event title")
    spread: float = Field(description="Price spread percentage")
    trend: TickerTrend = Field(description="Price trend direction")
    volume: str = Field(description="Trading volume")
    source: MarketProvider = Field(description="Market provider")
    
    @property
    def is_trending_up(self) -> bool:
        """Check if the market is trending up."""
        return self.trend == TickerTrend.UP
    
    @property
    def is_trending_down(self) -> bool:
        """Check if the market is trending down."""
        return self.trend == TickerTrend.DOWN
