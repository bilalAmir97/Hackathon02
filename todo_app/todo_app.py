#!/usr/bin/env python3
"""
Evolution of Todo - Phase I
An in-memory console-based todo list manager
"""

from typing import Dict, List, Optional


# Constants
MAX_DESCRIPTION_LENGTH = 500

# Menu Options
MENU_OPTIONS = {
    1: "Add Task",
    2: "View Task List",
    3: "Update Task",
    4: "Delete Task",
    5: "Mark Task Complete",
    6: "Mark Task Incomplete",
    7: "Exit"
}

# ANSI Color Codes
COLORS = {
    'HEADER': '\033[95m',
    'OKBLUE': '\033[94m',
    'OKCYAN': '\033[96m',
    'OKGREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}


# ============================================================================
# Task Data Model
# ============================================================================

class Task:
    """Represents a single todo item"""

    def __init__(self, task_id: int, description: str, completed: bool = False):
        """
        Initialize a Task

        Args:
            task_id: Unique identifier (zero-based)
            description: Text content of the task
            completed: Completion status (default: False)
        """
        self.id = task_id
        self.description = description
        self.completed = completed

    def __str__(self) -> str:
        """String representation of the task"""
        status = "X" if self.completed else " "
        return f"[{status}] ID {self.id}: {self.description}"


# ============================================================================
# Task Manager
# ============================================================================

class TaskManager:
    """Manages all task data operations"""

    def __init__(self):
        """Initialize the task manager"""
        self.tasks: Dict[int, Task] = {}
        self.next_id: int = 0

    def add_task(self, description: str) -> Optional[Task]:
        """
        Add a new task

        Args:
            description: Task description

        Returns:
            The created Task object, or None if validation fails
        """
        # Validate description
        if not description or not description.strip():
            return None

        if len(description) > MAX_DESCRIPTION_LENGTH:
            return None

        # Create task with next available ID
        task = Task(self.next_id, description.strip())
        self.tasks[self.next_id] = task
        self.next_id += 1

        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by ID

        Args:
            task_id: ID of the task to retrieve

        Returns:
            The Task object, or None if not found
        """
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks sorted by ID

        Returns:
            List of all tasks
        """
        return [self.tasks[task_id] for task_id in sorted(self.tasks.keys())]

    def update_task(self, task_id: int, new_description: str) -> bool:
        """
        Update task description

        Args:
            task_id: ID of the task to update
            new_description: New description text

        Returns:
            True on success, False otherwise
        """
        # Validate task exists
        task = self.get_task(task_id)
        if not task:
            return False

        # Validate new description
        if not new_description or not new_description.strip():
            return False

        if len(new_description) > MAX_DESCRIPTION_LENGTH:
            return False

        # Update description
        task.description = new_description.strip()
        return True

    def mark_complete(self, task_id: int) -> bool:
        """
        Mark task as complete

        Args:
            task_id: ID of the task to mark complete

        Returns:
            True on success, False otherwise
        """
        task = self.get_task(task_id)
        if not task:
            return False

        task.completed = True
        return True

    def mark_incomplete(self, task_id: int) -> bool:
        """
        Mark task as incomplete

        Args:
            task_id: ID of the task to mark incomplete

        Returns:
            True on success, False otherwise
        """
        task = self.get_task(task_id)
        if not task:
            return False

        task.completed = False
        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID (maintains ID gaps)

        Args:
            task_id: ID of the task to delete

        Returns:
            True on success, False otherwise
        """
        if task_id not in self.tasks:
            return False

        del self.tasks[task_id]
        return True


# ============================================================================
# CLI Interface
# ============================================================================

class CLIInterface:
    """Handles all user interface operations"""

    def __init__(self, task_manager: TaskManager):
        """
        Initialize the CLI interface

        Args:
            task_manager: TaskManager instance to use
        """
        self.task_manager = task_manager

    def display_menu(self):
        """Display the main menu"""
        print(f"\n{COLORS['HEADER']}{COLORS['BOLD']}{'=' * 50}{COLORS['ENDC']}")
        print(f"{COLORS['HEADER']}{COLORS['BOLD']}{'TODO LIST MANAGER':^50}{COLORS['ENDC']}")
        print(f"{COLORS['HEADER']}{COLORS['BOLD']}{'=' * 50}{COLORS['ENDC']}\n")

        for option, text in MENU_OPTIONS.items():
            print(f"{COLORS['OKCYAN']}{option}. {text}{COLORS['ENDC']}")

        print(f"\n{COLORS['HEADER']}{'=' * 50}{COLORS['ENDC']}")

    def get_user_choice(self) -> int:
        """
        Get and validate user menu choice

        Returns:
            User's menu choice (1-7)
        """
        while True:
            try:
                choice = input(f"\n{COLORS['BOLD']}Enter your choice (1-7): {COLORS['ENDC']}")
                choice = int(choice)
                if 1 <= choice <= 7:
                    return choice
                else:
                    self.display_error("Invalid choice. Please enter a number between 1 and 7.")
            except ValueError:
                self.display_error("Invalid input. Please enter a number.")

    def display_tasks(self):
        """Display all tasks"""
        tasks = self.task_manager.get_all_tasks()

        if not tasks:
            self.display_message("Your task list is empty.", 'WARNING')
            return

        print(f"\n{COLORS['HEADER']}{COLORS['BOLD']}{'─' * 50}{COLORS['ENDC']}")
        print(f"{COLORS['HEADER']}{COLORS['BOLD']}{'YOUR TASKS':^50}{COLORS['ENDC']}")
        print(f"{COLORS['HEADER']}{COLORS['BOLD']}{'─' * 50}{COLORS['ENDC']}\n")

        for task in tasks:
            if task.completed:
                color = COLORS['OKGREEN']
                status_icon = "X"
            else:
                color = COLORS['WARNING']
                status_icon = " "

            print(f"{color}[{status_icon}] ID {task.id}: {task.description}{COLORS['ENDC']}")

        print(f"\n{COLORS['HEADER']}{COLORS['BOLD']}{'─' * 50}{COLORS['ENDC']}")

    def get_task_description(self) -> str:
        """
        Get task description from user

        Returns:
            Task description string
        """
        description = input(f"{COLORS['BOLD']}Enter task description: {COLORS['ENDC']}")
        return description

    def get_task_id(self) -> Optional[int]:
        """
        Get and validate task ID from user

        Returns:
            Task ID, or None if invalid
        """
        try:
            task_id = input(f"{COLORS['BOLD']}Enter task ID: {COLORS['ENDC']}")
            return int(task_id)
        except ValueError:
            return None

    def display_message(self, message: str, color_key: str = 'OKBLUE'):
        """
        Display a message to the user

        Args:
            message: Message text
            color_key: Color key from COLORS dict
        """
        color = COLORS.get(color_key, COLORS['ENDC'])
        print(f"\n{color}{message}{COLORS['ENDC']}")

    def display_error(self, error: str):
        """
        Display an error message

        Args:
            error: Error message text
        """
        print(f"\n{COLORS['FAIL']}{COLORS['BOLD']}ERROR: {error}{COLORS['ENDC']}")


# ============================================================================
# Application Controller
# ============================================================================

class TodoApp:
    """Main application controller"""

    def __init__(self):
        """Initialize the application"""
        self.task_manager = TaskManager()
        self.cli = CLIInterface(self.task_manager)
        self.running = True

    def run(self):
        """Main application loop"""
        print(f"\n{COLORS['OKGREEN']}{COLORS['BOLD']}Welcome to Todo List Manager!{COLORS['ENDC']}")

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
                self.handle_exit()

    def handle_add_task(self):
        """Handle add task operation"""
        description = self.cli.get_task_description()

        task = self.task_manager.add_task(description)

        if task:
            self.cli.display_message(f"Task added successfully with ID {task.id}!", 'OKGREEN')
        else:
            if not description or not description.strip():
                self.cli.display_error("Task description cannot be empty.")
            elif len(description) > MAX_DESCRIPTION_LENGTH:
                self.cli.display_error(f"Task description cannot exceed {MAX_DESCRIPTION_LENGTH} characters.")
            else:
                self.cli.display_error("Failed to add task.")

    def handle_view_tasks(self):
        """Handle view tasks operation"""
        self.cli.display_tasks()

    def handle_update_task(self):
        """Handle update task operation"""
        task_id = self.cli.get_task_id()

        if task_id is None:
            self.cli.display_error("Invalid task ID. Please enter a number.")
            return

        new_description = self.cli.get_task_description()

        success = self.task_manager.update_task(task_id, new_description)

        if success:
            self.cli.display_message(f"Task {task_id} updated successfully!", 'OKGREEN')
        else:
            task = self.task_manager.get_task(task_id)
            if not task:
                self.cli.display_error(f"Task with ID {task_id} not found.")
            elif not new_description or not new_description.strip():
                self.cli.display_error("Task description cannot be empty.")
            elif len(new_description) > MAX_DESCRIPTION_LENGTH:
                self.cli.display_error(f"Task description cannot exceed {MAX_DESCRIPTION_LENGTH} characters.")
            else:
                self.cli.display_error("Failed to update task.")

    def handle_delete_task(self):
        """Handle delete task operation"""
        task_id = self.cli.get_task_id()

        if task_id is None:
            self.cli.display_error("Invalid task ID. Please enter a number.")
            return

        success = self.task_manager.delete_task(task_id)

        if success:
            self.cli.display_message(f"Task {task_id} deleted successfully!", 'OKGREEN')
        else:
            self.cli.display_error(f"Task with ID {task_id} not found.")

    def handle_mark_complete(self):
        """Handle mark complete operation"""
        task_id = self.cli.get_task_id()

        if task_id is None:
            self.cli.display_error("Invalid task ID. Please enter a number.")
            return

        success = self.task_manager.mark_complete(task_id)

        if success:
            self.cli.display_message(f"Task {task_id} marked as complete!", 'OKGREEN')
        else:
            self.cli.display_error(f"Task with ID {task_id} not found.")

    def handle_mark_incomplete(self):
        """Handle mark incomplete operation"""
        task_id = self.cli.get_task_id()

        if task_id is None:
            self.cli.display_error("Invalid task ID. Please enter a number.")
            return

        success = self.task_manager.mark_incomplete(task_id)

        if success:
            self.cli.display_message(f"Task {task_id} marked as incomplete!", 'OKGREEN')
        else:
            self.cli.display_error(f"Task with ID {task_id} not found.")

    def handle_exit(self):
        """Handle application exit"""
        self.cli.display_message("Thank you for using Todo List Manager. Goodbye!", 'OKGREEN')
        self.running = False


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    app = TodoApp()
    app.run()
