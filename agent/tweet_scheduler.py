"""
Hourly Tweet Scheduler for the Prediction Market Agent
Automatically posts diverse, engaging content every hour
"""

import logging
import random
from datetime import datetime
from typing import Callable, List, Optional
from enum import Enum

logger = logging.getLogger("agent.tweet_scheduler")


class TweetContentType(Enum):
    """Types of tweets to post hourly"""
    MARKET_UPDATE = "market_update"
    ARBITRAGE_ALERT = "arbitrage_alert"
    DATA_INSIGHT = "data_insight"
    EDUCATIONAL = "educational"
    PRICE_MOVEMENT = "price_movement"
    VOLUME_ANALYSIS = "volume_analysis"
    PLATFORM_COMPARISON = "platform_comparison"
    RISK_ANALYSIS = "risk_analysis"
    TREND_ANALYSIS = "trend_analysis"
    ENGAGEMENT = "engagement"


class HourlyTweetScheduler:
    """
    Manages hourly tweet scheduling with diverse content types.
    Uses the agent to generate contextually appropriate tweets every hour.
    """
    
    def __init__(self, agent, config: Optional[dict] = None):
        """
        Initialize the hourly tweet scheduler.
        
        Args:
            agent: PredictionMarketAgent instance for generating tweets
            config: Optional configuration dict with settings like:
                - content_types: List of TweetContentType to cycle through
                - randomize_order: Whether to randomize content type order
                - include_threads: Whether to allow multi-tweet threads
                - max_retries: Max attempts to generate valid tweet
        """
        self.agent = agent
        self.config = config or {}
        
        # Default configuration
        self.content_types = self.config.get('content_types', [
            TweetContentType.MARKET_UPDATE,
            TweetContentType.ARBITRAGE_ALERT,
            TweetContentType.DATA_INSIGHT,
            TweetContentType.EDUCATIONAL,
            TweetContentType.PRICE_MOVEMENT,
            TweetContentType.VOLUME_ANALYSIS,
            TweetContentType.PLATFORM_COMPARISON,
            TweetContentType.RISK_ANALYSIS,
            TweetContentType.TREND_ANALYSIS,
            TweetContentType.ENGAGEMENT,
        ])
        
        self.randomize_order = self.config.get('randomize_order', True)
        self.include_threads = self.config.get('include_threads', True)
        self.max_retries = self.config.get('max_retries', 3)
        
        # Track which content type to post next
        self.content_rotation = list(self.content_types)
        if self.randomize_order:
            random.shuffle(self.content_rotation)
        self.current_index = 0
        
        # Track hourly tweet statistics
        self.tweets_posted = 0
        self.failed_attempts = 0
        
    def get_next_content_type(self) -> TweetContentType:
        """Get the next content type to post, cycling through available types"""
        content_type = self.content_rotation[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.content_rotation)
        
        # Reshuffle occasionally for variety
        if self.current_index == 0 and self.randomize_order:
            random.shuffle(self.content_rotation)
        
        return content_type
    
    def _get_prompt_for_content_type(self, content_type: TweetContentType) -> str:
        """Generate a prompt for the agent based on content type"""
        
        prompts = {
            TweetContentType.MARKET_UPDATE: """
            Generate a current market update tweet about prediction markets.
            Include:
            - 1-2 most active markets right now
            - Any significant price movements (>5%)
            - Current volume leaders
            
            Write like a market professional sharing timely info. Keep under 280 chars.
            Make it sound natural and informative, not promotional.
            End with something actionable or interesting.
            """,
            
            TweetContentType.ARBITRAGE_ALERT: """
            Search for current arbitrage opportunities across prediction markets.
            If found, create an alert tweet with:
            - Specific markets and platforms
            - Price discrepancies
            - Potential profit margin
            
            Write professionally. Keep under 280 chars.
            If no good opportunities exist, write about arbitrage importance instead.
            """,
            
            TweetContentType.DATA_INSIGHT: """
            Analyze current prediction market data and share an interesting insight.
            Look for:
            - Unusual probability shifts
            - Volume spikes in specific markets
            - Correlation between markets
            - Historical pattern deviations
            
            Present as a data-driven insight. Keep under 280 chars.
            Sound like a data analyst sharing interesting findings.
            """,
            
            TweetContentType.EDUCATIONAL: """
            Create an educational tweet teaching about prediction markets.
            Pick from:
            - How to read market odds
            - Understanding different platforms
            - Risk management basics
            - Liquidity and slippage concepts
            - Arbitrage identification
            
            Explain clearly with a practical example. Keep under 280 chars.
            Sound like a knowledgeable mentor helping others learn.
            """,
            
            TweetContentType.PRICE_MOVEMENT: """
            Analyze recent significant price movements in prediction markets.
            Include:
            - Which market(s) moved significantly
            - Direction and magnitude of movement
            - Possible reasons (news, data release, etc.)
            - Market context
            
            Write analytically. Keep under 280 chars.
            Help readers understand the drivers behind price action.
            """,
            
            TweetContentType.VOLUME_ANALYSIS: """
            Analyze current trading volume patterns in prediction markets.
            Look at:
            - Which markets have highest volume
            - Volume trends (increasing/decreasing)
            - What this implies about market confidence
            - Liquidity conditions
            
            Present as insightful analysis. Keep under 280 chars.
            Sound like a trader analyzing market health.
            """,
            
            TweetContentType.PLATFORM_COMPARISON: """
            Compare prediction market platforms objectively.
            Choose 2-3 platforms and highlight:
            - Key differences in pricing/liquidity
            - Unique market types each offers
            - Current trading activity on each
            - Platform-specific advantages
            
            Stay neutral and informative. Keep under 280 chars.
            Help traders understand which platform for which use case.
            """,
            
            TweetContentType.RISK_ANALYSIS: """
            Discuss risk management or market risk insights.
            Cover topics like:
            - Position sizing advice
            - When to take profits
            - Portfolio diversification
            - Black swan risk management
            - Liquidity risks
            
            Write professionally and balanced. Keep under 280 chars.
            Sound like an experienced risk manager.
            """,
            
            TweetContentType.TREND_ANALYSIS: """
            Identify and analyze a current trend in prediction markets.
            Could be:
            - Increasing interest in specific event types
            - Platform adoption trends
            - Market maker activity changes
            - Seasonal patterns
            - Topic-based trends (crypto, politics, etc.)
            
            Analyze as a trend analyst. Keep under 280 chars.
            Explain why the trend matters.
            """,
            
            TweetContentType.ENGAGEMENT: """
            Create an engaging, accessible tweet about prediction markets.
            Make it interesting to newcomers and pros alike.
            Could be:
            - Fun market fact
            - Interesting historical parallel
            - "Did you know" insight
            - Market trivia
            - Thought-provoking question
            
            Keep tone conversational and engaging. Keep under 280 chars.
            Get people excited about prediction markets.
            """,
        }
        
        base_prompt = prompts.get(
            content_type,
            "Generate an interesting tweet about prediction markets. Keep under 280 characters."
        )
        
        return base_prompt + """
        
        IMPORTANT:
        - Return ONLY the tweet text, no quotes or explanations
        - Must be under 280 characters
        - Sound natural and professional, not promotional
        - Include specific numbers/data when possible
        - Be genuine and informative
        """
    
    def generate_hourly_tweet(self) -> Optional[str]:
        """
        Generate an hourly tweet with content appropriate to the current time.
        
        Returns:
            The generated tweet text, or None if generation failed
        """
        content_type = self.get_next_content_type()
        
        for attempt in range(self.max_retries):
            try:
                prompt = self._get_prompt_for_content_type(content_type)
                
                logger.info(f"Generating {content_type.value} tweet (attempt {attempt + 1})")
                
                response = self.agent.chat(prompt)
                
                # Validate response
                if not response or len(response.strip()) < 10:
                    logger.warning(f"Generated tweet too short: {response}")
                    continue
                
                # Clean response (remove quotes if present)
                tweet_text = response.strip().strip('"\'')
                
                # Ensure it fits in 280 characters
                if len(tweet_text) > 280:
                    tweet_text = tweet_text[:277] + "..."
                
                logger.info(f"Successfully generated {content_type.value} tweet")
                self.tweets_posted += 1
                
                return tweet_text
                
            except Exception as e:
                logger.error(f"Error generating {content_type.value} tweet (attempt {attempt + 1}): {e}")
                self.failed_attempts += 1
                continue
        
        logger.error(f"Failed to generate {content_type.value} tweet after {self.max_retries} attempts")
        return None
    
    def post_hourly_tweet(self) -> bool:
        """
        Generate and post an hourly tweet.
        
        Returns:
            True if tweet was successfully posted, False otherwise
        """
        try:
            # Generate the tweet
            tweet_text = self.generate_hourly_tweet()
            if not tweet_text:
                logger.error("Could not generate hourly tweet")
                return False
            
            # Post it using the agent's Twitter tools
            if not self.agent.twitter_tools or not self.agent.twitter_tools.twitter_client.is_ready:
                logger.error("Twitter client not available")
                return False
            
            result = self.agent.twitter_tools.post_tweet(tweet_text)
            
            if result.get("success"):
                logger.info(f"✓ Posted hourly tweet: {tweet_text[:80]}...")
                return True
            else:
                logger.error(f"Failed to post tweet: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error in post_hourly_tweet: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get scheduler statistics"""
        return {
            "tweets_posted": self.tweets_posted,
            "failed_attempts": self.failed_attempts,
            "success_rate": (
                self.tweets_posted / (self.tweets_posted + self.failed_attempts)
                if (self.tweets_posted + self.failed_attempts) > 0 else 0
            ),
            "current_content_type": self.content_rotation[self.current_index].value
        }
