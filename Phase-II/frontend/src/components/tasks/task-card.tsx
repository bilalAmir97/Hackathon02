'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GlassCard } from '../ui/glass-card';

export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface TaskCardProps {
  task: Task;
  onToggleComplete?: (task: Task) => void;
  onDelete?: (id: string) => void;
  onEdit?: (task: Task) => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onToggleComplete,
  onDelete,
  onEdit
}) => {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = () => {
    setIsDeleting(true);
    setTimeout(() => {
      onDelete?.(task.id);
    }, 300); // Match animation duration
  };

  return (
    <AnimatePresence>
      {!isDeleting ? (
        <motion.div
          layout
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -20, scale: 0.95, height: 0 }}
          transition={{
            type: 'spring',
            stiffness: 300,
            damping: 25,
            duration: 0.3
          }}
          className="overflow-hidden"
        >
          <GlassCard
            variant="floating"
            className={`p-4 md:p-5 relative glow-element ${
              task.completed
                ? 'opacity-70 border border-green-500/30'
                : 'border border-slate-500/20'
            }`}
          >
            <div className="flex items-start gap-3">
              <button
                onClick={() => onToggleComplete?.(task)}
                className={`mt-1 flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all duration-200 ${
                  task.completed
                    ? 'bg-gradient-to-r from-green-500 to-emerald-500 border-transparent'
                    : 'border-slate-400 hover:border-blue-400'
                }`}
                aria-label={task.completed ? "Mark as incomplete" : "Mark as complete"}
              >
                {task.completed && (
                  <svg
                    className="w-3 h-3 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={3}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
              </button>

              <div className="flex-1 min-w-0">
                <h3
                  className={`text-base md:text-lg font-medium truncate ${
                    task.completed
                      ? 'line-through text-slate-400'
                      : 'text-slate-100'
                  }`}
                >
                  {task.title}
                </h3>

                {task.description && (
                  <p className={`mt-1 text-sm truncate ${
                    task.completed
                      ? 'line-through text-slate-500'
                      : 'text-slate-300'
                  }`}>
                    {task.description}
                  </p>
                )}
              </div>

              <div className="flex gap-2 ml-2">
                {onEdit && (
                  <button
                    onClick={() => onEdit(task)}
                    className="p-1.5 rounded-lg hover:bg-slate-700/50 transition-colors text-slate-300 hover:text-slate-100"
                    aria-label="Edit task"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                      />
                    </svg>
                  </button>
                )}

                <button
                  onClick={handleDelete}
                  className="p-1.5 rounded-lg hover:bg-red-500/20 transition-colors text-slate-300 hover:text-red-400"
                  aria-label="Delete task"
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
};