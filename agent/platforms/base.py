"""Base class for prediction market platform clients."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import aiohttp
import requests


class Platform(Enum):
    """Supported prediction market platforms."""
    POLYMARKET = "polymarket"
    KALSHI = "kalshi"
    LIMITLESS = "limitless"
    MANIFOLD = "manifold"
    METACULUS = "metaculus"
    PREDICTIT = "predictit"


@dataclass
class Market:
    """Unified market representation across platforms."""
    id: str
    platform: Platform
    title: str
    description: str = ""
    url: str = ""
    
    # Pricing
    probability: Optional[float] = None  # 0-1
    yes_price: Optional[float] = None
    no_price: Optional[float] = None
    
    # Volume & liquidity
    volume: Optional[float] = None
    volume_24h: Optional[float] = None
    liquidity: Optional[float] = None
    
    # Timing
    created_at: Optional[datetime] = None
    close_time: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Resolution
    is_resolved: bool = False
    resolution: Optional[str] = None  # "YES", "NO", "N/A", "CANCEL"
    
    # Categories
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Raw data from platform
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def formatted_probability(self) -> str:
        """Return probability as percentage string."""
        if self.probability is not None:
            return f"{self.probability * 100:.1f}%"
        return "N/A"
    
    @property
    def is_active(self) -> bool:
        """Check if market is still active."""
        if self.is_resolved:
            return False
        if self.close_time and datetime.now() > self.close_time:
            return False
        return True


@dataclass
class MarketHistory:
    """Price history for a market."""
    market_id: str
    platform: Platform
    timestamps: List[datetime]
    prices: List[float]
    volumes: Optional[List[float]] = None


@dataclass  
class OrderBook:
    """Order book data."""
    market_id: str
    platform: Platform
    bids: List[Dict[str, float]]  # [{"price": 0.50, "size": 100}, ...]
    asks: List[Dict[str, float]]
    timestamp: datetime = field(default_factory=datetime.now)


class BasePlatformClient(ABC):
    """Abstract base class for platform API clients."""
    
    platform: Platform
    base_url: str
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session: Optional[requests.Session] = None
        self._async_session: Optional[aiohttp.ClientSession] = None
    
    def _get_session(self) -> requests.Session:
        """Get or create sync session."""
        if self.session is None:
            self.session = requests.Session()
            if self.api_key:
                self.session.headers["Authorization"] = f"Bearer {self.api_key}"
        return self.session
    
    async def _get_async_session(self) -> aiohttp.ClientSession:
        """Get or create async session."""
        if self._async_session is None or self._async_session.closed:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._async_session = aiohttp.ClientSession(headers=headers)
        return self._async_session
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        json: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make sync HTTP request."""
        session = self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        response = session.request(method, url, params=params, json=json)
        response.raise_for_status()
        return response.json()
    
    async def _async_request(
        self,
        method: str,
        endpoint: str, 
        params: Optional[Dict] = None,
        json: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make async HTTP request."""
        session = await self._get_async_session()
        url = f"{self.base_url}{endpoint}"
        
        async with session.request(method, url, params=params, json=json) as response:
            response.raise_for_status()
            return await response.json()
    
    @abstractmethod
    def get_market(self, market_id: str) -> Market:
        """Get a single market by ID."""
        pass
    
    @abstractmethod
    def search_markets(
        self, 
        query: str, 
        limit: int = 20,
        **kwargs
    ) -> List[Market]:
        """Search for markets."""
        pass
    
    @abstractmethod
    def get_trending_markets(self, limit: int = 20) -> List[Market]:
        """Get trending/popular markets."""
        pass
    
    def get_market_history(
        self, 
        market_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Optional[MarketHistory]:
        """Get price history for a market. Override in subclass if supported."""
        return None
    
    def get_orderbook(self, market_id: str) -> Optional[OrderBook]:
        """Get order book for a market. Override in subclass if supported."""
        return None
    
    def close(self):
        """Close sessions."""
        if self.session:
            self.session.close()
    
    async def aclose(self):
        """Close async sessions."""
        if self._async_session:
            await self._async_session.close()
