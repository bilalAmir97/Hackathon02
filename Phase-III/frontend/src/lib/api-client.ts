/**
 * API Client with Better Auth Session Integration
 *
 * Centralized API client that automatically adds Better Auth session tokens to requests.
 * Handles authentication errors and token expiration using httpOnly cookies.
 */

// API base URL from environment variable
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Token refresh state management
 */
let isRefreshing = false;
let failedQueue: Array<{ resolve: (value: unknown) => void; reject: (reason: unknown) => void }> = [];

/**
 * Process the queue of failed requests
 */
const processQueue = (error?: Error | null, token?: string | null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

/**
 * Get the stored JWT token from localStorage
 */
function getStoredToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem("jwt_token");
}

/**
 * Store JWT token in localStorage
 */
function setStoredToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("jwt_token", token);
  }
}

/**
 * Remove JWT token from localStorage
 */
function removeStoredToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("jwt_token");
  }
}

/**
 * Get the current session from stored JWT token
 */
async function getSession(): Promise<{ user: { id: string; email: string }; token: string } | null> {
  if (typeof window === "undefined") {
    return null;
  }

  try {
    const token = getStoredToken();
    if (!token) {
      return null;
    }

    // Decode JWT token to get user info
    const tokenParts = token.split('.');
    if (tokenParts.length !== 3) {
      return null;
    }

    try {
      const payload = JSON.parse(atob(tokenParts[1]));
      return {
        user: {
          id: payload.user_id || payload.sub,
          email: payload.email,
        },
        token: token
      };
    } catch (decodeError) {
      console.error("Failed to decode JWT token:", decodeError);
      return null;
    }
  } catch (error) {
    console.error("Failed to get session:", error);
    return null;
  }
}

/**
 * Check if user is authenticated by verifying session
 */
export async function isAuthenticated(): Promise<boolean> {
  const session = await getSession();
  return session !== null;
}

/**
 * Get the stored user data from Better Auth session
 */
export async function getStoredUser(): Promise<{ id: string; email: string } | null> {
  const session = await getSession();
  return session?.user || null;
}

/**
 * Clear authentication data (remove JWT token)
 */
export async function clearAuth(): Promise<void> {
  if (typeof window === "undefined") {
    return;
  }

  try {
    // Clear the stored JWT token
    removeStoredToken();
  } catch (error) {
    console.error("Failed to clear auth:", error);
  }
}

/**
 * API Error class for structured error handling
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    public message: string,
    public detail?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Loading state management
 */
let loadingRequests = 0;
const setLoadingState = (isLoading: boolean) => {
  if (isLoading) {
    loadingRequests++;
  } else if (loadingRequests > 0) {
    loadingRequests--;
  }

  // Update document body to indicate loading state
  if (typeof document !== 'undefined') {
    if (loadingRequests > 0) {
      document.body.classList.add('api-loading');
    } else {
      document.body.classList.remove('api-loading');
    }
  }
};

/**
 * Generic fetch wrapper with JWT token injection and error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {},
  showLoading: boolean = true
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  // Prepare headers with proper typing
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  // Add Authorization header if we have a JWT token
  const token = getStoredToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Merge with any additional headers from options
  if (options.headers) {
    Object.entries(options.headers).forEach(([key, value]) => {
      if (typeof value === "string") {
        headers[key] = value;
      }
    });
  }

  try {
    if (showLoading) {
      setLoadingState(true);
    }

    const response = await fetch(url, {
      ...options,
      headers,
      // Don't include credentials since we're using JWT tokens
    });

    // Handle 401 Unauthorized - session expired or invalid
    if (response.status === 401) {
      // Check if we're already refreshing the token
      if (isRefreshing) {
        // Add request to queue and wait for the refresh to complete
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          // Retry the original request with the new token
          return apiFetch<T>(endpoint, options, showLoading);
        }) as Promise<T>;
      }

      // Start the refresh process
      isRefreshing = true;

      try {
        // For custom JWT tokens, we can't refresh them automatically
        // The user needs to re-login when the token expires
        await clearAuth();

        // Redirect to login if in browser
        if (typeof window !== "undefined") {
          window.location.href = "/login?error=session_expired";
        }

        processQueue(new Error("Session expired and could not be refreshed"), null);
        throw new ApiError(401, "Authentication required", "Your session has expired. Please login again.");
      } finally {
        isRefreshing = false;
      }
    }

    // Handle 204 No Content responses (common for DELETE operations)
    if (response.status === 204) {
      return undefined as T; // Return undefined for 204 responses
    }

    // Parse response body for other status codes
    const data = await response.json();

    // Handle non-2xx responses
    if (!response.ok) {
      throw new ApiError(
        response.status,
        data.error || "Request failed",
        data.detail || response.statusText
      );
    }

    return data as T;
  } catch (error) {
    // Re-throw ApiError as-is
    if (error instanceof ApiError) {
      throw error;
    }

    // Handle network errors
    if (error instanceof TypeError) {
      throw new ApiError(0, "Network error", "Unable to connect to the server. Please check your connection.");
    }

    // Handle other errors
    throw new ApiError(500, "Unexpected error", error instanceof Error ? error.message : "An unexpected error occurred");
  } finally {
    if (showLoading) {
      setLoadingState(false);
    }
  }
}

/**
 * Authentication API Response Types
 */
export interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
    status: string;
    created_at: string;
  };
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Authentication API Methods
 */
