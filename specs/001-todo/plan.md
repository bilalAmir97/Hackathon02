# Implementation Plan: Evolution of Todo - Phase I

**Feature Branch**: `001-todo`
**Created**: 2025-12-27
**Status**: Draft
**Input**: User description: "Create the Phase I technical plan for the Todo in-memory Python console application. The plan must be derived strictly from the Phase I specification and global constitution. Include: 1. High-level application structure (single Python program) 2. In-memory data structures to store tasks 3. Task identification strategy (ID generation) 4. CLI control flow (menu loop, user input handling) 5. Separation of responsibilities (data handling vs CLI) 6. Error handling strategy for invalid input and missing tasks. Constraints: - No databases - No file storage - No web frameworks - No external services - No future phase concepts. The plan must not introduce new features. It must only describe HOW the approved Phase I requirements will be implemented."

## Architecture Overview

The application will be a single Python file implementing an in-memory console-based todo list manager with the following architectural components:

### Core Components

1. **Task Data Model** - Defines the structure and attributes of a task
2. **Task Manager** - Handles all data operations (add, update, delete, mark complete)
3. **CLI Interface** - Handles user input/output and menu navigation
4. **Application Controller** - Main loop that orchestrates the application flow

### Technology Stack

- Python 3.8+ (primary application in single main file)
- Standard library only (no external dependencies)
- ANSI color codes for visual enhancement (as per clarifications)

## Project Structure

### File Organization

```
specs/
├── 001-todo/
│   ├── spec.md          # Feature specification
│   ├── plan.md          # Implementation plan (this file)
│   └── tasks.md         # Implementation tasks
history/
├── prompts/
│   └── 001-todo/        # Prompt history records for this feature
todo_app/
├── todo_app.py          # Main application file
├── __init__.py          # Package initialization (if converted to package later)
└── README.md            # Application documentation
tests/
├── __init__.py
└── test_todo_app.py     # Unit tests for the application
.gitignore
README.md
requirements.txt         # Empty file or minimal dependencies
```

### Main Application File Structure

The main application file `todo_app.py` will be organized as follows:

```
1.  Imports (standard library only)
2.  Constants definitions
3.  ANSI color codes and formatting constants
4.  Task class definition
5.  TaskManager class definition
6.  CLIInterface class definition
7.  TodoApp class definition
8.  Main execution block (if __name__ == "__main__")
```

### Constants Module Structure

If needed, a constants module will contain:

```
# Configuration constants
MAX_DESCRIPTION_LENGTH = 500
MENU_OPTIONS = {
    1: "Add Task",
    2: "View Task List",
    3: "Update Task",
    4: "Delete Task",
    5: "Mark Task Complete",
    6: "Mark Task Incomplete",
    7: "Exit"
}

# ANSI Color codes
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
```

### Test Structure

Unit tests will follow the naming convention and organization:

```
tests/
└── test_todo_app.py
    ├── TestTask - Tests for Task class
    ├── TestTaskManager - Tests for TaskManager class
    ├── TestCLIInterface - Tests for CLIInterface class
    └── TestTodoApp - Tests for TodoApp class
```

## Component Design

### Task Data Model

```python
class Task:
    def __init__(self, task_id: int, description: str, completed: bool = False):
        self.id = task_id
        self.description = description
        self.completed = completed
```

- ID: Integer, zero-based sequential assignment as per clarifications
- Description: String, maximum 500 characters as per clarifications
- Completed: Boolean, tracks completion status

### Task Manager

The Task Manager will be implemented as a class that handles all data operations:

```python
class TaskManager:
    def __init__(self):
        self.tasks = {}  # Dictionary mapping ID to Task objects
        self.next_id = 0  # For sequential ID assignment

    def add_task(self, description: str) -> Task:
        # Creates a new task with next available ID
        # Validates description length (max 500 chars)
        # Returns the created Task

    def get_task(self, task_id: int) -> Task:
        # Retrieves a task by ID, returns None if not found

    def get_all_tasks(self) -> List[Task]:
        # Returns all tasks sorted by ID

    def update_task(self, task_id: int, new_description: str) -> bool:
        # Updates task description, validates ID exists and description length
        # Returns True on success, False otherwise

    def mark_complete(self, task_id: int) -> bool:
        # Marks task as complete, validates ID exists
        # Returns True on success, False otherwise

    def mark_incomplete(self, task_id: int) -> bool:
        # Marks task as incomplete, validates ID exists
        # Returns True on success, False otherwise

    def delete_task(self, task_id: int) -> bool:
        # Deletes task by ID, maintains ID gaps as per clarifications
        # Returns True on success, False otherwise
```

### CLI Interface

The CLI Interface will handle all user interactions:

