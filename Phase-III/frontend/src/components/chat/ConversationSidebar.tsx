/**
 * ConversationSidebar Component
 *
 * Premium sidebar with glassmorphism displaying conversation list.
 * Features smooth animations and modern design.
 */

'use client';

import { motion } from 'framer-motion';
import { ConversationItem } from './ConversationItem';
import { NewChatButton } from './NewChatButton';
import { useConversations } from '@/lib/hooks/useConversations';

interface ConversationSidebarProps {
  activeId: number | null;
  onSelect: (id: number) => void;
  onNewChat: () => void;
}

/**
 * ConversationSidebar component with premium styling
 */
export function ConversationSidebar({
  activeId,
  onSelect,
  onNewChat,
}: ConversationSidebarProps) {
  const { conversations, isLoading, error } = useConversations();

  return (
    <div className="w-80 bg-[var(--soft-dark-bg)]/95 backdrop-blur-xl border-r border-[var(--glass-border)] flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-[var(--glass-border)]">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <svg
              className="w-5 h-5 text-[var(--primary-accent)]"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            Conversations
          </h2>
          <NewChatButton onClick={onNewChat} />
        </motion.div>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2 scrollbar-thin scrollbar-thumb-[var(--glass-border)] scrollbar-track-transparent">
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center justify-center py-12"
          >
            <div className="relative">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-[var(--glass-border)] border-t-[var(--primary-accent)]"></div>
              <div className="absolute inset-0 h-8 w-8 animate-ping rounded-full border-4 border-[var(--primary-accent)] opacity-20"></div>
            </div>
          </motion.div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 backdrop-blur-xl"
          >
            <div className="flex items-start gap-2">
              <svg
                className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-red-300">{error}</p>
            </div>
          </motion.div>
        )}

        {!isLoading && !error && conversations.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12 px-4"
          >
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--glass-bg)] backdrop-blur-xl border border-[var(--glass-border)] flex items-center justify-center">
              <svg
                className="w-8 h-8 text-[var(--text-secondary)]"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <p className="text-sm text-[var(--text-secondary)] mb-1">No conversations yet</p>
            <p className="text-xs text-[var(--text-secondary)]/70">
              Start a new chat to begin
            </p>
          </motion.div>
        )}

        {!isLoading &&
          !error &&
          conversations.map((conversation, index) => (
            <motion.div
              key={conversation.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2, delay: index * 0.05 }}
            >
              <ConversationItem
                conversation={conversation}
                isActive={conversation.id === activeId}
                onClick={() => onSelect(conversation.id)}
              />
            </motion.div>
          ))}
      </div>
    </div>
  );
}