export const authApi = {
  /**
   * Register a new user account
   */
  async register(data: RegisterRequest, showLoading: boolean = true): Promise<AuthResponse> {
    setLoadingState(showLoading);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: "Registration failed" }));
        throw new ApiError(response.status, errorData.error || "Registration failed", errorData.detail);
      }

      const result = await response.json();

      // Store the JWT token in localStorage
      if (result.token) {
        setStoredToken(result.token);
      }

      return result;
    } finally {
      if (showLoading) {
        setLoadingState(false);
      }
    }
  },

  /**
   * Login with existing credentials
   */
  async login(data: LoginRequest, showLoading: boolean = true): Promise<AuthResponse> {
    setLoadingState(showLoading);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: "Login failed" }));
        throw new ApiError(response.status, errorData.error || "Login failed", errorData.detail);
      }

      const result = await response.json();

      // Store the JWT token in localStorage
      if (result.token) {
        setStoredToken(result.token);
      }

      return result;
    } finally {
      if (showLoading) {
        setLoadingState(false);
      }
    }
  },

  /**
   * Logout (call backend logout endpoint and remove JWT token)
   */
  async logout(): Promise<void> {
    try {
      // Call the backend logout endpoint to properly invalidate the session
      await fetch(`${API_BASE_URL}/api/auth/sign-out`, {
        method: "POST",
        credentials: "include", // Include httpOnly cookies if any
      });
    } catch (error) {
      console.error("Backend logout failed:", error);
      // Continue with local cleanup even if backend call fails
    } finally {
      // Always clear local auth data
      await clearAuth();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
  },
};

/**
 * Task API Response Types
 */
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: string; // pending or completed from backend
  created_at: string;
  updated_at: string;
}

// Internal representation used by frontend
export interface FrontendTask {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean; // converted from status
  created_at: string;
  updated_at: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  completed?: boolean;
}

export interface PaginatedTaskResponse {
  items: Task[];
  total: number;
  offset: number;
  limit: number;
  has_next: boolean;
  has_previous: boolean;
}

/**
 * Task API Methods with loading states
 */
export const taskApi = {
  /**
   * Convert backend task format to frontend format
   */
  convertToBackendTask(frontendTask: FrontendTask): Task {
    const { completed, ...backendTask } = frontendTask;
    return {
      ...backendTask,
      status: frontendTask.completed ? 'completed' : 'pending',
    };
  },

  /**
   * Convert backend task format to frontend format
   */
  convertToFrontendTask(backendTask: Task): FrontendTask {
    return {
      ...backendTask,
      completed: backendTask.status === 'completed',
    };
  },

  /**
   * Get all tasks for the authenticated user
   */
  async getTasks(userId: string, showLoading: boolean = true): Promise<FrontendTask[]> {
    const response = await apiFetch<PaginatedTaskResponse>(`/api/${userId}/tasks`, {}, showLoading);
    return response.items.map(this.convertToFrontendTask.bind(this));
  },

  /**
   * Get a specific task by ID
   */
  async getTask(userId: string, taskId: string, showLoading: boolean = true): Promise<FrontendTask> {
    const backendTask = await apiFetch<Task>(`/api/${userId}/tasks/${taskId}`, {}, showLoading);
    return this.convertToFrontendTask(backendTask);
  },

  /**
   * Create a new task
   */
  async createTask(userId: string, data: CreateTaskRequest, showLoading: boolean = true): Promise<FrontendTask> {
    // Send data without status field - backend will set status to 'pending' automatically
    const backendData = {
      ...data
      // Don't include status - backend sets it automatically to 'pending'
    };

    const backendTask = await apiFetch<Task>(`/api/${userId}/tasks`, {
      method: "POST",
      body: JSON.stringify(backendData),
    }, showLoading);

    return this.convertToFrontendTask(backendTask);
  },

  /**
   * Update an existing task
   */
  async updateTask(userId: string, taskId: string, data: UpdateTaskRequest, showLoading: boolean = true): Promise<FrontendTask> {
    // Convert frontend format to backend format for update
    const { completed, ...rest } = data;

    // Create backend data object with proper typing
    const backendData: Partial<Task> = { ...rest };

    // Handle the completed field conversion to status
    if (completed !== undefined) {
      backendData.status = completed ? 'completed' : 'pending';
    }

    const backendTask = await apiFetch<Task>(`/api/${userId}/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(backendData),
    }, showLoading);

    return this.convertToFrontendTask(backendTask);
  },

  /**
   * Delete a task
   */
  async deleteTask(userId: string, taskId: string, showLoading: boolean = true): Promise<void> {
    await apiFetch<void>(`/api/${userId}/tasks/${taskId}`, {
      method: "DELETE",
    }, showLoading);
    // Return nothing since DELETE returns 204 No Content
  },

  /**
   * Toggle task completion status
   */
  async toggleComplete(userId: string, taskId: string, showLoading: boolean = true): Promise<FrontendTask> {
    const backendTask = await apiFetch<Task>(`/api/${userId}/tasks/${taskId}/complete`, {
      method: "PATCH",
    }, showLoading);

    return this.convertToFrontendTask(backendTask);
  },
};

/**
 * Get current loading state
 */
export function isApiLoading(): boolean {
  return loadingRequests > 0;
}

/**
 * Check if a token refresh is in progress
 */
export function isTokenRefreshing(): boolean {
  return isRefreshing;
}
