/**
 * ConversationItem Component
 *
 * Displays a single conversation in the sidebar with preview,
 * timestamp, and active highlight.
 * Optimized with React.memo to prevent unnecessary re-renders.
 */

'use client';

import { memo } from 'react';
import { Conversation } from '@/types/chat';

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onClick: () => void;
}

/**
 * ConversationItem component for displaying conversation preview
 */
export const ConversationItem = memo(function ConversationItem({
  conversation,
  isActive,
  onClick,
}: ConversationItemProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <button
      onClick={onClick}
      aria-label={`${isActive ? 'Current conversation: ' : 'Switch to conversation: '}${conversation.preview || 'New conversation'}`}
      aria-current={isActive ? 'true' : 'false'}
      className={`w-full text-left px-4 py-3 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
        isActive
          ? 'bg-blue-50 border-2 border-blue-500'
          : 'bg-white border border-gray-200 hover:bg-gray-50'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p
            className={`text-sm font-medium truncate ${
              isActive ? 'text-blue-900' : 'text-gray-900'
            }`}
          >
            {conversation.preview || 'New conversation'}
          </p>
          <div className="flex items-center mt-1 space-x-2">
            <p className="text-xs text-gray-500">
              <time dateTime={conversation.updated_at}>
                {formatDate(conversation.updated_at)}
              </time>
            </p>
            {conversation.message_count !== undefined && (
              <>
                <span className="text-xs text-gray-400" aria-hidden="true">•</span>
                <p className="text-xs text-gray-500">
                  {conversation.message_count} message{conversation.message_count !== 1 ? 's' : ''}
                </p>
              </>
            )}
          </div>
        </div>
        {isActive && (
          <div className="ml-2 flex-shrink-0" aria-hidden="true">
            <div className="h-2 w-2 rounded-full bg-blue-600"></div>
          </div>
        )}
      </div>
    </button>
  );
});
