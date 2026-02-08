# Data Model: Frontend Premium UI & Full-Stack Integration

## Overview

This data model describes the frontend-specific data structures, state management patterns, and client-side representations for the premium UI application. The actual task and user data is managed on the backend, but this model defines how the frontend handles and represents this data.

## Client-Side State Models

### 1. Authentication State
```typescript
interface AuthState {
  isAuthenticated: boolean;
  user?: {
    id: string;
    email: string;
    // Additional user properties from JWT
  };
  token: string | null;
  loading: boolean;
  error: string | null;
}
```

**Validation Rules**:
- `isAuthenticated` must be boolean
- `user.id` must be non-empty string when authenticated
- `token` must be properly formatted JWT when present
- `loading` indicates ongoing auth operations
- `error` contains user-friendly error messages

### 2. Task State
```typescript
interface TaskState {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  filters: {
    status: 'all' | 'completed' | 'pending';
    searchTerm: string;
  };
  currentView: 'list' | 'grid' | 'kanban'; // Future extensibility
}
```

**Validation Rules**:
- `tasks` array contains valid Task objects
- `loading` indicates ongoing API operations
- `filters.status` must be one of allowed values
- `filters.searchTerm` must be less than 1000 characters

### 3. Task Entity (Client Representation)
```typescript
interface Task {
  id: string;
  userId: string; // Derived from JWT, not user input
  title: string;
  description: string;
  completed: boolean;
  createdAt: Date;
  updatedAt: Date;
  // Additional fields for future phases
  priority?: 'low' | 'medium' | 'high';
  dueDate?: Date;
  tags?: string[];
}
```

**Validation Rules**:
- `id` must be unique within user's tasks
- `userId` must match authenticated user (derived from JWT)
- `title` must be 1-255 characters
- `description` can be empty but limited to 1000 characters
- `completed` is boolean indicating completion status
- `createdAt` and `updatedAt` are ISO date strings

### 4. UI State Models

#### Loading State
```typescript
interface LoadingState {
  global: boolean;
  specific: {
    [key: string]: boolean; // e.g., 'login', 'fetchTasks', 'createTask'
  };
}
```

#### Error State
```typescript
interface ErrorState {
  global: string | null;
  specific: {
    [key: string]: string | null; // e.g., 'login', 'fetchTasks', 'createTask'
  };
}
```

### 5. Animation State
```typescript
interface AnimationState {
  pageTransition: 'idle' | 'entering' | 'exiting';
  scanLineEnabled: boolean; // Based on prefers-reduced-motion
  gsapTimelines: {
    [key: string]: any; // GSAP timeline instances
  };
}
```

## Form Data Models

### 1. Login Form
```typescript
interface LoginForm {
  email: string;
  password: string;
}

// Validation rules:
// - email must be valid email format
// - password must be 8+ characters
```

### 2. Registration Form
```typescript
interface RegistrationForm {
  email: string;
  password: string;
  confirmPassword: string;
}

// Validation rules:
// - email must be valid email format
// - password must be 8+ characters
// - confirmPassword must match password
```

### 3. Task Form
```typescript
interface TaskForm {
  title: string;
  description: string;
  completed: boolean;
}

// Validation rules:
// - title must be 1-255 characters
// - description can be empty but limited to 1000 characters
```

## API Response Models

### 1. Auth API Responses
```typescript
interface LoginResponse {
  token: string;
  user: {
    id: string;
    email: string;
  };
}

interface RegisterResponse {
  token: string;
  user: {
    id: string;
    email: string;
  };
}
```

### 2. Task API Responses
```typescript
interface TaskApiResponse {
  tasks: Task[];
}

interface SingleTaskApiResponse {
  task: Task;
}

interface CreateTaskResponse {
  task: Task;
}

interface UpdateTaskResponse {
  task: Task;
}
```

## Configuration Models

### 1. App Configuration
```typescript
interface AppConfig {
  apiUrl: string;
  authConfig: {
    tokenStorageMethod: 'cookie' | 'localStorage';
    tokenExpiryBuffer: number; // Minutes before expiry to refresh
  };
  animationConfig: {
    enabled: boolean;
    scanLine: {
      enabled: boolean;
      speed: number; // Pixels per second
      opacity: number; // 0.0 to 1.0
    };
    gsap: {
      defaultDuration: number; // Seconds
      ease: string; // GSAP easing function
    };
  };
  responsiveBreakpoints: {
    mobile: number;
    tablet: number;
    desktop: number;
    ultraWide: number;
  };
}
```

## State Management Patterns

### 1. Global State Structure
```
state/
├── auth/           # Authentication state
├── tasks/          # Task management state
├── ui/             # UI-specific state (loading, errors, animations)
├── forms/          # Form state management
└── config/         # App configuration
```

### 2. State Persistence Strategy
- Authentication token: httpOnly cookies (as per spec)
- User preferences: localStorage (theme, layout preferences)
- Form data: In-memory only (reset on navigation)
- Temporary UI states: In-memory only

## Validation Rules Summary

### Authentication Validation
- Email format validation using RFC 5322 standards
- Password strength requirements (8+ characters)
- JWT token format validation
- Token expiration checking

### Task Validation
- Title length: 1-255 characters
- Description length: 0-1000 characters
- User ID validation against JWT
- Completion status as boolean

### Form Validation
- Required field validation
- Format validation (emails, etc.)
- Length constraints
- Cross-field validation (password confirmation)

## State Transitions

### Authentication State Transitions
```
UNAUTHENTICATED → LOGGING_IN → AUTHENTICATED
UNAUTHENTICATED ← TOKEN_EXPIRED ← AUTHENTICATED
UNAUTHENTICATED ← LOGOUT_REQUESTED ← AUTHENTICATED
```

### Task State Transitions
```
LOADING_TASKS → TASKS_LOADED
LOADING_TASKS → TASK_LOAD_ERROR
TASK_CREATING → TASK_CREATED
TASK_CREATING → TASK_CREATE_ERROR
TASK_UPDATING → TASK_UPDATED
TASK_UPDATING → TASK_UPDATE_ERROR
```

## Error Handling Models

### 1. Error Types
```typescript
enum ErrorType {
  NETWORK_ERROR = 'NETWORK_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  AUTH_ERROR = 'AUTH_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  PERMISSION_ERROR = 'PERMISSION_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}
```

### 2. Error Response Format
```typescript
interface AppError {
  type: ErrorType;
  message: string;
  details?: any;
  code?: number;
  timestamp: Date;
}
```