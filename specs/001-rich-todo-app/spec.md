# Feature Specification: Advanced Phase I Rich Console Todo App

**Feature Branch**: `001-rich-todo-app`
**Created**: 2025-12-28
**Status**: Draft
**Input**: User description: "Create the specification for an \"Advanced Phase I\" In-Memory Console Todo App.

Context:
- Project: \"Evolution of Todo\" (Extended Phase I)
- Current State: Basic Console App.
- Goal: Upgrade to a visually stunning, feature-rich CLI tool using `rich`.

User Interface (UI/UX) Requirements:
1. Library: Use `rich` for all output (Tables, Panels, Colors).
2. Dashboard: Main menu must be wrapped in a `rich.panel.Panel` with a title.
3. Task Table: Replace simple list with a `rich.table.Table` containing:
   - ID (Cyan, Centered)
   - Status (Emoji: ✅/⏳/🔄)
   - Priority (Color-coded: High=Red, Medium=Yellow, Low=Blue)
   - Due Date (Format: YYYY-MM-DD HH:MM, Red if overdue)
   - Title & Tags (e.g., \"Buy Milk [Home]\")
4. Progress: Show a progress bar summary (e.g., \"4/10 Tasks Completed\").

Functional Requirements (New Features):

1. Intermediate Features (Organization):
   - Priority: Field to set High/Medium/Low during creation/update.
   - Tags: Allow adding labels like [Work], [Home] during creation.
   - Search: New Menu Option \"Search Tasks\" (filter by keyword in title/desc).
   - Filter: New Menu Option \"Filter View\" (by Status, Priority, or Tag).
   - Sort: Auto-sort the list by Priority (High first) then Due Date (Soonest first).

2. Advanced Features (Intelligence):
   - Due Dates: Input format 'YYYY-MM-DD HH:MM'. Highlight overdue tasks in Red.
   - Recurring Tasks:
     - Field: `is_recurring` (Daily/Weekly).
     - Logic: When a recurring task is marked \"Complete\", automatically create a NEW task with the next due date (do not uncheck the old one, keep history).
   - Reminders: On app startup, display a \"Critical Alert\" panel listing any overdue tasks.

Data Model Updates (In-Memory `Task` Class):
- Add fields: `priority: str`, `tags: List[str]`, `due_date: datetime`, `recurring_interval: str`.

Strict Constraints:
- NO Database (Keep using `TaskManager` dictionary/list in memory)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enhanced Task Management with Rich UI (Priority: P1)

A user wants to manage their tasks with a visually appealing console interface that provides better organization and visual cues. The user should be able to see task priorities, due dates, and status at a glance using color coding and emojis.

**Why this priority**: This is the foundational feature that transforms the basic console app into a rich experience, providing immediate visual value that users can appreciate.

**Independent Test**: Can be fully tested by launching the app and viewing the dashboard with tasks displayed in the rich table format, delivering enhanced visual organization.

**Acceptance Scenarios**:

1. **Given** a user has tasks in the system, **When** they view the main dashboard, **Then** tasks are displayed in a rich table with color-coded priorities, emojis for status, and centered IDs
2. **Given** a user launches the app, **When** they see the dashboard, **Then** it's wrapped in a rich panel with a title and shows a progress summary

---

### User Story 2 - Task Organization with Priority and Tags (Priority: P1)

A user wants to organize their tasks by setting priorities and adding tags to categorize them, making it easier to filter and focus on important items.

**Why this priority**: Priority and tagging are core organizational features that significantly improve task management efficiency.

**Independent Test**: Can be fully tested by creating tasks with different priorities and tags, then viewing them in the sorted table format.

**Acceptance Scenarios**:

1. **Given** a user is creating a new task, **When** they set priority and tags, **Then** the task is saved with these attributes and displayed correctly in the UI
2. **Given** tasks with different priorities exist, **When** the task list is displayed, **Then** tasks are sorted by priority (High first) then by due date (soonest first)

---

### User Story 3 - Task Search and Filtering (Priority: P2)

A user wants to quickly find specific tasks by searching keywords or filtering by status, priority, or tags to efficiently navigate through their task list.

**Why this priority**: As the task list grows, search and filtering become essential for maintaining productivity and focus.

**Independent Test**: Can be fully tested by creating multiple tasks with different attributes, then using search and filter functions to narrow down the results.

**Acceptance Scenarios**:

1. **Given** multiple tasks exist with different attributes, **When** a user searches by keyword, **Then** only tasks containing the keyword in title or description are shown
2. **Given** tasks with different priorities exist, **When** a user filters by priority, **Then** only tasks with that priority level are displayed

---

### User Story 4 - Due Date Management and Overdue Alerts (Priority: P2)

A user wants to set due dates for tasks and receive visual alerts for overdue items to ensure nothing gets missed.

**Why this priority**: Due date management is crucial for time-sensitive tasks and helps users maintain their schedule.

**Independent Test**: Can be fully tested by creating tasks with various due dates, including overdue ones, and verifying the visual indicators and startup alerts.

**Acceptance Scenarios**:

1. **Given** tasks with various due dates exist, **When** the dashboard is displayed, **Then** overdue tasks are highlighted in red
2. **Given** overdue tasks exist, **When** the app starts up, **Then** a critical alert panel shows all overdue tasks

---

### User Story 5 - Recurring Task Management (Priority: P3)

A user wants to create recurring tasks (daily/weekly) that automatically generate new tasks when completed, maintaining a history of completed tasks.

**Why this priority**: Recurring tasks help users manage routine activities without manual recreation, improving long-term productivity.

**Independent Test**: Can be fully tested by creating a recurring task, marking it complete, and verifying that a new instance is created with the next due date.

**Acceptance Scenarios**:

1. **Given** a recurring task exists, **When** the user marks it as complete, **Then** a new task with the same properties and next due date is automatically created
2. **Given** a completed recurring task, **When** the user views history, **Then** both the original and new recurring instances are visible

---

### Edge Cases

- What happens when a user enters an invalid date format for due dates?
- How does the system handle tasks with the same priority and due date during sorting?
- What happens when a recurring task is marked complete but the system fails to create a new instance?
- How does the system handle tasks with multiple tags during filtering?
- What happens when the task list is empty during search/filter operations?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display the main dashboard using rich panels with a title
- **FR-002**: System MUST show tasks in a rich table format with ID (cyan, centered), status (emoji), priority (color-coded), due date (red if overdue), and title with tags
- **FR-003**: System MUST show a progress bar summary indicating completed/total tasks
- **FR-004**: Users MUST be able to set task priority as High, Medium, or Low during creation/update
- **FR-005**: Users MUST be able to add tags to tasks during creation/update
- **FR-006**: System MUST sort tasks by priority (High first) then by due date (soonest first)
- **FR-007**: Users MUST be able to search tasks by keyword in title or description
- **FR-008**: Users MUST be able to filter tasks by status, priority, or tag
- **FR-009**: Users MUST be able to set due dates in 'YYYY-MM-DD HH:MM' format
- **FR-010**: System MUST highlight overdue tasks in red
- **FR-011**: Users MUST be able to create recurring tasks with Daily or Weekly intervals
- **FR-012**: System MUST automatically create a new task when a recurring task is marked complete
- **FR-013**: System MUST display overdue task alerts on app startup
- **FR-014**: System MUST maintain all task data in memory (no database)

### Key Entities

- **Task**: Represents a single task with ID, title, description, status, priority, tags, due date, and recurring interval
- **TaskManager**: In-memory storage system that manages the collection of tasks using dictionary/list structures

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view tasks in a rich, color-coded table format that is 100% more visually appealing than the basic console output
- **SC-002**: Users can create tasks with priority and tags in under 30 seconds
- **SC-003**: Users can search and filter tasks in under 10 seconds with results displayed immediately
- **SC-004**: Users can identify overdue tasks at a glance with 100% accuracy due to visual indicators
- **SC-005**: Recurring tasks generate new instances correctly 100% of the time when marked complete
- **SC-006**: App startup time remains under 5 seconds even with overdue task alerts

## Clarifications

### Session 2025-12-28

- Q: How should the system handle invalid date formats for due dates? → A: Strict validation with clear error messages
- Q: What should be the exact behavior when a recurring task is marked complete? → A: Create new instance with same properties but next scheduled date
- Q: What should be the format and behavior of the tagging system? → A: Simple text tags with bracket notation
- Q: How should tasks be ordered when they have identical priority and due date values? → A: Sort by creation order (oldest first)
- Q: Should the app always show the alert panel or only when there are overdue tasks? → A: Show alert panel only when overdue tasks exist