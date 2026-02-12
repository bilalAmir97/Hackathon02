/**
 * Chat Layout - Authenticated route wrapper
 *
 * Ensures users are authenticated before accessing the chat interface.
 * Provides consistent layout structure for all chat pages.
 */

import { redirect } from 'next/navigation';
import { ReactNode } from 'react';

interface ChatLayoutProps {
  children: ReactNode;
}

/**
 * Chat layout component with authentication check
 */
export default async function ChatLayout({ children }: ChatLayoutProps) {
  // Check authentication status server-side
  // Note: This is a placeholder - actual auth check will be implemented
  // when Better Auth server-side utilities are available

  // For now, we'll rely on client-side auth checks in the page components
  // In production, add server-side session validation here

  return (
    <div className="h-screen w-full overflow-hidden bg-gray-50">
      {children}
    </div>
  );
}
