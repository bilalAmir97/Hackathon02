"""Retry policy with exponential backoff for transient failures.

Task IDs: T015-T018
Implements exponential backoff retry logic for LLM and tool failures.
"""

import asyncio
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class RetryPolicy:
    """Retry policy with exponential backoff for transient failures.

    Implements exponential backoff retry logic with configurable parameters.
    Retries transient errors (rate limits, timeouts, connection errors, server errors)
    but fails immediately on non-retryable errors (authentication, bad request, not found).
    """

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay_ms: int = 100,
        max_delay_ms: int = 5000,
        backoff_multiplier: float = 2.0,
    ):
        """Initialize retry policy with exponential backoff.

        Args:
            max_attempts: Maximum number of retry attempts (default: 3)
            initial_delay_ms: Initial delay before first retry in milliseconds (default: 100)
            max_delay_ms: Maximum delay between retries in milliseconds (default: 5000)
            backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
        """
        self.max_attempts = max_attempts
        self.initial_delay_ms = initial_delay_ms
        self.max_delay_ms = max_delay_ms
        self.backoff_multiplier = backoff_multiplier

    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Execute function with retry logic.

        Retries the function on transient errors with exponential backoff.
        Fails immediately on non-retryable errors.

        Args:
            func: Async function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Result from the function

        Raises:
            Exception: If all retry attempts fail or error is non-retryable
        """
        last_exception = None
        delay_ms = self.initial_delay_ms

        for attempt in range(1, self.max_attempts + 1):
            try:
                result = await func(*args, **kwargs)
                if attempt > 1:
                    logger.info(
                        "Function succeeded after retry",
                        extra={
                            "event": "retry_success",
                            "attempt": attempt,
                            "max_attempts": self.max_attempts,
                        },
                    )
                return result

            except Exception as e:
                last_exception = e

                # Check if error is retryable
                if not self.is_retryable_error(e):
                    logger.warning(
                        "Non-retryable error encountered",
                        extra={
                            "event": "non_retryable_error",
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                            "attempt": attempt,
                        },
                    )
                    raise

                # If this was the last attempt, raise the exception
                if attempt == self.max_attempts:
                    logger.error(
                        "Max retry attempts exceeded",
                        extra={
                            "event": "max_attempts_exceeded",
                            "max_attempts": self.max_attempts,
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                        },
                    )
                    raise

                # Log retry attempt
                logger.warning(
                    "Retrying after transient error",
                    extra={
                        "event": "retry_attempt",
                        "attempt": attempt,
                        "max_attempts": self.max_attempts,
                        "error_type": type(e).__name__,
                        "delay_ms": delay_ms,
                        "next_action": "retry",
                    },
                )

                # Wait before retrying
                await asyncio.sleep(delay_ms / 1000.0)

                # Calculate next delay with exponential backoff (capped at max_delay_ms)
                delay_ms = min(int(delay_ms * self.backoff_multiplier), self.max_delay_ms)

        # This should never be reached, but just in case
        if last_exception:
            raise last_exception

    def is_retryable_error(self, error: Exception) -> bool:
        """Determine if error is transient and retryable.

        Retryable errors:
        - Rate limit errors (429)
        - Timeout errors
        - Connection errors
        - Server errors (500, 502, 503, 504)

        Non-retryable errors:
        - Authentication errors (401, 403)
        - Bad request errors (400)
        - Not found errors (404)

        Args:
            error: Exception to check

        Returns:
            True if error is retryable, False otherwise
        """
        error_str = str(error).lower()

        # Non-retryable HTTP status codes
        non_retryable_codes = ["400", "401", "403", "404"]
        for code in non_retryable_codes:
            if code in error_str:
                return False

        # Retryable errors
        retryable_patterns = [
            "429",  # Rate limit
            "500",  # Internal server error
            "502",  # Bad gateway
            "503",  # Service unavailable
            "504",  # Gateway timeout
            "timeout",
            "connection",
            "rate limit",
        ]

        for pattern in retryable_patterns:
            if pattern in error_str:
                return True

        # Check exception types
        if isinstance(error, (asyncio.TimeoutError, ConnectionError)):
            return True

        # Default to retryable for unknown errors (conservative approach)
        return True
