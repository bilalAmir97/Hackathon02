/**
 * Chat Page - Main chat interface container
 *
 * Entry point for the AI chat interface. Handles authentication
 * and renders the chat interface once user is authenticated.
 */

import { ChatPageClient } from './ChatPageClient';

// Disable static generation for this page since it requires client-side auth
export const dynamic = 'force-dynamic';

/**
 * Chat page component (server component wrapper)
 */
export default function ChatPage() {
  return <ChatPageClient />;
}
