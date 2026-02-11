/**
 * ConversationItem Component
 *
 * Premium conversation item with glassmorphism and smooth hover effects.
 * Shows conversation preview and handles selection.
 */

'use client';

import { memo } from 'react';
import { motion } from 'framer-motion';
import { Conversation } from '@/types/chat';

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onClick: () => void;
}

/**
 * ConversationItem component with premium styling
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
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`w-full text-left px-4 py-3 rounded-xl transition-all duration-200 ${
        isActive
          ? 'bg-[var(--glass-bg)] backdrop-blur-xl border border-[var(--primary-accent)]/50 shadow-lg'
          : 'hover:bg-[var(--glass-bg)] backdrop-blur-xl border border-transparent hover:border-[var(--glass-border)]'
      }`}
      aria-label={`${isActive ? 'Current conversation: ' : 'Switch to conversation: '}${conversation.preview || 'New conversation'}`}
      aria-current={isActive ? 'true' : 'false'}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p
            className={`text-sm font-medium truncate ${
              isActive ? 'text-[var(--primary-accent)]' : 'text-[var(--text-primary)]'
            }`}
          >
            {conversation.preview || 'New Conversation'}
          </p>
          <div className="flex items-center mt-1 gap-2 text-xs text-[var(--text-secondary)]">
            <time dateTime={conversation.updated_at}>
              {formatDate(conversation.updated_at)}
            </time>
            {conversation.message_count !== undefined && conversation.message_count > 0 && (
              <>
                <span aria-hidden="true">•</span>
                <span>{conversation.message_count} msg</span>
              </>
            )}
          </div>
        </div>
        {isActive && (
          <div className="flex-shrink-0 mt-1">
            <div className="h-2 w-2 rounded-full bg-[var(--primary-accent)] animate-pulse"></div>
          </div>
        )}
      </div>
    </motion.button>
  );
});
