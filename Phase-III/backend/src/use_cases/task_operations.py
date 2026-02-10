"""Use cases for task operations.

Business logic for task CRUD operations including creation, retrieval,
updates, and deletion. All operations enforce user-scoped data access.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from src.domain.models import Task, TaskStatus
from src.middleware.error_handler import DatabaseError, TaskNotFoundError
from src.schemas.task import TaskCreate, TaskUpdate


async def create_task(
    session: AsyncSession,
    user_id: UUID,
    task_data: TaskCreate,
) -> Task:
    """Create a new task for a user.

    Validates input data, generates UUID, sets timestamps, and persists
    the task to the database. All tasks default to PENDING status.

    Args:
        session: Async database session
        user_id: UUID of the user creating the task
        task_data: Validated task creation data (title, description)

    Returns:
        Created Task instance with all fields populated

    Raises:
        DatabaseError: If database operation fails
        ValueError: If validation fails (handled by Pydantic)

    Example:
        task_data = TaskCreate(title="Buy groceries", description="Milk, eggs")
        task = await create_task(session, user_id, task_data)
    """
    try:
        # Create task instance with generated UUID and timestamps
        task = Task(
            id=uuid4(),  # Generate UUID v4
            user_id=user_id,  # Set owner
            title=task_data.title.strip(),  # Strip whitespace
            description=task_data.description.strip() if task_data.description else None,
            status=TaskStatus.PENDING,  # Default status
            created_at=datetime.utcnow(),  # UTC timestamp
            updated_at=datetime.utcnow(),  # UTC timestamp
        )

        # Add to session and commit
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return task

    except Exception as e:
        # Rollback on error
        await session.rollback()
        raise DatabaseError(f"Failed to create task: {str(e)}") from e


async def get_task_by_id(
    session: AsyncSession,
    user_id: UUID,
    task_id: UUID,
) -> Task:
    """Retrieve a task by ID with ownership verification.

    Queries the database for a task with the given ID and verifies that
    it belongs to the specified user. Returns 404 for both non-existent
    tasks and tasks belonging to other users (timing attack prevention).

    Args:
        session: Async database session
        user_id: UUID of the user requesting the task
        task_id: UUID of the task to retrieve

    Returns:
        Task instance if found and owned by user

    Raises:
        TaskNotFoundError: If task doesn't exist or doesn't belong to user
        DatabaseError: If database operation fails

    Example:
        task = await get_task_by_id(session, user_id, task_id)
    """
    try:
        # Query task by ID AND user_id (ownership check)
        # This prevents timing attacks by always filtering by user_id
        query = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,  # Critical: enforce ownership
        )

        result = await session.execute(query)
        task = result.scalar_one_or_none()

        # Return 404 if not found OR doesn't belong to user
        # Same response for both cases (timing attack prevention)
        if task is None:
            raise TaskNotFoundError(task_id=str(task_id), user_id=str(user_id))

        return task

    except TaskNotFoundError:
        # Re-raise TaskNotFoundError as-is
        raise
    except Exception as e:
        # Wrap other exceptions as DatabaseError
        raise DatabaseError(f"Failed to retrieve task: {str(e)}") from e


async def update_task(
    session: AsyncSession,
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
) -> Task:
    """Update an existing task with ownership verification and optimistic locking.

    Updates only the fields provided in task_data (partial update support).
    Automatically updates the updated_at timestamp and increments version.
    Uses optimistic locking to prevent concurrent modification conflicts.

    Args:
        session: Async database session
        user_id: UUID of the user updating the task
        task_id: UUID of the task to update
        task_data: Validated task update data (title, description, status)

    Returns:
        Updated Task instance

    Raises:
        TaskNotFoundError: If task doesn't exist or doesn't belong to user
        DatabaseError: If database operation fails or concurrent modification detected
        ValueError: If no fields provided for update (handled by Pydantic)

    Example:
        task_data = TaskUpdate(title="Updated title", status="completed")
        task = await update_task(session, user_id, task_id, task_data)
    """
    try:
        # First, retrieve the task with ownership verification
        task = await get_task_by_id(session, user_id, task_id)

        # Store the current version for optimistic locking
        current_version = task.version

        # Update only provided fields
        if task_data.title is not None:
            task.title = task_data.title.strip()

        if task_data.description is not None:
            task.description = task_data.description.strip() if task_data.description else None

        if task_data.status is not None:
            task.status = task_data.status

        # Update timestamp and increment version
        task.updated_at = datetime.utcnow()
        task.version = current_version + 1

        # Use optimistic locking: update only if version matches
        from sqlalchemy import update
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .where(Task.version == current_version)
            .values(
                title=task.title,
                description=task.description,
                status=task.status,
                updated_at=task.updated_at,
                version=task.version
            )
        )

        result = await session.execute(stmt)
        await session.commit()

        # Check if update succeeded (rowcount should be 1)
        if result.rowcount == 0:
            raise DatabaseError(
                "Concurrent modification detected. Task was modified by another process."
            )

        # Refresh task to get updated state
        await session.refresh(task)

        return task

    except TaskNotFoundError:
        # Re-raise TaskNotFoundError as-is
        raise
    except DatabaseError:
        # Re-raise DatabaseError as-is (includes concurrent modification)
        await session.rollback()
        raise
    except Exception as e:
        # Rollback on error
        await session.rollback()
        raise DatabaseError(f"Failed to update task: {str(e)}") from e


async def delete_task(
    session: AsyncSession,
    user_id: UUID,
    task_id: UUID,
) -> None:
    """Delete a task with ownership verification.

    Performs a hard delete (permanent removal) of the task.

    Args:
        session: Async database session
        user_id: UUID of the user deleting the task
        task_id: UUID of the task to delete

    Returns:
        None

    Raises:
        TaskNotFoundError: If task doesn't exist or doesn't belong to user
        DatabaseError: If database operation fails

    Example:
        await delete_task(session, user_id, task_id)
    """
    try:
        # First, retrieve the task with ownership verification
        task = await get_task_by_id(session, user_id, task_id)

        # Hard delete - permanent removal
        await session.delete(task)
        await session.commit()

    except TaskNotFoundError:
        # Re-raise TaskNotFoundError as-is
        raise
    except Exception as e:
        # Rollback on error
        await session.rollback()
        raise DatabaseError(f"Failed to delete task: {str(e)}") from e


async def toggle_task_completion(
    session: AsyncSession,
    user_id: UUID,
    task_id: UUID,
) -> Task:
    """Toggle task completion status with ownership verification.

    Toggles between PENDING and COMPLETED status.
    Automatically updates the updated_at timestamp.

    Args:
        session: Async database session
        user_id: UUID of the user toggling the task
        task_id: UUID of the task to toggle

    Returns:
        Updated Task instance with toggled status

    Raises:
        TaskNotFoundError: If task doesn't exist or doesn't belong to user
        DatabaseError: If database operation fails

    Example:
        task = await toggle_task_completion(session, user_id, task_id)
    """
    try:
        # First, retrieve the task with ownership verification
        task = await get_task_by_id(session, user_id, task_id)

        # Toggle status: PENDING ↔ COMPLETED
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.COMPLETED
        else:
            task.status = TaskStatus.PENDING

        # Update timestamp
        task.updated_at = datetime.utcnow()

        # Commit changes
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return task

    except TaskNotFoundError:
        # Re-raise TaskNotFoundError as-is
        raise
    except Exception as e:
        # Rollback on error
        await session.rollback()
        raise DatabaseError(f"Failed to toggle task completion: {str(e)}") from e


async def list_tasks(
    session: AsyncSession,
    user_id: UUID,
    status: TaskStatus | None = None,
    offset: int = 0,
    limit: int = 20,
) -> list[Task]:
    """List tasks for a user with optional filtering and pagination.

    Retrieves tasks belonging to the specified user with optional status
    filtering and pagination support. Results are ordered by created_at
    DESC (newest first) for consistent pagination.

    Args:
        session: Async database session
        user_id: UUID of the user requesting tasks
        status: Optional status filter (pending or completed)
        offset: Starting position for pagination (default: 0)
        limit: Maximum number of tasks to return (default: 20, max: 100)

    Returns:
        List of Task instances matching the criteria

    Raises:
        DatabaseError: If database operation fails

    Example:
        # List all tasks for user
        tasks = await list_tasks(session, user_id)

        # List pending tasks with pagination
        tasks = await list_tasks(session, user_id, status=TaskStatus.PENDING, offset=0, limit=10)
    """
    try:
        # Build query with user_id filter (always required)
        query = select(Task).where(Task.user_id == user_id)

        # Add optional status filter
        if status is not None:
            query = query.where(Task.status == status)

        # Add ordering (newest first for consistent pagination)
        query = query.order_by(Task.created_at.desc())

        # Add pagination
        query = query.offset(offset).limit(limit)

        # Execute query
        result = await session.execute(query)
        tasks = result.scalars().all()

        return list(tasks)

    except Exception as e:
        # Wrap exceptions as DatabaseError
        raise DatabaseError(f"Failed to list tasks: {str(e)}") from e


async def count_tasks(
    session: AsyncSession,
    user_id: UUID,
    status: TaskStatus | None = None,
) -> int:
    """Count total tasks for a user with optional filtering.

    Counts the total number of tasks matching the criteria. Used for
    pagination metadata calculation (total count, has_next, has_previous).

    Args:
        session: Async database session
        user_id: UUID of the user requesting tasks
        status: Optional status filter (pending or completed)

    Returns:
        Total count of tasks matching the criteria

    Raises:
        DatabaseError: If database operation fails

    Example:
        # Count all tasks for user
        total = await count_tasks(session, user_id)

        # Count pending tasks
        total = await count_tasks(session, user_id, status=TaskStatus.PENDING)
    """
    try:
        # Build count query with user_id filter (always required)
        query = select(func.count(Task.id)).where(Task.user_id == user_id)

        # Add optional status filter
        if status is not None:
            query = query.where(Task.status == status)

        # Execute query
        result = await session.execute(query)
        count = result.scalar_one()

        return count

    except Exception as e:
        # Wrap exceptions as DatabaseError
        raise DatabaseError(f"Failed to count tasks: {str(e)}") from e
