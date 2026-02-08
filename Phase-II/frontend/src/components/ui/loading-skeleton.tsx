import React from 'react';

interface LoadingSkeletonProps {
  className?: string;
  width?: string;
  height?: string;
  count?: number;
  rounded?: string;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  className = '',
  width = '100%',
  height = '20px',
  count = 1,
  rounded = 'rounded-md',
}) => {
  const skeletons = Array.from({ length: count }, (_, index) => (
    <div
      key={index}
      className={`bg-gray-200 dark:bg-gray-700 animate-pulse ${rounded} ${className}`}
      style={{ width, height }}
      aria-busy="true"
      role="progressbar"
      aria-label="Loading content"
    />
  ));

  return <>{skeletons}</>;
};

// Specific loading skeletons for common components
export const CardSkeleton: React.FC = () => (
  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
    <LoadingSkeleton height="24px" width="60%" className="mb-4" />
    <LoadingSkeleton height="16px" width="100%" className="mb-2" />
    <LoadingSkeleton height="16px" width="90%" className="mb-2" />
    <LoadingSkeleton height="16px" width="70%" />
  </div>
);

export const TaskItemSkeleton: React.FC = () => (
  <div className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
    <div className="flex items-center space-x-3">
      <LoadingSkeleton width="20px" height="20px" rounded="rounded-full" />
      <div className="flex flex-col space-y-2">
        <LoadingSkeleton height="18px" width="120px" />
        <LoadingSkeleton height="14px" width="80px" />
      </div>
    </div>
    <div className="flex space-x-2">
      <LoadingSkeleton width="30px" height="30px" rounded="rounded" />
      <LoadingSkeleton width="30px" height="30px" rounded="rounded" />
    </div>
  </div>
);

export const DashboardHeaderSkeleton: React.FC = () => (
  <div className="glass-effect backdrop-blur-xl bg-white/30 p-6 rounded-2xl mb-8">
    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <LoadingSkeleton height="32px" width="200px" className="mb-2" />
        <LoadingSkeleton height="16px" width="150px" />
      </div>
      <div className="flex flex-col sm:flex-row gap-3">
        <LoadingSkeleton height="40px" width="100px" />
        <LoadingSkeleton height="40px" width="100px" />
      </div>
    </div>
  </div>
);