```python
class CLIInterface:
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

    def display_menu(self):
        # Displays the main menu with numbered options
        # Uses ANSI colors and simple borders as per clarifications

    def get_user_choice(self) -> int:
        # Gets and validates user menu choice

    def display_tasks(self):
        # Displays all tasks with ID, description, and completion status
        # Uses visual indicators for different states

    def get_task_description(self) -> str:
        # Gets task description from user input

    def get_task_id(self) -> int:
        # Gets and validates task ID from user input

    def display_message(self, message: str):
        # Displays a message to the user
        # Uses ANSI colors for different message types (info, error, success)

    def display_error(self, error: str):
        # Displays an error message in a visually distinct way
```

### Application Controller

The main application controller manages the flow:

```python
class TodoApp:
    def __init__(self):
        self.task_manager = TaskManager()
        self.cli = CLIInterface(self.task_manager)
        self.running = True

    def run(self):
        # Main application loop
        # Displays menu, processes user choice, returns to menu
        # Continues until user chooses to exit

    def handle_add_task(self):
        # Handles the add task flow

    def handle_view_tasks(self):
        # Handles the view tasks flow

    def handle_update_task(self):
        # Handles the update task flow

    def handle_delete_task(self):
        # Handles the delete task flow

    def handle_mark_complete(self):
        # Handles the mark complete flow

    def handle_mark_incomplete(self):
        # Handles the mark incomplete flow

    def handle_exit(self):
        # Handles application exit
```

## Data Flow & State Management

### In-Memory Data Structure

- Tasks will be stored in a dictionary (`tasks: Dict[int, Task]`) for O(1) lookup by ID
- The `next_id` counter will track the next available ID for new tasks
- When a task is deleted, the ID will remain unused (creating gaps) to maintain consistency as per clarifications

### ID Generation Strategy

- Start with ID 0 for the first task
- Increment `next_id` after each successful task creation
- When deleting tasks, do not reuse the deleted ID (as per clarifications)
- This maintains consistent IDs for remaining tasks

## Error Handling Strategy

### Input Validation

- Validate task IDs exist before operations
- Validate task descriptions are not empty and within 500 character limit
- Handle invalid menu choices gracefully
- Provide clear error messages for all failure cases

### Error Response Patterns

- All data operations return boolean success/failure indicators
- CLI interface displays appropriate error messages for user-facing issues
- Invalid operations show clear, actionable error messages within 1 second as per success criteria

### Edge Cases Handled

- Empty task list detection and appropriate messaging
- Invalid task ID handling with clear error messages
- Empty or whitespace-only task descriptions
- Maximum description length enforcement (500 characters)

## CLI Control Flow

### Main Menu Loop

```
1. Add Task
2. View Task List
3. Update Task
4. Delete Task
5. Mark Task Complete
6. Mark Task Incomplete
7. Exit
```

### Menu Flow

1. Display menu options with numbered choices
2. Get user input and validate choice
3. Execute selected operation
4. Display results or error messages
5. Return to main menu (as per clarifications)
6. Continue until user selects Exit

### User Input Handling

- Validate numeric input for menu choices
- Validate numeric input for task IDs
- Validate string input for task descriptions
- Handle invalid input gracefully with appropriate error messages

## Separation of Responsibilities

### Data Layer (TaskManager)
- Responsible for all data operations
- Validates data integrity
- Maintains the in-memory task store
- Does not handle user interface concerns

### Presentation Layer (CLIInterface)
- Responsible for user interaction
- Formats output for display
- Validates user input format
- Does not directly access task storage

### Control Layer (TodoApp)
- Orchestrates application flow
- Coordinates between data and presentation layers
- Handles application state (running/not running)

## Implementation Sequence

### Phase 1: Core Data Model
1. Implement Task class
2. Implement TaskManager with basic CRUD operations
3. Add validation logic

### Phase 2: CLI Interface
1. Implement CLIInterface with basic display methods
2. Add user input handling
3. Implement error message display

### Phase 3: Application Flow
1. Implement TodoApp controller
2. Add main menu loop
3. Connect all components

### Phase 4: Enhancement & Testing
1. Add ANSI color formatting
2. Add visual borders and formatting
3. Test all error cases
4. Verify all acceptance scenarios

## Quality Attributes

### Performance
- O(1) task lookup by ID
- Menu response time under 2 seconds as per success criteria
- Task list display within 1 second as per success criteria

### Reliability
- No crashes during valid or invalid operations
- Proper error handling for all edge cases
- Graceful handling of invalid input

### Usability
- Clear menu options with numbered choices as per clarifications
- Intuitive operation flow
- Clear error messages for invalid operations

## Constraints Compliance

- ✅ Single main application file (todo_app.py) with potential for modular expansion
- ✅ In-memory storage only (no persistence)
- ✅ No external dependencies beyond standard library
- ✅ No databases or file storage
- ✅ No web frameworks or external services
- ✅ Implements only specified features (no additions)
- ✅ Follows clarifications from spec (ID handling, CLI format, etc.)