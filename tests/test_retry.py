"""Tests for retry logic with exponential backoff."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ghlicense.utils.retry import async_retry, RateLimitError


class TestRateLimitError:
    """Tests for RateLimitError exception."""

    def test_rate_limit_error_is_exception(self):
        """Test RateLimitError inherits from Exception."""
        assert issubclass(RateLimitError, Exception)

    def test_rate_limit_error_can_be_raised(self):
        """Test RateLimitError can be raised with message."""
        with pytest.raises(RateLimitError) as exc_info:
            raise RateLimitError("Rate limit exceeded")
        assert str(exc_info.value) == "Rate limit exceeded"


class TestAsyncRetryDecorator:
    """Tests for async_retry decorator."""

    @pytest.mark.asyncio
    async def test_successful_call_no_retries(self):
        """Test successful call executes without retries."""
        mock_func = AsyncMock(return_value="success")

        @async_retry(max_retries=5, base_delay=0.01)
        async def func():
            return await mock_func()

        result = await func()
        assert result == "success"
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_rate_limit_error(self):
        """Test retry is triggered on RateLimitError."""
        mock_func = AsyncMock(side_effect=[
            RateLimitError("429"),
            RateLimitError("429"),
            "success"
        ])

        @async_retry(max_retries=5, base_delay=0.01)
        async def func():
            return await mock_func()

        result = await func()
        assert result == "success"
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test exception is raised after max retries."""
        mock_func = AsyncMock(side_effect=RateLimitError("429"))

        @async_retry(max_retries=3, base_delay=0.01)
        async def func():
            return await mock_func()

        with pytest.raises(RateLimitError):
            await func()

        assert mock_func.call_count == 3  # Initial + 2 retries = 3

    @pytest.mark.asyncio
    async def test_non_rate_limit_error_not_retried(self):
        """Test non-rate-limit errors are not retried."""
        mock_func = AsyncMock(side_effect=ValueError("Some other error"))

        @async_retry(max_retries=5, base_delay=0.01)
        async def func():
            return await mock_func()

        with pytest.raises(ValueError) as exc_info:
            await func()

        assert str(exc_info.value) == "Some other error"
        assert mock_func.call_count == 1  # No retries for non-rate-limit errors

    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self):
        """Test exponential backoff delays: 1s, 2s, 4s, 8s, 16s."""
        call_count = 0

        @async_retry(max_retries=5, base_delay=1)
        async def func():
            nonlocal call_count
            call_count += 1
            if call_count < 5:
                raise RateLimitError("429")
            return "success"

        import time
        start = time.time()
        result = await func()
        elapsed = time.time() - start

        assert result == "success"
        # Expected delays: 1 + 2 + 4 + 8 = 15 seconds for 4 retries
        # Allow some tolerance for test execution time
        assert 14 <= elapsed <= 20

    @pytest.mark.asyncio
    async def test_respects_retry_after_header(self):
        """Test Retry-After header is respected when present."""
        mock_response = MagicMock()
        mock_response.status = 429
        mock_response.headers = {'Retry-After': '3'}

        call_count = 0
        mock_func = AsyncMock(side_effect=[
            RateLimitError("429", response=mock_response),
            "success"
        ])

        @async_retry(max_retries=5, base_delay=1)
        async def func():
            return await mock_func()

        import time
        start = time.time()
        result = await func()
        elapsed = time.time() - start

        # Should use Retry-After (3s) instead of exponential backoff
        assert 2.5 <= elapsed <= 5
        assert result == "success"

    @pytest.mark.asyncio
    async def test_logs_retry_attempts(self):
        """Test retry attempts are logged."""
        mock_func = AsyncMock(side_effect=[
            RateLimitError("429"),
            "success"
        ])

        @async_retry(max_retries=5, base_delay=0.01)
        async def func():
            return await mock_func()

        with patch('ghlicense.utils.retry.logger') as mock_logger:
            await func()
            # Should log retry attempts
            assert mock_logger.warning.called or mock_logger.info.called


class TestAsyncRetryWithArgs:
    """Tests for async_retry with function arguments."""

    @pytest.mark.asyncio
    async def test_passes_arguments_to_function(self):
        """Test arguments are passed to the wrapped function."""
        mock_func = AsyncMock(return_value="result")

        @async_retry(max_retries=5, base_delay=0.01)
        async def func(arg1, arg2, kwarg1=None):
            return await mock_func(arg1, arg2, kwarg1=kwarg1)

        result = await func("test", 123, kwarg1="value")
        assert result == "result"
        mock_func.assert_called_once_with("test", 123, kwarg1="value")

    @pytest.mark.asyncio
    async def test_retries_with_same_arguments(self):
        """Test same arguments are used on retry."""
        mock_func = AsyncMock(side_effect=[
            RateLimitError("429"),
            "success"
        ])

        @async_retry(max_retries=5, base_delay=0.01)
        async def func(arg1):
            return await mock_func(arg1)

        result = await func("test-arg")
        assert result == "success"
        # Both calls should use the same argument
        assert mock_func.call_count == 2
        mock_func.assert_called_with("test-arg")


class TestSyncFunctionRetry:
    """Tests for async_retry with sync functions (wrapped to async)."""

    @pytest.mark.asyncio
    async def test_retries_sync_function(self):
        """Test retry works with sync functions."""
        call_count = 0

        def sync_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RateLimitError("429")
            return "success"

        @async_retry(max_retries=5, base_delay=0.01)
        async def wrapper():
            return sync_func()

        result = await wrapper()
        assert result == "success"
        assert call_count == 3