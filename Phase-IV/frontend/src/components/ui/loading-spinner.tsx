import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  message = 'Loading...',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-12 w-12',
    lg: 'h-16 w-16'
  };

  const borderSize = {
    sm: 'border-2',
    md: 'border-4',
    lg: 'border-4'
  };

  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <div
        className={`animate-spin rounded-full border-t-2 border-r-2 ${borderSize[size]} ${sizeClasses[size]} border-blue-500 ease-in-out`}
        role="status"
      >
        <span className="sr-only">Loading...</span>
      </div>
      {message && (
        <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">{message}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;