'use client';

import React from 'react';

interface InputProps {
  id?: string;
  name?: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'textarea';
  placeholder?: string;
  value?: string | number;
  onChange?: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  onFocus?: () => void;
  onBlur?: () => void;
  disabled?: boolean;
  required?: boolean;
  className?: string;
  label?: string;
  error?: string;
  rows?: number;
  autoComplete?: string;
  icon?: React.ReactNode;
  helperText?: string;
}

export const Input: React.FC<InputProps> = ({
  id,
  name,
  type = 'text',
  placeholder,
  value,
  onChange,
  onFocus,
  onBlur,
  disabled = false,
  required = false,
  className = '',
  label,
  error,
  rows = 3,
  autoComplete,
  icon,
  helperText,
}) => {
  const baseClasses = 'w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-200 bg-white/30 dark:bg-black/20 backdrop-blur-sm border border-white/40 dark:border-gray-600/50';

  const errorClasses = error ? 'border-red-500/50 bg-red-500/5 dark:bg-red-500/10' : 'border-gray-300/50 dark:border-gray-600/50';

  const classes = `input-focus-effect ${baseClasses} ${errorClasses} ${icon ? 'pl-10' : ''} ${disabled ? 'bg-gray-100/50 cursor-not-allowed opacity-70' : ''} ${className}`;

  return (
    <div className="flex flex-col space-y-2 w-full">
      {label && (
        <label htmlFor={id} className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <div className="relative group w-full">
        {icon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 z-10">
            {icon}
          </div>
        )}
        {type === 'textarea' ? (
          <textarea
            id={id}
            name={name}
            placeholder={placeholder}
            value={value}
            onChange={(e) => onChange?.(e as React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>)}
            onFocus={onFocus}
            onBlur={onBlur}
            disabled={disabled}
            required={required}
            className={`${classes} transition-all duration-300`}
            rows={rows}
            aria-invalid={!!error}
            aria-describedby={error ? `${id}-error` : undefined}
          />
        ) : (
          <input
            id={id}
            name={name}
            type={type}
            placeholder={placeholder}
            value={value}
            onChange={(e) => onChange?.(e as React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>)}
            onFocus={onFocus}
            onBlur={onBlur}
            disabled={disabled}
            required={required}
            className={`${classes} transition-all duration-300`}
            aria-invalid={!!error}
            aria-describedby={error ? `${id}-error` : undefined}
            autoComplete={autoComplete}
          />
        )}
        {error && <p className="text-sm text-red-500 dark:text-red-400 mt-1">{error}</p>}
        {!error && helperText && <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{helperText}</p>}
      </div>
    </div>
  );
};

export default Input;