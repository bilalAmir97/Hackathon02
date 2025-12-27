# Evolution of Todo - Phase I

A simple in-memory Python console todo list application.

## Features

- Add new tasks
- View task list
- Mark tasks as complete/incomplete
- Update task descriptions
- Delete tasks

## Requirements

- Python 3.8 or higher
- No external dependencies (standard library only)

## Installation

```bash
git clone <repository-url>
cd hackathon-02
```

## Usage

```bash
python todo_app/todo_app.py
```

## Project Structure

```
hackathon-02/
├── todo_app/
│   ├── __init__.py
│   └── todo_app.py          # Main application
├── tests/
│   ├── __init__.py
│   └── test_todo_app.py     # Unit tests
├── specs/
│   └── 001-todo/
│       ├── spec.md          # Feature specification
│       ├── plan.md          # Implementation plan
│       └── tasks.md         # Implementation tasks
├── .gitignore
├── README.md
└── requirements.txt
```

## Testing

```bash
python -m pytest tests/
```

## License

MIT
