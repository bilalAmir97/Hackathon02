# Tasks: Dashboard UI Rebuild (Modern Soft Dark SaaS)

**Feature**: 001-soft-dark-theme | **Date**: 2026-01-24 | **Spec**: [specs/001-soft-dark-theme/spec.md](./spec.md)

## Overview

This document contains executable tasks for the Dashboard UI Rebuild with Modern Soft Dark SaaS theme. Tasks are organized by user story priority (P1, P2, P3) to enable independent implementation and testing. Each task includes acceptance criteria, file paths, and dependencies for systematic development.

## Phase 1: Setup & Foundation

### Task 1.1: Initialize Soft Dark Theme Design System
- [X] Create global CSS variables for soft dark theme colors (FR-001, FR-002, FR-003)
- [X] Define soft dark design tokens (background, primary accent, secondary accent)
- [X] Set up Tailwind configuration for soft dark theme
- [X] Create theme provider component for context management

**Files**:
- `Phase-II/frontend/src/styles/globals.css`
- `Phase-II/frontend/src/components/theme/ThemeProvider.tsx`
- `Phase-II/frontend/tailwind.config.ts`

**Acceptance**:
- Soft deep dark background (not pure black) implemented
- Professional soft blue primary accent defined
- Subtle indigo secondary accent defined
- Theme context available throughout app

### Task 1.2: Create Reusable Soft Dark UI Components
- [X] Create SoftDarkCard component with subtle surface layers (FR-004)
- [X] Create SoftDarkButton with soft dark styling
- [X] Create SoftDarkInput with appropriate styling
- [X] Create SoftDarkModal with soft dark theme

**Files**:
- `Phase-II/frontend/src/components/ui/SoftDarkCard.tsx`
- `Phase-II/frontend/src/components/ui/SoftDarkButton.tsx`
- `Phase-II/frontend/src/components/ui/SoftDarkInput.tsx`
- `Phase-II/frontend/src/components/ui/SoftDarkModal.tsx`

**Acceptance**:
- Card surfaces use calm dark panels with appropriate contrast
- All components follow soft dark theme design
- Components are reusable across the application

## Phase 2: Foundational Blocking Tasks

### Task 2.1: Update Dashboard Layout Structure
- [X] Replace existing dashboard layout with new structure (FR-007, FR-009)
- [X] Implement left sidebar navigation container
- [X] Implement top navigation bar container
- [X] Create central content workspace area
- [X] Set up responsive grid layout

**Files**:
- `Phase-II/frontend/src/app/dashboard/layout.tsx`

**Acceptance**:
- Layout follows professional SaaS standards
- Left sidebar, top bar, and central workspace are present
- Responsive layout works across device sizes

### Task 2.2: Create Sidebar Navigation Component
- [X] Implement SoftDarkSidebar component with collapsible behavior (FR-007, FR-008)
- [X] Add icon + label navigation items
- [X] Create clear active indicator for current page
- [X] Implement fixed by default, collapsible on demand behavior
- [X] Add mobile hamburger menu conversion

**Files**:
- `Phase-II/frontend/src/components/navigation/Sidebar.tsx`
- `Phase-II/frontend/src/components/navigation/SidebarItem.tsx`

**Acceptance**:
- Sidebar uses soft dark panel styling
- Navigation items have icon + label
- Active indicator is clear and visible
- Sidebar is fixed by default, collapsible on demand
- Converts to hamburger menu on mobile

### Task 2.3: Create Top Navigation Bar Component
- [X] Implement TopNavigation component with search input (FR-009)
- [X] Add user profile menu dropdown
- [X] Include theme toggle switch (included by default)
- [X] Add logout action button
- [X] Ensure responsive behavior

**Files**:
- `Phase-II/frontend/src/components/navigation/TopNavigation.tsx`
- `Phase-II/frontend/src/components/navigation/UserProfileMenu.tsx`
- `Phase-II/frontend/src/components/navigation/SearchBar.tsx`
- `Phase-II/frontend/src/components/navigation/ThemeToggle.tsx`

**Acceptance**:
- Top bar includes search input functionality
- User profile menu is accessible
- Theme toggle is included and functional
- Logout action is available
- Responsive behavior works correctly

### Task 2.4: Implement API Client with Backend Integration
- [X] Create/update API client to connect with existing backend endpoints (FR-015)
- [X] Verify all task management API endpoints are accessible from new UI (GET, POST, PUT, DELETE, PATCH)
- [X] Test authentication flow integration with Better Auth
- [X] Validate user session management and JWT token handling
- [X] Confirm user data isolation (each user only sees their own tasks)

