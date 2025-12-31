"""Base transport class for HTTP operations."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional
from urllib.parse import urlencode, urljoin

from oraclyst_sdk.config import OraclystConfig
from oraclyst_sdk.exceptions import ApiError, NotFoundError, RateLimitExceededError

logger = logging.getLogger("oraclyst_sdk")


class BaseTransport(ABC):
    """
    Abstract base class for HTTP transport.
    
    Handles URL building, header construction, and error processing.
    """
    
    def __init__(self, config: OraclystConfig):
        self.config = config
    
    def _build_url(self, path: str, params: Optional[dict[str, Any]] = None) -> str:
        """Build full URL with query parameters."""
        url = urljoin(self.config.base_url, path)
        if params:
            filtered = {k: v for k, v in params.items() if v is not None}
            if filtered:
                url = f"{url}?{urlencode(filtered)}"
        return url
    
    def _build_headers(self) -> dict[str, str]:
        """Build request headers."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": self.config.user_agent,
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers
    
    def _handle_error_response(self, status_code: int, response_data: dict[str, Any]) -> None:
        """
        Handle error responses from the API.
        
        Raises:
            NotFoundError: For 404 responses.
            RateLimitExceededError: For 429 responses.
            ApiError: For other error responses.
        """
        error_message = response_data.get("error", "Unknown error")
        
        if status_code == 404:
            raise NotFoundError(message=error_message, details=response_data)
        
        if status_code == 429:
            retry_after = response_data.get("retryAfter")
            raise RateLimitExceededError(
                message=error_message,
                retry_after=retry_after,
                details=response_data,
            )
        
        raise ApiError(
            message=error_message,
            status_code=status_code,
            error_code=response_data.get("code"),
            details=response_data,
        )
    
    @abstractmethod
    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Make a GET request."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the transport and release resources."""
        pass
