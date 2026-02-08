import React from 'react';
import { TaskCard } from '@/components/tasks/TaskCard';

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
}

interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (task: Task) => void;
  onDelete: (taskId: string) => void;
  showEmptyState?: boolean;
  emptyStateMessage?: string;
}

export const TaskList: React.FC<TaskListProps> = ({
  tasks,
  onToggleComplete,
  onDelete,
  showEmptyState = true,
  emptyStateMessage = 'No tasks to display'
}) => {
  return (
    <div className="space-y-4">
      {tasks.length > 0 ? (
        tasks.map(task => (
          <TaskCard
            key={task.id}
            task={task}
            onToggleComplete={onToggleComplete}
            onDelete={onDelete}
          />
        ))
      ) : showEmptyState ? (
        <div className="text-center py-8">
          <div className="mx-auto w-16 h-16 rounded-full bg-[var(--soft-dark-bg-secondary)] flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <p className="text-[var(--text-secondary)]">{emptyStateMessage}</p>
        </div>
      ) : null}
    </div>
  );
};