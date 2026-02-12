/**
 * ConversationSidebar Component
 *
 * Sidebar displaying conversation list with new chat button.
 * Handles conversation selection and creation.
 */

'use client';

import { ConversationItem } from './ConversationItem';
import { NewChatButton } from './NewChatButton';
import { useConversations } from '@/lib/hooks/useConversations';

interface ConversationSidebarProps {
  activeId: number | null;
  onSelect: (id: number) => void;
  onNewChat: () => void;
}

/**
 * ConversationSidebar component
 */
export function ConversationSidebar({
  activeId,
  onSelect,
  onNewChat,
}: ConversationSidebarProps) {
  const { conversations, isLoading, error } = useConversations();

  return (
    <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">
          Conversations
        </h2>
        <NewChatButton onClick={onNewChat} />
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600"></div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {!isLoading && !error && conversations.length === 0 && (
          <div className="text-center py-8">
            <p className="text-sm text-gray-500">No conversations yet</p>
            <p className="text-xs text-gray-400 mt-1">
              Start a new chat to begin
            </p>
          </div>
        )}

        {!isLoading &&
          !error &&
          conversations.map((conversation) => (
            <ConversationItem
              key={conversation.id}
              conversation={conversation}
              isActive={conversation.id === activeId}
              onClick={() => onSelect(conversation.id)}
            />
          ))}
      </div>
    </div>
  );
}
