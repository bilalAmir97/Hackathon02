#!/usr/bin/env python3
# Task ID: T014, T026, T036, T044-T045, T061
# Spec: specs/001-rich-todo-app/spec.md
"""
Application Controller for Advanced Phase I Rich Console Todo App.

This module provides the main application controller that orchestrates
the CLI interface and task manager operations.
"""

from src.models.task import Priority, RecurringInterval
from src.services.task_manager import TaskManager
from src.cli.cli_interface import CLIInterface


class TodoApp:
    """
    Main application controller.

    Orchestrates the interaction between the CLI interface and
    the task manager, handling all user operations.
    """

    def __init__(self):
        """Initialize the application."""
        self.task_manager = TaskManager()
        self.cli = CLIInterface(self.task_manager)
        self.running = True

    def run(self) -> None:
        """Main application loop."""
        self.cli.display_welcome()
        self.cli.display_startup_alerts()

        while self.running:
            self.cli.display_menu()
            choice = self.cli.get_user_choice()

            if choice == 1:
                self.handle_add_task()
            elif choice == 2:
                self.handle_view_tasks()
            elif choice == 3:
                self.handle_update_task()
            elif choice == 4:
                self.handle_delete_task()
            elif choice == 5:
                self.handle_mark_complete()
            elif choice == 6:
                self.handle_mark_incomplete()
            elif choice == 7:
                self.handle_search()
            elif choice == 8:
                self.handle_filter()
            elif choice == 9:
                self.handle_exit()

    # =========================================================================
    # Task Operations
    # =========================================================================

    def handle_add_task(self) -> None:
        """Handle add task operation with all enhanced fields."""
        title = self.cli.get_task_title()

        if not title or not title.strip():
            self.cli.display_error("Task title cannot be empty.")
            return

        description = self.cli.get_task_description()
        priority = self.cli.get_priority()
        tags = self.cli.get_tags()
        due_date = self.cli.get_due_date()
        recurring_interval = self.cli.get_recurring_interval()

        task = self.task_manager.add_task(
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=due_date,
            recurring_interval=recurring_interval
        )

        if task:
            self.cli.display_success(f"Task added successfully with ID {task.id}!")

            # Show recurring info if applicable
            if task.is_recurring:
                self.cli.display_info(
                    f"This is a recurring task ({task.recurring_interval.value}). "
                    "A new instance will be created when marked complete."
                )
        else:
            self.cli.display_error("Failed to add task. Please check your input.")

    def handle_view_tasks(self) -> None:
        """Handle view tasks operation."""
        self.cli.display_tasks()

    def handle_update_task(self) -> None:
        """Handle update task operation."""
        task_id = self.cli.get_task_id()

        if task_id is None:
            self.cli.display_error("Invalid task ID. Please enter a number.")
            return

        task = self.task_manager.get_task(task_id)
        if not task:
            self.cli.display_error(f"Task with ID {task_id} not found.")
            return

        self.cli.display_info(f"Current task: {task.title}")
        self.cli.display_info("Leave fields empty to keep current values.")

        # Get new values (empty means keep current)
        new_title = self.cli.get_task_title()
        title = new_title if new_title.strip() else None

        new_description = self.cli.get_task_description()
        description = new_description if new_description.strip() else None

        # For priority, tags, due_date, recurring - ask if user wants to change
        if self.cli.confirm_action("Update priority?"):
            priority = self.cli.get_priority()
        else:
            priority = None

        if self.cli.confirm_action("Update tags?"):
            tags = self.cli.get_tags()
        else:
            tags = None

        if self.cli.confirm_action("Update due date?"):
            due_date = self.cli.get_due_date()
        else:
            due_date = None

        if self.cli.confirm_action("Update recurring interval?"):
            recurring_interval = self.cli.get_recurring_interval()
        else:
            recurring_interval = None

        success = self.task_manager.update_task(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=due_date,
            recurring_interval=recurring_interval
        )

        if success:
            self.cli.display_success(f"Task {task_id} updated successfully!")
        else:
            self.cli.display_error("Failed to update task. Please check your input.")

    def handle_delete_task(self) -> None:
        """Handle delete task operation."""
        task_id = self.cli.get_task_id()

        if task_id is None:
            self.cli.display_error("Invalid task ID. Please enter a number.")
            return

        task = self.task_manager.get_task(task_id)
        if not task:
            self.cli.display_error(f"Task with ID {task_id} not found.")
            return

        # Confirm deletion
        if not self.cli.confirm_action(f"Delete task '{task.title}'?"):
            self.cli.display_info("Deletion cancelled.")
            return

        success = self.task_manager.delete_task(task_id)

        if success:
            self.cli.display_success(f"Task {task_id} deleted successfully!")
        else:
            self.cli.display_error(f"Failed to delete task {task_id}.")

    def handle_mark_complete(self) -> None:
        """Handle mark complete operation with recurring task support."""
        task_id = self.cli.get_task_id()

        if task_id is None:
            self.cli.display_error("Invalid task ID. Please enter a number.")
            return

        task = self.task_manager.get_task(task_id)
        if not task:
            self.cli.display_error(f"Task with ID {task_id} not found.")
            return

        new_task = self.task_manager.mark_complete(task_id)

        self.cli.display_success(f"Task {task_id} marked as complete!")

        # If a new recurring task was created, notify user
        if new_task:
            self.cli.display_info(
                f"New recurring task created with ID {new_task.id} "
                f"(due: {new_task.due_date.strftime('%Y-%m-%d %H:%M')})"
            )

    def handle_mark_incomplete(self) -> None:
        """Handle mark incomplete operation."""
        task_id = self.cli.get_task_id()

        if task_id is None:
            self.cli.display_error("Invalid task ID. Please enter a number.")
            return

        success = self.task_manager.mark_incomplete(task_id)

        if success:
            self.cli.display_success(f"Task {task_id} marked as incomplete!")
        else:
            self.cli.display_error(f"Task with ID {task_id} not found.")

    # =========================================================================
    # Search and Filter Operations
    # =========================================================================

    def handle_search(self) -> None:
        """Handle search tasks operation."""
        keyword = self.cli.get_search_keyword()

        if not keyword or not keyword.strip():
            self.cli.display_error("Search keyword cannot be empty.")
            return

        results = self.task_manager.search_tasks(keyword)

        if results:
            self.cli.display_tasks(results, title=f"SEARCH RESULTS: '{keyword}'")
        else:
            self.cli.display_warning(f"No tasks found matching '{keyword}'.")

    def handle_filter(self) -> None:
        """Handle filter tasks operation."""
        filter_type, filter_value = self.cli.get_filter_choice()

        if filter_type == "status":
            results = self.task_manager.get_tasks_by_status(filter_value)
            title = f"TASKS BY STATUS: {filter_value.upper()}"
        elif filter_type == "priority":
            results = self.task_manager.get_tasks_by_priority(filter_value)
            title = f"TASKS BY PRIORITY: {filter_value.upper()}"
        else:  # tag
            results = self.task_manager.filter_by_tag(filter_value)
            title = f"TASKS BY TAG: [{filter_value}]"

        if results:
            self.cli.display_tasks(results, title=title)
        else:
            self.cli.display_warning(f"No tasks found with {filter_type}: {filter_value}")

    # =========================================================================
    # Application Control
    # =========================================================================

    def handle_exit(self) -> None:
        """Handle application exit."""
        self.cli.display_goodbye()
        self.running = False


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main entry point for the application."""
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()
