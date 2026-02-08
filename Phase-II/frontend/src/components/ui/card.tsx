'use client';

import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  role?: string;
  'aria-label'?: string;
  [key: string]: any; // Allow additional props
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  title,
  subtitle,
  role,
  'aria-label': ariaLabel,
  ...props
}) => {
  return (
    <div
      className={`glass-effect backdrop-blur-xl bg-white/20 dark:bg-black/20 border border-white/30 dark:border-white/10 rounded-2xl shadow-xl overflow-hidden w-full max-w-full ${className}`}
      role={role}
      aria-label={ariaLabel}
      {...props}
    >
      {(title || subtitle) && (
        <div className="border-b border-white/20 dark:border-white/10 p-4 sm:p-6">
          {title && <h3 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">{title}</h3>}
          {subtitle && <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300 mt-1">{subtitle}</p>}
        </div>
      )}
      <div className={`p-4 sm:p-6 ${!(title || subtitle) ? 'pt-4 sm:pt-6' : ''}`}>
        {children}
      </div>
    </div>
  );
};

export default Card;