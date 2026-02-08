import React from 'react';

interface SoftDarkInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const SoftDarkInput: React.FC<SoftDarkInputProps> = ({
  label,
  error,
  helperText,
  className = '',
  ...props
}) => {
  const baseClasses = 'w-full px-4 py-3 bg-[var(--glass-bg)] border rounded-lg text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:ring-2 transition-all duration-200 ease-in-out backdrop-blur-[var(--glass-blur)]';

  const errorClasses = error ? 'border-[var(--color-danger)] focus:ring-[var(--color-danger)]' : 'border-[var(--glass-border)] focus:ring-[var(--primary-accent)]';

  const classes = `${baseClasses} ${errorClasses} ${className}`;

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
          {label}
        </label>
      )}
      <input
        className={classes}
        {...props}
      />
      {helperText && !error && (
        <p className="mt-1 text-sm text-[var(--text-secondary)]">
          {helperText}
        </p>
      )}
      {error && (
        <p className="mt-1 text-sm text-[var(--color-danger)]">
          {error}
        </p>
      )}
    </div>
  );
};