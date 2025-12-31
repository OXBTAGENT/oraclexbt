"""
Unified Prediction Market Aggregator

Aggregates data from all connected prediction market platforms.
This is the main interface OracleXBT uses to query markets across all platforms.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

from .base import Platform, Market, MarketHistory, BasePlatformClient
from .manifold import ManifoldClient, AsyncManifoldClient
from .metaculus import MetaculusClient, AsyncMetaculusClient
from .predictit import PredictItClient, AsyncPredictItClient
from .polymarket_direct import PolymarketDirectClient, AsyncPolymarketDirectClient


class PredictionMarketAggregator:
    """
    Unified interface to all prediction market platforms.
    
    The Oracle sees all markets! 🔮
    """
    
    def __init__(
        self,
        enable_manifold: bool = True,
        enable_metaculus: bool = True,
        enable_predictit: bool = True,
        enable_polymarket: bool = True,
        manifold_api_key: Optional[str] = None,
        metaculus_api_key: Optional[str] = None,
        polymarket_api_key: Optional[str] = None,
    ):
        """
        Initialize aggregator with selected platforms.
        
        Args:
            enable_*: Enable/disable specific platforms
            *_api_key: Optional API keys for authenticated features
        """
        self.clients: Dict[Platform, BasePlatformClient] = {}
        
        if enable_manifold:
            self.clients[Platform.MANIFOLD] = ManifoldClient(api_key=manifold_api_key)
        
        if enable_metaculus:
            self.clients[Platform.METACULUS] = MetaculusClient(api_key=metaculus_api_key)
        
        if enable_predictit:
            self.clients[Platform.PREDICTIT] = PredictItClient()
        
        if enable_polymarket:
            self.clients[Platform.POLYMARKET] = PolymarketDirectClient(api_key=polymarket_api_key)
    
    @property
    def enabled_platforms(self) -> List[Platform]:
        """Get list of enabled platforms."""
        return list(self.clients.keys())
    
    def get_client(self, platform: Platform) -> Optional[BasePlatformClient]:
        """Get client for a specific platform."""
        return self.clients.get(platform)
    
    def search_all(
        self,
        query: str,
        limit_per_platform: int = 10,
        platforms: Optional[List[Platform]] = None
    ) -> Dict[Platform, List[Market]]:
        """
        Search across all platforms in parallel.
        
        Args:
            query: Search query
            limit_per_platform: Max results per platform
            platforms: Specific platforms to search (default: all enabled)
        
        Returns:
            Dict mapping platform to list of markets
        """
        target_platforms = platforms or self.enabled_platforms
        results: Dict[Platform, List[Market]] = {}
        
        def search_platform(platform: Platform) -> Tuple[Platform, List[Market]]:
            client = self.clients.get(platform)
            if not client:
                return (platform, [])
            try:
                markets = client.search_markets(query, limit=limit_per_platform)
                return (platform, markets)
            except Exception as e:
                print(f"Error searching {platform.value}: {e}")
                return (platform, [])
        
        with ThreadPoolExecutor(max_workers=len(target_platforms)) as executor:
            futures = {
                executor.submit(search_platform, p): p 
                for p in target_platforms 
                if p in self.clients
            }
            
            for future in as_completed(futures):
                platform, markets = future.result()
                results[platform] = markets
        
        return results
    
    def search_all_flat(
        self,
        query: str,
        limit: int = 50,
        platforms: Optional[List[Platform]] = None
    ) -> List[Market]:
        """
        Search across all platforms and return flat list.
        
        Results are interleaved from each platform for variety.
        """
        per_platform = max(limit // len(self.enabled_platforms), 10)
        platform_results = self.search_all(query, per_platform, platforms)
        
        # Interleave results
        all_markets = []
        max_len = max(len(m) for m in platform_results.values()) if platform_results else 0
        
        for i in range(max_len):
            for platform in platform_results:
                markets = platform_results[platform]
                if i < len(markets):
                    all_markets.append(markets[i])
                    if len(all_markets) >= limit:
                        return all_markets
        
        return all_markets[:limit]
    
    def get_trending_all(
        self,
        limit_per_platform: int = 10,
        platforms: Optional[List[Platform]] = None
    ) -> Dict[Platform, List[Market]]:
        """Get trending markets from all platforms."""
        target_platforms = platforms or self.enabled_platforms
        results: Dict[Platform, List[Market]] = {}
        
        def get_trending(platform: Platform) -> Tuple[Platform, List[Market]]:
            client = self.clients.get(platform)
            if not client:
                return (platform, [])
            try:
                markets = client.get_trending_markets(limit=limit_per_platform)
                return (platform, markets)
            except Exception as e:
                print(f"Error getting trending from {platform.value}: {e}")
                return (platform, [])
        
        with ThreadPoolExecutor(max_workers=len(target_platforms)) as executor:
            futures = {
                executor.submit(get_trending, p): p 
                for p in target_platforms 
                if p in self.clients
            }
            
            for future in as_completed(futures):
                platform, markets = future.result()
                results[platform] = markets
        
        return results
    
    def get_market(self, market_id: str) -> Optional[Market]:
        """
        Get a market by ID (auto-detects platform from prefix).
        
        ID formats:
        - manifold-xxx
        - metaculus-xxx
        - predictit-xxx
        - pm-xxx (Polymarket)
        """
        platform = self._detect_platform(market_id)
        
        if platform and platform in self.clients:
            try:
                return self.clients[platform].get_market(market_id)
            except Exception as e:
                print(f"Error fetching market {market_id}: {e}")
        
        # Try all platforms if prefix not recognized
        for client in self.clients.values():
            try:
                return client.get_market(market_id)
            except Exception:
                continue
        
        return None
    
    def _detect_platform(self, market_id: str) -> Optional[Platform]:
        """Detect platform from market ID prefix."""
        if market_id.startswith("manifold-"):
            return Platform.MANIFOLD
        elif market_id.startswith("metaculus-"):
            return Platform.METACULUS
        elif market_id.startswith("predictit-"):
            return Platform.PREDICTIT
        elif market_id.startswith("pm-"):
            return Platform.POLYMARKET
        return None
    
    def find_arbitrage(
        self,
        query: str,
        min_spread: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Find potential arbitrage opportunities across platforms.
        
        Searches for similar markets on different platforms
        and identifies price discrepancies.
        
        Args:
            query: Topic to search for
            min_spread: Minimum price difference to report (default 5%)
        
        Returns:
            List of arbitrage opportunities with market details
        """
        results = self.search_all(query, limit_per_platform=20)
        
        # Group markets by similar titles
        opportunities = []
        all_markets = []
        
        for platform, markets in results.items():
            for market in markets:
                if market.probability is not None and market.is_active:
                    all_markets.append(market)
        
        # Simple matching: look for markets with similar titles
        checked_pairs = set()
        
        for i, market1 in enumerate(all_markets):
            for market2 in all_markets[i+1:]:
                # Skip same platform
                if market1.platform == market2.platform:
                    continue
                
                # Check if titles are similar (simple word overlap)
                title1_words = set(market1.title.lower().split())
                title2_words = set(market2.title.lower().split())
                
                # Remove common words
                common_words = {'the', 'a', 'an', 'will', 'be', 'in', 'to', 'of', 'for', 'on', 'at'}
                title1_words -= common_words
                title2_words -= common_words
                
                if not title1_words or not title2_words:
                    continue
                
                overlap = len(title1_words & title2_words)
                similarity = overlap / min(len(title1_words), len(title2_words))
                
                if similarity < 0.5:  # Require 50% word overlap
                    continue
                
                # Calculate spread
                spread = abs(market1.probability - market2.probability)
                
                if spread >= min_spread:
                    pair_key = tuple(sorted([market1.id, market2.id]))
                    if pair_key not in checked_pairs:
                        checked_pairs.add(pair_key)
                        
                        opportunities.append({
                            "market1": market1,
                            "market2": market2,
                            "spread": spread,
                            "spread_pct": f"{spread * 100:.1f}%",
                            "similarity": similarity,
                        })
        
        # Sort by spread (largest first)
        opportunities.sort(key=lambda x: x["spread"], reverse=True)
        
        return opportunities
    
    def compare_markets(self, market_ids: List[str]) -> List[Market]:
        """Get multiple markets for comparison."""
        markets = []
        for mid in market_ids:
            market = self.get_market(mid)
            if market:
                markets.append(market)
        return markets
    
    def get_platform_stats(self) -> Dict[str, Any]:
        """Get stats about enabled platforms."""
        stats = {
            "enabled_platforms": [p.value for p in self.enabled_platforms],
            "platform_count": len(self.enabled_platforms),
        }
        
        # Get sample market counts
        for platform in self.enabled_platforms:
            try:
                markets = self.clients[platform].get_trending_markets(limit=1)
                stats[f"{platform.value}_connected"] = True
            except Exception:
                stats[f"{platform.value}_connected"] = False
        
        return stats
    
    def close(self):
        """Close all client connections."""
        for client in self.clients.values():
            client.close()


