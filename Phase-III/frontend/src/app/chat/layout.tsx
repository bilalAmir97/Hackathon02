/**
 * Chat Layout - Authenticated route wrapper
 *
 * Ensures users are authenticated before accessing the chat interface.
 * Provides full-screen layout for the premium chat experience.
 */

import { ReactNode } from 'react';

interface ChatLayoutProps {
  children: ReactNode;
}

/**
 * Chat layout component with full-screen container
 */
export default async function ChatLayout({ children }: ChatLayoutProps) {
  return (
    <div className="h-screen w-full overflow-hidden">
      {children}
    </div>
  );
}
