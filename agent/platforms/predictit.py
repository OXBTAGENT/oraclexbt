"""
PredictIt API Client

PredictIt is a real-money prediction market platform focused on US politics.
Based in New Zealand, operates under a CFTC no-action letter.
API Docs: https://www.predictit.org/api/marketdata/all/
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from .base import BasePlatformClient, Platform, Market


class PredictItClient(BasePlatformClient):
    """Client for PredictIt API."""
    
    platform = Platform.PREDICTIT
    base_url = "https://www.predictit.org/api"
    
    def __init__(self):
        """
        Initialize PredictIt client.
        PredictIt has a public API - no authentication needed for market data.
        """
        super().__init__(api_key=None)
        self._markets_cache: Optional[Dict[str, Any]] = None
        self._cache_time: Optional[datetime] = None
    
    def _get_all_markets_raw(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetch all markets from PredictIt.
        Uses caching since PredictIt serves all markets in one endpoint.
        """
        # Cache for 1 minute
        if (
            not force_refresh 
            and self._markets_cache 
            and self._cache_time
            and (datetime.now() - self._cache_time).seconds < 60
        ):
            return self._markets_cache
        
        data = self._request("GET", "/marketdata/all/")
        self._markets_cache = data
        self._cache_time = datetime.now()
        return data
    
    def _parse_contract(
        self, 
        contract_data: Dict[str, Any], 
        market_data: Dict[str, Any]
    ) -> Market:
        """Parse a PredictIt contract (individual yes/no) into Market object."""
        # PredictIt has markets containing multiple contracts
        # Each contract is essentially a yes/no question
        
        # Parse timestamps
        end_date = None
        if contract_data.get("dateEnd") and contract_data["dateEnd"] != "N/A":
            try:
                end_date = datetime.fromisoformat(contract_data["dateEnd"].replace("Z", "+00:00"))
            except ValueError:
                pass
        
        # Get prices (in cents, convert to 0-1)
        yes_price = None
        no_price = None
        
        if contract_data.get("lastTradePrice"):
            yes_price = contract_data["lastTradePrice"]
            no_price = 1 - yes_price
        elif contract_data.get("bestBuyYesCost"):
            yes_price = contract_data["bestBuyYesCost"]
            no_price = contract_data.get("bestBuyNoCost", 1 - yes_price)
        
        return Market(
            id=f"predictit-{contract_data['id']}",
            platform=Platform.PREDICTIT,
            title=contract_data.get("name", ""),
            description=market_data.get("shortName", ""),
            url=contract_data.get("url", market_data.get("url", "")),
            probability=yes_price,
            yes_price=yes_price,
            no_price=no_price,
            volume=None,  # PredictIt doesn't expose volume in API
            liquidity=None,
            created_at=None,
            close_time=end_date,
            resolved_at=None,
            is_resolved=contract_data.get("status") == "Closed",
            resolution=None,
            categories=[market_data.get("shortName", "")],
            tags=[],
            raw_data={
                "contract": contract_data,
                "market": market_data
            }
        )
    
    def _parse_market_group(self, market_data: Dict[str, Any]) -> List[Market]:
        """Parse a PredictIt market (which contains multiple contracts)."""
        markets = []
        for contract in market_data.get("contracts", []):
            markets.append(self._parse_contract(contract, market_data))
        return markets
    
    def get_market(self, market_id: str) -> Market:
        """
        Get a single contract by ID.
        
        Args:
            market_id: PredictIt contract ID (with or without 'predictit-' prefix)
        """
        if market_id.startswith("predictit-"):
            market_id = market_id[10:]
        
        contract_id = int(market_id)
        
        # Search through all markets
        data = self._get_all_markets_raw()
        for market in data.get("markets", []):
            for contract in market.get("contracts", []):
                if contract.get("id") == contract_id:
                    return self._parse_contract(contract, market)
        
        raise ValueError(f"Contract {market_id} not found")
    
    def get_market_group(self, market_id: int) -> List[Market]:
        """
        Get all contracts in a market group.
        
        PredictIt groups related questions (e.g., "Who will win the election?")
        into markets with multiple contracts (e.g., one per candidate).
        """
        data = self._get_all_markets_raw()
        for market in data.get("markets", []):
            if market.get("id") == market_id:
                return self._parse_market_group(market)
        
        raise ValueError(f"Market {market_id} not found")
    
    def search_markets(
        self,
        query: str,
        limit: int = 20,
        **kwargs
    ) -> List[Market]:
        """
        Search for contracts.
        
        Args:
            query: Search query (searches contract names)
            limit: Max results
        """
        query_lower = query.lower()
        data = self._get_all_markets_raw()
        
        results = []
        for market in data.get("markets", []):
            market_name = market.get("shortName", "").lower()
            
            for contract in market.get("contracts", []):
                contract_name = contract.get("name", "").lower()
                
                # Search in both market and contract names
                if query_lower in contract_name or query_lower in market_name:
                    results.append(self._parse_contract(contract, market))
                    
                    if len(results) >= limit:
                        return results
        
        return results
    
    def get_trending_markets(self, limit: int = 20) -> List[Market]:
        """
        Get all active contracts sorted by activity.
        Since PredictIt doesn't expose volume, we return all open contracts.
        """
        data = self._get_all_markets_raw()
        
        results = []
        for market in data.get("markets", []):
            for contract in market.get("contracts", []):
                # Only include active contracts with trading data
                if (
                    contract.get("status") == "Open" 
                    and contract.get("lastTradePrice") is not None
                ):
                    results.append(self._parse_contract(contract, market))
        
        # Sort by most recent trade price (closer to 50% = more interesting)
        results.sort(key=lambda m: abs(0.5 - (m.probability or 0)))
        
        return results[:limit]
    
    def get_all_markets(self) -> List[Market]:
        """Get all contracts from all markets."""
        data = self._get_all_markets_raw()
        
        results = []
        for market in data.get("markets", []):
            results.extend(self._parse_market_group(market))
        
        return results
    
    def get_political_markets(self, limit: int = 50) -> List[Market]:
        """Get markets related to politics (PredictIt's main focus)."""
        # PredictIt is primarily political markets
        return self.get_all_markets()[:limit]
    
    def get_market_groups(self) -> List[Dict[str, Any]]:
        """
        Get all market groups (not individual contracts).
        
        Returns list of markets with their metadata.
        """
        data = self._get_all_markets_raw()
        return data.get("markets", [])
    
    def refresh_cache(self) -> None:
        """Force refresh the market cache."""
        self._get_all_markets_raw(force_refresh=True)


