"""
Unit tests for rate limiting middleware - Story 1.2 Git Repository Import System
"""
import pytest
import time
from unittest.mock import Mock, patch, AsyncMock
import redis

from src.middleware.rate_limiting import RateLimiter, apply_rate_limit
from fastapi import HTTPException, Request


class TestRateLimiter:
    """Test suite for RateLimiter functionality."""

    @pytest.fixture
    def rate_limiter(self):
        """Create RateLimiter instance for testing."""
        return RateLimiter(redis_url="redis://localhost:6379/0")

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client for testing."""
        mock_redis = Mock()
        mock_redis.pipeline.return_value = mock_redis
        mock_redis.zremrangebyscore.return_value = mock_redis
        mock_redis.zcard.return_value = mock_redis
        mock_redis.zadd.return_value = mock_redis
        mock_redis.expire.return_value = mock_redis
        mock_redis.execute.return_value = [None, 0, None, None]  # No previous requests
        return mock_redis

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limiter_allows_first_request(self, rate_limiter, mock_redis):
        """Test that first request is always allowed."""
        with patch.object(rate_limiter, 'get_redis_pool', return_value=mock_redis):
            result = await rate_limiter.is_allowed("test_user", limit=10, window=60)

        assert result["allowed"] is True
        assert result["limit"] == 10
        assert result["remaining"] == 9
        assert "reset_time" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_when_limit_exceeded(self, rate_limiter, mock_redis):
        """Test that requests are blocked when limit is exceeded."""
        # Mock Redis to return 10 existing requests (at limit)
        mock_redis.execute.return_value = [None, 10, None, None]

        with patch.object(rate_limiter, 'get_redis_pool', return_value=mock_redis):
            result = await rate_limiter.is_allowed("test_user", limit=10, window=60)

        assert result["allowed"] is False
        assert result["remaining"] == 0
        assert result["retry_after"] == 60

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limiter_tracks_remaining_requests(self, rate_limiter, mock_redis):
        """Test that remaining requests are tracked correctly."""
        # Mock Redis to return 5 existing requests
        mock_redis.execute.return_value = [None, 5, None, None]

        with patch.object(rate_limiter, 'get_redis_pool', return_value=mock_redis):
            result = await rate_limiter.is_allowed("test_user", limit=10, window=60)

        assert result["allowed"] is True
        assert result["remaining"] == 4  # 10 - 5 - 1 (current request)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limiter_fails_open_on_redis_error(self, rate_limiter):
        """Test that rate limiter allows requests when Redis fails."""
        with patch.object(rate_limiter, 'get_redis_pool', side_effect=Exception("Redis unavailable")):
            result = await rate_limiter.is_allowed("test_user", limit=10, window=60)

        assert result["allowed"] is True  # Fail open

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_apply_rate_limit_allows_within_limit(self):
        """Test apply_rate_limit allows requests within limit."""
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()

        with patch('src.middleware.rate_limiting.rate_limiter') as mock_rate_limiter:
            async def async_return(*args, **kwargs):
                return {
                    "allowed": True,
                    "limit": 10,
                    "remaining": 9,
                    "reset_time": int(time.time() + 60),
                    "retry_after": None
                }
            mock_rate_limiter.is_allowed.side_effect = async_return

            # Should not raise exception
            await apply_rate_limit(mock_request, "user123", limit=10, window=60)

            # Should set rate limit headers
            assert hasattr(mock_request.state, 'rate_limit_headers')
            assert mock_request.state.rate_limit_headers["X-RateLimit-Limit"] == "10"
            assert mock_request.state.rate_limit_headers["X-RateLimit-Remaining"] == "9"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_apply_rate_limit_raises_exception_when_exceeded(self):
        """Test apply_rate_limit raises HTTPException when limit exceeded."""
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()

        with patch('src.middleware.rate_limiting.rate_limiter') as mock_rate_limiter:
            async def async_return(*args, **kwargs):
                return {
                    "allowed": False,
                    "limit": 10,
                    "remaining": 0,
                    "reset_time": int(time.time() + 60),
                    "retry_after": 60
                }
            mock_rate_limiter.is_allowed.side_effect = async_return

            with pytest.raises(HTTPException) as exc_info:
                await apply_rate_limit(mock_request, "user123", limit=10, window=60)

            assert exc_info.value.status_code == 429
            assert "Rate limit exceeded" in exc_info.value.detail["error"]
            assert "X-RateLimit-Limit" in exc_info.value.headers
            assert "Retry-After" in exc_info.value.headers

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limiter_key_generation(self, rate_limiter, mock_redis):
        """Test that different endpoint keys create different rate limit buckets."""
        with patch('src.middleware.rate_limiting.rate_limiter') as mock_rate_limiter:
            async def async_return(*args, **kwargs):
                return {
                    "allowed": True,
                    "limit": 10,
                    "remaining": 9,
                    "reset_time": int(time.time() + 60),
                    "retry_after": None
                }
            mock_rate_limiter.is_allowed.side_effect = async_return

            # First call for import endpoint
            await apply_rate_limit(
                Mock(state=Mock()), "user123",
                limit=10, window=60, endpoint_key="repository_import"
            )

            # Second call for general API endpoint
            await apply_rate_limit(
                Mock(state=Mock()), "user123",
                limit=100, window=60, endpoint_key="repository_api"
            )

        # Verify different Redis keys were used
        assert mock_rate_limiter.is_allowed.call_count == 2
        call_args = [call[0] for call in mock_rate_limiter.is_allowed.call_args_list]
        assert "rate_limit:repository_import:user123" in call_args[0]
        assert "rate_limit:repository_api:user123" in call_args[1]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limiter_sliding_window(self, rate_limiter, mock_redis):
        """Test sliding window implementation removes expired entries."""
        current_time = time.time()

        with patch.object(rate_limiter, 'get_redis_pool', return_value=mock_redis):
            with patch('time.time', return_value=current_time):
                await rate_limiter.is_allowed("test_user", limit=10, window=60)

        # Verify expired entries are removed (older than current_time - 60)
        expected_min_score = current_time - 60
        mock_redis.zremrangebyscore.assert_called_with("test_user", 0, expected_min_score)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limiter_different_users_separate_limits(self, rate_limiter, mock_redis):
        """Test that different users have separate rate limit buckets."""
        with patch.object(rate_limiter, 'get_redis_pool', return_value=mock_redis):
            # Request from user1
            result1 = await rate_limiter.is_allowed("user1", limit=10, window=60)

            # Request from user2
            result2 = await rate_limiter.is_allowed("user2", limit=10, window=60)

        # Both should be allowed independently
        assert result1["allowed"] is True
        assert result2["allowed"] is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limiter_expiry_set_correctly(self, rate_limiter, mock_redis):
        """Test that Redis key expiry is set correctly."""
        window = 120  # 2 minutes

        with patch.object(rate_limiter, 'get_redis_pool', return_value=mock_redis):
            await rate_limiter.is_allowed("test_user", limit=10, window=window)

        # Verify expiry is set to window duration
        mock_redis.expire.assert_called_with("test_user", window)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limiter_reset_time_calculation(self, rate_limiter, mock_redis):
        """Test that reset time is calculated correctly."""
        current_time = 1000000  # Fixed timestamp
        window = 60

        with patch.object(rate_limiter, 'get_redis_pool', return_value=mock_redis):
            with patch('time.time', return_value=current_time):
                result = await rate_limiter.is_allowed("test_user", limit=10, window=window)

        expected_reset_time = current_time + window
        assert result["reset_time"] == expected_reset_time