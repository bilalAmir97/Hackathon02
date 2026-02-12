"""Database connection and session management for Neon PostgreSQL.

This module provides async database engine, session factory, and dependency
injection for FastAPI endpoints. Optimized for Neon Serverless PostgreSQL
with connection pooling and health checks.
"""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import text

from src.config import settings

# Create async engine with asyncpg driver
# Configuration optimized for Neon Serverless PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "development",  # Log SQL in development
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    # Use NullPool for serverless environments to avoid connection exhaustion
    poolclass=NullPool if settings.app_env == "test" else None,
)

# Create AsyncSession factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent lazy loading issues
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency that provides a database session.

    Yields an AsyncSession that is automatically closed after the request.
    Handles transaction management and ensures proper cleanup.

    Usage:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()

    Yields:
        AsyncSession: Database session for the request
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_database_health() -> dict[str, Any]:
    """Check database connectivity and return health status.

    Executes a simple query to verify the database connection is working.
    Used by health check endpoints to monitor database availability.

    Returns:
        dict: Health status with 'healthy' boolean and optional 'error' message

    Example:
        {
            "healthy": True,
            "message": "Database connection successful"
        }

        or on failure:

        {
            "healthy": False,
            "error": "Connection timeout"
        }
    """
    try:
        async with AsyncSessionLocal() as session:
            # Execute simple query to verify connection
            result = await session.execute(text("SELECT 1"))
            result.scalar_one()

            return {"healthy": True, "message": "Database connection successful"}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def init_db() -> None:
    """Initialize database tables.

    Creates all tables defined in SQLModel metadata. Should be called
    during application startup in development. For production, use
    proper migration tools like Alembic.

    Note:
        This is a convenience function for development. In production,
        use versioned migrations with Alembic for schema management.
    """
    from src.domain.models import SQLModel

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Close database connections and dispose of the engine.

    Should be called during application shutdown to ensure all
    connections are properly closed and resources are released.
    """
    await engine.dispose()
