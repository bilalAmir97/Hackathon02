#!/usr/bin/env python3
# Task ID: T010, T030, T031, T050, T057
# Spec: specs/001-rich-todo-app/spec.md - FR-004, FR-005, FR-009, FR-011
"""
Enhanced Task data model for Advanced Phase I Rich Console Todo App.

This module defines the Task entity with priority, tags, due dates, and
recurring functionality as specified in the data model documentation.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional


class Priority(Enum):
    """Task priority levels with display colors for rich UI."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def color(self) -> str:
        """Return the rich color for this priority level."""
        colors = {
            Priority.HIGH: "red",
            Priority.MEDIUM: "yellow",
            Priority.LOW: "blue"
        }
        return colors[self]

    @property
    def sort_order(self) -> int:
        """Return sort order (lower is higher priority)."""
        order = {
            Priority.HIGH: 0,
            Priority.MEDIUM: 1,
            Priority.LOW: 2
        }
        return order[self]


class RecurringInterval(Enum):
    """Recurring task interval options."""
    DAILY = "daily"
    WEEKLY = "weekly"
    NONE = "none"


class TaskStatus(Enum):
    """Task completion status with emoji indicators."""
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"

    @property
    def emoji(self) -> str:
        """Return the emoji indicator for this status."""
        emojis = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅"
        }
        return emojis[self]


class Task:
    """
    Represents a single todo item with enhanced organizational features.

    Attributes:
        id: Unique identifier assigned sequentially (immutable)
        title: Task description/title (required, max 500 characters)
        description: Optional detailed description (max 1000 characters)
        status: Completion status (pending, in-progress, completed)
        priority: Task priority level (high, medium, low)
        tags: List of text tags (e.g., ["Work", "Home"])
        due_date: Due date and time (nullable)
        recurring_interval: Recurring schedule (daily, weekly, none)
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last updated
    """

    MAX_TITLE_LENGTH = 500
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_TAGS = 10

    def __init__(
        self,
        task_id: int,
        title: str,
        description: str = "",
        status: TaskStatus = TaskStatus.PENDING,
        priority: Priority = Priority.MEDIUM,
        tags: Optional[List[str]] = None,
        due_date: Optional[datetime] = None,
        recurring_interval: RecurringInterval = RecurringInterval.NONE,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize a Task.

        Args:
            task_id: Unique identifier (zero-based)
            title: Text content of the task (required)
            description: Detailed description (optional)
            status: Completion status (default: PENDING)
            priority: Priority level (default: MEDIUM)
            tags: List of tags (default: empty list)
            due_date: Due date and time (default: None)
            recurring_interval: Recurring schedule (default: NONE)
            created_at: Creation timestamp (default: now)
            updated_at: Last update timestamp (default: now)

        Raises:
            ValueError: If title is empty or exceeds max length
            ValueError: If description exceeds max length
            ValueError: If tags exceed max count
        """
        # Validate title
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        if len(title) > self.MAX_TITLE_LENGTH:
            raise ValueError(f"Task title cannot exceed {self.MAX_TITLE_LENGTH} characters")

        # Validate description
        if description and len(description) > self.MAX_DESCRIPTION_LENGTH:
            raise ValueError(f"Task description cannot exceed {self.MAX_DESCRIPTION_LENGTH} characters")

        # Validate tags
        if tags and len(tags) > self.MAX_TAGS:
            raise ValueError(f"Task cannot have more than {self.MAX_TAGS} tags")

        self.id = task_id
        self.title = title.strip()
        self.description = description.strip() if description else ""
        self.status = status
        self.priority = priority
        self.tags = [tag.lower().strip() for tag in (tags or [])]
        self.due_date = due_date
        self.recurring_interval = recurring_interval

        now = datetime.now()
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == TaskStatus.COMPLETED

    @property
    def is_recurring(self) -> bool:
        """Check if task is recurring."""
        return self.recurring_interval != RecurringInterval.NONE

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue (past due date and not completed)."""
        if self.due_date is None:
            return False
        if self.is_completed:
            return False
        return datetime.now() > self.due_date

    @property
    def tags_display(self) -> str:
        """Format tags for display with brackets."""
        if not self.tags:
            return ""
        return " ".join(f"[{tag}]" for tag in self.tags)

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.status = TaskStatus.COMPLETED
        self.updated_at = datetime.now()

    def mark_incomplete(self) -> None:
        """Mark the task as incomplete (pending)."""
        self.status = TaskStatus.PENDING
        self.updated_at = datetime.now()

    def mark_in_progress(self) -> None:
        """Mark the task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now()

    def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[Priority] = None,
        tags: Optional[List[str]] = None,
        due_date: Optional[datetime] = None,
        recurring_interval: Optional[RecurringInterval] = None
    ) -> None:
        """
        Update task attributes.

        Args:
            title: New title (if provided)
            description: New description (if provided)
            priority: New priority (if provided)
            tags: New tags list (if provided)
            due_date: New due date (if provided)
            recurring_interval: New recurring interval (if provided)

        Raises:
            ValueError: If any validation fails
        """
        if title is not None:
            if not title or not title.strip():
                raise ValueError("Task title cannot be empty")
            if len(title) > self.MAX_TITLE_LENGTH:
                raise ValueError(f"Task title cannot exceed {self.MAX_TITLE_LENGTH} characters")
            self.title = title.strip()

        if description is not None:
            if len(description) > self.MAX_DESCRIPTION_LENGTH:
                raise ValueError(f"Task description cannot exceed {self.MAX_DESCRIPTION_LENGTH} characters")
            self.description = description.strip()

        if priority is not None:
            self.priority = priority

        if tags is not None:
            if len(tags) > self.MAX_TAGS:
                raise ValueError(f"Task cannot have more than {self.MAX_TAGS} tags")
            self.tags = [tag.lower().strip() for tag in tags]

        if due_date is not None:
            self.due_date = due_date

        if recurring_interval is not None:
            self.recurring_interval = recurring_interval

        self.updated_at = datetime.now()

    def clone_for_recurring(self, next_due_date: datetime) -> "Task":
        """
        Create a clone of this task for the next recurring instance.

        Args:
            next_due_date: The due date for the new instance

        Returns:
            A new Task instance with the same properties but new due date
        """
        # Note: The new task ID will be assigned by TaskManager
        return Task(
            task_id=-1,  # Placeholder, will be set by TaskManager
            title=self.title,
            description=self.description,
            status=TaskStatus.PENDING,
            priority=self.priority,
            tags=self.tags.copy(),
            due_date=next_due_date,
            recurring_interval=self.recurring_interval
        )

    def __str__(self) -> str:
        """String representation of the task."""
        status_str = self.status.emoji
        priority_str = f"[{self.priority.value.upper()}]"
        tags_str = self.tags_display

        parts = [f"{status_str} ID {self.id}: {priority_str} {self.title}"]

        if tags_str:
            parts[0] += f" {tags_str}"

        if self.due_date:
            due_str = self.due_date.strftime("%Y-%m-%d %H:%M")
            if self.is_overdue:
                parts.append(f"  [OVERDUE] Due: {due_str}")
            else:
                parts.append(f"  Due: {due_str}")

        if self.is_recurring:
            parts.append(f"  Recurring: {self.recurring_interval.value}")

        return "\n".join(parts)

    def __repr__(self) -> str:
        """Detailed representation of the task."""
        return (
            f"Task(id={self.id}, title='{self.title[:30]}...', "
            f"status={self.status.value}, priority={self.priority.value}, "
            f"tags={self.tags}, due_date={self.due_date}, "
            f"recurring={self.recurring_interval.value})"
        )
