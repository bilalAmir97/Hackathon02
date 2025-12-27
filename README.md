# Evolution of Todo - Advanced Phase I

A feature-rich, visually stunning in-memory Python console todo list application using the `rich` library.

## Features

### Basic Features
- Add new tasks with rich metadata
- View task list in a beautiful table format
- Mark tasks as complete/incomplete
- Update task descriptions and attributes
- Delete tasks

### Advanced Features
- **Priority Management**: Set High/Medium/Low priority with color-coded display
- **Tags**: Organize tasks with custom tags (e.g., [work], [home])
- **Due Dates**: Set due dates in YYYY-MM-DD HH:MM format
- **Overdue Alerts**: Visual alerts for overdue tasks on startup
- **Recurring Tasks**: Create daily/weekly recurring tasks that auto-generate new instances
- **Search**: Find tasks by keyword in title or description
- **Filter**: Filter tasks by status, priority, or tag
- **Auto-Sort**: Tasks automatically sorted by priority then due date

### Rich UI
- Color-coded priorities (Red=High, Yellow=Medium, Blue=Low)
- Emoji status indicators (✅ Complete, ⏳ Pending, 🔄 In Progress)
- Progress bar showing completion status
- Beautiful panels and tables using the `rich` library

## Requirements

- Python 3.9 or higher
- rich library (for UI)
- pytest (for testing)

## Installation

```bash
git clone https://github.com/bilalAmir97/Hackathon02-Phase-I.git
cd Hackathon02-Phase-I
pip install -r requirements.txt
```

## Usage

### Run the Advanced Rich Console App
```bash
python -m src.cli.app_controller
```

### Run the Basic Console App (Original)
```bash
python todo_app/todo_app.py
```

## Project Structure

```
hackathon-02/
├── src/                          # Advanced Rich Console App
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py              # Enhanced Task model
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_manager.py      # TaskManager with search/filter/sort
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── cli_interface.py     # Rich UI interface
│   │   └── app_controller.py    # Main application controller
│   └── lib/
│       ├── __init__.py
│       └── utils.py             # Utility functions
├── todo_app/                     # Basic Console App (Original)
│   ├── __init__.py
│   └── todo_app.py
├── tests/
│   ├── __init__.py
│   └── test_todo_app.py
├── specs/
│   ├── 001-todo/                # Basic Phase I specs
│   └── 001-rich-todo-app/       # Advanced Phase I specs
├── history/
│   └── prompts/                 # Prompt History Records
├── .gitignore
├── README.md
└── requirements.txt
```

## Menu Options

1. **Add Task** - Create a new task with priority, tags, due date, and recurring options
2. **View Task List** - Display all tasks in a rich table format
3. **Update Task** - Modify task attributes
4. **Delete Task** - Remove a task
5. **Mark Task Complete** - Complete a task (creates new instance for recurring tasks)
6. **Mark Task Incomplete** - Reopen a completed task
7. **Search Tasks** - Find tasks by keyword
8. **Filter Tasks** - Filter by status, priority, or tag
9. **Exit** - Close the application

## Testing

```bash
python -m pytest tests/
```

## Specification Documents

- [Feature Specification](./specs/001-rich-todo-app/spec.md)
- [Implementation Plan](./specs/001-rich-todo-app/plan.md)
- [Task List](./specs/001-rich-todo-app/tasks.md)

## License

MIT
