"""Common models and enums for the Oraclyst SDK."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field


class MarketProvider(str, Enum):
    """Supported prediction market providers."""
    
    POLYMARKET = "polymarket"
    KALSHI = "kalshi"
    LIMITLESS = "limitless"


class MarketStatus(str, Enum):
    """Market status values."""
    
    ACTIVE = "active"
    RESOLVED = "resolved"
    CLOSED = "closed"
    EXPIRED = "expired"


T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata from API responses."""
    
    total: int = Field(description="Total number of items")
    limit: int = Field(description="Items per page")
    offset: int = Field(description="Current offset")
    has_more: bool = Field(alias="hasMore", description="Whether more items exist")
    filters: dict = Field(default_factory=dict, description="Applied filters")
    
    model_config = {"populate_by_name": True}


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""
    
    success: bool = Field(description="Whether the request was successful")
    data: T = Field(description="Response data")
    timestamp: datetime = Field(description="Response timestamp")
    message: Optional[str] = Field(default=None, description="Optional message")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated API response with metadata."""
    
    success: bool = Field(description="Whether the request was successful")
    data: list[T] = Field(description="List of items")
    meta: PaginationMeta = Field(description="Pagination metadata")
    timestamp: datetime = Field(description="Response timestamp")
