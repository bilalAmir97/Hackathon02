'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { ToastProvider } from '../ui/toast';
import { AuthProvider } from '@/hooks/useAuth';
import { TransitionProvider } from './transition-provider';
import ErrorBoundary from './error-boundary';
import GlobalErrorHandler from './global-error-handler';
import { ScanlineProvider } from '@/context/scanline-context';
import { CursorProvider } from '@/components/cursor/CursorContext';
import GlobalCursor from '@/components/cursor/GlobalCursor';
import { ThemeProvider } from '@/components/theme/ThemeProvider';
import { TaskRefreshProvider } from '@/context/TaskRefreshContext';
import { FloatingChatButton } from '@/components/chat/FloatingChatButton';

interface ClientWrapperProps {
  children: React.ReactNode;
}

export const ClientWrapper: React.FC<ClientWrapperProps> = ({ children }) => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Create a refresh callback that dispatches a custom event
  const handleRefreshTasks = useCallback(() => {
    console.log('[ClientWrapper] Dispatching task-refresh event');
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('task-refresh'));
    }
  }, []);

  // Always provide AuthProvider (safe for SSR), but conditionally render other providers
  if (!isMounted) {
    // Render minimal providers during SSR
    return (
      <ErrorBoundary>
        <AuthProvider>
          {children}
        </AuthProvider>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <ToastProvider>
        <GlobalErrorHandler>
          <ThemeProvider>
            <AuthProvider>
              <TaskRefreshProvider refreshTasks={handleRefreshTasks}>
                <TransitionProvider>
                  <ScanlineProvider>
                    <CursorProvider>
                      <GlobalCursor />
                      {children}
                      <FloatingChatButton />
                    </CursorProvider>
                  </ScanlineProvider>
                </TransitionProvider>
              </TaskRefreshProvider>
            </AuthProvider>
          </ThemeProvider>
        </GlobalErrorHandler>
      </ToastProvider>
    </ErrorBoundary>
  );
};