/**
 * TaskRefreshContext
 *
 * Provides a way for components (like the chat widget) to trigger
 * task list refreshes across the application.
 */

'use client';

import { createContext, useContext, ReactNode } from 'react';

interface TaskRefreshContextType {
  refreshTasks: () => void;
}

const TaskRefreshContext = createContext<TaskRefreshContextType | undefined>(undefined);

export function TaskRefreshProvider({
  children,
  refreshTasks,
}: {
  children: ReactNode;
  refreshTasks: () => void;
}) {
  return (
    <TaskRefreshContext.Provider value={{ refreshTasks }}>
      {children}
    </TaskRefreshContext.Provider>
  );
}

export function useTaskRefresh() {
  const context = useContext(TaskRefreshContext);
  if (context === undefined) {
    // Return a no-op function if context is not available
    // This allows components to work even outside the provider
    return { refreshTasks: () => {} };
  }
  return context;
}
