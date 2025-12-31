"""Configuration management for the Oraclyst SDK."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

from oraclyst_sdk.version import __version__


@dataclass(frozen=True)
class OraclystConfig:
    """
    Configuration for the Oraclyst SDK client.
    
    Attributes:
        base_url: Base URL for the Oraclyst API. Defaults to production.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retry attempts for failed requests.
        retry_delay: Base delay between retries in seconds.
        rate_limit_requests: Maximum requests per rate limit window.
        rate_limit_window: Rate limit window in seconds.
        user_agent: Custom User-Agent string for requests.
        api_key: Optional API key for authenticated endpoints.
    
    Example:
        config = OraclystConfig(
            base_url="https://api.oraclyst.app",
            timeout=30,
            max_retries=3
        )
        client = OraclystClient(config=config)
    """
    
    base_url: str = "https://oraclyst.app"
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit_requests: int = 100
    rate_limit_window: float = 60.0
    user_agent: str = field(default_factory=lambda: f"oraclyst-python-sdk/{__version__}")
    api_key: Optional[str] = None
    
    @classmethod
    def from_env(cls, prefix: str = "ORACLYST_") -> OraclystConfig:
        """
        Create configuration from environment variables.
        
        Environment variables:
            ORACLYST_BASE_URL: Base URL for the API
            ORACLYST_TIMEOUT: Request timeout in seconds
            ORACLYST_MAX_RETRIES: Maximum retry attempts
            ORACLYST_API_KEY: API key for authentication
        
        Args:
            prefix: Prefix for environment variable names.
        
        Returns:
            OraclystConfig instance with values from environment.
        """
        return cls(
            base_url=os.getenv(f"{prefix}BASE_URL", cls.base_url),
            timeout=float(os.getenv(f"{prefix}TIMEOUT", str(cls.timeout))),
            max_retries=int(os.getenv(f"{prefix}MAX_RETRIES", str(cls.max_retries))),
            api_key=os.getenv(f"{prefix}API_KEY"),
        )
    
    def with_base_url(self, base_url: str) -> OraclystConfig:
        """Create a new config with a different base URL."""
        return OraclystConfig(
            base_url=base_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            rate_limit_requests=self.rate_limit_requests,
            rate_limit_window=self.rate_limit_window,
            user_agent=self.user_agent,
            api_key=self.api_key,
        )
    
    def with_api_key(self, api_key: str) -> OraclystConfig:
        """Create a new config with a different API key."""
        return OraclystConfig(
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            rate_limit_requests=self.rate_limit_requests,
            rate_limit_window=self.rate_limit_window,
            user_agent=self.user_agent,
            api_key=api_key,
        )
