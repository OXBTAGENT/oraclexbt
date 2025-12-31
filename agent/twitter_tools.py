"""Twitter/X tools for the Prediction Market Agent."""

from __future__ import annotations

import json
from typing import Any, Optional

from agent.twitter import (
    TwitterClient,
    TwitterConfig,
    TweetComposer,
    Tweet,
    PREDICTION_MARKET_ACCOUNTS
)


# Twitter tool definitions for LLM function calling
TWITTER_TOOL_DEFINITIONS = [
    {
        "name": "post_tweet",
        "description": "Post a tweet to X/Twitter. Use this to share market insights, analysis, or findings with followers. Keep tweets concise and engaging.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The tweet content (max 280 characters). Should be engaging and informative."
                },
                "tweet_type": {
                    "type": "string",
                    "description": "Type of tweet for formatting help",
                    "enum": ["market_insight", "arbitrage_alert", "price_movement", "general"]
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "post_thread",
        "description": "Post a thread of multiple connected tweets. Use for detailed analysis that needs more than 280 characters.",
        "parameters": {
            "type": "object",
            "properties": {
                "tweets": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of tweets to post as a thread (each max 280 chars)"
                }
            },
            "required": ["tweets"]
        }
    },
    {
        "name": "reply_to_tweet",
        "description": "Reply to a specific tweet. Use to engage with prediction market discussions or answer questions.",
        "parameters": {
            "type": "object",
            "properties": {
                "tweet_id": {
                    "type": "string",
                    "description": "The ID of the tweet to reply to"
                },
                "text": {
                    "type": "string",
                    "description": "Your reply text (max 280 characters)"
                }
            },
            "required": ["tweet_id", "text"]
        }
    },
    {
        "name": "quote_tweet",
        "description": "Quote retweet with your commentary. Good for adding context or analysis to existing tweets.",
        "parameters": {
            "type": "object",
            "properties": {
                "tweet_id": {
                    "type": "string",
                    "description": "The ID of the tweet to quote"
                },
                "text": {
                    "type": "string",
                    "description": "Your commentary (max 280 characters)"
                }
            },
            "required": ["tweet_id", "text"]
        }
    },
    {
        "name": "search_prediction_market_tweets",
        "description": "Search X/Twitter for tweets about prediction markets. Find discussions, news, and opportunities.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'polymarket bitcoin', 'prediction market election')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of tweets to return",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_platform_tweets",
        "description": "Get recent tweets from a prediction market platform's official account.",
        "parameters": {
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "description": "The platform to get tweets from",
                    "enum": ["polymarket", "kalshi", "metaculus", "manifold", "predictit"]
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum tweets to return",
                    "default": 5
                }
            },
            "required": ["platform"]
        }
    },
    {
        "name": "get_tweet_details",
        "description": "Get details about a specific tweet including engagement metrics.",
        "parameters": {
            "type": "object",
            "properties": {
                "tweet_id": {
                    "type": "string",
                    "description": "The tweet ID to look up"
                }
            },
            "required": ["tweet_id"]
        }
    },
    {
        "name": "get_mentions",
        "description": "Get recent mentions of the agent's Twitter account. Use to find questions or discussions to engage with.",
        "parameters": {
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Maximum mentions to return",
                    "default": 10
                }
            },
            "required": []
        }
    },
    {
        "name": "compose_market_tweet",
        "description": "Generate a well-formatted tweet about a prediction market. Provides template-based formatting.",
        "parameters": {
            "type": "object",
            "properties": {
                "market_title": {
                    "type": "string",
                    "description": "The market title/question"
                },
                "yes_price": {
                    "type": "number",
                    "description": "Current YES price (0-1)"
                },
                "insight": {
                    "type": "string",
                    "description": "Your insight or analysis about the market"
                },
                "category": {
                    "type": "string",
                    "description": "Market category for hashtag selection",
                    "enum": ["politics", "crypto", "sports", "general"]
                },
                "market_url": {
                    "type": "string",
                    "description": "Optional URL to the market"
                }
            },
            "required": ["market_title", "yes_price", "insight"]
        }
    },
    {
        "name": "compose_arbitrage_tweet",
        "description": "Generate a formatted arbitrage alert tweet.",
        "parameters": {
            "type": "object",
            "properties": {
                "event": {
                    "type": "string",
                    "description": "The event/question"
                },
                "platform_a": {
                    "type": "string",
                    "description": "First platform name"
                },
                "price_a": {
                    "type": "number",
                    "description": "Price on first platform (0-1)"
                },
                "platform_b": {
                    "type": "string",
                    "description": "Second platform name"
                },
                "price_b": {
                    "type": "number",
                    "description": "Price on second platform (0-1)"
                },
                "spread": {
                    "type": "number",
                    "description": "Spread percentage"
                }
            },
            "required": ["event", "platform_a", "price_a", "platform_b", "price_b", "spread"]
        }
    },
    {
        "name": "like_tweet",
        "description": "Like a tweet. Use to engage positively with good prediction market content.",
        "parameters": {
            "type": "object",
            "properties": {
                "tweet_id": {
                    "type": "string",
                    "description": "The tweet ID to like"
                }
            },
            "required": ["tweet_id"]
        }
    },
    {
        "name": "retweet",
        "description": "Retweet content. Use sparingly for high-quality prediction market news or analysis.",
        "parameters": {
            "type": "object",
            "properties": {
                "tweet_id": {
                    "type": "string",
                    "description": "The tweet ID to retweet"
                }
            },
            "required": ["tweet_id"]
        }
    }
]


