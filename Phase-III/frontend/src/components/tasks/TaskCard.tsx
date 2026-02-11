import React, { useState } from 'react';
import gsap from 'gsap';
import { SoftDarkButton } from '@/components/ui/SoftDarkButton';

interface TaskCardProps {
  task: {
    id: string;
    title: string;
    description?: string;
    completed: boolean;
    createdAt: string;
    updatedAt: string;
  };
  onToggleComplete: (task: { id: string; title: string; description?: string; completed: boolean; createdAt: string; updatedAt: string }) => void;
  onDelete: (taskId: string) => void;
  onEdit?: (task: { id: string; title: string; description?: string; completed: boolean; createdAt: string; updatedAt: string }) => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({ task, onToggleComplete, onDelete, onEdit }) => {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleToggleComplete = () => {
    // Add a subtle completion toggle animation
    const element = document.getElementById(`task-${task.id}`);
    if (element) {
      gsap.to(element, {
        scale: 0.98,
        duration: 0.1,
        yoyo: true,
        repeat: 1,
        ease: 'power1.inOut',
        onComplete: () => {
          // Update the task state after animation
          onToggleComplete(task);
        }
      });
    } else {
      onToggleComplete(task);
    }
  };

  const handleDelete = () => {
    setIsDeleting(true);

    // Refined deletion animation - smoother and more natural
    const element = document.getElementById(`task-${task.id}`);
    if (element) {
      gsap.to(element, {
        duration: 0.4,
        opacity: 0,
        scale: 0.9,
        height: 0,
        paddingTop: 0,
        paddingBottom: 0,
        marginTop: 0,
        marginBottom: 0,
        ease: 'power2.in',
        onComplete: () => {
          onDelete(task.id);
        }
      });
    } else {
      // If element not found, just call delete
      onDelete(task.id);
    }
  };

  return (
    <div
      id={`task-${task.id}`}
      className={`w-full max-w-full p-4 rounded-lg border transition-all duration-300 hover:shadow-lg hover:shadow-[var(--glass-shadow)] ${
        task.completed
          ? 'bg-[var(--soft-dark-bg-secondary)]/50 border-[var(--color-success)]/30'
          : 'bg-[var(--glass-bg)] border-[var(--glass-border)] hover:border-[var(--primary-accent)]/40'
      }`}
    >
      <div className="flex flex-col sm:flex-row sm:items-start gap-3 sm:gap-4 w-full">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={handleToggleComplete}
          className="h-5 w-5 rounded border-[var(--glass-border)] bg-[var(--soft-dark-bg-secondary)] text-[var(--primary-accent)] focus:ring-[var(--primary-accent)] focus:ring-offset-0 flex-shrink-0"
        />

        <div className="flex-1 min-w-0 overflow-hidden">
          <h3 className={`text-lg font-medium break-words ${task.completed ? 'text-[var(--text-secondary)] line-through' : 'text-[var(--text-primary)]'}`}>
            {task.title}
          </h3>

          {task.description && (
            <p className={`mt-1 text-sm break-words ${task.completed ? 'text-[var(--text-secondary)]/70' : 'text-[var(--text-secondary)]'}`}>
              {task.description}
            </p>
          )}

          <div className="mt-3 flex flex-wrap items-center text-xs text-[var(--text-secondary)] gap-2">
            <span>Created: {new Date(task.createdAt).toLocaleDateString()}</span>
            {task.updatedAt !== task.createdAt && (
              <span>Updated: {new Date(task.updatedAt).toLocaleDateString()}</span>
            )}
          </div>
        </div>

        <div className="flex flex-wrap gap-2 justify-end sm:justify-start w-full sm:w-auto">
          <SoftDarkButton
            variant="ghost"
            size="sm"
            onClick={handleToggleComplete}
            className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:scale-105 transition-transform duration-200"
          >
            {task.completed ? 'Undo' : 'Complete'}
          </SoftDarkButton>

          {onEdit && (
            <SoftDarkButton
              variant="ghost"
              size="sm"
              onClick={() => onEdit(task)}
              className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:scale-105 transition-transform duration-200"
            >
              Edit
            </SoftDarkButton>
          )}

          <SoftDarkButton
            variant="ghost"
            size="sm"
            onClick={handleDelete}
            className="text-[var(--color-danger)] hover:text-[var(--color-danger)]/80 hover:scale-105 transition-transform duration-200"
          >
            Delete
          </SoftDarkButton>
        </div>
      </div>
    </div>
  );
};