'use client';

import React, { useState } from 'react';
import { FrontendTask as Task } from '@/lib/api-client';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface TaskFormProps {
  task?: Task;
  onSubmit: (taskData: Partial<Task> | Pick<Task, 'title' | 'description'>) => void;
  onCancel?: () => void;
  submitLabel?: string;
  cancelLabel?: string;
  loading?: boolean;
  disabled?: boolean;
}

export const TaskForm: React.FC<TaskFormProps> = ({
  task,
  onSubmit,
  onCancel,
  submitLabel = 'Save Task',
  cancelLabel = 'Cancel',
  loading = false,
  disabled = false
}) => {
  const [title, setTitle] = useState(task?.title || '');
  const [description, setDescription] = useState(task?.description || '');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!title.trim()) {
      newErrors.title = 'Title is required';
    } else if (title.length > 255) {
      newErrors.title = 'Title must be less than 255 characters';
    }

    if (description && description.length > 1000) {
      newErrors.description = 'Description must be less than 1000 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      // Focus on the first error field
      const firstErrorField = Object.keys(errors)[0];
      if (firstErrorField) {
        const element = document.getElementById(firstErrorField);
        element?.focus();
      }
      return;
    }

    onSubmit({
      title: title.trim(),
      description: description.trim()
    });
  };

  const combinedDisabled = loading || disabled;

  return (
    <Card className="glass-effect backdrop-blur-xl bg-white/20 dark:bg-black/20 border border-white/30 dark:border-white/10 p-6 shadow-xl hover:shadow-2xl transition-all duration-500" role="form" aria-label={task ? "Edit Task Form" : "Create Task Form"}>
      <form onSubmit={handleSubmit} className="space-y-6" noValidate>
        <div className="space-y-4">
          <div className="relative group">
            <label htmlFor="title-input" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Task Title <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <input
                id="title-input"
                name="title"
                type="text"
                placeholder="Enter task title"
                value={title}
                onChange={(e) => {
                  setTitle(e.target.value);
                  if (errors.title) {
                    setErrors(prev => {
                      const newErrors = { ...prev };
                      delete newErrors.title;
                      return newErrors;
                    });
                  }
                }}
                required
                disabled={combinedDisabled}
                className="w-full pl-10 pr-4 py-3 bg-white/30 dark:bg-black/20 backdrop-blur-sm border border-white/40 dark:border-gray-600/50 rounded-xl text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-200"
              />
            </div>
            {errors.title && <p className="text-sm text-red-500 dark:text-red-400 mt-1">{errors.title}</p>}
          </div>

          <div className="relative group">
            <label htmlFor="description-input" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description
            </label>
            <div className="relative">
              <div className="absolute top-3 left-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
              </div>
              <textarea
                id="description-input"
                name="description"
                placeholder="Enter task description (optional)"
                value={description}
                onChange={(e) => {
                  setDescription(e.target.value);
                  if (errors.description) {
                    setErrors(prev => {
                      const newErrors = { ...prev };
                      delete newErrors.description;
                      return newErrors;
                    });
                  }
                }}
                disabled={combinedDisabled}
                rows={4}
                className="w-full pl-10 pr-4 py-3 bg-white/30 dark:bg-black/20 backdrop-blur-sm border border-white/40 dark:border-gray-600/50 rounded-xl text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-200 resize-none"
              />
            </div>
            {errors.description && <p className="text-sm text-red-500 dark:text-red-400 mt-1">{errors.description}</p>}
          </div>
        </div>

        <div className="flex justify-end space-x-4 pt-2">
          {onCancel && (
            <Button
              type="button"
              variant="ghost"
              onClick={onCancel}
              disabled={combinedDisabled}
              className="relative overflow-hidden group/btn"
              aria-label={cancelLabel}
            >
              <span className="relative z-10 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                {cancelLabel}
              </span>
              <span className="absolute inset-0 bg-gradient-to-r from-gray-200/20 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-300 -translate-x-full group-hover/btn:translate-x-0"></span>
            </Button>
          )}
          <Button
            type="submit"
            variant="primary"
            disabled={combinedDisabled}
            className="relative overflow-hidden group/btn"
            aria-label={loading ? `${submitLabel} (loading)` : submitLabel}
          >
            <span className="relative z-10 flex items-center">
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {submitLabel}...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {submitLabel}
                </>
              )}
            </span>
            <span className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-300 -translate-x-full group-hover/btn:translate-x-0"></span>
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default TaskForm;