class TwitterTools:
    """
    Twitter tools for the prediction market agent.
    
    Enables the agent to post insights, engage with the community,
    and monitor prediction market discussions on X.
    """
    
    def __init__(self, config: Optional[TwitterConfig] = None):
        """Initialize Twitter tools."""
        self.config = config or TwitterConfig.from_env()
        self._client: Optional[TwitterClient] = None
        
        if self.config.is_configured:
            self._client = TwitterClient(self.config)
    
    @property
    def is_available(self) -> bool:
        """Check if Twitter tools are available."""
        return self._client is not None and self._client.is_ready
    
    def execute(self, tool_name: str, arguments: dict[str, Any]) -> dict:
        """Execute a Twitter tool by name."""
        handlers = {
            "post_tweet": self.post_tweet,
            "post_thread": self.post_thread,
            "reply_to_tweet": self.reply_to_tweet,
            "quote_tweet": self.quote_tweet,
            "search_prediction_market_tweets": self.search_tweets,
            "get_platform_tweets": self.get_platform_tweets,
            "get_tweet_details": self.get_tweet_details,
            "get_mentions": self.get_mentions,
            "compose_market_tweet": self.compose_market_tweet,
            "compose_arbitrage_tweet": self.compose_arbitrage_tweet,
            "like_tweet": self.like_tweet,
            "retweet": self.retweet,
        }
        
        if tool_name not in handlers:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
        
        try:
            result = handlers[tool_name](**arguments)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def post_tweet(self, text: str, tweet_type: str = "general") -> dict:
        """Post a tweet."""
        if not self.is_available:
            return {"posted": False, "error": "Twitter not configured", "text": text}
        
        tweet = self._client.post_tweet(text)
        return {
            "posted": True,
            "tweet_id": tweet.id,
            "text": tweet.text,
            "url": f"https://twitter.com/i/status/{tweet.id}"
        }
    
    def post_thread(self, tweets: list[str]) -> dict:
        """Post a thread."""
        if not self.is_available:
            return {"posted": False, "error": "Twitter not configured", "tweets": tweets}
        
        posted = self._client.post_thread(tweets)
        return {
            "posted": True,
            "thread_length": len(posted),
            "tweet_ids": [t.id for t in posted],
            "thread_url": f"https://twitter.com/i/status/{posted[0].id}" if posted else None
        }
    
    def reply_to_tweet(self, tweet_id: str, text: str) -> dict:
        """Reply to a tweet."""
        if not self.is_available:
            return {"posted": False, "error": "Twitter not configured"}
        
        tweet = self._client.reply_to_tweet(tweet_id, text)
        return {
            "posted": True,
            "tweet_id": tweet.id,
            "reply_to": tweet_id,
            "text": tweet.text
        }
    
    def quote_tweet(self, tweet_id: str, text: str) -> dict:
        """Quote a tweet."""
        if not self.is_available:
            return {"posted": False, "error": "Twitter not configured"}
        
        tweet = self._client.quote_tweet(tweet_id, text)
        return {
            "posted": True,
            "tweet_id": tweet.id,
            "quoted": tweet_id,
            "text": tweet.text
        }
    
    def search_tweets(self, query: str, max_results: int = 10) -> list[dict]:
        """Search for tweets about prediction markets."""
        if not self.is_available:
            return [{"error": "Twitter not configured"}]
        
        # Enhance query with prediction market context
        enhanced_query = f"{query} -is:retweet lang:en"
        
        tweets = self._client.search_tweets(enhanced_query, max_results)
        return [self._format_tweet(t) for t in tweets]
    
    def get_platform_tweets(self, platform: str, max_results: int = 5) -> list[dict]:
        """Get tweets from a prediction market platform."""
        if not self.is_available:
            return [{"error": "Twitter not configured"}]
        
        account = PREDICTION_MARKET_ACCOUNTS.get(platform.lower())
        if not account:
            return [{"error": f"Unknown platform: {platform}"}]
        
        tweets = self._client.get_user_tweets(account["username"], max_results)
        return [self._format_tweet(t) for t in tweets]
    
    def get_tweet_details(self, tweet_id: str) -> dict:
        """Get details about a specific tweet."""
        if not self.is_available:
            return {"error": "Twitter not configured"}
        
        tweet = self._client.get_tweet(tweet_id)
        if tweet:
            return self._format_tweet(tweet)
        return {"error": "Tweet not found"}
    
    def get_mentions(self, max_results: int = 10) -> list[dict]:
        """Get recent mentions."""
        if not self.is_available:
            return [{"error": "Twitter not configured"}]
        
        tweets = self._client.get_mentions(max_results)
        return [self._format_tweet(t) for t in tweets]
    
    def compose_market_tweet(
        self,
        market_title: str,
        yes_price: float,
        insight: str,
        category: str = "general",
        market_url: Optional[str] = None
    ) -> dict:
        """Compose a formatted market tweet (doesn't post)."""
        text = TweetComposer.market_insight(
            market_title=market_title,
            yes_price=yes_price,
            insight=insight,
            market_url=market_url,
            category=category
        )
        return {
            "composed": True,
            "text": text,
            "length": len(text),
            "ready_to_post": len(text) <= 280
        }
    
    def compose_arbitrage_tweet(
        self,
        event: str,
        platform_a: str,
        price_a: float,
        platform_b: str,
        price_b: float,
        spread: float
    ) -> dict:
        """Compose a formatted arbitrage alert tweet."""
        text = TweetComposer.arbitrage_alert(
            event=event,
            platform_a=platform_a,
            price_a=price_a,
            platform_b=platform_b,
            price_b=price_b,
            spread=spread
        )
        return {
            "composed": True,
            "text": text,
            "length": len(text),
            "ready_to_post": len(text) <= 280
        }
    
    def like_tweet(self, tweet_id: str) -> dict:
        """Like a tweet."""
        if not self.is_available:
            return {"success": False, "error": "Twitter not configured"}
        
        success = self._client.like_tweet(tweet_id)
        return {"success": success, "tweet_id": tweet_id}
    
    def retweet(self, tweet_id: str) -> dict:
        """Retweet."""
        if not self.is_available:
            return {"success": False, "error": "Twitter not configured"}
        
        success = self._client.retweet(tweet_id)
        return {"success": success, "tweet_id": tweet_id}
    
    def _format_tweet(self, tweet: Tweet) -> dict:
        """Format a Tweet object for output."""
        result = {
            "id": tweet.id,
            "text": tweet.text,
            "author": tweet.author_username,
            "created_at": str(tweet.created_at) if tweet.created_at else None,
            "url": f"https://twitter.com/{tweet.author_username}/status/{tweet.id}" if tweet.author_username else None
        }
        
        if tweet.metrics:
            result["metrics"] = {
                "likes": tweet.metrics.get("like_count", 0),
                "retweets": tweet.metrics.get("retweet_count", 0),
                "replies": tweet.metrics.get("reply_count", 0),
                "impressions": tweet.metrics.get("impression_count", 0)
            }
        
        return result
