"""
Prediction Market Platform Integrations for OracleXBT

Direct API connections to major prediction market platforms.
The Oracle sees all markets! 🔮

Supported Platforms:
- Manifold Markets (play money, great API)
- Metaculus (forecasting, calibration tracking)
- PredictIt (real money, US politics)
- Polymarket (crypto, largest volume)

Usage:
    from agent.platforms import PredictionMarketAggregator
    
    # Search across all platforms
    aggregator = PredictionMarketAggregator()
    results = aggregator.search_all("Bitcoin")
    
    # Or use individual clients
    from agent.platforms import ManifoldClient
    manifold = ManifoldClient()
    markets = manifold.search_markets("AI")
"""

from agent.platforms.base import Platform, Market, MarketHistory, OrderBook
from agent.platforms.manifold import ManifoldClient, AsyncManifoldClient
from agent.platforms.metaculus import MetaculusClient, AsyncMetaculusClient
from agent.platforms.predictit import PredictItClient, AsyncPredictItClient
from agent.platforms.polymarket_direct import PolymarketDirectClient, AsyncPolymarketDirectClient
from agent.platforms.aggregator import PredictionMarketAggregator, AsyncPredictionMarketAggregator

__all__ = [
    # Core types
    "Platform",
    "Market", 
    "MarketHistory",
    "OrderBook",
    
    # Aggregator (main interface)
    "PredictionMarketAggregator",
    "AsyncPredictionMarketAggregator",
    
    # Individual clients
    "ManifoldClient",
    "AsyncManifoldClient",
    "MetaculusClient",
    "AsyncMetaculusClient",
    "PredictItClient",
    "AsyncPredictItClient",
    "PolymarketDirectClient",
    "AsyncPolymarketDirectClient",
]

