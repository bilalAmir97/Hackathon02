'use client';

import React, { useEffect, useState, useContext } from 'react';
import { ToastContext } from '@/components/ui/toast';

interface GlobalErrorHandlerProps {
  children: React.ReactNode;
}

export const GlobalErrorHandler: React.FC<GlobalErrorHandlerProps> = ({ children }) => {
  // Directly access the toast context to avoid hook dependency issues
  const toastContext = useContext(ToastContext);

  useEffect(() => {
    // Handle uncaught promise rejections
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error('Unhandled promise rejection:', event.reason);

      // Only show toast if context is available
      if (toastContext) {
        toastContext.addToast({
          message: 'An unexpected error occurred. Please try again.',
          type: 'error',
        });
      } else {
        console.warn('Toast not available, showing console error instead:', event.reason);
      }
    };

    // Handle uncaught errors
    const handleError = (event: ErrorEvent) => {
      console.error('Uncaught error:', event.error);

      // Don't show duplicate error messages for network errors during development
      if (toastContext) {
        if (event.error?.message?.includes?.('Network Error') ||
            event.error?.message?.includes?.('Failed to fetch')) {
          toastContext.addToast({
            message: 'Connection error. Please check your internet connection.',
            type: 'error',
          });
        } else {
          toastContext.addToast({
            message: 'An unexpected error occurred. Please try again.',
            type: 'error',
          });
        }
      } else {
        console.warn('Toast not available, showing console error instead:', event.error);
      }
    };

    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    window.addEventListener('error', handleError);

    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      window.removeEventListener('error', handleError);
    };
  }, [toastContext]);

  return <>{children}</>;
};

export default GlobalErrorHandler;