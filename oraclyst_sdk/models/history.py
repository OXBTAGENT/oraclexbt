"""Price history models for the Oraclyst SDK."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


TimeRange = Literal["1m", "5m", "1h", "4h", "1d"]


class PricePoint(BaseModel):
    """A single price point in the history."""
    
    timestamp: int = Field(description="Unix timestamp in milliseconds")
    yes_price: float = Field(alias="yesPrice", description="Yes outcome price")
    no_price: float = Field(alias="noPrice", description="No outcome price")
    
    model_config = {"populate_by_name": True}
    
    @property
    def datetime(self) -> datetime:
        """Convert timestamp to datetime object."""
        return datetime.fromtimestamp(self.timestamp / 1000)
    
    @property
    def yes_percent(self) -> float:
        """Get Yes price as percentage (0-100)."""
        return self.yes_price * 100
    
    @property
    def no_percent(self) -> float:
        """Get No price as percentage (0-100)."""
        return self.no_price * 100


class PriceHistory(BaseModel):
    """Price history for a market."""
    
    points: list[PricePoint] = Field(description="List of price points")
    range: str = Field(description="Time range (1m, 5m, 1h, 4h, 1d)")
    
    @property
    def is_empty(self) -> bool:
        """Check if history has any data points."""
        return len(self.points) == 0
    
    @property
    def latest(self) -> PricePoint | None:
        """Get the most recent price point."""
        return self.points[-1] if self.points else None
    
    @property
    def oldest(self) -> PricePoint | None:
        """Get the oldest price point."""
        return self.points[0] if self.points else None
    
    def price_change(self) -> tuple[float, float] | None:
        """
        Calculate price change (Yes, No) between oldest and newest points.
        
        Returns:
            Tuple of (yes_change, no_change) or None if insufficient data.
        """
        if len(self.points) < 2:
            return None
        oldest = self.points[0]
        newest = self.points[-1]
        return (
            newest.yes_price - oldest.yes_price,
            newest.no_price - oldest.no_price,
        )
