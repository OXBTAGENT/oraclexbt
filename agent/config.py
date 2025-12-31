"""Configuration for the Prediction Market Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class AgentConfig:
    """
    Configuration for the Prediction Market Agent.
    
    Attributes:
        llm_provider: Which LLM provider to use (openai or anthropic)
        llm_model: Model name to use
        api_key: API key for the LLM provider (reads from env if not provided)
        temperature: Sampling temperature for LLM responses
        max_tokens: Maximum tokens in LLM response
        oraclyst_base_url: Base URL for Oraclyst API
        verbose: Enable verbose logging
        max_tool_calls: Maximum tool calls per agent turn
        market_cache_ttl: How long to cache market data (seconds)
    """
    llm_provider: LLMProvider = LLMProvider.ANTHROPIC
    llm_model: str = "claude-sonnet-4-20250514"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    oraclyst_base_url: Optional[str] = None
    verbose: bool = False
    max_tool_calls: int = 10
    market_cache_ttl: int = 60
    
    # Analysis settings
    min_volume_filter: float = 1000.0  # Minimum volume for recommendations
    arbitrage_threshold: float = 0.02  # 2% spread to flag arbitrage
    
    # Automation settings (for hourly tweeting and monitoring)
    enable_hourly_tweets: bool = True
    hourly_tweet_interval: int = 3600  # Seconds between tweets (default 1 hour)
    enable_realtime_monitoring: bool = True
    monitoring_check_interval: int = 300  # Seconds between monitoring cycles (default 5 min)
    max_daily_tweets: int = 24  # Max tweets per day
    max_daily_replies: int = 100  # Max replies per day
    
    def __post_init__(self):
        """Load API key from environment if not provided."""
        if self.api_key is None:
            if self.llm_provider == LLMProvider.OPENAI:
                self.api_key = os.getenv("OPENAI_API_KEY")
            elif self.llm_provider == LLMProvider.ANTHROPIC:
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                f"No API key provided for {self.llm_provider.value}. "
                f"Set {self.llm_provider.value.upper()}_API_KEY environment variable "
                "or pass api_key to AgentConfig."
            )
    
    @classmethod
    def from_env(cls) -> AgentConfig:
        """Create config from environment variables."""
        provider_str = os.getenv("AGENT_LLM_PROVIDER", "anthropic").lower()
        provider = LLMProvider(provider_str)
        
        model = os.getenv("AGENT_LLM_MODEL")
        if model is None:
            model = "claude-sonnet-4-20250514" if provider == LLMProvider.ANTHROPIC else "gpt-4o"
        
        return cls(
            llm_provider=provider,
            llm_model=model,
            temperature=float(os.getenv("AGENT_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("AGENT_MAX_TOKENS", "4096")),
            oraclyst_base_url=os.getenv("ORACLYST_BASE_URL"),
            verbose=os.getenv("AGENT_VERBOSE", "").lower() in ("true", "1", "yes"),
            # Automation settings
            enable_hourly_tweets=os.getenv("ENABLE_HOURLY_TWEETS", "true").lower() in ("true", "1", "yes"),
            hourly_tweet_interval=int(os.getenv("HOURLY_TWEET_INTERVAL", "3600")),
            enable_realtime_monitoring=os.getenv("ENABLE_REALTIME_MONITORING", "true").lower() in ("true", "1", "yes"),
            monitoring_check_interval=int(os.getenv("MONITORING_CHECK_INTERVAL", "300")),
            max_daily_tweets=int(os.getenv("MAX_DAILY_TWEETS", "24")),
            max_daily_replies=int(os.getenv("MAX_DAILY_REPLIES", "100")),
        )
    
    @classmethod
    def openai(cls, model: str = "gpt-4o", **kwargs) -> AgentConfig:
        """Create config for OpenAI."""
        return cls(llm_provider=LLMProvider.OPENAI, llm_model=model, **kwargs)
    
    @classmethod
    def anthropic(cls, model: str = "claude-sonnet-4-20250514", **kwargs) -> AgentConfig:
        """Create config for Anthropic."""
        return cls(llm_provider=LLMProvider.ANTHROPIC, llm_model=model, **kwargs)
