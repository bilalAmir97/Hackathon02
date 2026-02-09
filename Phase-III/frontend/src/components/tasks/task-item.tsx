'use client';

import React, { useEffect, useRef } from 'react';
import { FrontendTask as Task } from '@/lib/api-client';
import { Button } from '../ui/button';
import { useGsapAnimations } from '@/hooks/useGsapAnimations';
import CursorEnhancedElement from '@/components/cursor/CursorEnhancedElement';

interface TaskItemProps {
  task: Task;
  onToggleComplete: (task: Task) => void;
  onDelete: (taskId: string) => void;
  onUpdate: (task: Task) => void;
  index?: number;
}

export const TaskItem: React.FC<TaskItemProps> = ({
  task,
  onToggleComplete,
  onDelete,
  onUpdate,
  index = 0
}) => {
  const { useAnimateTaskItem, useButtonHoverAnimation, quickAnimation } = useGsapAnimations();
  const taskItemRef = useAnimateTaskItem(index);
  const editButtonRef = useButtonHoverAnimation();
  const deleteButtonRef = useButtonHoverAnimation();

  const handleToggleComplete = () => {
    onToggleComplete(task);

    // Add a quick visual feedback animation
    if (taskItemRef.current) {
      quickAnimation(taskItemRef.current, {
        scale: 0.98,
        duration: 0.1,
        ease: 'power1.out',
        clearProps: 'transform'
      });
    }
  };

  const handleDelete = () => {
    // Add a quick visual feedback animation before deletion
    if (taskItemRef.current) {
      quickAnimation(taskItemRef.current, {
        scale: 0.95,
        opacity: 0.8,
        duration: 0.2,
        ease: 'power1.out',
        clearProps: 'transform opacity'
      });
    }

    // Delay the actual deletion to allow animation to complete
    setTimeout(() => {
      onDelete(task.id);
    }, 100);
  };

  return (
    <div
      ref={taskItemRef}
      className="glass-effect backdrop-blur-xl bg-white/20 dark:bg-black/20 border border-white/30 dark:border-white/10 p-5 rounded-2xl transition-all duration-300 hover:shadow-xl hover:border-blue-300/50 group relative overflow-hidden"
      role="listitem"
      aria-labelledby={`task-title-${task.id}`}
    >
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-pink-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl -z-10"></div>

      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 pt-1">
          <div className="relative">
            <input
              type="checkbox"
              id={`task-checkbox-${task.id}`}
              checked={task.completed}
              onChange={handleToggleComplete}
              className="h-6 w-6 rounded-lg border-2 border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 focus:ring-2 cursor-pointer appearance-none transition-all duration-200 checked:bg-gradient-to-r checked:from-blue-500 checked:to-purple-500 checked:border-transparent"
              aria-label={task.completed ? `Mark "${task.title}" as incomplete` : `Mark "${task.title}" as complete`}
            />
            {task.completed && (
              <svg
                className="absolute top-0.5 left-0.5 w-5 h-5 text-white pointer-events-none transition-opacity duration-200"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>
        </div>

        <div className="flex-grow min-w-0">
          <h3
            id={`task-title-${task.id}`}
            className={`text-lg font-semibold truncate ${task.completed ? 'line-through text-gray-500 dark:text-gray-400' : 'text-gray-900 dark:text-white'} transition-colors duration-200`}
          >
            {task.title}
          </h3>

          {task.description && (
            <p
              id={`task-desc-${task.id}`}
              className={`mt-2 text-sm ${task.completed ? 'line-through text-gray-400 dark:text-gray-500' : 'text-gray-600 dark:text-gray-300'} transition-colors duration-200 leading-relaxed`}
            >
              {task.description}
            </p>
          )}

          <div className="mt-3 flex items-center text-xs text-gray-500 dark:text-gray-400" aria-label="Task metadata">
            <div className="flex items-center gap-1">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>Created: {new Date(task.created_at).toLocaleDateString()}</span>
            </div>
            {task.updated_at !== task.created_at && (
              <div className="flex items-center gap-1 ml-3">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Updated: {new Date(task.updated_at).toLocaleDateString()}</span>
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-shrink-0 gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300" role="group" aria-label="Task actions">
          <CursorEnhancedElement>
            <Button
              ref={editButtonRef}
              variant="ghost"
              size="sm"
              onClick={() => onUpdate(task)}
              className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 relative overflow-hidden group/btn"
              aria-label={`Edit task "${task.title}"`}
            >
              <span className="relative z-10 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </span>
              <span className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-300 -translate-x-full group-hover/btn:translate-x-0"></span>
            </Button>
          </CursorEnhancedElement>
          <CursorEnhancedElement>
            <Button
              ref={deleteButtonRef}
              variant="ghost"
              size="sm"
              onClick={handleDelete}
              className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 relative overflow-hidden group/btn"
              aria-label={`Delete task "${task.title}"`}
            >
              <span className="relative z-10 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </span>
              <span className="absolute inset-0 bg-gradient-to-r from-red-500/10 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-300 -translate-x-full group-hover/btn:translate-x-0"></span>
            </Button>
          </CursorEnhancedElement>
        </div>
      </div>
    </div>
  );
};

export default TaskItem;