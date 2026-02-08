"""Domain layer containing entity models and business logic.

This package defines the core domain models (User, Task) and their
relationships. Models use SQLModel for ORM functionality and Pydantic
for validation.

Exports:
    User: User entity model
    Task: Task entity model
    TaskStatus: Task status enumeration
    create_tables: Function to create database tables
"""

from src.domain.models import Task, TaskStatus, User, create_tables

__all__ = [
    "User",
    "Task",
    "TaskStatus",
    "create_tables",
]
