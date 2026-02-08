# Data Model: Dashboard UI Rebuild — Premium Futuristic Redesign

**Feature**: 008-dashboard-ui-redesign | **Date**: 2026-01-24

## Overview

This data model describes the entities and data structures for the redesigned dashboard UI. The model preserves all existing backend data structures while defining new UI-specific data representations for the premium futuristic design elements.

## Key Entities

### Dashboard Layout
**Description**: Container structure organizing the sidebar, top navigation, and central task workspace with responsive behavior
**Fields**:
- `sidebarCollapsed: boolean` - State of sidebar collapse/expand
- `activeView: string` - Current active view/tab in dashboard
- `breakpoint: string` - Current responsive breakpoint (mobile, tablet, desktop, ultra-wide)
- `theme: string` - Current theme state (dark, light, futuristic)

**Validation**:
- `sidebarCollapsed` must be boolean
- `activeView` must be valid navigation option
- `breakpoint` must be one of predefined values

### Glassmorphic Components
**Description**: UI state and properties for glassmorphism effects
**Fields**:
- `blurIntensity: number` - Backdrop blur value (0-20px)
- `opacity: number` - Surface opacity (0.1-0.8)
- `gradientStart: string` - Starting color of gradient overlay
- `gradientEnd: string` - Ending color of gradient overlay
- `borderOpacity: number` - Border transparency (0.1-0.3)

**Validation**:
- `blurIntensity` must be between 0-20
- `opacity` must be between 0.1-0.8
- `borderOpacity` must be between 0.1-0.3

### Futuristic Theme
**Description**: Visual design system encompassing colors, gradients, typography, and motion patterns
**Fields**:
- `backgroundColor: string` - Background gradient (deep space black → midnight blue)
- `primaryAccent: string` - Electric blue → indigo gradient
- `secondaryAccent: string` - Soft neon cyan for glow/highlights
- `glassSurface: object` - Glassmorphism properties
- `motionPattern: string` - Animation style (smooth, premium, subtle)

**Validation**:
- All color values must be valid CSS color formats
- `motionPattern` must be one of predefined values

### Task Cards
**Description**: Interactive elements representing individual tasks with floating glass appearance and action capabilities
**Fields**:
- `id: string` - Unique identifier for the task
- `title: string` - Task title
- `description: string` - Task description
- `completed: boolean` - Completion status
- `createdAt: Date` - Creation timestamp
- `updatedAt: Date` - Last update timestamp
- `glassProperties: GlassmorphicComponents` - Visual properties for glass effect
- `animationState: string` - Current animation state (idle, hover, complete, delete)

**Validation**:
- `id` must be unique
- `title` must be non-empty string
- `completed` must be boolean
- `animationState` must be one of predefined values

### Navigation Elements
**Description**: Sidebar and top navigation components with glowing effects and responsive behavior
**Fields**:
- `icon: string` - Navigation icon identifier
- `label: string` - Navigation label text
- `active: boolean` - Whether this is the currently selected item
- `glowEffect: boolean` - Whether glow effect is active
- `collapsed: boolean` - Whether sidebar is collapsed (for mobile)
- `responsiveBehavior: object` - Behavior based on screen size

**Validation**:
- `icon` must be valid icon identifier
- `active` must be boolean
- `glowEffect` must be boolean

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

### Dashboard Layout → Task Cards
- One dashboard layout contains multiple task cards
- Task cards arranged in grid/column layout based on screen size

### Futuristic Theme → Glassmorphic Components
- One theme defines properties for multiple glassmorphic components
- Glassmorphic components inherit theme properties with overrides possible

### Task Cards → Navigation Elements
- Task cards may highlight navigation elements based on category/filter
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
- Backend data transformed for glassmorphic display
- Animation states calculated from task properties
- Responsive properties calculated from screen dimensions

## Validation Rules

### Task Card Validation
- Task titles must be between 1-200 characters
- Descriptions must be between 0-1000 characters
- Task IDs must be unique within user's task list
- Completed tasks must maintain strikethrough visual indicator

### Glassmorphism Validation
- Blur values must be within performance guidelines
- Opacity values must maintain sufficient contrast
- Gradient combinations must follow accessibility standards

### Responsive Validation
- Mobile view must convert sidebar to hamburger menu
- Tablet view must optimize for medium screen width
- Ultra-wide view must utilize available space effectively
- All views must maintain glassmorphism effects appropriately