#!/usr/bin/env python3
# Task ID: T011, T035, T040, T041, T053, T058, T060
# Spec: specs/001-rich-todo-app/spec.md - FR-006, FR-007, FR-008, FR-012, FR-014
"""
Enhanced TaskManager service for Advanced Phase I Rich Console Todo App.

This module provides in-memory storage and management for tasks with
sorting, filtering, search, and recurring task functionality.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable

from src.models.task import Task, Priority, RecurringInterval, TaskStatus
from src.lib.utils import calculate_next_due_date


class TaskManager:
    """
    Manages all task data operations with enhanced functionality.

    Provides CRUD operations, sorting, filtering, search, and
    recurring task management for in-memory task storage.
    """

    def __init__(self):
        """Initialize the task manager."""
        self.tasks: Dict[int, Task] = {}
        self.next_id: int = 0

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        tags: Optional[List[str]] = None,
        due_date: Optional[datetime] = None,
        recurring_interval: RecurringInterval = RecurringInterval.NONE
    ) -> Optional[Task]:
        """
        Add a new task.

        Args:
            title: Task title (required)
            description: Task description (optional)
            priority: Priority level (default: MEDIUM)
            tags: List of tags (optional)
            due_date: Due date and time (optional)
            recurring_interval: Recurring schedule (default: NONE)

        Returns:
            The created Task object, or None if validation fails
        """
        try:
            task = Task(
                task_id=self.next_id,
                title=title,
                description=description,
                priority=priority,
                tags=tags,
                due_date=due_date,
                recurring_interval=recurring_interval
            )
            self.tasks[self.next_id] = task
            self.next_id += 1
            return task
        except ValueError:
            return None

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by ID.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            The Task object, or None if not found
        """
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks sorted by priority and due date.

        Returns:
            List of all tasks, sorted by priority (high first),
            then by due date (soonest first), then by creation order
        """
        return self._sort_tasks(list(self.tasks.values()))

    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks by priority, due date, and creation order.

        Sorting order:
        1. Priority: HIGH > MEDIUM > LOW
        2. Due date: Soonest first (None at end)
        3. Creation order: Oldest first

        Args:
            tasks: List of tasks to sort

        Returns:
            Sorted list of tasks
        """
        def sort_key(task: Task):
            # Priority order (0=HIGH, 1=MEDIUM, 2=LOW)
            priority_order = task.priority.sort_order

            # Due date (use max datetime for None to sort at end)
            if task.due_date is None:
                due_date_order = datetime.max
            else:
                due_date_order = task.due_date

            # Creation order
            creation_order = task.created_at

            return (priority_order, due_date_order, creation_order)

        return sorted(tasks, key=sort_key)

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[Priority] = None,
        tags: Optional[List[str]] = None,
        due_date: Optional[datetime] = None,
        recurring_interval: Optional[RecurringInterval] = None
    ) -> bool:
        """
        Update task attributes.

        Args:
            task_id: ID of the task to update
            title: New title (if provided)
            description: New description (if provided)
            priority: New priority (if provided)
            tags: New tags list (if provided)
            due_date: New due date (if provided)
            recurring_interval: New recurring interval (if provided)

        Returns:
            True on success, False otherwise
        """
        task = self.get_task(task_id)
        if not task:
            return False

        try:
            task.update(
                title=title,
                description=description,
                priority=priority,
                tags=tags,
                due_date=due_date,
                recurring_interval=recurring_interval
            )
            return True
        except ValueError:
            return False

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID (maintains ID gaps).

        Args:
            task_id: ID of the task to delete

        Returns:
            True on success, False otherwise
        """
        if task_id not in self.tasks:
            return False

        del self.tasks[task_id]
        return True

    def mark_complete(self, task_id: int) -> Optional[Task]:
        """
        Mark task as complete. If recurring, creates new task with next due date.

        Args:
            task_id: ID of the task to mark complete

        Returns:
            The new recurring task if created, None otherwise
        """
        task = self.get_task(task_id)
        if not task:
            return None

        task.mark_complete()

        # Handle recurring task logic
        if task.is_recurring and task.due_date:
            next_due_date = calculate_next_due_date(
                task.due_date,
                task.recurring_interval
            )
            new_task = task.clone_for_recurring(next_due_date)
            new_task.id = self.next_id
            self.tasks[self.next_id] = new_task
            self.next_id += 1
            return new_task

        return None

    def mark_incomplete(self, task_id: int) -> bool:
        """
        Mark task as incomplete (pending).

        Args:
            task_id: ID of the task to mark incomplete

        Returns:
            True on success, False otherwise
        """
        task = self.get_task(task_id)
        if not task:
            return False

        task.mark_incomplete()
        return True

    def mark_in_progress(self, task_id: int) -> bool:
        """
        Mark task as in progress.

        Args:
            task_id: ID of the task to mark in progress

        Returns:
            True on success, False otherwise
        """
        task = self.get_task(task_id)
        if not task:
            return False

        task.mark_in_progress()
        return True

    # =========================================================================
    # Search and Filter Methods
    # =========================================================================

    def search_tasks(self, keyword: str) -> List[Task]:
        """
        Search tasks by keyword in title or description.

        Args:
            keyword: Search term (case-insensitive)

        Returns:
            List of matching tasks, sorted by priority and due date
        """
        keyword_lower = keyword.lower().strip()
        if not keyword_lower:
            return []

        matching_tasks = [
            task for task in self.tasks.values()
            if keyword_lower in task.title.lower()
            or keyword_lower in task.description.lower()
        ]

        return self._sort_tasks(matching_tasks)

    def filter_by_status(self, status: TaskStatus) -> List[Task]:
        """
        Filter tasks by status.

        Args:
            status: Status to filter by

        Returns:
            List of tasks with matching status, sorted
        """
        filtered = [
            task for task in self.tasks.values()
            if task.status == status
        ]
        return self._sort_tasks(filtered)

    def filter_by_priority(self, priority: Priority) -> List[Task]:
        """
        Filter tasks by priority.

        Args:
            priority: Priority to filter by

        Returns:
            List of tasks with matching priority, sorted
        """
        filtered = [
            task for task in self.tasks.values()
            if task.priority == priority
        ]
        return self._sort_tasks(filtered)

    def filter_by_tag(self, tag: str) -> List[Task]:
        """
        Filter tasks by tag.

        Args:
            tag: Tag to filter by (case-insensitive)

        Returns:
            List of tasks containing the tag, sorted
        """
        tag_lower = tag.lower().strip()
        if not tag_lower:
            return []

        filtered = [
            task for task in self.tasks.values()
            if tag_lower in task.tags
        ]
        return self._sort_tasks(filtered)

    def get_overdue_tasks(self) -> List[Task]:
        """
        Get all overdue tasks.

        Returns:
            List of tasks that are past due and not completed, sorted
        """
        overdue = [
            task for task in self.tasks.values()
            if task.is_overdue
        ]
        return self._sort_tasks(overdue)

    def get_tasks_by_status(self, status: str) -> List[Task]:
        """
        Get tasks by status string.

        Args:
            status: Status string ("pending", "in-progress", "completed")

        Returns:
            List of tasks with matching status
        """
        try:
            task_status = TaskStatus(status)
            return self.filter_by_status(task_status)
        except ValueError:
            return []

    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """
        Get tasks by priority string.

        Args:
            priority: Priority string ("high", "medium", "low")

        Returns:
            List of tasks with matching priority
        """
        try:
            task_priority = Priority(priority)
            return self.filter_by_priority(task_priority)
        except ValueError:
            return []

    # =========================================================================
    # Statistics Methods
    # =========================================================================

    def get_task_count(self) -> int:
        """Get total number of tasks."""
        return len(self.tasks)

    def get_completed_count(self) -> int:
        """Get number of completed tasks."""
        return len([t for t in self.tasks.values() if t.is_completed])

    def get_pending_count(self) -> int:
        """Get number of pending tasks (not completed)."""
        return len([t for t in self.tasks.values() if not t.is_completed])

    def get_overdue_count(self) -> int:
        """Get number of overdue tasks."""
        return len(self.get_overdue_tasks())

    def get_progress_summary(self) -> tuple:
        """
        Get progress summary.

        Returns:
            Tuple of (completed_count, total_count, percentage)
        """
        total = self.get_task_count()
        completed = self.get_completed_count()
        percentage = (completed / total * 100) if total > 0 else 0
        return (completed, total, percentage)
