"""Tools that the agent can use to interact with prediction markets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Optional

from oraclyst_sdk import OraclystClient, Market, PriceHistory, TickerItem

# Import trading tools
try:
    from agent.trading_tools import TRADING_TOOLS
    TRADING_ENABLED = True
except ImportError:
    TRADING_TOOLS = []
    TRADING_ENABLED = False


# Tool definitions for LLM function calling
TOOL_DEFINITIONS = [
    {
        "name": "search_markets",
        "description": "Search for prediction markets by keyword, category, or provider. Use this to find markets about specific topics.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'Trump', 'Bitcoin', 'Super Bowl')"
                },
                "category": {
                    "type": "string",
                    "description": "Category filter (e.g., 'Politics', 'Crypto', 'Sports', 'Science')",
                    "enum": ["Politics", "Crypto", "Sports", "Science", "Economics", "Entertainment", "Technology"]
                },
                "provider": {
                    "type": "string", 
                    "description": "Market provider filter",
                    "enum": ["polymarket", "kalshi", "limitless"]
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default 10)",
                    "default": 10
                }
            },
            "required": []
        }
    },
    {
        "name": "get_market_details",
        "description": "Get detailed information about a specific market by its ID. Use this after finding markets to get more details.",
        "parameters": {
            "type": "object",
            "properties": {
                "market_id": {
                    "type": "string",
                    "description": "The market ID (e.g., 'pm-551963' for Polymarket, 'kalshi-ABC' for Kalshi)"
                }
            },
            "required": ["market_id"]
        }
    },
    {
        "name": "get_price_history",
        "description": "Get historical price data for a market. Useful for analyzing trends and momentum.",
        "parameters": {
            "type": "object",
            "properties": {
                "market_id": {
                    "type": "string",
                    "description": "The market ID"
                },
                "time_range": {
                    "type": "string",
                    "description": "Time range for history",
                    "enum": ["1h", "6h", "24h", "7d", "30d", "all"],
                    "default": "24h"
                }
            },
            "required": ["market_id"]
        }
    },
    {
        "name": "find_arbitrage",
        "description": "Scan for arbitrage opportunities - price discrepancies across different platforms for similar events.",
        "parameters": {
            "type": "object",
            "properties": {
                "min_spread": {
                    "type": "number",
                    "description": "Minimum spread percentage to report (default 1.0)",
                    "default": 1.0
                },
                "limit": {
                    "type": "integer", 
                    "description": "Maximum opportunities to return",
                    "default": 10
                }
            },
            "required": []
        }
    },
    {
        "name": "get_trending_markets",
        "description": "Get markets with highest recent volume or price movement. Good for finding active markets.",
        "parameters": {
            "type": "object",
            "properties": {
                "sort_by": {
                    "type": "string",
                    "description": "How to sort results",
                    "enum": ["volume", "volume_24h", "price_change"],
                    "default": "volume_24h"
                },
                "category": {
                    "type": "string",
                    "description": "Optional category filter"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of markets to return",
                    "default": 10
                }
            },
            "required": []
        }
    },
    {
        "name": "compare_markets",
        "description": "Compare multiple markets side-by-side. Useful for analyzing related markets or finding best odds.",
        "parameters": {
            "type": "object",
            "properties": {
                "market_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of market IDs to compare"
                }
            },
            "required": ["market_ids"]
        }
    },
    {
        "name": "analyze_market",
        "description": "Perform deep analysis on a market including price trends, volume analysis, and generate insights.",
        "parameters": {
            "type": "object",
            "properties": {
                "market_id": {
                    "type": "string",
                    "description": "The market ID to analyze"
                }
            },
            "required": ["market_id"]
        }
    },
    {
        "name": "get_orderbook",
        "description": "Get the order book (bids and asks) for a market. Shows liquidity depth.",
        "parameters": {
            "type": "object", 
            "properties": {
                "market_id": {
                    "type": "string",
                    "description": "The market ID"
                }
            },
            "required": ["market_id"]
        }
    }
]

# Add trading tools if available
if TRADING_ENABLED:
    TOOL_DEFINITIONS.extend(TRADING_TOOLS)


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    data: Any
    error: Optional[str] = None
    
    def to_message(self) -> str:
        """Convert to a message string for the LLM."""
        if self.success:
            if isinstance(self.data, str):
                return self.data
            return json.dumps(self.data, indent=2, default=str)
        return f"Error: {self.error}"


class AgentTools:
    """
    Tools for the prediction market agent.
    
    Wraps the Oraclyst SDK with additional analysis and formatting
    for agent consumption.
    """
    
    def __init__(self, client: Optional[OraclystClient] = None):
        """Initialize with an Oraclyst client."""
        self._client = client or OraclystClient()
        self._owns_client = client is None
        
        # Register tool handlers
        self._handlers: dict[str, Callable] = {
            "search_markets": self.search_markets,
            "get_market_details": self.get_market_details,
            "get_price_history": self.get_price_history,
            "find_arbitrage": self.find_arbitrage,
            "get_trending_markets": self.get_trending_markets,
            "compare_markets": self.compare_markets,
            "analyze_market": self.analyze_market,
            "get_orderbook": self.get_orderbook,
        }
    
    def execute(self, tool_name: str, arguments: dict[str, Any]) -> ToolResult:
        """Execute a tool by name with arguments."""
        if tool_name not in self._handlers:
            return ToolResult(
                success=False,
                data=None,
                error=f"Unknown tool: {tool_name}"
            )
        
        try:
            result = self._handlers[tool_name](**arguments)
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))
    
    def search_markets(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        provider: Optional[str] = None,
        limit: int = 10
    ) -> list[dict]:
        """Search for markets matching criteria."""
        kwargs = {"limit": limit}
        if query:
            kwargs["search"] = query
        if category:
            kwargs["category"] = category
        if provider:
            kwargs["provider"] = provider
        
        response = self._client.list_markets(**kwargs)
        
        return [self._format_market_summary(m) for m in response.data]
    
    def get_market_details(self, market_id: str) -> dict:
        """Get detailed market information."""
        market = self._client.get_market(market_id)
        return self._format_market_detail(market)
    
    def get_price_history(self, market_id: str, time_range: str = "24h") -> dict:
        """Get price history for a market."""
        history = self._client.get_price_history(market_id, range=time_range)
        
        result = {
            "market_id": market_id,
            "time_range": time_range,
            "points_count": len(history.points) if history.points else 0,
        }
        
        if history.points:
            result["latest"] = {
                "timestamp": str(history.latest.timestamp),
                "yes_price": history.latest.yes_price,
                "no_price": history.latest.no_price,
            }
            result["earliest"] = {
                "timestamp": str(history.points[0].timestamp),
                "yes_price": history.points[0].yes_price,
                "no_price": history.points[0].no_price,
            }
            
            # Calculate price change
            if history.points[0].yes_price and history.latest.yes_price:
                change = history.latest.yes_price - history.points[0].yes_price
                result["price_change"] = {
                    "absolute": round(change, 4),
                    "percent": round(change * 100, 2)
                }
            
            # Sample some intermediate points
            if len(history.points) > 5:
                step = len(history.points) // 5
                result["sample_points"] = [
                    {
                        "timestamp": str(p.timestamp),
                        "yes_price": p.yes_price
                    }
                    for p in history.points[::step]
                ]
        
        return result
    
    def find_arbitrage(self, min_spread: float = 1.0, limit: int = 10) -> list[dict]:
        """Find arbitrage opportunities."""
        ticker = self._client.get_arb_scanner()
        
        opportunities = []
        for item in ticker:
            if item.spread and item.spread >= min_spread:
                opportunities.append({
                    "event": item.event,
                    "spread": item.spread,
                    "markets": [
                        {
                            "source": m.source if hasattr(m, 'source') else "unknown",
                            "yes_price": m.yes_price if hasattr(m, 'yes_price') else None,
                        }
                        for m in (item.markets if hasattr(item, 'markets') else [])
                    ]
                })
            
            if len(opportunities) >= limit:
                break
        
        return opportunities
    
    def get_trending_markets(
        self,
        sort_by: str = "volume_24h",
        category: Optional[str] = None,
        limit: int = 10
    ) -> list[dict]:
        """Get trending/high-volume markets."""
        kwargs = {"limit": limit * 2}  # Get extra to filter
        if category:
            kwargs["category"] = category
        
        response = self._client.list_markets(**kwargs)
        markets = list(response.data)
        
        # Sort by requested field
        def get_sort_key(m: Market):
            if sort_by == "volume":
                return self._parse_volume(m.volume)
            elif sort_by == "volume_24h" and m.volume_24h:
                return self._parse_volume(m.volume_24h)
            elif sort_by == "price_change":
                return abs(m.outcomes[0].change) if m.outcomes else 0
            return 0
        
        markets.sort(key=get_sort_key, reverse=True)
        
        return [self._format_market_summary(m) for m in markets[:limit]]
    
    def compare_markets(self, market_ids: list[str]) -> list[dict]:
        """Compare multiple markets."""
        results = []
        for mid in market_ids:
            try:
                market = self._client.get_market(mid)
                results.append(self._format_market_detail(market))
            except Exception as e:
                results.append({"market_id": mid, "error": str(e)})
        
        return results
    
    def analyze_market(self, market_id: str) -> dict:
        """Deep analysis of a market."""
        market = self._client.get_market(market_id)
        history = self._client.get_price_history(market_id, range="7d")
        
        analysis = {
            "market": self._format_market_detail(market),
            "trend_analysis": {},
            "volume_analysis": {},
            "insights": []
        }
        
        # Trend analysis
        if history.points and len(history.points) >= 2:
            first_price = history.points[0].yes_price or 0
            last_price = history.latest.yes_price or 0
            change = last_price - first_price
            
            analysis["trend_analysis"] = {
                "7d_change": round(change * 100, 2),
                "trend": "bullish" if change > 0.02 else "bearish" if change < -0.02 else "sideways",
                "volatility": self._calculate_volatility(history.points)
            }
        
        # Volume analysis
        volume = self._parse_volume(market.volume)
        volume_24h = self._parse_volume(market.volume_24h) if market.volume_24h else 0
        
        analysis["volume_analysis"] = {
            "total_volume": volume,
            "volume_24h": volume_24h,
            "liquidity_rating": "high" if volume > 100000 else "medium" if volume > 10000 else "low"
        }
        
        # Generate insights
        insights = []
        
        if market.yes_price:
            if market.yes_price > 0.9:
                insights.append("Market is highly confident (>90%) in YES outcome")
            elif market.yes_price < 0.1:
                insights.append("Market is highly confident (>90%) in NO outcome")
            elif 0.45 < market.yes_price < 0.55:
                insights.append("Market is uncertain - essentially a coin flip")
        
        if volume_24h > volume * 0.1:
            insights.append("High recent activity - 24h volume is >10% of total")
        
        if analysis["trend_analysis"].get("trend") == "bullish":
            insights.append("Trending upward over the past 7 days")
        elif analysis["trend_analysis"].get("trend") == "bearish":
            insights.append("Trending downward over the past 7 days")
        
        analysis["insights"] = insights
        
        return analysis
    
    def get_orderbook(self, market_id: str) -> dict:
        """Get orderbook for a market."""
        try:
            orderbook = self._client.get_orderbook(market_id)
            return {
                "market_id": market_id,
                "bids": [{"price": b.price, "size": b.size} for b in orderbook.bids[:10]],
                "asks": [{"price": a.price, "size": a.size} for a in orderbook.asks[:10]],
                "spread": orderbook.spread if hasattr(orderbook, 'spread') else None,
                "mid_price": orderbook.mid_price if hasattr(orderbook, 'mid_price') else None,
            }
        except Exception as e:
            return {"market_id": market_id, "error": str(e)}
    
    # Helper methods
    
    def _format_market_summary(self, market: Market) -> dict:
        """Format market for summary display."""
        return {
            "id": market.id,
            "title": market.title,
            "source": market.source.value if hasattr(market.source, 'value') else str(market.source),
            "yes_price": market.yes_price,
            "no_price": market.no_price,
            "volume": market.volume,
            "categories": market.categories,
        }
    
    def _format_market_detail(self, market: Market) -> dict:
        """Format market with full details."""
        return {
            "id": market.id,
            "source_id": market.source_id,
            "source": market.source.value if hasattr(market.source, 'value') else str(market.source),
            "title": market.title,
            "description": market.description,
            "outcomes": [
                {"name": o.name, "price": o.price, "change": o.change}
                for o in market.outcomes
            ],
            "yes_price": market.yes_price,
            "no_price": market.no_price,
            "volume": market.volume,
            "volume_24h": market.volume_24h,
            "liquidity": market.liquidity,
            "expiry_date": market.expiry_date,
            "categories": market.categories,
            "market_url": market.market_url,
            "status": market.status.value if hasattr(market.status, 'value') else str(market.status),
        }
    
    def _parse_volume(self, volume: Optional[str]) -> float:
        """Parse volume string to float."""
        if not volume:
            return 0.0
        
        # Remove currency symbols and commas
        clean = volume.replace("$", "").replace(",", "").strip()
        
        # Handle K/M/B suffixes
        multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}
        for suffix, mult in multipliers.items():
            if clean.upper().endswith(suffix):
                return float(clean[:-1]) * mult
        
        try:
            return float(clean)
        except ValueError:
            return 0.0
    
    def _calculate_volatility(self, points: list) -> str:
        """Calculate simple volatility measure."""
        if len(points) < 2:
            return "unknown"
        
        prices = [p.yes_price for p in points if p.yes_price is not None]
        if len(prices) < 2:
            return "unknown"
        
        # Calculate standard deviation
        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        std_dev = variance ** 0.5
        
        if std_dev > 0.1:
            return "high"
        elif std_dev > 0.03:
            return "medium"
        return "low"
    
    def close(self):
        """Close the underlying client if we own it."""
        if self._owns_client:
            self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
