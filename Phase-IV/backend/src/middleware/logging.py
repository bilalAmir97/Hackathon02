"""
Structured JSON logging middleware for FastAPI.

Logs all incoming requests and responses with correlation IDs for tracing.
"""

import json
import logging
import time
from collections.abc import Callable
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


# Configure JSON logging
class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        return json.dumps(log_data)


# Configure logger
logger = logging.getLogger("todo_api")
logger.setLevel(logging.INFO)

# Add JSON handler if not already configured
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured JSON logging of all HTTP requests and responses.

    Logs include:
    - timestamp: ISO 8601 UTC timestamp
    - level: Log level (INFO, ERROR, etc.)
    - request_id: UUID v4 for request correlation
    - method: HTTP method (GET, POST, etc.)
    - path: Request path
    - status_code: HTTP response status code
    - duration_ms: Request processing duration in milliseconds
    - user_id: User ID from path parameters (if available)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response
        """
        # Generate unique request ID for correlation
        request_id = str(uuid4())
        request.state.request_id = request_id

        # Extract user_id from path parameters if present
        user_id = request.path_params.get("user_id")
        if user_id:
            request.state.user_id = user_id

        # Record start time
        start_time = time.time()

        # Process request
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log error and re-raise
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "Request failed with exception",
                extra={
                    "request_id": request_id,
                    "user_id": user_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "error": str(exc),
                },
            )
            raise

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log request completion
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )

        # Add request ID to response headers for client-side correlation
        response.headers["X-Request-ID"] = request_id

        return response
