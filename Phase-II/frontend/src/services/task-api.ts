/**
 * Task API Service
 * Implements the API contracts defined in specs/001-soft-dark-theme/contracts/dashboard-api-contracts.yaml
 * Provides all task management operations with proper error handling and data transformation
 */

import { taskApi, FrontendTask, CreateTaskRequest, UpdateTaskRequest } from '@/lib/api-client';

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskFilterOptions {
  status?: 'all' | 'pending' | 'completed';
}

export interface TaskService {
  /**
   * List all tasks for a user with optional filtering
   */
  listTasks: (userId: string, filters?: TaskFilterOptions) => Promise<Task[]>;

  /**
   * Create a new task
   */
  createTask: (userId: string, taskData: Omit<Task, 'id' | 'user_id' | 'created_at' | 'updated_at' | 'completed'>) => Promise<Task>;

  /**
   * Get task details by ID
   */
  getTask: (userId: string, taskId: string) => Promise<Task>;

  /**
   * Update an existing task
   */
  updateTask: (userId: string, taskId: string, taskData: Partial<Omit<Task, 'id' | 'user_id' | 'created_at' | 'updated_at'>>) => Promise<Task>;

  /**
   * Delete a task
   */
  deleteTask: (userId: string, taskId: string) => Promise<void>;

  /**
   * Toggle task completion status
   */
  toggleComplete: (userId: string, taskId: string) => Promise<Task>;
}

/**
 * Implementation of the TaskService interface using the existing api-client
 */
export const taskService: TaskService = {
  /**
   * List all tasks for a user with optional filtering
   */
  async listTasks(userId: string, filters?: TaskFilterOptions): Promise<Task[]> {
    try {
      const tasks = await taskApi.getTasks(userId);

      // Apply client-side filtering if needed
      if (filters?.status && filters.status !== 'all') {
        return tasks.filter(task => {
          if (filters.status === 'completed') {
            return task.completed;
          } else if (filters.status === 'pending') {
            return !task.completed;
          }
          return true;
        });
      }

      return tasks;
    } catch (error) {
      console.error('Error listing tasks:', error);
      throw error;
    }
  },

  /**
   * Create a new task
   */
  async createTask(userId: string, taskData: Omit<Task, 'id' | 'user_id' | 'created_at' | 'updated_at' | 'completed'>): Promise<Task> {
    try {
      const requestData: CreateTaskRequest = {
        title: taskData.title,
        description: taskData.description || undefined
      };

      const newTask = await taskApi.createTask(userId, requestData);
      return newTask;
    } catch (error) {
      console.error('Error creating task:', error);
      throw error;
    }
  },

  /**
   * Get task details by ID
   */
  async getTask(userId: string, taskId: string): Promise<Task> {
    try {
      const task = await taskApi.getTask(userId, taskId);
      return task;
    } catch (error) {
      console.error('Error getting task:', error);
      throw error;
    }
  },

  /**
   * Update an existing task
   */
  async updateTask(userId: string, taskId: string, taskData: Partial<Omit<Task, 'id' | 'user_id' | 'created_at' | 'updated_at'>>): Promise<Task> {
    try {
      const requestData: UpdateTaskRequest = {};

      if (taskData.title !== undefined) {
        requestData.title = taskData.title;
      }

      if (taskData.description !== undefined) {
        requestData.description = taskData.description;
      }

      if (taskData.completed !== undefined) {
        requestData.completed = taskData.completed;
      }

      const updatedTask = await taskApi.updateTask(userId, taskId, requestData);
      return updatedTask;
    } catch (error) {
      console.error('Error updating task:', error);
      throw error;
    }
  },

  /**
   * Delete a task
   */
  async deleteTask(userId: string, taskId: string): Promise<void> {
    try {
      await taskApi.deleteTask(userId, taskId);
    } catch (error) {
      console.error('Error deleting task:', error);
      throw error;
    }
  },

  /**
   * Toggle task completion status
   */
  async toggleComplete(userId: string, taskId: string): Promise<Task> {
    try {
      const updatedTask = await taskApi.toggleComplete(userId, taskId);
      return updatedTask;
    } catch (error) {
      console.error('Error toggling task completion:', error);
      throw error;
    }
  }
};

// Export individual functions for convenience
export const {
  listTasks,
  createTask,
  getTask,
  updateTask,
  deleteTask,
  toggleComplete
} = taskService;