# Async version
class AsyncPredictItClient(PredictItClient):
    """Async client for PredictIt API."""
    
    async def _get_all_markets_raw_async(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Async version of market fetch."""
        if (
            not force_refresh 
            and self._markets_cache 
            and self._cache_time
            and (datetime.now() - self._cache_time).seconds < 60
        ):
            return self._markets_cache
        
        data = await self._async_request("GET", "/marketdata/all/")
        self._markets_cache = data
        self._cache_time = datetime.now()
        return data
    
    async def get_market(self, market_id: str) -> Market:
        if market_id.startswith("predictit-"):
            market_id = market_id[10:]
        
        contract_id = int(market_id)
        data = await self._get_all_markets_raw_async()
        
        for market in data.get("markets", []):
            for contract in market.get("contracts", []):
                if contract.get("id") == contract_id:
                    return self._parse_contract(contract, market)
        
        raise ValueError(f"Contract {market_id} not found")
    
    async def search_markets(
        self,
        query: str,
        limit: int = 20,
        **kwargs
    ) -> List[Market]:
        query_lower = query.lower()
        data = await self._get_all_markets_raw_async()
        
        results = []
        for market in data.get("markets", []):
            market_name = market.get("shortName", "").lower()
            
            for contract in market.get("contracts", []):
                contract_name = contract.get("name", "").lower()
                
                if query_lower in contract_name or query_lower in market_name:
                    results.append(self._parse_contract(contract, market))
                    
                    if len(results) >= limit:
                        return results
        
        return results
    
    async def get_trending_markets(self, limit: int = 20) -> List[Market]:
        data = await self._get_all_markets_raw_async()
        
        results = []
        for market in data.get("markets", []):
            for contract in market.get("contracts", []):
                if (
                    contract.get("status") == "Open" 
                    and contract.get("lastTradePrice") is not None
                ):
                    results.append(self._parse_contract(contract, market))
        
        results.sort(key=lambda m: abs(0.5 - (m.probability or 0)))
        return results[:limit]
