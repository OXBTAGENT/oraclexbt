"""Market-related models for the Oraclyst SDK."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from oraclyst_sdk.models.common import MarketProvider, MarketStatus


class MarketOutcome(BaseModel):
    """A single outcome option for a market."""
    
    name: str = Field(description="Outcome name (e.g., 'Yes', 'No')")
    price: float = Field(description="Current price (0-1 probability)")
    change: float = Field(default=0.0, description="Price change percentage")
    
    @property
    def probability_percent(self) -> float:
        """Get the probability as a percentage (0-100)."""
        return self.price * 100
    
    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Ensure price is within valid range (0-1)."""
        if v < 0:
            return 0.0
        if v > 1:
            return 1.0
        return v


class Market(BaseModel):
    """Represents a prediction market from any provider."""
    
    id: str = Field(description="Unique market identifier")
    source_id: str = Field(alias="sourceId", description="Original ID from the provider")
    source: MarketProvider = Field(description="Market provider (polymarket, kalshi, limitless)")
    title: str = Field(description="Market question/title")
    description: Optional[str] = Field(default=None, description="Detailed market description")
    outcomes: list[MarketOutcome] = Field(description="List of possible outcomes")
    volume: str = Field(description="Total trading volume")
    volume_24h: Optional[str] = Field(alias="volume24h", default=None, description="24-hour volume")
    liquidity: Optional[str] = Field(default=None, description="Available liquidity")
    expiry_date: str = Field(alias="expiryDate", description="Market expiration date")
    categories: list[str] = Field(default_factory=list, description="Market categories")
    image_url: Optional[str] = Field(alias="imageUrl", default=None, description="Market image URL")
    market_url: Optional[str] = Field(alias="marketUrl", default=None, description="Original market URL")
    status: MarketStatus = Field(default=MarketStatus.ACTIVE, description="Market status")
    last_updated: datetime = Field(alias="lastUpdated", description="Last update timestamp")
    clob_token_ids: Optional[list[str]] = Field(
        alias="clobTokenIds",
        default=None,
        description="CLOB token IDs (Polymarket specific)"
    )
    
    model_config = {"populate_by_name": True}
    
    @property
    def yes_price(self) -> Optional[float]:
        """Get the 'Yes' outcome price if available."""
        for outcome in self.outcomes:
            if outcome.name.lower() == "yes":
                return outcome.price
        return self.outcomes[0].price if self.outcomes else None
    
    @property
    def no_price(self) -> Optional[float]:
        """Get the 'No' outcome price if available."""
        for outcome in self.outcomes:
            if outcome.name.lower() == "no":
                return outcome.price
        return self.outcomes[1].price if len(self.outcomes) > 1 else None
    
    @property
    def volume_decimal(self) -> Decimal:
        """Parse volume string to Decimal for calculations."""
        cleaned = self.volume.replace("$", "").replace(",", "")
        multiplier = Decimal(1)
        if cleaned.endswith("M"):
            multiplier = Decimal(1_000_000)
            cleaned = cleaned[:-1]
        elif cleaned.endswith("K") or cleaned.endswith("k"):
            multiplier = Decimal(1_000)
            cleaned = cleaned[:-1]
        elif cleaned.endswith("B"):
            multiplier = Decimal(1_000_000_000)
            cleaned = cleaned[:-1]
        return Decimal(cleaned) * multiplier


class MarketFilters(BaseModel):
    """Filters for querying markets."""
    
    provider: Optional[MarketProvider] = Field(default=None, description="Filter by provider")
    category: Optional[str] = Field(default=None, description="Filter by category")
    search: Optional[str] = Field(default=None, description="Search query")
    status: Optional[MarketStatus] = Field(default=None, description="Filter by status")
    sort_by: Optional[str] = Field(
        alias="sortBy",
        default=None,
        description="Sort field (volume, volume24h, expiry, price)"
    )
    sort_order: Optional[str] = Field(
        alias="sortOrder",
        default=None,
        description="Sort order (asc, desc)"
    )
    
    model_config = {"populate_by_name": True}
    
    def to_query_params(self) -> dict[str, str]:
        """Convert filters to query parameters."""
        params = {}
        if self.provider:
            params["provider"] = self.provider.value
        if self.category:
            params["category"] = self.category
        if self.search:
            params["search"] = self.search
        if self.status:
            params["status"] = self.status.value
        if self.sort_by:
            params["sortBy"] = self.sort_by
        if self.sort_order:
            params["sortOrder"] = self.sort_order
        return params
