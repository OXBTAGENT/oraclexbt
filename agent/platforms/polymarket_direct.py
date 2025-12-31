"""
Polymarket Direct API Client

Direct connection to Polymarket's CLOB (Central Limit Order Book) API.
This provides more detailed data than the Oraclyst SDK aggregator.
Docs: https://docs.polymarket.com/
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import os

from .base import BasePlatformClient, Platform, Market, MarketHistory, OrderBook


class PolymarketDirectClient(BasePlatformClient):
    """Direct client for Polymarket's CLOB API."""
    
    platform = Platform.POLYMARKET
    base_url = "https://clob.polymarket.com"
    gamma_url = "https://gamma-api.polymarket.com"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Polymarket client.
        
        Args:
            api_key: Optional API key for authenticated requests.
                    Can also be set via POLYMARKET_API_KEY env var.
        """
        super().__init__(api_key or os.getenv("POLYMARKET_API_KEY"))
    
    def _parse_market(self, data: Dict[str, Any]) -> Market:
        """Parse Polymarket market data into unified Market object."""
        # Parse timestamps
        created_at = None
        close_time = None
        resolved_at = None
        
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass
        
        if data.get("end_date_iso"):
            try:
                close_time = datetime.fromisoformat(data["end_date_iso"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass
        
        if data.get("closed_time"):
            try:
                resolved_at = datetime.fromisoformat(data["closed_time"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass
        
        # Get price/probability
        probability = None
        yes_price = None
        no_price = None
        
        # Try different price fields
        if data.get("outcomePrices"):
            try:
                prices = data["outcomePrices"]
                if isinstance(prices, str):
                    import json
                    prices = json.loads(prices)
                if isinstance(prices, list) and len(prices) >= 2:
                    yes_price = float(prices[0])
                    no_price = float(prices[1])
                    probability = yes_price
            except (ValueError, TypeError, IndexError):
                pass
        
        if probability is None and data.get("lastTradePrice"):
            try:
                probability = float(data["lastTradePrice"])
                yes_price = probability
                no_price = 1 - probability
            except (ValueError, TypeError):
                pass
        
        # Get volume
        volume = None
        if data.get("volume"):
            try:
                volume = float(data["volume"])
            except (ValueError, TypeError):
                pass
        
        volume_24h = None
        if data.get("volume24hr"):
            try:
                volume_24h = float(data["volume24hr"])
            except (ValueError, TypeError):
                pass
        
        # Get liquidity
        liquidity = None
        if data.get("liquidity"):
            try:
                liquidity = float(data["liquidity"])
            except (ValueError, TypeError):
                pass
        
        # Resolution
        is_resolved = data.get("closed", False) or data.get("resolved", False)
        resolution = None
        if data.get("outcome"):
            resolution = data["outcome"]
        
        # Categories/tags
        categories = []
        if data.get("category"):
            categories = [data["category"]]
        
        tags = data.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        
        # Build URL
        slug = data.get("slug", data.get("market_slug", ""))
        url = f"https://polymarket.com/event/{slug}" if slug else ""
        
        return Market(
            id=f"pm-{data.get('condition_id', data.get('id', ''))}",
            platform=Platform.POLYMARKET,
            title=data.get("question", data.get("title", "")),
            description=data.get("description", ""),
            url=url,
            probability=probability,
            yes_price=yes_price,
            no_price=no_price,
            volume=volume,
            volume_24h=volume_24h,
            liquidity=liquidity,
            created_at=created_at,
            close_time=close_time,
            resolved_at=resolved_at,
            is_resolved=is_resolved,
            resolution=resolution,
            categories=categories,
            tags=tags if isinstance(tags, list) else [],
            raw_data=data
        )
    
    def get_market(self, market_id: str) -> Market:
        """
        Get a single market by condition ID.
        
        Args:
            market_id: Polymarket condition ID (with or without 'pm-' prefix)
        """
        if market_id.startswith("pm-"):
            market_id = market_id[3:]
        
        # Try CLOB API first
        try:
            data = self._request("GET", f"/markets/{market_id}")
            return self._parse_market(data)
        except Exception:
            pass
        
        # Fallback to Gamma API
        data = self._request_gamma("GET", f"/markets/{market_id}")
        return self._parse_market(data)
    
    def _request_gamma(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make request to Gamma API."""
        session = self._get_session()
        url = f"{self.gamma_url}{endpoint}"
        
        response = session.request(method, url, params=params, json=json)
        response.raise_for_status()
        return response.json()
    
    def search_markets(
        self,
        query: str,
        limit: int = 20,
        active: bool = True,
        **kwargs
    ) -> List[Market]:
        """
        Search for markets.
        
        Args:
            query: Search query
            limit: Max results
            active: Only return active markets
        """
        params = {
            "limit": limit,
            "active": str(active).lower(),
        }
        
        if query:
            params["tag"] = query  # Gamma API uses tag for search
        
        # Use Gamma API for search
        try:
            data = self._request_gamma("GET", "/markets", params=params)
            
            if isinstance(data, list):
                markets = data
            else:
                markets = data.get("markets", data.get("data", []))
            
            results = []
            query_lower = query.lower()
            
            for m in markets:
                title = m.get("question", m.get("title", "")).lower()
                desc = m.get("description", "").lower()
                
                if query_lower in title or query_lower in desc:
                    results.append(self._parse_market(m))
                
                if len(results) >= limit:
                    break
            
            return results
        except Exception as e:
            # Fallback: get all and filter
            return self._search_fallback(query, limit, active)
    
    def _search_fallback(self, query: str, limit: int, active: bool) -> List[Market]:
        """Fallback search by fetching all markets."""
        try:
            params = {"limit": 100, "active": str(active).lower()}
            data = self._request_gamma("GET", "/markets", params=params)
            
            if isinstance(data, list):
                markets = data
            else:
                markets = data.get("markets", data.get("data", []))
            
            results = []
            query_lower = query.lower()
            
            for m in markets:
                title = m.get("question", m.get("title", "")).lower()
                if query_lower in title:
                    results.append(self._parse_market(m))
                    if len(results) >= limit:
                        break
            
            return results
        except Exception:
            return []
    
    def get_trending_markets(self, limit: int = 20) -> List[Market]:
        """Get markets sorted by volume."""
        params = {
            "limit": limit,
            "active": "true",
            "order": "volume24hr",
            "ascending": "false",
        }
        
        try:
            data = self._request_gamma("GET", "/markets", params=params)
            
            if isinstance(data, list):
                markets = data
            else:
                markets = data.get("markets", data.get("data", []))
            
            return [self._parse_market(m) for m in markets[:limit]]
        except Exception:
            return []
    
    def get_orderbook(self, market_id: str) -> Optional[OrderBook]:
        """Get order book for a market."""
        if market_id.startswith("pm-"):
            market_id = market_id[3:]
        
        try:
            # Get token IDs for this market
            market_data = self._request("GET", f"/markets/{market_id}")
            
            # Fetch order book
            data = self._request("GET", f"/book", params={"token_id": market_id})
            
            bids = []
            asks = []
            
            for bid in data.get("bids", []):
                bids.append({
                    "price": float(bid.get("price", 0)),
                    "size": float(bid.get("size", 0))
                })
            
            for ask in data.get("asks", []):
                asks.append({
                    "price": float(ask.get("price", 0)),
                    "size": float(ask.get("size", 0))
                })
            
            return OrderBook(
                market_id=f"pm-{market_id}",
                platform=Platform.POLYMARKET,
                bids=bids,
                asks=asks
            )
        except Exception:
            return None
    
    def get_market_history(
        self,
        market_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Optional[MarketHistory]:
        """Get price history for a market."""
        if market_id.startswith("pm-"):
            market_id = market_id[3:]
        
        try:
            params = {"market": market_id, "interval": "1d"}
            
            if start_time:
                params["startTs"] = int(start_time.timestamp())
            if end_time:
                params["endTs"] = int(end_time.timestamp())
            
            data = self._request("GET", "/prices-history", params=params)
            
            timestamps = []
            prices = []
            
            for point in data.get("history", []):
                timestamps.append(datetime.fromtimestamp(point["t"]))
                prices.append(float(point["p"]))
            
            if timestamps:
                return MarketHistory(
                    market_id=f"pm-{market_id}",
                    platform=Platform.POLYMARKET,
                    timestamps=timestamps,
                    prices=prices
                )
        except Exception:
            pass
        
        return None
    
    def get_markets_by_slug(self, slug: str) -> List[Market]:
        """Get markets by event slug."""
        try:
            data = self._request_gamma("GET", f"/events/{slug}")
            markets = data.get("markets", [])
            return [self._parse_market(m) for m in markets]
        except Exception:
            return []
    
    def get_events(self, limit: int = 20, active: bool = True) -> List[Dict[str, Any]]:
        """Get events (groups of related markets)."""
        params = {"limit": limit, "active": str(active).lower()}
        
        try:
            data = self._request_gamma("GET", "/events", params=params)
            return data if isinstance(data, list) else data.get("events", [])
        except Exception:
            return []


# Async version
class AsyncPolymarketDirectClient(PolymarketDirectClient):
    """Async client for Polymarket API."""
    
    async def get_market(self, market_id: str) -> Market:
        if market_id.startswith("pm-"):
            market_id = market_id[3:]
        
        try:
            data = await self._async_request("GET", f"/markets/{market_id}")
            return self._parse_market(data)
        except Exception:
            pass
        
        # Fallback to gamma
        session = await self._get_async_session()
        async with session.get(f"{self.gamma_url}/markets/{market_id}") as resp:
            data = await resp.json()
            return self._parse_market(data)
    
    async def search_markets(
        self,
        query: str,
        limit: int = 20,
        active: bool = True,
        **kwargs
    ) -> List[Market]:
        params = {"limit": 100, "active": str(active).lower()}
        
        session = await self._get_async_session()
        async with session.get(f"{self.gamma_url}/markets", params=params) as resp:
            data = await resp.json()
        
        if isinstance(data, list):
            markets = data
        else:
            markets = data.get("markets", data.get("data", []))
        
        results = []
        query_lower = query.lower()
        
        for m in markets:
            title = m.get("question", m.get("title", "")).lower()
            if query_lower in title:
                results.append(self._parse_market(m))
                if len(results) >= limit:
                    break
        
        return results
    
    async def get_trending_markets(self, limit: int = 20) -> List[Market]:
        params = {
            "limit": limit,
            "active": "true",
            "order": "volume24hr",
            "ascending": "false",
        }
        
        session = await self._get_async_session()
        async with session.get(f"{self.gamma_url}/markets", params=params) as resp:
            data = await resp.json()
        
        if isinstance(data, list):
            markets = data
        else:
            markets = data.get("markets", data.get("data", []))
        
        return [self._parse_market(m) for m in markets[:limit]]