# Async version
class AsyncPredictionMarketAggregator:
    """Async version of the aggregator."""
    
    def __init__(
        self,
        enable_manifold: bool = True,
        enable_metaculus: bool = True,
        enable_predictit: bool = True,
        enable_polymarket: bool = True,
        manifold_api_key: Optional[str] = None,
        metaculus_api_key: Optional[str] = None,
        polymarket_api_key: Optional[str] = None,
    ):
        self.clients: Dict[Platform, Any] = {}
        
        if enable_manifold:
            self.clients[Platform.MANIFOLD] = AsyncManifoldClient(api_key=manifold_api_key)
        
        if enable_metaculus:
            self.clients[Platform.METACULUS] = AsyncMetaculusClient(api_key=metaculus_api_key)
        
        if enable_predictit:
            self.clients[Platform.PREDICTIT] = AsyncPredictItClient()
        
        if enable_polymarket:
            self.clients[Platform.POLYMARKET] = AsyncPolymarketDirectClient(api_key=polymarket_api_key)
    
    @property
    def enabled_platforms(self) -> List[Platform]:
        return list(self.clients.keys())
    
    async def search_all(
        self,
        query: str,
        limit_per_platform: int = 10,
        platforms: Optional[List[Platform]] = None
    ) -> Dict[Platform, List[Market]]:
        target_platforms = platforms or self.enabled_platforms
        
        async def search_platform(platform: Platform) -> Tuple[Platform, List[Market]]:
            client = self.clients.get(platform)
            if not client:
                return (platform, [])
            try:
                markets = await client.search_markets(query, limit=limit_per_platform)
                return (platform, markets)
            except Exception as e:
                print(f"Error searching {platform.value}: {e}")
                return (platform, [])
        
        tasks = [search_platform(p) for p in target_platforms if p in self.clients]
        results_list = await asyncio.gather(*tasks)
        
        return {platform: markets for platform, markets in results_list}
    
    async def get_trending_all(
        self,
        limit_per_platform: int = 10,
        platforms: Optional[List[Platform]] = None
    ) -> Dict[Platform, List[Market]]:
        target_platforms = platforms or self.enabled_platforms
        
        async def get_trending(platform: Platform) -> Tuple[Platform, List[Market]]:
            client = self.clients.get(platform)
            if not client:
                return (platform, [])
            try:
                markets = await client.get_trending_markets(limit=limit_per_platform)
                return (platform, markets)
            except Exception as e:
                print(f"Error getting trending from {platform.value}: {e}")
                return (platform, [])
        
        tasks = [get_trending(p) for p in target_platforms if p in self.clients]
        results_list = await asyncio.gather(*tasks)
        
        return {platform: markets for platform, markets in results_list}
    
    async def close(self):
        """Close all client connections."""
        for client in self.clients.values():
            await client.aclose()
