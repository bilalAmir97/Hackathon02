# Data Model: Frontend Application & Full-Stack Integration

## Frontend State Models

### User Session Model
- **entity**: UserSession
- **fields**:
  - id: string (user identifier from JWT)
  - email: string (user email)
  - token: string (JWT token)
  - expiresAt: Date (token expiration)
  - isAuthenticated: boolean (authentication status)
- **relationships**: None (client-side only)
- **validation**:
  - token must be valid JWT format
  - expiresAt must be in the future
- **state transitions**: unauthenticated → authenticating → authenticated → expired

### Task ViewModel
- **entity**: TaskView
- **fields**:
  - id: string (task identifier from backend)
  - userId: string (owner identifier)
  - title: string (task title, max 255 chars)
  - description: string (optional task description)
  - completed: boolean (completion status)
  - createdAt: Date (creation timestamp)
  - updatedAt: Date (last update timestamp)
- **relationships**: Belongs to UserSession (via userId)
- **validation**:
  - title is required and non-empty
  - userId must match authenticated user
- **state transitions**: pending → completed, completed → pending

### API Response Models

#### AuthResponse
- **entity**: AuthResponse
- **fields**:
  - token: string (JWT token)
  - user: object (user details)
  - expiresIn: number (seconds until expiration)

#### TaskResponse
- **entity**: TaskResponse
- **fields**:
  - id: string (task identifier)
  - user_id: string (owner identifier)
  - title: string (task title)
  - description: string (optional task description)
  - completed: boolean (completion status)
  - created_at: string (ISO date string)
  - updated_at: string (ISO date string)

#### ErrorResponse
- **entity**: ErrorResponse
- **fields**:
  - error: string (error message)
  - code: string (error code)
  - details?: object (optional error details)

## Frontend Form Models

### LoginForm
- **entity**: LoginForm
- **fields**:
  - email: string (user email)
  - password: string (user password)
  - rememberMe: boolean (stay logged in)

### RegisterForm
- **entity**: RegisterForm
- **fields**:
  - email: string (user email)
  - password: string (user password)
  - confirmPassword: string (password confirmation)

### TaskForm
- **entity**: TaskForm
- **fields**:
  - title: string (task title)
  - description: string (optional task description)
  - completed: boolean (initial completion status)

## UI State Models

### LoadingState
- **entity**: LoadingState
- **fields**:
  - isLoading: boolean (loading indicator)
  - message: string (optional loading message)
  - progress?: number (optional progress percentage)

### ErrorState
- **entity**: ErrorState
- **fields**:
  - hasError: boolean (error indicator)
  - message: string (error message)
  - code?: string (optional error code)
  - retryAction?: Function (optional retry function)