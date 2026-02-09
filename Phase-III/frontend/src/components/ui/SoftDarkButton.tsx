import React from 'react';

interface SoftDarkButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  children: React.ReactNode;
}

export const SoftDarkButton: React.FC<SoftDarkButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[var(--soft-dark-bg)]';

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  const variantClasses = {
    primary: 'bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] text-white hover:opacity-90 focus:ring-[var(--primary-accent)] border border-[rgba(56,189,248,0.2)]',
    secondary: 'bg-[var(--soft-dark-bg-tertiary)] text-[var(--text-primary)] hover:bg-[var(--soft-dark-bg-secondary)] focus:ring-[var(--primary-accent)] border border-[var(--glass-border)]',
    ghost: 'text-[var(--text-primary)] hover:bg-[var(--soft-dark-bg-secondary)] focus:ring-[var(--primary-accent)]',
    outline: 'border border-[var(--glass-border)] text-[var(--text-primary)] hover:bg-[var(--soft-dark-bg-secondary)] focus:ring-[var(--primary-accent)]',
  };

  const disabledClass = disabled || isLoading ? 'opacity-50 cursor-not-allowed' : '';

  const classes = `${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${disabledClass} ${className}`;

  return (
    <button className={classes} disabled={disabled || isLoading} {...props}>
      {isLoading ? (
        <>
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading...
        </>
      ) : (
        children
      )}
    </button>
  );
};