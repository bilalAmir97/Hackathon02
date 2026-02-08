"""Health check endpoint for monitoring and load balancer checks.

Provides a simple endpoint to verify API availability and database connectivity.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, status

from src.database import check_database_health

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Returns API health status and timestamp. Used for monitoring and load balancer health checks.",
    response_description="Health status with timestamp",
)
async def health_check():
    """Health check endpoint.

    Returns the current health status of the API including timestamp.
    This endpoint does not require authentication and is used by
    monitoring systems and load balancers.

    Returns:
        dict: Health status with timestamp
            - status: "healthy" if API is running
            - timestamp: Current UTC timestamp in ISO 8601 format

    Example response:
        {
            "status": "healthy",
            "timestamp": "2026-01-12T10:30:45.123456Z"
        }
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get(
    "/health/db",
    status_code=status.HTTP_200_OK,
    summary="Database health check",
    description="Returns database connectivity status. Used for deep health checks.",
    response_description="Database health status",
)
async def database_health_check():
    """Database health check endpoint.

    Verifies database connectivity by executing a simple query.
    Returns detailed health information including any errors.

    Returns:
        dict: Database health status
            - healthy: True if database is accessible, False otherwise
            - message: Success message or error details
            - timestamp: Current UTC timestamp

    Example response (healthy):
        {
            "healthy": true,
            "message": "Database connection successful",
            "timestamp": "2026-01-12T10:30:45.123456Z"
        }

    Example response (unhealthy):
        {
            "healthy": false,
            "error": "Connection timeout",
            "timestamp": "2026-01-12T10:30:45.123456Z"
        }
    """
    db_health = await check_database_health()
    db_health["timestamp"] = datetime.now(UTC).isoformat()
    return db_health
