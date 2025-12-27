# Quickstart Guide: Advanced Phase I Rich Console Todo App

**Created**: 2025-12-28
**Feature**: Advanced Phase I Rich Console Todo App
**Branch**: 001-rich-todo-app

## Overview

This guide provides quick instructions to set up and run the rich console todo application with enhanced UI and intelligent features.

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Terminal/command prompt access

## Setup

### 1. Clone or Navigate to Project Directory

```bash
cd /path/to/hackathon-02
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install rich
```

Or if using a requirements.txt file:

```bash
pip install -r requirements.txt
```

## Running the Application

### 1. Navigate to Source Directory

```bash
cd src
```

### 2. Run the Application

```bash
python cli/cli_interface.py
```

## Basic Usage

### Main Menu Options

When the application starts, you'll see a rich-formatted dashboard with the following options:

1. **Add Task** - Create a new task with title, description, priority, tags, due date, and recurring settings
2. **View Tasks** - Display all tasks in a rich table format with color-coded priorities and status emojis
3. **Update Task** - Modify an existing task's details
4. **Mark Complete/Incomplete** - Change a task's completion status
5. **Search Tasks** - Filter tasks by keyword in title or description
6. **Filter View** - Filter tasks by status, priority, or tag
7. **Show Overdue Tasks** - Display only overdue tasks in a critical alert panel
8. **Exit** - Quit the application

### Adding a Task

1. Select "Add Task" from the menu
2. Enter the task title
3. Optionally add a description
4. Select priority (High/Medium/Low)
5. Add tags separated by commas (e.g., "Work,Personal")
6. Optionally set a due date in 'YYYY-MM-DD HH:MM' format
7. Select recurring interval (None/Daily/Weekly)

### Viewing Tasks

The task list is displayed as a rich table with:
- Cyan, centered ID column
- Status emojis (✅ completed, ⏳ pending, 🔄 in-progress)
- Color-coded priority (Red=High, Yellow=Medium, Blue=Low)
- Due date in red if overdue
- Title and tags displayed as "Title [tag1] [tag2]"

## Key Features

### Rich UI Elements
- Dashboard wrapped in a rich panel
- Color-coded task table with emojis
- Progress bar showing completion percentage
- Overdue alerts in critical panels

### Organizational Features
- Priority levels (High/Medium/Low)
- Tagging system for categorization
- Multi-criteria sorting (Priority → Due Date → Creation Order)

### Intelligent Features
- Due date tracking with overdue highlighting
- Recurring tasks that create new instances when completed
- Startup alerts for overdue tasks
- Search and filtering capabilities

## Common Commands

### Date Format
- Use 'YYYY-MM-DD HH:MM' format (e.g., '2025-12-31 15:30')

### Tag Format
- Use alphanumeric characters, spaces will be converted to hyphens
- Multiple tags separated by commas

## Troubleshooting

### Rich Library Not Working
- Ensure you're running in a terminal that supports ANSI colors
- Try running in a different terminal application if formatting doesn't appear

### Date Format Errors
- Verify date input follows 'YYYY-MM-DD HH:MM' format exactly
- Check that the date/time is valid (e.g., no Feb 30, valid hours/minutes)

### Application Not Starting
- Verify all dependencies are installed: `pip install rich`
- Check that you're running from the correct directory

## Development

### File Structure
- `src/models/task.py` - Task model with enhanced attributes
- `src/services/task_manager.py` - Task management logic
- `src/cli/cli_interface.py` - Rich UI interface
- `src/lib/utils.py` - Helper functions for validation and parsing

### Testing
Run tests with pytest:
```bash
pytest tests/
```