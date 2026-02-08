# Data Model: Dashboard UI Rebuild — Modern Soft Dark SaaS

**Feature**: 001-soft-dark-theme | **Date**: 2026-01-24

## Overview

This data model describes the entities and data structures for the redesigned dashboard UI with modern soft dark SaaS theme. The model preserves all existing backend data structures while defining new UI-specific data representations for the soft dark theme elements and navigation components.

## Key Entities

### Dashboard Layout
**Description**: Container structure organizing the sidebar, top navigation, and central task workspace with responsive behavior
**Fields**:
- `sidebarCollapsed: boolean` - State of sidebar collapse/expand
- `activeView: string` - Current active view/tab in dashboard
- `breakpoint: string` - Current responsive breakpoint (mobile, tablet, desktop, ultra-wide)
- `theme: string` - Current theme state (dark, light, soft-dark)

**Validation**:
- `sidebarCollapsed` must be boolean
- `activeView` must be valid navigation option
- `breakpoint` must be one of predefined values

### Soft Dark Theme
**Description**: Visual design system encompassing colors, gradients, typography, and motion patterns for the soft dark theme
**Fields**:
- `backgroundColor: string` - Background gradient (soft deep dark → midnight blue)
- `primaryAccent: string` - Professional soft blue accent
- `secondaryAccent: string` - Subtle indigo for supporting elements
- `surfaceLayers: object` - Calm dark panel properties
- `bordersDividers: string` - Soft muted contrast properties
- `motionPattern: string` - Animation style (subtle, soft, minimal)

**Validation**:
- All color values must be valid CSS color formats
- `motionPattern` must be one of predefined values
- Contrast ratios must meet accessibility standards

### Navigation Elements
**Description**: Sidebar and top navigation components with soft dark styling and responsive behavior
**Fields**:
- `icon: string` - Navigation icon identifier
- `label: string` - Navigation label text
- `active: boolean` - Whether this is the currently selected item
- `hoverEffect: boolean` - Whether soft hover effect is active
- `collapsed: boolean` - Whether sidebar is collapsed (for mobile)
- `responsiveBehavior: object` - Behavior based on screen size

**Validation**:
- `icon` must be valid icon identifier
- `active` must be boolean
- `hoverEffect` must be boolean

### Task Management Elements
**Description**: Task cards and forms with subtle card surfaces and appropriate visual feedback
**Fields**:
- `id: string` - Unique identifier for the task
- `title: string` - Task title
- `description: string` - Task description
- `completed: boolean` - Completion status
- `createdAt: Date` - Creation timestamp
- `updatedAt: Date` - Last update timestamp
- `cardProperties: object` - Visual properties for soft dark card appearance
- `animationState: string` - Current animation state (idle, hover, complete, delete)

**Validation**:
- `id` must be unique
- `title` must be non-empty string
- `completed` must be boolean
- `animationState` must be one of predefined values

## State Transitions

### Task Card States
- `idle` → `hover`: Mouse enters card
- `hover` → `idle`: Mouse leaves card
- `idle` → `complete`: Task completion triggered
- `complete` → `idle`: Undo completion
- `idle` → `delete`: Delete animation initiated
- `delete` → `idle`: Undo deletion

### Sidebar States
- `expanded` → `collapsed`: Collapse action triggered
- `collapsed` → `expanded`: Expand action triggered
- `expanded` → `mobile`: Screen resized to mobile width
- `mobile` → `expanded`: Screen resized to desktop width

## Relationships

### Dashboard Layout → Navigation Elements
- One dashboard layout contains multiple navigation elements
- Navigation elements change based on responsive breakpoint

### Dashboard Layout → Task Management Elements
- One dashboard layout contains multiple task management elements
- Task management elements arranged in clean workspace based on screen size

### Soft Dark Theme → Navigation Elements
- One theme defines properties for multiple navigation elements
- Navigation elements inherit theme properties with overrides possible

### Task Management Elements → Navigation Elements
- Task management elements may highlight navigation elements based on category/filter
- Navigation elements may affect task card display

## API Data Flow

### From Backend
- Task objects from existing API endpoints
- User data from authentication system
- Task statistics computed from task list

### To Backend
- Task creation/update/deletion requests to existing endpoints
- Task completion toggles to existing endpoints
- User session data to authentication system

### UI Processing
- Backend data transformed for soft dark theme display
- Animation states calculated from task properties
- Responsive properties calculated from screen dimensions

## Validation Rules

### Task Card Validation
- Task titles must be between 1-200 characters
- Descriptions must be between 0-1000 characters
- Task IDs must be unique within user's task list
- Completed tasks must maintain visual indicator with subtle styling

### Soft Dark Theme Validation
- Contrast values must meet WCAG 2.1 AA accessibility standards
- Color combinations must follow professional aesthetic guidelines
- Gradient combinations must maintain readability

### Responsive Validation
- Mobile view must convert sidebar to hamburger menu
- Tablet view must optimize for medium screen width
- Ultra-wide view must utilize available space effectively
- All views must maintain soft dark theme consistently