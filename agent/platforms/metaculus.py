"""
Metaculus API Client

Metaculus is a forecasting platform focused on science, technology, and long-term predictions.
Known for calibration tracking and serious forecasters.
Docs: https://www.metaculus.com/api/
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import os

from .base import BasePlatformClient, Platform, Market, MarketHistory


class MetaculusClient(BasePlatformClient):
    """Client for Metaculus API."""
    
    platform = Platform.METACULUS
    base_url = "https://www.metaculus.com/api2"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Metaculus client.
        
        Args:
            api_key: Optional API key for authenticated requests.
                    Can also be set via METACULUS_API_KEY env var.
        """
        super().__init__(api_key or os.getenv("METACULUS_API_KEY"))
    
    def _parse_market(self, data: Dict[str, Any]) -> Market:
        """Parse Metaculus question data into unified Market object."""
        # Parse timestamps
        created_at = None
        close_time = None
        resolved_at = None
        
        if data.get("created_time"):
            created_at = datetime.fromisoformat(data["created_time"].replace("Z", "+00:00"))
        if data.get("close_time"):
            close_time = datetime.fromisoformat(data["close_time"].replace("Z", "+00:00"))
        if data.get("resolve_time"):
            resolved_at = datetime.fromisoformat(data["resolve_time"].replace("Z", "+00:00"))
        
        # Get community prediction (probability)
        probability = None
        prediction_data = data.get("community_prediction", {})
        if prediction_data:
            # Binary questions have "full" prediction
            if isinstance(prediction_data, dict):
                probability = prediction_data.get("full", {}).get("q2")  # Median
                if probability is None:
                    probability = prediction_data.get("q2")
            elif isinstance(prediction_data, (int, float)):
                probability = prediction_data
        
        # Check resolution
        is_resolved = data.get("resolution") is not None
        resolution = None
        if is_resolved:
            res = data.get("resolution")
            if res == 1:
                resolution = "YES"
            elif res == 0:
                resolution = "NO"
            elif res == -1:
                resolution = "AMBIGUOUS"
            elif res == -2:
                resolution = "ANNULLED"
            else:
                resolution = str(res)
        
        # Get categories/tags
        categories = []
        if data.get("categories"):
            categories = [c.get("name", "") for c in data["categories"] if c.get("name")]
        
        tags = data.get("tags", [])
        if isinstance(tags, list) and tags and isinstance(tags[0], dict):
            tags = [t.get("name", "") for t in tags]
        
        return Market(
            id=f"metaculus-{data['id']}",
            platform=Platform.METACULUS,
            title=data.get("title", ""),
            description=data.get("description", "") or data.get("description_html", ""),
            url=data.get("url", f"https://www.metaculus.com/questions/{data['id']}/"),
            probability=probability,
            yes_price=probability,
            no_price=1 - probability if probability else None,
            volume=data.get("number_of_predictions"),  # Use prediction count as proxy
            liquidity=None,
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
        Get a single question by ID.
        
        Args:
            market_id: Metaculus question ID (with or without 'metaculus-' prefix)
        """
        if market_id.startswith("metaculus-"):
            market_id = market_id[10:]
        
        data = self._request("GET", f"/questions/{market_id}/")
        return self._parse_market(data)
    
    def search_markets(
        self,
        query: str,
        limit: int = 20,
        status: str = "open",  # open, closed, resolved
        order_by: str = "-activity",  # -activity, -publish_time, -close_time, -resolve_time
        **kwargs
    ) -> List[Market]:
        """
        Search for questions.
        
        Args:
            query: Search query
            limit: Max results
            status: Filter by status (open, closed, resolved)
            order_by: Sort order
        """
        params = {
            "search": query,
            "limit": limit,
            "order_by": order_by,
        }
        
        if status == "open":
            params["status"] = "open"
        elif status == "closed":
            params["status"] = "closed"
        elif status == "resolved":
            params["has_resolution"] = "true"
        
        data = self._request("GET", "/questions/", params=params)
        results = data.get("results", [])
        return [self._parse_market(q) for q in results[:limit]]
    
    def get_trending_markets(self, limit: int = 20) -> List[Market]:
        """Get questions with most recent activity."""
        params = {
            "limit": limit,
            "status": "open",
            "order_by": "-activity",
            "type": "forecast",  # Only forecasting questions
        }
        
        data = self._request("GET", "/questions/", params=params)
        results = data.get("results", [])
        return [self._parse_market(q) for q in results[:limit]]
    
    def get_questions_by_topic(
        self, 
        topic: str, 
        limit: int = 20,
        status: str = "open"
    ) -> List[Market]:
        """
        Get questions by topic/category.
        
        Topics include: ai, biosecurity, climate, economics, geopolitics, 
        nuclear, science, space, sports, tech, etc.
        """
        params = {
            "limit": limit,
            "status": status,
            "categories": topic,
            "order_by": "-activity",
        }
        
        data = self._request("GET", "/questions/", params=params)
        results = data.get("results", [])
        return [self._parse_market(q) for q in results[:limit]]
    
    def get_ai_questions(self, limit: int = 20) -> List[Market]:
        """Get AI-related forecasting questions."""
        return self.get_questions_by_topic("ai", limit)
    
    def get_tournament_questions(self, tournament_id: int, limit: int = 50) -> List[Market]:
        """Get questions from a specific tournament."""
        params = {
            "limit": limit,
            "project": tournament_id,
        }
        
        data = self._request("GET", "/questions/", params=params)
        results = data.get("results", [])
        return [self._parse_market(q) for q in results[:limit]]
    
    def get_tournaments(self) -> List[Dict[str, Any]]:
        """Get list of active tournaments/projects."""
        data = self._request("GET", "/projects/")
        return data.get("results", [])
    
    def get_question_history(self, question_id: str) -> Optional[MarketHistory]:
        """Get prediction history for a question."""
        if question_id.startswith("metaculus-"):
            question_id = question_id[10:]
        
        try:
            data = self._request("GET", f"/questions/{question_id}/")
            
            # Metaculus provides prediction history in the question data
            history = data.get("prediction_histogram", [])
            if not history:
                return None
            
            timestamps = []
            prices = []
            
            for point in history:
                if point.get("time") and point.get("community_prediction"):
                    timestamps.append(datetime.fromisoformat(point["time"].replace("Z", "+00:00")))
                    prices.append(point["community_prediction"])
            
            if timestamps:
                return MarketHistory(
                    market_id=f"metaculus-{question_id}",
                    platform=Platform.METACULUS,
                    timestamps=timestamps,
                    prices=prices
                )
        except Exception:
            pass
        
        return None
    
    # ========== Authenticated Methods ==========
    
    def make_prediction(
        self,
        question_id: str,
        prediction: float  # 0-1 for binary, or value for continuous
    ) -> Dict[str, Any]:
        """
        Submit a prediction on a question.
        
        Args:
            question_id: Question ID
            prediction: Your prediction (0-1 for binary questions)
        """
        if not self.api_key:
            raise ValueError("API key required for making predictions")
        
        if question_id.startswith("metaculus-"):
            question_id = question_id[10:]
        
        payload = {"prediction": prediction}
        return self._request("POST", f"/questions/{question_id}/predict/", json=payload)
    
    def get_my_predictions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get your prediction history."""
        if not self.api_key:
            raise ValueError("API key required")
        
        params = {"limit": limit}
        data = self._request("GET", "/predictions/", params=params)
        return data.get("results", [])


# Async version
class AsyncMetaculusClient(MetaculusClient):
    """Async client for Metaculus API."""
    
    async def get_market(self, market_id: str) -> Market:
        if market_id.startswith("metaculus-"):
            market_id = market_id[10:]
        
        data = await self._async_request("GET", f"/questions/{market_id}/")
        return self._parse_market(data)
    
    async def search_markets(
        self,
        query: str,
        limit: int = 20,
        status: str = "open",
        order_by: str = "-activity",
        **kwargs
    ) -> List[Market]:
        params = {
            "search": query,
            "limit": limit,
            "order_by": order_by,
        }
        
        if status == "open":
            params["status"] = "open"
        elif status == "closed":
            params["status"] = "closed"
        elif status == "resolved":
            params["has_resolution"] = "true"
        
        data = await self._async_request("GET", "/questions/", params=params)
        results = data.get("results", [])
        return [self._parse_market(q) for q in results[:limit]]
    
    async def get_trending_markets(self, limit: int = 20) -> List[Market]:
        params = {
            "limit": limit,
            "status": "open", 
            "order_by": "-activity",
            "type": "forecast",
        }
        
        data = await self._async_request("GET", "/questions/", params=params)
        results = data.get("results", [])
        return [self._parse_market(q) for q in results[:limit]]