**Files**:
- `Phase-II/frontend/src/lib/api-client.ts`
- `Phase-II/frontend/src/hooks/useAuth.ts`
- `Phase-II/frontend/src/services/task-api.ts`

**Acceptance**:
- All existing backend API integrations functional with new UI
- Authentication flow works seamlessly with new theme
- User data isolation maintained
- API error handling implemented properly

## Phase 3: User Story 1 - Navigate Dashboard with Professional Soft Dark Theme (P1)

### Task 3.1: Implement Dashboard Page Structure
- [X] Replace existing dashboard page with new soft dark theme (FR-001)
- [X] Apply soft deep dark background gradient
- [X] Implement professional soft blue accent colors
- [X] Add subtle indigo secondary accents
- [X] Ensure proper spacing and typography hierarchy (FR-006)

**Files**:
- `Phase-II/frontend/src/app/dashboard/page.tsx`

**Acceptance**:
- Dashboard displays with soft dark theme
- Colors follow the specified palette
- Typography has strong visual hierarchy
- Layout is clean and professional

### Task 3.2: Add Micro-interactions with GSAP Animations
- [X] Implement subtle fade + slide transitions (FR-012)
- [X] Add soft hover feedback for interactive elements
- [X] Ensure no aggressive motion in animations
- [X] Respect reduced motion preferences
- [X] Test 60fps performance on mid/high-end devices

**Files**:
- `Phase-II/frontend/src/hooks/useAnimation.ts`
- `Phase-II/frontend/src/components/dashboard/DashboardEntrance.tsx`

**Acceptance**:
- Subtle fade + slide transitions implemented
- Hover effects are soft and unobtrusive
- No aggressive motion in animations
- Reduced motion preferences respected
- Performance targets met

### Task 3.3: Implement Responsive Dashboard Layout
- [X] Ensure pixel-perfect layout across mobile, tablet, desktop (FR-016)
- [X] Implement standard breakpoints (320px, 768px, 1024px, 1200px)
- [X] Test sidebar responsive behavior
- [X] Verify top bar responsive behavior
- [X] Confirm zero layout shift during transitions

**Files**:
- `Phase-II/frontend/src/components/dashboard/ResponsiveDashboard.tsx`
- `Phase-II/frontend/src/hooks/useBreakpoint.ts`

**Acceptance**:
- Layout works perfectly across all device sizes
- Standard breakpoints implemented correctly
- Sidebar and top bar respond appropriately
- Zero layout shift occurs during transitions

## Phase 4: User Story 2 - Manage Tasks in Professional Workspace (P1)

### Task 4.1: Create Task Card Component with Soft Dark Styling
- [X] Implement TaskCard component with subtle card surfaces (FR-010)
- [X] Apply soft dark theme styling to task cards
- [X] Add clear visual indicators for task status
- [X] Implement subtle fade transitions for task completion
- [X] Ensure high readability and spacing clarity (FR-014)

**Files**:
- `Phase-II/frontend/src/components/tasks/TaskCard.tsx`

**Acceptance**:
- Task cards use subtle card surfaces
- Soft dark theme applied consistently
- Visual indicators for task status are clear
- Fade transitions for completion work smoothly
- Readability and spacing meet requirements

### Task 4.2: Update Task Form with Soft Dark Styling
- [X] Update TaskForm component with soft dark theme (FR-011)
- [X] Apply appropriate styling matching the soft dark theme
- [X] Implement create, edit, delete, complete actions
- [X] Add appropriate visual feedback for actions
- [X] Ensure form elements follow soft dark design

**Files**:
- `Phase-II/frontend/src/components/tasks/TaskForm.tsx`

**Acceptance**:
- Task form matches soft dark theme design
- All actions (create, edit, delete, complete) work
- Visual feedback is appropriate
- Form elements follow soft dark styling

### Task 4.3: Implement Task Management Workspace
- [X] Create clean task list layout in main workspace (FR-010)
- [X] Implement clear task grouping functionality
- [X] Add create, edit, delete, complete actions
- [X] Ensure appropriate visual feedback for all actions
- [X] Implement task filtering and organization

**Files**:
- `Phase-II/frontend/src/components/tasks/TaskWorkspace.tsx`
- `Phase-II/frontend/src/components/tasks/TaskList.tsx`

**Acceptance**:
- Task list layout is clean and organized
- Task grouping is clear and logical
- All task actions work with proper feedback
- Workspace follows soft dark theme

## Phase 5: User Story 3 - Navigate with Responsive Sidebar and Top Bar (P2)

### Task 5.1: Enhance Sidebar with Collapsible Behavior
- [X] Implement smooth collapse/expand animation for sidebar (FR-008)
- [X] Maintain soft dark panel appearance during transitions
- [X] Add desktop collapse/expand functionality
- [X] Implement mobile hamburger menu conversion
- [X] Test responsive behavior across devices

