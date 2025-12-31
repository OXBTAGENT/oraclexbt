"""Asynchronous HTTP transport using aiohttp."""

from __future__ import annotations

import logging
from typing import Any, Optional

import aiohttp

from oraclyst_sdk.config import OraclystConfig
from oraclyst_sdk.exceptions import TransportError
from oraclyst_sdk.http.base import BaseTransport

logger = logging.getLogger("oraclyst_sdk")


class AsyncTransport(BaseTransport):
    """
    Asynchronous HTTP transport using the aiohttp library.
    
    Features:
        - Connection pooling
        - Async/await support
        - Configurable timeouts
    
    Example:
        async with AsyncTransport(config) as transport:
            data = await transport.get("/api/v1/markets")
    """
    
    def __init__(self, config: OraclystConfig):
        super().__init__(config)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(
                limit=20,
                limit_per_host=10,
            )
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self._build_headers(),
            )
        return self._session
    
    async def get(  # type: ignore[override]
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Make an async GET request.
        
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
        session = await self._get_session()
        
        logger.debug(f"GET {url}")
        
        try:
            async with session.get(url) as response:
                try:
                    data = await response.json()
                except (ValueError, aiohttp.ContentTypeError) as e:
                    text = await response.text()
                    raise TransportError(
                        f"Invalid JSON response: {text[:200]}",
                        status_code=response.status,
                    ) from e
                
                if response.status >= 400:
                    self._handle_error_response(response.status, data)
                
                return data
                
        except aiohttp.ClientTimeout as e:
            raise TransportError(f"Request timeout: {e}") from e
        except aiohttp.ClientConnectionError as e:
            raise TransportError(f"Connection error: {e}") from e
        except aiohttp.ClientError as e:
            raise TransportError(f"Request failed: {e}") from e
    
    async def close(self) -> None:  # type: ignore[override]
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self) -> AsyncTransport:
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        await self.close()
