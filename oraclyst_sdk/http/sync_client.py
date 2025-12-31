"""Synchronous HTTP transport using requests."""

from __future__ import annotations

import logging
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from oraclyst_sdk.config import OraclystConfig
from oraclyst_sdk.exceptions import TransportError
from oraclyst_sdk.http.base import BaseTransport

logger = logging.getLogger("oraclyst_sdk")


class SyncTransport(BaseTransport):
    """
    Synchronous HTTP transport using the requests library.
    
    Features:
        - Connection pooling
        - Automatic retries with exponential backoff
        - Configurable timeouts
    """
    
    def __init__(self, config: OraclystConfig):
        super().__init__(config)
        self._session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a configured requests session with retry logic."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD", "OPTIONS"],
            raise_on_status=False,
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20,
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Make a GET request.
        
        Args:
            path: API endpoint path.
            params: Optional query parameters.
        
        Returns:
            Parsed JSON response.
        
        Raises:
            TransportError: For network errors.
            ApiError: For API error responses.
        """
        url = self._build_url(path, params)
        headers = self._build_headers()
        
        logger.debug(f"GET {url}")
        
        try:
            response = self._session.get(
                url,
                headers=headers,
                timeout=self.config.timeout,
            )
        except requests.exceptions.Timeout as e:
            raise TransportError(f"Request timeout: {e}") from e
        except requests.exceptions.ConnectionError as e:
            raise TransportError(f"Connection error: {e}") from e
        except requests.exceptions.RequestException as e:
            raise TransportError(f"Request failed: {e}") from e
        
        try:
            data = response.json()
        except ValueError as e:
            raise TransportError(
                f"Invalid JSON response: {response.text[:200]}",
                status_code=response.status_code,
            ) from e
        
        if response.status_code >= 400:
            self._handle_error_response(response.status_code, data)
        
        return data
    
    def close(self) -> None:
        """Close the session."""
        self._session.close()
    
    def __enter__(self) -> SyncTransport:
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.close()
