import React from 'react';

interface SoftDarkCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined';
  children: React.ReactNode;
}

export const SoftDarkCard: React.FC<SoftDarkCardProps> = ({
  variant = 'default',
  children,
  className = '',
  ...props
}) => {
  const baseClasses = 'rounded-xl border transition-all duration-300 ease-out';

  const variantClasses = {
    default: 'bg-[var(--glass-bg)] border-[var(--glass-border)] shadow-[var(--glass-shadow)] backdrop-blur-[var(--glass-blur)]',
    elevated: 'bg-[var(--glass-bg)] border-[var(--glass-border)] shadow-[var(--glass-shadow)] backdrop-blur-[var(--glass-blur)] hover:shadow-[0_12px_40px_-10px_rgba(2,6,23,0.4)]',
    outlined: 'bg-transparent border-[var(--glass-border)] shadow-sm',
  };

  const classes = `${baseClasses} ${variantClasses[variant]} ${className}`;

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};