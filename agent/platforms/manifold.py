"""
Manifold Markets API Client

Manifold is a play-money prediction market platform with an excellent public API.
Docs: https://docs.manifold.markets/api
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import os

from .base import BasePlatformClient, Platform, Market, MarketHistory


class ManifoldClient(BasePlatformClient):
    """Client for Manifold Markets API."""
    
    platform = Platform.MANIFOLD
    base_url = "https://api.manifold.markets/v0"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Manifold client.
        
        Args:
            api_key: Optional API key for authenticated requests.
                    Can also be set via MANIFOLD_API_KEY env var.
        """
        super().__init__(api_key or os.getenv("MANIFOLD_API_KEY"))
    
    def _parse_market(self, data: Dict[str, Any]) -> Market:
        """Parse Manifold market data into unified Market object."""
        # Parse timestamps
        created_at = None
        close_time = None
        resolved_at = None
        
        if data.get("createdTime"):
            created_at = datetime.fromtimestamp(data["createdTime"] / 1000)
        if data.get("closeTime"):
            close_time = datetime.fromtimestamp(data["closeTime"] / 1000)
        if data.get("resolutionTime"):
            resolved_at = datetime.fromtimestamp(data["resolutionTime"] / 1000)
        
        # Get probability
        probability = data.get("probability")
        
        # Map resolution
        resolution = None
        if data.get("resolution"):
            res = data["resolution"]
            if res == "YES":
                resolution = "YES"
            elif res == "NO":
                resolution = "NO"
            elif res == "CANCEL":
                resolution = "CANCEL"
            elif res == "MKT":
                resolution = f"MKT ({data.get('resolutionProbability', 'N/A')})"
            else:
                resolution = str(res)
        
        return Market(
            id=f"manifold-{data['id']}",
            platform=Platform.MANIFOLD,
            title=data.get("question", ""),
            description=data.get("textDescription", ""),
            url=data.get("url", f"https://manifold.markets/{data.get('creatorUsername', '')}/{data.get('slug', '')}"),
            probability=probability,
            yes_price=probability,
            no_price=1 - probability if probability else None,
            volume=data.get("volume"),
            volume_24h=data.get("volume24Hours"),
            liquidity=data.get("totalLiquidity"),
            created_at=created_at,
            close_time=close_time,
            resolved_at=resolved_at,
            is_resolved=data.get("isResolved", False),
            resolution=resolution,
            categories=[data.get("groupSlugs", [])] if isinstance(data.get("groupSlugs"), str) else data.get("groupSlugs", []),
            tags=data.get("tags", []),
            raw_data=data
        )
    
    def get_market(self, market_id: str) -> Market:
        """
        Get a single market by ID.
        
        Args:
            market_id: Manifold market ID or slug (with or without 'manifold-' prefix)
        """
        # Strip prefix if present
        if market_id.startswith("manifold-"):
            market_id = market_id[9:]
        
        data = self._request("GET", f"/market/{market_id}")
        return self._parse_market(data)
    
    def get_market_by_slug(self, slug: str) -> Market:
        """Get market by URL slug."""
        data = self._request("GET", f"/slug/{slug}")
        return self._parse_market(data)
    
    def search_markets(
        self,
        query: str,
        limit: int = 20,
        sort: str = "score",  # score, newest, liquidity, volume24h, volume
        filter: str = "open",  # all, open, closed, resolved
        **kwargs
    ) -> List[Market]:
        """
        Search for markets.
        
        Args:
            query: Search query
            limit: Max results (default 20, max 1000)
            sort: Sort order (score, newest, liquidity, volume24h, volume)
            filter: Filter by status (all, open, closed, resolved)
        """
        params = {
            "term": query,
            "limit": min(limit, 1000),
            "sort": sort,
            "filter": filter,
        }
        
        data = self._request("GET", "/search-markets", params=params)
        return [self._parse_market(m) for m in data]
    
    def get_trending_markets(self, limit: int = 20) -> List[Market]:
        """Get markets sorted by recent activity/volume."""
        params = {
            "limit": min(limit, 1000),
            "sort": "score",
            "filter": "open",
        }
        
        data = self._request("GET", "/search-markets", params=params)
        return [self._parse_market(m) for m in data]
    
    def get_markets_by_group(self, group_slug: str, limit: int = 50) -> List[Market]:
        """Get markets in a specific group/category."""
        params = {
            "groupSlug": group_slug,
            "limit": min(limit, 1000),
        }
        
        data = self._request("GET", "/markets", params=params)
        return [self._parse_market(m) for m in data]
    
    def get_user_markets(self, username: str, limit: int = 50) -> List[Market]:
        """Get markets created by a user."""
        # First get user ID
        user_data = self._request("GET", f"/user/{username}")
        user_id = user_data.get("id")
        
        params = {
            "userId": user_id,
            "limit": min(limit, 1000),
        }
        
        data = self._request("GET", "/markets", params=params)
        return [self._parse_market(m) for m in data]
    
    def get_market_positions(self, market_id: str) -> List[Dict[str, Any]]:
        """Get positions (bets) on a market."""
        if market_id.startswith("manifold-"):
            market_id = market_id[9:]
        
        data = self._request("GET", f"/market/{market_id}/positions")
        return data
    
    def get_groups(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get available groups/categories."""
        params = {"availableToUserId": "", "limit": limit}
        return self._request("GET", "/groups", params=params)
    
    # ========== Authenticated Methods (require API key) ==========
    
    def place_bet(
        self,
        market_id: str,
        amount: float,
        outcome: str = "YES",  # YES or NO
        limit_prob: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Place a bet on a market.
        
        Args:
            market_id: Market ID (without prefix)
            amount: Amount in mana (Manifold's play money)
            outcome: YES or NO
            limit_prob: Optional limit price (0-1)
        
        Returns:
            Bet confirmation data
        """
        if not self.api_key:
            raise ValueError("API key required for placing bets")
        
        if market_id.startswith("manifold-"):
            market_id = market_id[9:]
        
        payload = {
            "amount": amount,
            "outcome": outcome,
            "contractId": market_id,
        }
        
        if limit_prob is not None:
            payload["limitProb"] = limit_prob
        
        return self._request("POST", "/bet", json=payload)
    
    def create_market(
        self,
        question: str,
        description: str = "",
        close_time: Optional[datetime] = None,
        initial_prob: float = 0.5,
        **kwargs
    ) -> Market:
        """
        Create a new market.
        
        Args:
            question: Market question/title
            description: Market description (markdown supported)
            close_time: When the market closes
            initial_prob: Starting probability (default 0.5)
        """
        if not self.api_key:
            raise ValueError("API key required for creating markets")
        
        payload = {
            "outcomeType": "BINARY",
            "question": question,
            "description": description,
            "initialProb": int(initial_prob * 100),
        }
        
        if close_time:
            payload["closeTime"] = int(close_time.timestamp() * 1000)
        
        data = self._request("POST", "/market", json=payload)
        return self._parse_market(data)
    
    def add_liquidity(self, market_id: str, amount: float) -> Dict[str, Any]:
        """Add liquidity to a market."""
        if not self.api_key:
            raise ValueError("API key required")
        
        if market_id.startswith("manifold-"):
            market_id = market_id[9:]
        
        return self._request("POST", f"/market/{market_id}/add-liquidity", json={"amount": amount})
    
    def resolve_market(
        self,
        market_id: str,
        outcome: str,  # YES, NO, CANCEL, MKT
        probability_int: Optional[int] = None  # For MKT resolution
    ) -> Dict[str, Any]:
        """Resolve a market you created."""
        if not self.api_key:
            raise ValueError("API key required")
        
        if market_id.startswith("manifold-"):
            market_id = market_id[9:]
        
        payload = {"outcome": outcome}
        if probability_int is not None:
            payload["probabilityInt"] = probability_int
        
        return self._request("POST", f"/market/{market_id}/resolve", json=payload)


# Async version
class AsyncManifoldClient(ManifoldClient):
    """Async client for Manifold Markets API."""
    
    async def get_market(self, market_id: str) -> Market:
        if market_id.startswith("manifold-"):
            market_id = market_id[9:]
        
        data = await self._async_request("GET", f"/market/{market_id}")
        return self._parse_market(data)
    
    async def search_markets(
        self,
        query: str,
        limit: int = 20,
        sort: str = "score",
        filter: str = "open",
        **kwargs
    ) -> List[Market]:
        params = {
            "term": query,
            "limit": min(limit, 1000),
            "sort": sort,
            "filter": filter,
        }
        
        data = await self._async_request("GET", "/search-markets", params=params)
        return [self._parse_market(m) for m in data]
    
    async def get_trending_markets(self, limit: int = 20) -> List[Market]:
        params = {
            "limit": min(limit, 1000),
            "sort": "score",
            "filter": "open",
        }
        
        data = await self._async_request("GET", "/search-markets", params=params)
        return [self._parse_market(m) for m in data]
