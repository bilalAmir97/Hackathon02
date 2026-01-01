#!/usr/bin/env python3
# Task ID: T013, T020-T025, T032-T034, T042-T043, T052, T054-T056, T059
# Spec: specs/001-rich-todo-app/spec.md - FR-001, FR-002, FR-003, FR-010, FR-013
"""
Rich CLI Interface for Advanced Phase I Rich Console Todo App.

This module provides the rich UI components including panels, tables,
color-coded displays, and emoji status indicators.
"""

import sys
import os
from datetime import datetime
from typing import List, Optional

# Fix Windows console encoding for Unicode/emoji support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    os.system("")  # Enable ANSI escape sequences on Windows

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.text import Text
from rich import box

from src.models.task import Task, Priority, RecurringInterval, TaskStatus
from src.services.task_manager import TaskManager
from src.lib.utils import (
    parse_date, format_date, parse_priority, parse_tags,
    parse_recurring_interval, validate_date_format
)


# Menu Options
MENU_OPTIONS = {
    1: "Add Task",
    2: "View Task List",
    3: "Update Task",
    4: "Delete Task",
    5: "Mark Task Complete",
    6: "Mark Task Incomplete",
    7: "Search Tasks",
    8: "Filter Tasks",
    9: "Exit"
}


class CLIInterface:
    """
    Rich CLI interface for task management.

    Provides a visually enhanced console interface using the rich library
    with panels, tables, color-coded priorities, and emoji status indicators.
    """

    def __init__(self, task_manager: TaskManager):
        """
        Initialize the CLI interface.

        Args:
            task_manager: TaskManager instance to use
        """
        self.task_manager = task_manager
        self.console = Console(force_terminal=True)

    # =========================================================================
    # Dashboard and Menu Display
    # =========================================================================

    def display_startup_alerts(self) -> None:
        """Display critical alert panel for overdue tasks on startup."""
        overdue_tasks = self.task_manager.get_overdue_tasks()

        if overdue_tasks:
            alert_content = self._format_overdue_alert(overdue_tasks)
            self.console.print(Panel(
                alert_content,
                title="[bold red]⚠️ CRITICAL: Overdue Tasks[/bold red]",
                border_style="red",
                box=box.DOUBLE
            ))
            self.console.print()

    def _format_overdue_alert(self, overdue_tasks: List[Task]) -> str:
        """Format overdue tasks for alert panel."""
        lines = []
        for task in overdue_tasks[:5]:  # Show max 5 tasks
            due_str = format_date(task.due_date) if task.due_date else "No due date"
            lines.append(f"[red]• ID {task.id}: {task.title} (Due: {due_str})[/red]")

        if len(overdue_tasks) > 5:
            lines.append(f"[dim]... and {len(overdue_tasks) - 5} more overdue tasks[/dim]")

        return "\n".join(lines)

    def display_menu(self) -> None:
        """Display the main menu wrapped in a rich panel."""
        menu_content = self._build_menu_content()

        self.console.print(Panel(
            menu_content,
            title="[bold cyan]📋 TODO LIST MANAGER[/bold cyan]",
            subtitle=self._get_progress_subtitle(),
            border_style="cyan",
            box=box.ROUNDED
        ))

    def _build_menu_content(self) -> str:
        """Build the menu content string."""
        lines = []
        for option, text in MENU_OPTIONS.items():
            lines.append(f"[cyan]{option}.[/cyan] {text}")
        return "\n".join(lines)

    def _get_progress_subtitle(self) -> str:
        """Get progress summary for menu subtitle."""
        completed, total, percentage = self.task_manager.get_progress_summary()
        if total == 0:
            return "[dim]No tasks yet[/dim]"
        return f"[green]{completed}/{total}[/green] Tasks Completed ([yellow]{percentage:.0f}%[/yellow])"

    def display_progress_bar(self) -> None:
        """Display a progress bar summary of task completion."""
        completed, total, percentage = self.task_manager.get_progress_summary()

        if total == 0:
            self.console.print("[dim]No tasks to show progress for.[/dim]")
            return

        # Create a visual progress bar
        filled = int(percentage / 5)  # 20 segments total
        empty = 20 - filled
        bar = f"[green]{'█' * filled}[/green][dim]{'░' * empty}[/dim]"

        self.console.print(f"\n{bar} [bold]{completed}/{total}[/bold] ({percentage:.1f}%)")

    # =========================================================================
    # Task Display
    # =========================================================================

    def display_tasks(self, tasks: Optional[List[Task]] = None, title: str = "YOUR TASKS") -> None:
        """
        Display tasks in a rich table format.

        Args:
            tasks: List of tasks to display (default: all tasks)
            title: Title for the table panel
        """
        if tasks is None:
            tasks = self.task_manager.get_all_tasks()

        if not tasks:
            self.console.print(Panel(
                "[yellow]Your task list is empty.[/yellow]",
                title=f"[bold]{title}[/bold]",
                border_style="yellow"
            ))
            return

        table = self._build_task_table(tasks)

        self.console.print(Panel(
            table,
            title=f"[bold cyan]{title}[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED
        ))

        self.display_progress_bar()

    def _build_task_table(self, tasks: List[Task]) -> Table:
        """Build a rich table for task display."""
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE_HEAD,
            expand=True
        )

        # Add columns
        table.add_column("ID", justify="center", style="cyan", width=6)
        table.add_column("Status", justify="center", width=8)
        table.add_column("Priority", justify="center", width=10)
        table.add_column("Due Date", justify="center", width=18)
        table.add_column("Title & Tags", style="white")
        table.add_column("Recurring", justify="center", width=10)

        # Add rows
        for task in tasks:
            table.add_row(*self._format_task_row(task))

        return table

    def _format_task_row(self, task: Task) -> tuple:
        """Format a single task as a table row."""
        # ID (centered, cyan)
        task_id = str(task.id)

        # Status (emoji)
        status = task.status.emoji

        # Priority (color-coded)
        priority_color = task.priority.color
        priority = f"[{priority_color}]{task.priority.value.upper()}[/{priority_color}]"

        # Due date (red if overdue)
        if task.due_date:
            due_str = format_date(task.due_date)
            if task.is_overdue:
                due_date = f"[red bold]{due_str}[/red bold]"
            else:
                due_date = due_str
        else:
            due_date = "[dim]—[/dim]"

        # Title with tags
        title_tags = task.title
        if task.tags:
            tags_str = " ".join(f"[dim][{tag}][/dim]" for tag in task.tags)
            title_tags = f"{task.title} {tags_str}"

        # Recurring indicator
        if task.is_recurring:
            recurring = f"🔄 {task.recurring_interval.value}"
        else:
            recurring = "[dim]—[/dim]"

        return (task_id, status, priority, due_date, title_tags, recurring)

    # =========================================================================
    # User Input Methods
    # =========================================================================

    def get_user_choice(self) -> int:
        """
        Get and validate user menu choice.

        Returns:
            User's menu choice (1-9)
        """
        while True:
            try:
                choice = IntPrompt.ask(
                    "\n[bold]Enter your choice[/bold]",
                    choices=[str(i) for i in range(1, 10)]
                )
                return choice
            except Exception:
                self.display_error("Invalid input. Please enter a number between 1 and 9.")

    def get_task_title(self) -> str:
        """Get task title from user."""
        return Prompt.ask("[bold]Enter task title[/bold]")

    def get_task_description(self) -> str:
        """Get optional task description from user."""
        description = Prompt.ask(
            "[bold]Enter task description[/bold]",
            default=""
        )
        return description

    def get_priority(self) -> Priority:
        """Get task priority from user."""
        while True:
            priority_str = Prompt.ask(
                "[bold]Enter priority[/bold] ([red]H[/red]igh/[yellow]M[/yellow]edium/[blue]L[/blue]ow)",
                default="m"
            )
            parsed = parse_priority(priority_str)
            if parsed:
                return Priority(parsed)
            self.display_error("Invalid priority. Use H, M, L or high, medium, low.")

    def get_tags(self) -> List[str]:
        """Get task tags from user."""
        tags_str = Prompt.ask(
            "[bold]Enter tags[/bold] (comma-separated, e.g., work, home)",
            default=""
        )
        return parse_tags(tags_str)

    def get_due_date(self) -> Optional[datetime]:
        """Get optional due date from user."""
        while True:
            date_str = Prompt.ask(
                "[bold]Enter due date[/bold] (YYYY-MM-DD HH:MM or leave empty)",
                default=""
            )

            if not date_str:
                return None

            parsed = parse_date(date_str)
            if parsed:
                return parsed

            self.display_error("Invalid date format. Use YYYY-MM-DD HH:MM (e.g., 2025-01-15 14:30)")

    def get_recurring_interval(self) -> RecurringInterval:
        """Get recurring interval from user."""
        while True:
            interval_str = Prompt.ask(
                "[bold]Set recurring[/bold] ([green]D[/green]aily/[blue]W[/blue]eekly/[dim]N[/dim]one)",
                default="n"
            )
            parsed = parse_recurring_interval(interval_str)
            if parsed:
                return RecurringInterval(parsed)
            self.display_error("Invalid interval. Use D, W, N or daily, weekly, none.")

    def get_task_id(self) -> Optional[int]:
        """
        Get and validate task ID from user.

        Returns:
            Task ID, or None if invalid
        """
        try:
            task_id = IntPrompt.ask("[bold]Enter task ID[/bold]")
            return task_id
        except Exception:
            return None

    def get_search_keyword(self) -> str:
        """Get search keyword from user."""
        return Prompt.ask("[bold]Enter search keyword[/bold]")

    def get_filter_choice(self) -> tuple:
        """
        Get filter type and value from user.

        Returns:
            Tuple of (filter_type, filter_value)
        """
        self.console.print("\n[bold]Filter by:[/bold]")
        self.console.print("1. Status (pending/in-progress/completed)")
        self.console.print("2. Priority (high/medium/low)")
        self.console.print("3. Tag")

        choice = Prompt.ask(
            "[bold]Choose filter type[/bold]",
            choices=["1", "2", "3"]
        )

        if choice == "1":
            status = Prompt.ask(
                "[bold]Enter status[/bold]",
                choices=["pending", "in-progress", "completed"]
            )
            return ("status", status)
        elif choice == "2":
            priority = Prompt.ask(
                "[bold]Enter priority[/bold]",
                choices=["high", "medium", "low"]
            )
            return ("priority", priority)
        else:
            tag = Prompt.ask("[bold]Enter tag[/bold]")
            return ("tag", tag)

    def confirm_action(self, message: str) -> bool:
        """Ask user to confirm an action."""
        return Confirm.ask(message)

    # =========================================================================
    # Message Display Methods
    # =========================================================================

    def display_message(self, message: str, style: str = "green") -> None:
        """
        Display a message to the user.

        Args:
            message: Message text
            style: Rich style (default: green)
        """
        self.console.print(f"\n[{style}]{message}[/{style}]")

    def display_error(self, error: str) -> None:
        """
        Display an error message.

        Args:
            error: Error message text
        """
        self.console.print(f"\n[red bold]ERROR:[/red bold] [red]{error}[/red]")

    def display_success(self, message: str) -> None:
        """Display a success message."""
        self.console.print(f"\n[green bold]✓[/green bold] [green]{message}[/green]")

    def display_warning(self, message: str) -> None:
        """Display a warning message."""
        self.console.print(f"\n[yellow bold]⚠[/yellow bold] [yellow]{message}[/yellow]")

    def display_info(self, message: str) -> None:
        """Display an info message."""
        self.console.print(f"\n[cyan]ℹ {message}[/cyan]")

    def display_welcome(self) -> None:
        """Display welcome message."""
        self.console.print(Panel(
            "[bold green]Welcome to the Advanced Todo List Manager![/bold green]\n"
            "[dim]A rich, feature-packed console todo application[/dim]",
            border_style="green",
            box=box.DOUBLE
        ))

    def display_goodbye(self) -> None:
        """Display goodbye message."""
        self.console.print(Panel(
            "[bold green]Thank you for using Todo List Manager. Goodbye![/bold green]",
            border_style="green"
        ))
