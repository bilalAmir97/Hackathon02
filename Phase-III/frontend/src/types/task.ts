// src/types/task.ts
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskRequest {
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
}