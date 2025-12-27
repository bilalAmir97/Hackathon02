#!/usr/bin/env python3
# Task ID: T012, T051
# Spec: specs/001-rich-todo-app/spec.md - FR-009
"""
Utility functions for Advanced Phase I Rich Console Todo App.

This module provides helper functions for date parsing, validation,
and other common operations.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import re

from src.models.task import RecurringInterval


# Date format constant
DATE_FORMAT = "%Y-%m-%d %H:%M"
DATE_REGEX = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"


def validate_date_format(date_string: str) -> bool:
    """
    Validate if a string matches the expected date format.

    Args:
        date_string: String to validate

    Returns:
        True if valid format, False otherwise
    """
    if not date_string:
        return False

    # Check regex pattern first
    if not re.match(DATE_REGEX, date_string.strip()):
        return False

    # Try to parse to verify it's a valid date
    try:
        datetime.strptime(date_string.strip(), DATE_FORMAT)
        return True
    except ValueError:
        return False


def parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse a date string in 'YYYY-MM-DD HH:MM' format.

    Args:
        date_string: Date string to parse

    Returns:
        datetime object if valid, None otherwise
    """
    if not validate_date_format(date_string):
        return None

    try:
        return datetime.strptime(date_string.strip(), DATE_FORMAT)
    except ValueError:
        return None


def format_date(date: datetime) -> str:
    """
    Format a datetime object to 'YYYY-MM-DD HH:MM' string.

    Args:
        date: datetime object to format

    Returns:
        Formatted date string
    """
    return date.strftime(DATE_FORMAT)


def calculate_next_due_date(
    current_due_date: datetime,
    recurring_interval: RecurringInterval
) -> datetime:
    """
    Calculate the next due date for a recurring task.

    Args:
        current_due_date: Current due date
        recurring_interval: Recurring interval (DAILY, WEEKLY)

    Returns:
        Next due date based on interval
    """
    if recurring_interval == RecurringInterval.DAILY:
        return current_due_date + timedelta(days=1)
    elif recurring_interval == RecurringInterval.WEEKLY:
        return current_due_date + timedelta(weeks=1)
    else:
        # No recurrence, return same date
        return current_due_date


def is_overdue(due_date: Optional[datetime]) -> bool:
    """
    Check if a due date is in the past.

    Args:
        due_date: Due date to check (None means not overdue)

    Returns:
        True if overdue, False otherwise
    """
    if due_date is None:
        return False
    return datetime.now() > due_date


def parse_priority(priority_string: str) -> Optional[str]:
    """
    Parse and validate a priority string.

    Args:
        priority_string: Priority string to parse

    Returns:
        Normalized priority string ("high", "medium", "low") or None if invalid
    """
    normalized = priority_string.lower().strip()
    valid_priorities = ["high", "medium", "low", "h", "m", "l"]

    if normalized not in valid_priorities:
        return None

    # Convert shortcuts to full names
    shortcut_map = {"h": "high", "m": "medium", "l": "low"}
    return shortcut_map.get(normalized, normalized)


def parse_tags(tags_string: str) -> list:
    """
    Parse a comma-separated tags string into a list.

    Args:
        tags_string: Comma-separated tags (e.g., "work, home, urgent")

    Returns:
        List of normalized tag strings
    """
    if not tags_string or not tags_string.strip():
        return []

    tags = [tag.strip().lower() for tag in tags_string.split(",")]
    return [tag for tag in tags if tag]  # Filter empty strings


def parse_recurring_interval(interval_string: str) -> Optional[str]:
    """
    Parse and validate a recurring interval string.

    Args:
        interval_string: Interval string to parse

    Returns:
        Normalized interval string ("daily", "weekly", "none") or None if invalid
    """
    normalized = interval_string.lower().strip()
    valid_intervals = ["daily", "weekly", "none", "d", "w", "n"]

    if normalized not in valid_intervals:
        return None

    # Convert shortcuts to full names
    shortcut_map = {"d": "daily", "w": "weekly", "n": "none"}
    return shortcut_map.get(normalized, normalized)


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length with suffix.

    Args:
        text: String to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add if truncated (default: "...")

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_relative_time(date: datetime) -> str:
    """
    Get a human-readable relative time string.

    Args:
        date: datetime to compare to now

    Returns:
        Relative time string (e.g., "2 hours ago", "in 3 days")
    """
    now = datetime.now()
    diff = date - now

    if diff.total_seconds() < 0:
        # Past
        diff = -diff
        suffix = "ago"
    else:
        # Future
        suffix = "from now"

    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    weeks = days / 7

    if seconds < 60:
        return f"{int(seconds)} seconds {suffix}"
    elif minutes < 60:
        return f"{int(minutes)} minutes {suffix}"
    elif hours < 24:
        return f"{int(hours)} hours {suffix}"
    elif days < 7:
        return f"{int(days)} days {suffix}"
    else:
        return f"{int(weeks)} weeks {suffix}"
