'use client';

import React, { useEffect, useState } from 'react';
import { ToastProvider } from '../ui/toast';
import { AuthProvider } from '@/hooks/useAuth';
import { TransitionProvider } from './transition-provider';
import ErrorBoundary from './error-boundary';
import GlobalErrorHandler from './global-error-handler';
import { ScanlineProvider } from '@/context/scanline-context';
import { CursorProvider } from '@/components/cursor/CursorContext';
import GlobalCursor from '@/components/cursor/GlobalCursor';
import { ThemeProvider } from '@/components/theme/ThemeProvider';

interface ClientWrapperProps {
  children: React.ReactNode;
}

export const ClientWrapper: React.FC<ClientWrapperProps> = ({ children }) => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    // Render a minimal fallback during SSR
    return <>{children}</>;
  }

  return (
    <ErrorBoundary>
      <ToastProvider>
        <GlobalErrorHandler>
          <ThemeProvider>
            <AuthProvider>
              <TransitionProvider>
                <ScanlineProvider>
                  <CursorProvider>
                    <GlobalCursor />
                    {children}
                  </CursorProvider>
                </ScanlineProvider>
              </TransitionProvider>
            </AuthProvider>
          </ThemeProvider>
        </GlobalErrorHandler>
      </ToastProvider>
    </ErrorBoundary>
  );
};