**Files**:
- `Phase-II/frontend/src/components/navigation/Sidebar.tsx`
- `Phase-II/frontend/src/hooks/useSidebarToggle.ts`

**Acceptance**:
- Sidebar has smooth collapse/expand animation
- Soft dark panel appearance maintained during transitions
- Desktop functionality works properly
- Mobile hamburger conversion works
- Responsive behavior verified

### Task 5.2: Implement Search Functionality in Top Bar
- [X] Add search input with soft dark styling to top navigation (FR-009)
- [X] Implement search functionality with visual feedback
- [X] Ensure search results appear with appropriate styling
- [X] Test search across different device sizes
- [X] Verify accessibility of search component

**Files**:
- `Phase-II/frontend/src/components/navigation/SearchBar.tsx`
- `Phase-II/frontend/src/hooks/useSearch.ts`

**Acceptance**:
- Search input has soft dark styling
- Search functionality works with visual feedback
- Results appear with appropriate styling
- Search works across all device sizes
- Search component is accessible

## Phase 6: Polish & Cross-Cutting Concerns

### Task 6.1: Implement Accessibility Features (WCAG 2.1 AA)
- [X] Ensure proper contrast ratios for soft dark theme (FR-014)
- [X] Add keyboard navigation support for all interactive elements
- [X] Implement proper ARIA labels and roles
- [X] Add semantic HTML structure
- [X] Test with screen readers

**Files**:
- `Phase-II/frontend/src/components/accessibility/A11yConfig.ts`
- Updates to all UI components for accessibility

**Acceptance**:
- Contrast ratios meet WCAG 2.1 AA standards
- All interactive elements are keyboard accessible
- Proper ARIA labels and roles implemented
- Semantic HTML structure used
- Screen reader compatibility verified

### Task 6.2: Performance Optimization
- [X] Optimize animations for 60fps on mid/high-end devices (FR-017)
- [X] Ensure 30fps is acceptable on lower-end devices
- [X] Optimize soft dark theme effects for performance
- [X] Implement lazy loading for components where appropriate
- [X] Test performance across different device tiers

**Files**:
- `Phase-II/frontend/src/utils/performance.ts`
- Optimization in all animation and component files

**Acceptance**:
- 60fps achieved on mid/high-end devices
- 30fps acceptable on lower-end devices
- Soft dark theme effects optimized
- Performance verified across device tiers

### Task 6.3: Final Integration and Testing
- [X] Verify all existing backend API integrations remain functional (FR-015)
- [X] Test task management functionality with new UI
- [X] Verify authentication flow remains intact
- [X] Test responsive behavior across all devices
- [X] Conduct final accessibility audit

**Files**:
- Integration testing across all components

**Acceptance**:
- All backend API integrations functional
- Task management works with new UI
- Authentication flow intact
- Responsive behavior verified
- Accessibility audit passed

### Task 6.4: Handle Edge Cases and Performance Under Load
- [X] Implement virtual scrolling or pagination for handling hundreds of tasks (addresses edge case)
- [X] Test performance with 500+ tasks loaded in the interface
- [X] Verify low-contrast accessibility compliance while maintaining dark theme aesthetic (addresses edge case)
- [X] Implement and test reduced motion preferences support (addresses edge case)
- [X] Validate UI behavior with maximum possible task count
- [X] Test memory usage and performance under high-load conditions

**Files**:
- `Phase-II/frontend/src/components/tasks/VirtualTaskList.tsx`
- `Phase-II/frontend/src/hooks/useReducedMotion.ts`
- `Phase-II/frontend/src/utils/performance.ts`

**Acceptance**:
- Interface performs well with 500+ tasks
- Low-contrast accessibility maintained while preserving dark theme
- Reduced motion preferences properly respected
- Memory usage remains reasonable under load
- Performance degrades gracefully with large task counts

## Dependencies

- Task 1.1 must be completed before Tasks 1.2, 2.1, 3.1, 4.1, 5.1, 6.1
- Task 2.1 must be completed before Tasks 3.1, 4.1, 5.1
- Task 2.2 must be completed before Task 3.1
- Task 2.3 must be completed before Task 3.1
- Task 4.1 must be completed before Task 4.3
- Task 2.4 must be completed before Task 6.3

## Parallel Execution Possibilities

- Tasks 1.2 (UI components) can be developed in parallel with Tasks 2.2-2.3 (navigation components)
- Tasks 3.2-3.3 (animations and responsiveness) can be developed in parallel with Tasks 4.1-4.3 (task management)
- Tasks 6.1-6.2 (polish) can be worked on in parallel after core functionality is complete