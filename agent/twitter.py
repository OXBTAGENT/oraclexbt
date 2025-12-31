"""Twitter/X client for the Prediction Market Agent."""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

logger = logging.getLogger("agent.twitter")


class TweetType(Enum):
    """Types of tweets the agent can post."""
    MARKET_INSIGHT = "market_insight"
    ARBITRAGE_ALERT = "arbitrage_alert"
    PRICE_MOVEMENT = "price_movement"
    DAILY_SUMMARY = "daily_summary"
    REPLY = "reply"
    QUOTE = "quote"


@dataclass
class Tweet:
    """Represents a tweet."""
    id: Optional[str]
    text: str
    author_id: Optional[str] = None
    author_username: Optional[str] = None
    created_at: Optional[datetime] = None
    conversation_id: Optional[str] = None
    in_reply_to_user_id: Optional[str] = None
    metrics: Optional[dict] = None


@dataclass
class TwitterConfig:
    """Configuration for Twitter API access."""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    bearer_token: Optional[str] = None
    
    # Agent settings
    max_tweet_length: int = 280
    enable_threads: bool = True
    
    def __post_init__(self):
        """Load from environment if not provided."""
        self.api_key = self.api_key or os.getenv("TWITTER_API_KEY")
        self.api_secret = self.api_secret or os.getenv("TWITTER_API_SECRET")
        self.access_token = self.access_token or os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = self.access_token_secret or os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        self.bearer_token = self.bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
    
    @property
    def is_configured(self) -> bool:
        """Check if Twitter credentials are configured."""
        return all([
            self.api_key,
            self.api_secret, 
            self.access_token,
            self.access_token_secret
        ])
    
    @classmethod
    def from_env(cls) -> TwitterConfig:
        """Create config from environment variables."""
        return cls()


# Key prediction market accounts on X
PREDICTION_MARKET_ACCOUNTS = {
    "polymarket": {
        "username": "Polymarket",
        "user_id": "1246931106031476736",
        "description": "Polymarket official account"
    },
    "kalshi": {
        "username": "Kalshi", 
        "user_id": "1285655947215048704",
        "description": "Kalshi official account"
    },
    "metaculus": {
        "username": "metacaboringulus",
        "user_id": "842115495715white white white white white white whitespace828288",
        "description": "Metaculus forecasting"
    },
    "manifold": {
        "username": "ManifoldMarkets",
        "user_id": "1466445683550208002",
        "description": "Manifold Markets"
    },
    "predictit": {
        "username": "PredictIt",
        "user_id": "2875639644",
        "description": "PredictIt official"
    }
}


