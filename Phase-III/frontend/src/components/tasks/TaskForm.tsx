import React, { useState } from 'react';
import { SoftDarkInput } from '@/components/ui/SoftDarkInput';
import { SoftDarkButton } from '@/components/ui/SoftDarkButton';

interface TaskFormData {
  title: string;
  description?: string;
}

interface TaskFormProps {
  initialData?: TaskFormData;
  onSubmit: (data: TaskFormData) => void;
  onCancel: () => void;
  submitLabel?: string;
  cancelLabel?: string;
}

export const TaskForm: React.FC<TaskFormProps> = ({
  initialData = { title: '', description: '' },
  onSubmit,
  onCancel,
  submitLabel = 'Save Task',
  cancelLabel = 'Cancel'
}) => {
  const [formData, setFormData] = useState<TaskFormData>({
    title: initialData.title || '',
    description: initialData.description || ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    } else if (formData.title.length > 200) {
      newErrors.title = 'Title must be 200 characters or less';
    }

    if (formData.description && formData.description.length > 1000) {
      newErrors.description = 'Description must be 1000 characters or less';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validate()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <SoftDarkInput
          label="Task Title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          error={errors.title}
          placeholder="Enter task title..."
          required
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-[var(--text-primary)] mb-2">
          Description
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Enter task description (optional)..."
          className="w-full px-4 py-3 bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-lg text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-accent)] focus:border-transparent backdrop-blur-[var(--glass-blur)]"
          rows={3}
        />
        {errors.description && (
          <p className="mt-1 text-sm text-[var(--color-danger)]">
            {errors.description}
          </p>
        )}
      </div>

      <div className="flex justify-end space-x-3 pt-2">
        <SoftDarkButton type="button" variant="ghost" onClick={onCancel}>
          {cancelLabel}
        </SoftDarkButton>
        <SoftDarkButton type="submit">
          {submitLabel}
        </SoftDarkButton>
      </div>
    </form>
  );
};