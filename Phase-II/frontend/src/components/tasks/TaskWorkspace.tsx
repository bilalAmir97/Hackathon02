import React, { useState } from 'react';
import { SoftDarkCard } from '@/components/ui/SoftDarkCard';
import { TaskForm } from '@/components/tasks/TaskForm';
import { TaskCard } from '@/components/tasks/TaskCard';

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
}

interface TaskWorkspaceProps {
  tasks: Task[];
  onCreate: (task: Omit<Task, 'id' | 'createdAt' | 'updatedAt' | 'completed'>) => void;
  onUpdate: (taskId: string, updates: Partial<Task>) => void;
  onDelete: (taskId: string) => void;
  onToggleComplete: (task: Task) => void;
}

export const TaskWorkspace: React.FC<TaskWorkspaceProps> = ({
  tasks,
  onCreate,
  onUpdate,
  onDelete,
  onToggleComplete
}) => {
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  const handleAddTask = () => {
    setEditingTask(null);
    setShowForm(true);
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setShowForm(true);
  };

  const handleFormSubmit = (formData: { title: string; description?: string }) => {
    if (editingTask) {
      onUpdate(editingTask.id, formData);
    } else {
      onCreate(formData);
    }
    setShowForm(false);
    setEditingTask(null);
  };

  const handleToggleComplete = (task: Task) => {
    onToggleComplete(task);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingTask(null);
  };

  // Group tasks by status
  const completedTasks = tasks.filter(task => task.completed);
  const pendingTasks = tasks.filter(task => !task.completed);

  return (
    <div className="space-y-6">
      {/* Header with Add Task button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-[var(--text-primary)]">Task Workspace</h2>
        <button
          onClick={handleAddTask}
          className="px-4 py-2 bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] rounded-lg text-white hover:opacity-90 transition-opacity"
        >
          Add Task
        </button>
      </div>

      {/* Task Form Modal */}
      {showForm && (
        <SoftDarkCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">
            {editingTask ? 'Edit Task' : 'Create New Task'}
          </h3>
          <TaskForm
            initialData={editingTask ? { title: editingTask.title, description: editingTask.description } : undefined}
            onSubmit={handleFormSubmit}
            onCancel={handleCancelForm}
            submitLabel={editingTask ? 'Update Task' : 'Create Task'}
          />
        </SoftDarkCard>
      )}

      {/* Task Lists */}
      <div className="space-y-8">
        {/* Pending Tasks */}
        {!showForm && pendingTasks.length > 0 && (
          <div>
            <h3 className="text-lg font-medium text-[var(--text-primary)] mb-4">Pending Tasks</h3>
            <div className="space-y-4">
              {pendingTasks.map(task => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onToggleComplete={handleToggleComplete}
                  onDelete={onDelete}
                />
              ))}
            </div>
          </div>
        )}

        {/* Completed Tasks */}
        {!showForm && completedTasks.length > 0 && (
          <div>
            <h3 className="text-lg font-medium text-[var(--text-primary)] mb-4">Completed Tasks</h3>
            <div className="space-y-4">
              {completedTasks.map(task => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onToggleComplete={handleToggleComplete}
                  onDelete={onDelete}
                />
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!showForm && tasks.length === 0 && (
          <SoftDarkCard className="p-12 text-center">
            <div className="mx-auto w-24 h-24 rounded-full bg-gradient-to-r from-[var(--primary-accent)]/20 to-[var(--primary-accent-end)]/20 flex items-center justify-center mb-6">
              <svg className="w-12 h-12 text-[var(--primary-accent)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-2">No tasks yet</h3>
            <p className="text-[var(--text-secondary)] mb-6">Get started by creating your first task</p>
            <button
              onClick={handleAddTask}
              className="px-6 py-3 bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] rounded-lg text-white hover:opacity-90 transition-opacity"
            >
              Create Your First Task
            </button>
          </SoftDarkCard>
        )}
      </div>
    </div>
  );
};