class TwitterClient:
    """
    Client for interacting with Twitter/X API.
    
    Supports both tweepy (v1.1 + v2) for full functionality.
    """
    
    def __init__(self, config: Optional[TwitterConfig] = None):
        """Initialize the Twitter client."""
        self.config = config or TwitterConfig.from_env()
        self._client = None
        self._api = None
        
        if self.config.is_configured:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the tweepy client."""
        try:
            import tweepy
            
            # V2 Client for most operations
            self._client = tweepy.Client(
                consumer_key=self.config.api_key,
                consumer_secret=self.config.api_secret,
                access_token=self.config.access_token,
                access_token_secret=self.config.access_token_secret,
                bearer_token=self.config.bearer_token,
                wait_on_rate_limit=True
            )
            
            # V1.1 API for media uploads
            auth = tweepy.OAuth1UserHandler(
                self.config.api_key,
                self.config.api_secret,
                self.config.access_token,
                self.config.access_token_secret
            )
            self._api = tweepy.API(auth)
            
            logger.info("Twitter client initialized successfully")
            
        except ImportError:
            raise ImportError(
                "tweepy package required for Twitter integration. "
                "Install with: pip install tweepy"
            )
    
    @property
    def is_ready(self) -> bool:
        """Check if the client is ready to use."""
        return self._client is not None
    
    def post_tweet(
        self,
        text: str,
        reply_to: Optional[str] = None,
        quote_tweet_id: Optional[str] = None,
        media_ids: Optional[list[str]] = None
    ) -> Tweet:
        """
        Post a tweet.
        
        Args:
            text: Tweet content (max 280 chars)
            reply_to: Tweet ID to reply to
            quote_tweet_id: Tweet ID to quote
            media_ids: List of media IDs to attach
            
        Returns:
            The posted Tweet
        """
        if not self.is_ready:
            raise RuntimeError("Twitter client not initialized. Check credentials.")
        
        # Truncate if needed
        if len(text) > self.config.max_tweet_length:
            text = text[:277] + "..."
        
        kwargs = {"text": text}
        
        if reply_to:
            kwargs["in_reply_to_tweet_id"] = reply_to
        if quote_tweet_id:
            kwargs["quote_tweet_id"] = quote_tweet_id
        if media_ids:
            kwargs["media_ids"] = media_ids
        
        response = self._client.create_tweet(**kwargs)
        
        return Tweet(
            id=response.data["id"],
            text=text,
            created_at=datetime.now()
        )
    
    def post_thread(self, tweets: list[str]) -> list[Tweet]:
        """
        Post a thread of tweets.
        
        Args:
            tweets: List of tweet texts
            
        Returns:
            List of posted Tweets
        """
        if not tweets:
            return []
        
        posted = []
        reply_to = None
        
        for text in tweets:
            tweet = self.post_tweet(text, reply_to=reply_to)
            posted.append(tweet)
            reply_to = tweet.id
        
        return posted
    
    def reply_to_tweet(self, tweet_id: str, text: str) -> Tweet:
        """Reply to a specific tweet."""
        return self.post_tweet(text, reply_to=tweet_id)
    
    def quote_tweet(self, tweet_id: str, text: str) -> Tweet:
        """Quote retweet with comment."""
        return self.post_tweet(text, quote_tweet_id=tweet_id)
    
    def search_tweets(
        self,
        query: str,
        max_results: int = 10,
        sort_order: str = "recency"
    ) -> list[Tweet]:
        """
        Search for tweets.
        
        Args:
            query: Search query
            max_results: Maximum tweets to return
            sort_order: "recency" or "relevancy"
        """
        if not self.is_ready:
            raise RuntimeError("Twitter client not initialized")
        
        response = self._client.search_recent_tweets(
            query=query,
            max_results=min(max_results, 100),
            sort_order=sort_order,
            tweet_fields=["created_at", "author_id", "conversation_id", "public_metrics"],
            expansions=["author_id"]
        )
        
        tweets = []
        if response.data:
            # Build author lookup
            authors = {}
            if response.includes and "users" in response.includes:
                authors = {u.id: u.username for u in response.includes["users"]}
            
            for tweet in response.data:
                tweets.append(Tweet(
                    id=tweet.id,
                    text=tweet.text,
                    author_id=tweet.author_id,
                    author_username=authors.get(tweet.author_id),
                    created_at=tweet.created_at,
                    conversation_id=tweet.conversation_id,
                    metrics=tweet.public_metrics
                ))
        
        return tweets
    
    def get_user_tweets(
        self,
        username: str,
        max_results: int = 10
    ) -> list[Tweet]:
        """Get recent tweets from a specific user."""
        if not self.is_ready:
            raise RuntimeError("Twitter client not initialized")
        
        # Get user ID
        user = self._client.get_user(username=username)
        if not user.data:
            return []
        
        response = self._client.get_users_tweets(
            id=user.data.id,
            max_results=min(max_results, 100),
            tweet_fields=["created_at", "public_metrics"]
        )
        
        tweets = []
        if response.data:
            for tweet in response.data:
                tweets.append(Tweet(
                    id=tweet.id,
                    text=tweet.text,
                    author_id=user.data.id,
                    author_username=username,
                    created_at=tweet.created_at,
                    metrics=tweet.public_metrics
                ))
        
        return tweets
    
    def get_tweet(self, tweet_id: str) -> Optional[Tweet]:
        """Get a specific tweet by ID."""
        if not self.is_ready:
            raise RuntimeError("Twitter client not initialized")
        
        response = self._client.get_tweet(
            id=tweet_id,
            tweet_fields=["created_at", "author_id", "conversation_id", "public_metrics"],
            expansions=["author_id"]
        )
        
        if not response.data:
            return None
        
        author_username = None
        if response.includes and "users" in response.includes:
            author_username = response.includes["users"][0].username
        
        return Tweet(
            id=response.data.id,
            text=response.data.text,
            author_id=response.data.author_id,
            author_username=author_username,
            created_at=response.data.created_at,
            conversation_id=response.data.conversation_id,
            metrics=response.data.public_metrics
        )
    
    def get_mentions(self, max_results: int = 10) -> list[Tweet]:
        """Get recent mentions of the authenticated user."""
        if not self.is_ready:
            raise RuntimeError("Twitter client not initialized")
        
        # Get authenticated user ID
        me = self._client.get_me()
        if not me.data:
            return []
        
        response = self._client.get_users_mentions(
            id=me.data.id,
            max_results=min(max_results, 100),
            tweet_fields=["created_at", "author_id", "conversation_id"],
            expansions=["author_id"]
        )
        
        tweets = []
        if response.data:
            authors = {}
            if response.includes and "users" in response.includes:
                authors = {u.id: u.username for u in response.includes["users"]}
            
            for tweet in response.data:
                tweets.append(Tweet(
                    id=tweet.id,
                    text=tweet.text,
                    author_id=tweet.author_id,
                    author_username=authors.get(tweet.author_id),
                    created_at=tweet.created_at,
                    conversation_id=tweet.conversation_id
                ))
        
        return tweets
    
    def like_tweet(self, tweet_id: str) -> bool:
        """Like a tweet."""
        if not self.is_ready:
            return False
        
        try:
            me = self._client.get_me()
            self._client.like(me.data.id, tweet_id)
            return True
        except Exception as e:
            logger.error(f"Failed to like tweet: {e}")
            return False
    
    def retweet(self, tweet_id: str) -> bool:
        """Retweet a tweet."""
        if not self.is_ready:
            return False
        
        try:
            me = self._client.get_me()
            self._client.retweet(me.data.id, tweet_id)
            return True
        except Exception as e:
            logger.error(f"Failed to retweet: {e}")
            return False


class TweetComposer:
    """
    Helper class for composing prediction market tweets.
    
    Handles formatting and thread creation without hashtags.
    """
    
    @classmethod
    def market_insight(
        cls,
        market_title: str,
        yes_price: float,
        insight: str,
        market_url: Optional[str] = None,
        category: str = "general"
    ) -> str:
        """Compose a market insight tweet."""
        price_str = f"{yes_price:.0%}"
        
        parts = [
            f"📊 {market_title}",
            f"",
            f"Current odds: {price_str} Yes",
            f"",
            insight
        ]
        
        if market_url:
            parts.append(f"")
            parts.append(market_url)
        
        return "\n".join(parts)
    
    @classmethod
    def arbitrage_alert(
        cls,
        event: str,
        platform_a: str,
        price_a: float,
        platform_b: str,
        price_b: float,
        spread: float
    ) -> str:
        """Compose an arbitrage alert tweet."""
        return (
            f"Arbitrage opportunity: {event}\n\n"
            f"{platform_a}: {price_a:.0%}\n"
            f"{platform_b}: {price_b:.0%}\n"
            f"Spread: {spread:.1f}%"
        )
    
    @classmethod
    def price_movement(
        cls,
        market_title: str,
        old_price: float,
        new_price: float,
        timeframe: str = "24h"
    ) -> str:
        """Compose a price movement alert."""
        change = (new_price - old_price) * 100
        direction = "up" if change > 0 else "down"
        
        return (
            f"Price movement: {market_title}\n\n"
            f"Was: {old_price:.0%} → Now: {new_price:.0%}\n"
            f"Change: {change:+.1f}% ({timeframe})"
        )
    
    @classmethod
    def daily_summary(
        cls,
        top_markets: list[dict],
        total_volume: str
    ) -> list[str]:
        """Compose a daily summary thread."""
        tweets = []
        
        # Header tweet
        tweets.append(
            f"Daily prediction markets roundup\n\n"
            f"Total volume today: {total_volume}\n\n"
            f"Top markets by activity:"
        )
        
        # Individual market tweets
        for i, market in enumerate(top_markets[:5], 1):
            tweet = (
                f"{i}. {market['title']}\n\n"
                f"Odds: {market['yes_price']:.0%} Yes\n"
                f"Volume: {market['volume']}"
            )
            if market.get('url'):
                tweet += f"\n{market['url']}"
            tweets.append(tweet)
        
        return tweets
    
    @classmethod
    def reply_with_data(
        cls,
        question: str,
        market_title: str,
        yes_price: float,
        source: str
    ) -> str:
        """Compose a data-driven reply."""
        return (
            f"Based on {source} data:\n\n"
            f"📊 {market_title}\n"
            f"Current: {yes_price:.0%} Yes\n\n"
            f"Prediction markets aggregate crowd wisdom on this!"
        )
