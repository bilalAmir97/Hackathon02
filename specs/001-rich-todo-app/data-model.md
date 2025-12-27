# Data Model: Advanced Phase I Rich Console Todo App

**Created**: 2025-12-28
**Feature**: Advanced Phase I Rich Console Todo App
**Branch**: 001-rich-todo-app

## Overview

This document defines the data model for the rich console todo application, including the enhanced Task entity with priority, tags, due dates, and recurring functionality.

## Entity Definitions

### Task

**Description**: Represents a single todo item with enhanced organizational and intelligence features.

**Attributes**:
- `id: int` - Unique identifier assigned sequentially (immutable)
- `title: str` - Task description/title (required, max 500 characters)
- `description: str` - Optional detailed description (max 1000 characters)
- `status: str` - Completion status ("pending", "in-progress", "completed")
- `priority: PriorityEnum` - Task priority level ("high", "medium", "low")
- `tags: List[str]` - List of text tags (e.g., ["Work", "Home"])
- `due_date: datetime` - Due date and time (nullable)
- `recurring_interval: RecurringEnum` - Recurring schedule ("daily", "weekly", "none")
- `created_at: datetime` - Timestamp when task was created
- `updated_at: datetime` - Timestamp when task was last updated

**Validation Rules**:
- `id` must be unique and non-negative
- `title` must not be empty and not exceed 500 characters
- `priority` must be one of the PriorityEnum values
- `tags` must be lowercase and not exceed 10 tags per task
- `due_date` must be in 'YYYY-MM-DD HH:MM' format when present
- `recurring_interval` must be one of the RecurringEnum values

**State Transitions**:
- `pending` → `in-progress`: When user marks task as in-progress
- `in-progress` → `pending`: When user marks task as pending again
- `in-progress` → `completed`: When user marks task as complete
- `completed` → `in-progress`: When user marks task as incomplete

### PriorityEnum

**Values**:
- `HIGH` = "high"
- `MEDIUM` = "medium"
- `LOW` = "low"

### RecurringEnum

**Values**:
- `DAILY` = "daily"
- `WEEKLY` = "weekly"
- `NONE` = "none"

### TaskManager

**Description**: In-memory storage and management system for tasks.

**Attributes**:
- `tasks: Dict[int, Task]` - Dictionary mapping task IDs to Task objects
- `next_id: int` - Next available task ID (auto-incrementing)

**Methods**:
- `add_task(title: str, description: str, priority: str, tags: List[str], due_date: datetime, recurring_interval: str) -> int`
- `get_task(task_id: int) -> Optional[Task]`
- `update_task(task_id: int, **kwargs) -> bool`
- `delete_task(task_id: int) -> bool`
- `get_all_tasks() -> List[Task]`
- `get_tasks_by_status(status: str) -> List[Task]`
- `get_tasks_by_priority(priority: str) -> List[Task]`
- `get_tasks_by_tag(tag: str) -> List[Task]`
- `search_tasks(keyword: str) -> List[Task]`
- `sort_tasks() -> List[Task]` - Sort by priority (high→medium→low), then by due date (soonest first), then by creation order
- `mark_task_complete(task_id: int) -> bool` - If recurring, creates new task with next due date
- `get_overdue_tasks() -> List[Task]` - Tasks with due_date < current time and status != "completed"

## Relationships

### Task Relationships
- Each Task exists independently in the TaskManager
- Recurring tasks create new Tasks when marked complete (preserves history)

## Constraints

### Data Integrity
- Task IDs must remain unique throughout the application lifecycle
- Deleted task IDs are not reused (to maintain consistency)
- All datetime operations use UTC to avoid timezone issues

### Business Rules
- A recurring task creates a new task with the same properties when marked complete
- Due date validation: must follow 'YYYY-MM-DD HH:MM' format
- Tag format: lowercase, alphanumeric with hyphens (e.g., "work-project")
- Priority levels directly affect sorting order

## State Diagram

```
[pending] <---> [in-progress] --> [completed]
    ^                                |
    |______ (recurring task) ________|
       |
    [new instance with next due date]
```

## Serialization Format

Tasks are stored in-memory as Python objects and are not persisted beyond runtime. The internal representation uses Python data types as defined above.