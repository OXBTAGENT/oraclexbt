"""Exception classes for the Oraclyst SDK."""

from __future__ import annotations

from typing import Any, Optional


class OraclystError(Exception):
    """Base exception for all Oraclyst SDK errors."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class ConfigError(OraclystError):
    """Raised when there's a configuration error."""
    pass


class TransportError(OraclystError):
    """Raised when there's a network or transport-level error."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.status_code = status_code


class ApiError(OraclystError):
    """Raised when the API returns an error response."""
    
    def __init__(
        self,
        message: str,
        status_code: int,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.status_code = status_code
        self.error_code = error_code
    
    def __str__(self) -> str:
        parts = [f"[{self.status_code}]"]
        if self.error_code:
            parts.append(f"({self.error_code})")
        parts.append(self.message)
        return " ".join(parts)


class NotFoundError(ApiError):
    """Raised when a requested resource is not found (404)."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=404, details=details)


class RateLimitExceededError(ApiError):
    """Raised when rate limit is exceeded (429)."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[float] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=429, details=details)
        self.retry_after = retry_after
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.retry_after:
            return f"{base} (retry after {self.retry_after}s)"
        return base


class ResponseValidationError(OraclystError):
    """Raised when response data fails validation."""
    
    def __init__(
        self,
        message: str,
        raw_data: Any = None,
        validation_errors: Optional[list[dict[str, Any]]] = None,
    ):
        super().__init__(message)
        self.raw_data = raw_data
        self.validation_errors = validation_errors or []
