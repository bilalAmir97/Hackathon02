"""Unit tests for RetryPolicy.

Task IDs: T005-T009
Tests exponential backoff retry logic for transient failures.
"""

import asyncio
from unittest.mock import AsyncMock

import pytest

from src.agent.retry_policy import RetryPolicy


class TestRetryPolicySuccessfulExecution:
    """Test successful execution on first attempt (T005)."""

    @pytest.mark.asyncio
    async def test_successful_execution_no_retry(self):
        """Given a function that succeeds, when executed with retry policy,
        then it should return result without retrying."""
        policy = RetryPolicy(max_attempts=3)
        mock_func = AsyncMock(return_value="success")

        result = await policy.execute_with_retry(mock_func, "arg1", kwarg1="value1")

        assert result == "success"
        assert mock_func.call_count == 1
        mock_func.assert_called_once_with("arg1", kwarg1="value1")


class TestRetryPolicyRetryOnTransientError:
    """Test retry on transient error (T006)."""

    @pytest.mark.asyncio
    async def test_retry_on_rate_limit_error(self):
        """Given a function that fails with rate limit error then succeeds,
        when executed with retry policy, then it should retry and return success."""
        policy = RetryPolicy(max_attempts=3)
        mock_func = AsyncMock(side_effect=[Exception("429 Rate Limit"), "success"])

        result = await policy.execute_with_retry(mock_func)

        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_on_timeout_error(self):
        """Given a function that times out then succeeds,
        when executed with retry policy, then it should retry and return success."""
        policy = RetryPolicy(max_attempts=3)
        mock_func = AsyncMock(side_effect=[asyncio.TimeoutError(), "success"])

        result = await policy.execute_with_retry(mock_func)

        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_on_connection_error(self):
        """Given a function that fails with connection error then succeeds,
        when executed with retry policy, then it should retry and return success."""
        policy = RetryPolicy(max_attempts=3)
        mock_func = AsyncMock(side_effect=[ConnectionError("Connection failed"), "success"])

        result = await policy.execute_with_retry(mock_func)

        assert result == "success"
        assert mock_func.call_count == 2


class TestRetryPolicyExponentialBackoff:
    """Test exponential backoff timing (T007)."""

    @pytest.mark.asyncio
    async def test_exponential_backoff_delays(self):
        """Given a function that fails multiple times,
        when executed with retry policy, then delays should follow exponential backoff."""
        policy = RetryPolicy(
            max_attempts=4, initial_delay_ms=100, max_delay_ms=5000, backoff_multiplier=2.0
        )
        mock_func = AsyncMock(
            side_effect=[Exception("Error 1"), Exception("Error 2"), Exception("Error 3"), "success"]
        )

        start_time = asyncio.get_event_loop().time()
        result = await policy.execute_with_retry(mock_func)
        end_time = asyncio.get_event_loop().time()

        assert result == "success"
        assert mock_func.call_count == 4
        # Total delay should be approximately: 100ms + 200ms + 400ms = 700ms
        elapsed_ms = (end_time - start_time) * 1000
        assert 600 <= elapsed_ms <= 900  # Allow some tolerance

    @pytest.mark.asyncio
    async def test_backoff_capped_at_max_delay(self):
        """Given a function that fails many times,
        when executed with retry policy, then delay should be capped at max_delay_ms."""
        policy = RetryPolicy(
            max_attempts=5, initial_delay_ms=1000, max_delay_ms=2000, backoff_multiplier=2.0
        )
        mock_func = AsyncMock(
            side_effect=[
                Exception("Error 1"),
                Exception("Error 2"),
                Exception("Error 3"),
                Exception("Error 4"),
                "success",
            ]
        )

        start_time = asyncio.get_event_loop().time()
        result = await policy.execute_with_retry(mock_func)
        end_time = asyncio.get_event_loop().time()

        assert result == "success"
        # Delays: 1000ms, 2000ms (capped), 2000ms (capped), 2000ms (capped) = 7000ms
        elapsed_ms = (end_time - start_time) * 1000
        assert 6500 <= elapsed_ms <= 7500


class TestRetryPolicyMaxAttemptsExceeded:
    """Test max attempts exceeded (T008)."""

    @pytest.mark.asyncio
    async def test_max_attempts_exceeded_raises_exception(self):
        """Given a function that always fails,
        when executed with retry policy, then it should raise exception after max attempts."""
        policy = RetryPolicy(max_attempts=3, initial_delay_ms=10)
        mock_func = AsyncMock(side_effect=Exception("Persistent error"))

        with pytest.raises(Exception, match="Persistent error"):
            await policy.execute_with_retry(mock_func)

        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_exception_includes_context(self):
        """Given a function that always fails,
        when max attempts exceeded, then exception should include full context."""
        policy = RetryPolicy(max_attempts=2, initial_delay_ms=10)
        mock_func = AsyncMock(side_effect=Exception("Original error"))

        with pytest.raises(Exception) as exc_info:
            await policy.execute_with_retry(mock_func)

        assert "Original error" in str(exc_info.value)


class TestRetryPolicyNonRetryableErrors:
    """Test non-retryable errors fail immediately (T009)."""

    @pytest.mark.asyncio
    async def test_authentication_error_not_retried(self):
        """Given a function that fails with authentication error,
        when executed with retry policy, then it should fail immediately without retry."""
        policy = RetryPolicy(max_attempts=3)
        mock_func = AsyncMock(side_effect=Exception("401 Unauthorized"))

        with pytest.raises(Exception, match="401 Unauthorized"):
            await policy.execute_with_retry(mock_func)

        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_bad_request_error_not_retried(self):
        """Given a function that fails with bad request error,
        when executed with retry policy, then it should fail immediately without retry."""
        policy = RetryPolicy(max_attempts=3)
        mock_func = AsyncMock(side_effect=Exception("400 Bad Request"))

        with pytest.raises(Exception, match="400 Bad Request"):
            await policy.execute_with_retry(mock_func)

        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_not_found_error_not_retried(self):
        """Given a function that fails with not found error,
        when executed with retry policy, then it should fail immediately without retry."""
        policy = RetryPolicy(max_attempts=3)
        mock_func = AsyncMock(side_effect=Exception("404 Not Found"))

        with pytest.raises(Exception, match="404 Not Found"):
            await policy.execute_with_retry(mock_func)

        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_forbidden_error_not_retried(self):
        """Given a function that fails with forbidden error,
        when executed with retry policy, then it should fail immediately without retry."""
        policy = RetryPolicy(max_attempts=3)
        mock_func = AsyncMock(side_effect=Exception("403 Forbidden"))

        with pytest.raises(Exception, match="403 Forbidden"):
            await policy.execute_with_retry(mock_func)

        assert mock_func.call_count == 1
