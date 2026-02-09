import { useState, useCallback } from 'react';
import { taskApi, FrontendTask as Task, CreateTaskRequest, UpdateTaskRequest } from '@/lib/api-client';
import { useAuth } from './useAuth';

interface TaskManagerState {
  tasks: Task[];
  loading: boolean;
  error: string | null;
}

export const useTaskManager = () => {
  const { user } = useAuth();
  const [state, setState] = useState<TaskManagerState>({
    tasks: [],
    loading: false,
    error: null,
  });

  const fetchTasks = useCallback(async () => {
    if (!user?.id) {
      console.warn('No user ID available for fetching tasks');
      return;
    }

    console.log('Fetching tasks for user ID:', user.id);

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const tasks = await taskApi.getTasks(user.id, true); // showLoading=true by default
      console.log(`Successfully fetched ${tasks.length} tasks`);
      setState({ tasks, loading: false, error: null });
    } catch (err) {
      console.error('Error fetching tasks:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch tasks';
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
    }
  }, [user?.id]);

  const createTask = useCallback(async (taskData: CreateTaskRequest) => {
    if (!user?.id) return;

    // Optimistic update: add the task to the list immediately
    const optimisticTask: Task = {
      id: Date.now().toString(), // Temporary ID
      user_id: user.id,
      title: taskData.title,
      description: taskData.description || null,
      completed: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    setState(prev => ({
      ...prev,
      tasks: [optimisticTask, ...prev.tasks],
    }));

    try {
      const createdTask = await taskApi.createTask(user.id, taskData, true); // showLoading=true by default

      // Replace the optimistic task with the actual one
      setState(prev => ({
        ...prev,
        tasks: prev.tasks.map(t =>
          t.id === optimisticTask.id ? createdTask : t
        ),
      }));
    } catch (err) {
      // Remove the optimistic task if creation failed
      setState(prev => ({
        ...prev,
        tasks: prev.tasks.filter(t => t.id !== optimisticTask.id),
        error: err instanceof Error ? err.message : 'Failed to create task'
      }));
    }
  }, [user?.id]);

  const updateTask = useCallback(async (taskId: string, taskData: UpdateTaskRequest) => {
    if (!user?.id) return;

    // Optimistic update: update the task immediately
    setState(prev => ({
      ...prev,
      tasks: prev.tasks.map(task =>
        task.id === taskId
          ? { ...task, ...taskData, updated_at: new Date().toISOString() }
          : task
      ),
    }));

    try {
      const updatedTask = await taskApi.updateTask(user.id, taskId, taskData, true); // showLoading=true by default

      // Update with the server response
      setState(prev => ({
        ...prev,
        tasks: prev.tasks.map(task =>
          task.id === taskId ? updatedTask : task
        ),
      }));
    } catch (err) {
      // Revert the optimistic update if failed
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : 'Failed to update task'
      }));
      // Refresh tasks to revert to server state
      fetchTasks();
    }
  }, [user?.id, fetchTasks]);

  const deleteTask = useCallback(async (taskId: string) => {
    if (!user?.id) return;

    // Optimistic update: remove the task immediately
    const deletedTask = state.tasks.find(t => t.id === taskId);
    setState(prev => ({
      ...prev,
      tasks: prev.tasks.filter(t => t.id !== taskId),
    }));

    try {
      await taskApi.deleteTask(user.id, taskId, true); // showLoading=true by default
      // Task was successfully deleted from server
    } catch (err) {
      // Restore the task if deletion failed
      if (deletedTask) {
        setState(prev => ({
          ...prev,
          tasks: [...prev.tasks, deletedTask],
          error: err instanceof Error ? err.message : 'Failed to delete task'
        }));
      }
    }
  }, [user?.id, state.tasks]);

  const toggleComplete = useCallback(async (task: Task) => {
    if (!user?.id) return;

    // Optimistic update: toggle the completion status immediately
    setState(prev => ({
      ...prev,
      tasks: prev.tasks.map(t =>
        t.id === task.id
          ? { ...t, completed: !t.completed, updated_at: new Date().toISOString() }
          : t
      ),
    }));

    try {
      const updatedTask = await taskApi.toggleComplete(user.id, task.id, true); // showLoading=true by default

      // Update with the server response
      setState(prev => ({
        ...prev,
        tasks: prev.tasks.map(t =>
          t.id === task.id ? updatedTask : t
        ),
      }));
    } catch (err) {
      // Revert the optimistic update if failed
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : 'Failed to update task status'
      }));
      // Refresh tasks to revert to server state
      fetchTasks();
    }
  }, [user?.id, fetchTasks]);

  return {
    tasks: state.tasks,
    loading: state.loading,
    error: state.error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
  };
};