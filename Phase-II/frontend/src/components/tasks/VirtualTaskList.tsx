import React, { useState, useEffect, useRef } from 'react';

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
}

interface VirtualTaskListProps {
  tasks: Task[];
  itemHeight?: number;
  containerHeight?: number;
  onToggleComplete: (taskId: string) => void;
  onDelete: (taskId: string) => void;
}

export const VirtualTaskList: React.FC<VirtualTaskListProps> = ({
  tasks,
  itemHeight = 100,
  containerHeight = 400,
  onToggleComplete,
  onDelete
}) => {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  // Calculate visible items based on scroll position
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + Math.ceil(containerHeight / itemHeight) + 5, // Add buffer
    tasks.length
  );

  // Calculate offset for smooth scrolling
  const offset = startIndex * itemHeight;

  // Calculate total height for scroll container
  const totalHeight = tasks.length * itemHeight;

  // Handle scroll events
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  };

  // Render only visible items plus buffer
  const visibleTasks = tasks.slice(startIndex, endIndex);

  return (
    <div className="relative">
      <div
        ref={containerRef}
        className="overflow-y-auto"
        style={{ height: `${containerHeight}px` }}
        onScroll={handleScroll}
      >
        {/* Spacer div to maintain scroll range */}
        <div style={{ height: `${totalHeight}px`, position: 'relative' }}>
          {/* Visible items container */}
          <div style={{ transform: `translateY(${offset}px)` }}>
            {visibleTasks.map((task, index) => {
              const actualIndex = startIndex + index;
              return (
                <div
                  key={task.id}
                  style={{ height: `${itemHeight}px` }}
                  className={`p-4 border-b border-[var(--glass-border)] ${
                    task.completed
                      ? 'bg-[var(--soft-dark-bg-secondary)]/50'
                      : 'bg-[var(--glass-bg)]'
                  }`}
                >
                  <div className="flex items-start">
                    <input
                      type="checkbox"
                      checked={task.completed}
                      onChange={() => onToggleComplete(task.id)}
                      className="mt-1 h-5 w-5 rounded border-[var(--glass-border)] bg-[var(--soft-dark-bg-secondary)] text-[var(--primary-accent)] focus:ring-[var(--primary-accent)] focus:ring-offset-0"
                    />

                    <div className="ml-4 flex-1">
                      <h3 className={`text-lg font-medium ${task.completed ? 'text-[var(--text-secondary)] line-through' : 'text-[var(--text-primary)]'}`}>
                        {task.title}
                      </h3>

                      {task.description && (
                        <p className={`mt-1 text-sm ${task.completed ? 'text-[var(--text-secondary)]/70' : 'text-[var(--text-secondary)]'}`}>
                          {task.description}
                        </p>
                      )}

                      <div className="mt-3 flex items-center text-xs text-[var(--text-secondary)]">
                        <span>Created: {new Date(task.createdAt).toLocaleDateString()}</span>
                        {task.updatedAt !== task.createdAt && (
                          <span className="ml-3">Updated: {new Date(task.updatedAt).toLocaleDateString()}</span>
                        )}
                      </div>
                    </div>

                    <button
                      onClick={() => onDelete(task.id)}
                      className="text-[var(--color-danger)] hover:text-[var(--color-danger)]/80 ml-2"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};