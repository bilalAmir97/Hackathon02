# Evolution of Todo - Advanced Phase I

A feature-rich, visually stunning in-memory Python console todo list application using the `rich` library. This project has been reorganized to isolate Phase I assets.

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

## Installation & Setup

1. **Clone the repository**:
```bash
git clone https://github.com/bilalAmir97/Hackathon02.git
cd Hackathon02
```

2. **Navigate to Phase I**:
```bash
cd "Phase I"
```

3. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

## Usage

All commands should be run from within the `Phase I/` directory.

### Run the Advanced Rich Console App
```bash
python -m src.cli.app_controller
```

### Run the Basic Console App (Original)
```bash
python todo_app/todo_app.py
```

## Project Structure (Inside Phase I/)

```
Phase I/
├── src/                          # Advanced Rich Console App
│   ├── models/
│   │   └── task.py              # Enhanced Task model
│   ├── services/
│   │   └── task_manager.py      # TaskManager with search/filter/sort
│   ├── cli/
│   │   ├── cli_interface.py     # Rich UI interface
│   │   └── app_controller.py    # Main application controller
│   └── lib/
│       └── utils.py             # Utility functions
├── todo_app/                     # Basic Console App (Original)
│   └── todo_app.py
├── tests/
│   └── test_todo_app.py
├── .gitignore
├── README.md                     # This file
└── requirements.txt
```

## Testing

```bash
python -m pytest tests/
```

## Specification Documents (Relative to repository root)

- [Feature Specification](../specs/001-rich-todo-app/spec.md)
- [Implementation Plan](../specs/001-rich-todo-app/plan.md)
- [Task List](../specs/001-rich-todo-app/tasks.md)
- [Reorganization Spec](../specs/002-reorganize-phase-1/spec.md)

## License

MIT
