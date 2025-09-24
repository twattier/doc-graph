"""
Rate limiting middleware for API endpoints.
"""

import time
import json
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import asyncio
import logging

from ..config import get_settings

logger = logging.getLogger(__name__)


class RateLimitExceeded(HTTPException):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, detail: Any = None, headers: Optional[dict] = None):
        super().__init__(status_code=429, detail=detail, headers=headers)


class RateLimiter:
    """Redis-based rate limiter with sliding window implementation."""

    def __init__(self, redis_url: str = None):
        """Initialize rate limiter with Redis connection."""
        self.redis_url = redis_url or get_settings().redis_url
        self._redis_pool = None

    async def get_redis_pool(self) -> redis.Redis:
        """Get or create Redis connection pool."""
        if self._redis_pool is None:
            self._redis_pool = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis_pool

    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int
    ) -> Dict[str, Any]:
        """
        Check if request is allowed using sliding window rate limiting.

        Args:
            key: Unique identifier for the rate limit (e.g., user_id, IP)
            limit: Maximum number of requests allowed in window
            window: Time window in seconds

        Returns:
            Dict with 'allowed' bool and rate limit info
        """
        try:
            redis_client = await self.get_redis_pool()
            now = time.time()
            pipeline = redis_client.pipeline()

            # Remove expired entries
            pipeline.zremrangebyscore(key, 0, now - window)

            # Count current requests
            pipeline.zcard(key)

            # Add current request
            pipeline.zadd(key, {str(now): now})

            # Set expiration
            pipeline.expire(key, window)

            results = pipeline.execute()
            if asyncio.iscoroutine(results):
                results = await results
            current_requests = results[1]

            # current_requests is the count BEFORE adding current request
            # We allow if current_requests < limit (so adding one more is still within limit)
            allowed = current_requests < limit

            return {
                "allowed": allowed,
                "limit": limit,
                "remaining": max(0, limit - current_requests - 1),
                "reset_time": int(now + window),
                "retry_after": window if not allowed else None
            }

        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Fail open - allow request if Redis is unavailable
            return {
                "allowed": True,
                "limit": limit,
                "remaining": limit - 1,
                "reset_time": int(time.time() + window),
                "retry_after": None
            }

    async def close(self):
        """Close Redis connection."""
        if self._redis_pool:
            await self._redis_pool.close()


# Global rate limiter instance
rate_limiter = RateLimiter()


async def apply_rate_limit(
    request: Request,
    user_id: str,
    limit: int = 1000,  # requests per window
    window: int = 60,   # window in seconds (1 minute)
    endpoint_key: str = "default"
) -> None:
    """
    Apply rate limiting to a request.

    Args:
        request: FastAPI request object
        user_id: User identifier for rate limiting
        limit: Maximum requests per window
        window: Window duration in seconds
        endpoint_key: Unique key for the endpoint type

    Raises:
        HTTPException: If rate limit is exceeded
    """
    # Create rate limit key combining user and endpoint
    rate_limit_key = f"rate_limit:{endpoint_key}:{user_id}"

    # Check rate limit
    result = await rate_limiter.is_allowed(rate_limit_key, limit, window)

    # Add rate limit headers to response (will be added by middleware)
    request.state.rate_limit_headers = {
        "X-RateLimit-Limit": str(result["limit"]),
        "X-RateLimit-Remaining": str(result["remaining"]),
        "X-RateLimit-Reset": str(result["reset_time"])
    }

    if not result["allowed"]:
        headers = {
            "X-RateLimit-Limit": str(result["limit"]),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(result["reset_time"]),
            "Retry-After": str(result["retry_after"])
        }

        logger.warning(f"Rate limit exceeded for user {user_id} on endpoint {endpoint_key}")

        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {limit} requests per {window} seconds",
                "retry_after": result["retry_after"]
            },
            headers=headers
        )


class RateLimitingMiddleware:
    """Middleware to add rate limit headers to responses."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))

                # Add rate limit headers if they were set during request processing
                if hasattr(request.state, "rate_limit_headers"):
                    for key, value in request.state.rate_limit_headers.items():
                        headers[key.encode()] = value.encode()

                message["headers"] = list(headers.items())

            await send(message)

        await self.app(scope, receive, send_wrapper)


# Rate limit decorators for common patterns
def rate_limit_repository_import(limit: int = 10, window: int = 60):
    """Rate limit decorator for repository import endpoints (10 requests per minute by default)."""
    def decorator(func):
        func._rate_limit_config = {
            "limit": limit,
            "window": window,
            "endpoint_key": "repository_import"
        }
        return func
    return decorator


def rate_limit_repository_api(limit: int = 100, window: int = 60):
    """Rate limit decorator for general repository API endpoints (100 requests per minute by default)."""
    def decorator(func):
        func._rate_limit_config = {
            "limit": limit,
            "window": window,
            "endpoint_key": "repository_api"
        }
        return func
    return decorator