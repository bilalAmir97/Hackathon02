'use client';

import React, { useEffect, useRef } from 'react';
import { FrontendTask as Task } from '@/lib/api-client';
import { TaskItem } from './task-item';
import { animateTaskList } from '@/lib/gsap-animations';
import { TaskItemSkeleton } from '../ui/loading-skeleton';

interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (task: Task) => void;
  onDelete: (taskId: string) => void;
  onUpdate: (task: Task) => void;
  loading?: boolean;
  emptyMessage?: string;
}

export const TaskList: React.FC<TaskListProps> = ({
  tasks,
  onToggleComplete,
  onDelete,
  onUpdate,
  loading = false,
  emptyMessage = 'No tasks found. Add a new task to get started.'
}) => {
  const taskListRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (taskListRef.current && tasks.length > 0) {
      // Get all task items in the list
      const taskItems = taskListRef.current.querySelectorAll('.task-item');
      animateTaskList(taskItems);
    }
  }, [tasks]);

  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, index) => (
          <TaskItemSkeleton key={`skeleton-${index}`} />
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-1">No tasks</h3>
        <p className="text-gray-500 dark:text-gray-400">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div ref={taskListRef} className="space-y-3">
      {tasks.map((task, index) => (
        <div key={task.id} className="task-item">
          <TaskItem
            task={task}
            onToggleComplete={onToggleComplete}
            onDelete={onDelete}
            onUpdate={onUpdate}
            index={index}
          />
        </div>
      ))}
    </div>
  );
};

export default TaskList;