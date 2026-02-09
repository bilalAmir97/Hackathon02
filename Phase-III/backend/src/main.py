"""
FastAPI application factory for Todo Backend API.

Creates and configures the FastAPI application with middleware,
exception handlers, and lifecycle events.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .middleware.error_handler import (
    DatabaseError,
    TaskNotFoundError,
    ValidationError,
    database_error_handler,
    generic_exception_handler,
    http_exception_handler,
    task_not_found_handler,
    validation_error_handler,
)
from .middleware.logging import LoggingMiddleware

logger = logging.getLogger("todo_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Application startup")

    # Create database tables on startup (development mode)
    # For production, use Alembic migrations instead
    from .database import close_db, init_db

    try:
        await init_db()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        # Continue startup even if table creation fails
        # (tables may already exist)

    yield

    # Shutdown
    logger.info("Application shutdown")

    # Close database connections
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    # T080: Create FastAPI instance with comprehensive API documentation
    app = FastAPI(
        title="Todo Backend API",
        version="1.0.0",
        description="""
## Multi-User Todo Backend API with JWT Authentication

A production-ready RESTful API for managing todo tasks with user authentication and authorization.

### Authentication

This API uses **JWT (JSON Web Token)** authentication with Bearer tokens.

#### How to Authenticate:

1. **Register a new account**: `POST /api/auth/register`
   - Provide email and password
   - Receive JWT token in response

2. **Login with existing account**: `POST /api/auth/login`
   - Provide email and password
   - Receive JWT token in response

3. **Use the token**: Include the token in the `Authorization` header for all protected endpoints
   ```
   Authorization: Bearer <your-jwt-token>
   ```

4. **Try it in Swagger UI**: Click the "Authorize" button (🔒) at the top right, enter your token, and click "Authorize"

### Features

- **User Registration & Login**: Secure account creation with password hashing
- **JWT Token Authentication**: Stateless authentication with 30-minute token expiration
- **User Isolation**: Each user can only access their own tasks
- **Task Management**: Full CRUD operations (Create, Read, Update, Delete)
- **Task Completion Toggle**: Quick status updates
- **Pagination & Filtering**: Efficient data retrieval with status filters
- **Error Handling**: RFC 7807 Problem Details for consistent error responses

### Security

- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens signed with HS256 algorithm
- Token invalidation on password change
- Account status validation (ACTIVE/DISABLED/DELETED)
- User ownership verification on all operations

### API Endpoints

#### Authentication (Public)
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Login and get token

#### Tasks (Protected - Requires JWT)
- `GET /api/{user_id}/tasks` - List user's tasks (with pagination & filtering)
- `POST /api/{user_id}/tasks` - Create new task
- `GET /api/{user_id}/tasks/{task_id}` - Get task details
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle completion status

### Response Codes

- `200 OK` - Successful GET/PUT/PATCH request
- `201 Created` - Successful POST request (resource created)
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing, invalid, or expired token
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate resource (e.g., email already exists)
- `422 Unprocessable Entity` - Validation error
- `503 Service Unavailable` - Database connection error

### Technology Stack

- **Framework**: FastAPI (Python 3.13+)
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Authentication**: JWT with PyJWT
- **Password Hashing**: bcrypt
        """,
        lifespan=lifespan,
        contact={
            "name": "API Support",
            "email": "support@example.com",
        },
        license_info={
            "name": "MIT",
        },
    )

    # T081: Configure CORS middleware for frontend access
    # Parse frontend URL(s) from settings (supports comma-separated list)
    allowed_origins = [origin.strip() for origin in settings.frontend_url.split(",")]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # Frontend URL(s) from environment
        allow_credentials=settings.cors_allow_credentials,  # Allow Authorization header
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # Explicit methods
        allow_headers=["Authorization", "Content-Type"],  # Required headers
        max_age=settings.cors_max_age,  # Cache preflight requests (1 hour default)
    )

    # Add structured JSON logging middleware
    app.add_middleware(LoggingMiddleware)

    # Register exception handlers (RFC 7807 Problem Details)
    from fastapi import HTTPException

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(TaskNotFoundError, task_not_found_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(DatabaseError, database_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Register API routers
    from .api.routes import auth, health, tasks

    app.include_router(auth.router)
    app.include_router(health.router)
    app.include_router(tasks.router)

    return app


# Create application instance
app = create_app()


# Root endpoint for basic health check
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint - basic API information.

    Returns:
        API metadata
    """
    return {
        "name": "Todo Backend API",
        "version": "1.0.0",
        "status": "running",
    }
