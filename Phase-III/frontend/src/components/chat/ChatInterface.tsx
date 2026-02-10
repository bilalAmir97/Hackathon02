/**
 * ChatInterface Component
 *
 * Main chat interface that composes ConversationSidebar, MessageList, and ChatInput.
 * Manages the active conversation and message flow.
 * Responsive design with collapsible sidebar on mobile.
 */

'use client';

import { useState } from 'react';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { ConversationSidebar } from './ConversationSidebar';
import { useChat } from '@/lib/hooks/useChat';
import { useConversations } from '@/lib/hooks/useConversations';

/**
 * ChatInterface component - main chat container
 */
export function ChatInterface() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const {
    conversations,
    activeConversationId,
    selectConversation,
    createNewConversation,
    refreshConversations,
  } = useConversations();

  const {
    messages,
    streamingMessage,
    isStreaming,
    isSending,
    error,
    sendMessage,
    clearError,
    retry,
  } = useChat(activeConversationId);

  // Handle new chat creation
  const handleNewChat = () => {
    createNewConversation();
    setIsSidebarOpen(false); // Close sidebar on mobile after creating new chat
  };

  // Handle conversation selection
  const handleSelectConversation = (id: number) => {
    selectConversation(id);
    setIsSidebarOpen(false); // Close sidebar on mobile after selecting conversation
  };

  // Handle message send with conversation refresh
  const handleSendMessage = async (content: string) => {
    await sendMessage(content);
    // Refresh conversations list after sending a message
    // This ensures new conversations appear in the sidebar
    await refreshConversations();
  };

  return (
    <div className="flex h-full relative">
      {/* Mobile menu button */}
      <button
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-lg border border-gray-200 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-label="Toggle conversation list"
      >
        <svg
          className="h-6 w-6 text-gray-700"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          {isSidebarOpen ? (
            <path d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {/* Conversation Sidebar - Desktop: always visible, Mobile: overlay */}
      <div
        className={`
          fixed lg:relative inset-y-0 left-0 z-40
          transform transition-transform duration-300 ease-in-out
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <ConversationSidebar
          activeId={activeConversationId}
          onSelect={handleSelectConversation}
          onNewChat={handleNewChat}
        />
      </div>

      {/* Overlay for mobile when sidebar is open */}
      {isSidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={() => setIsSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Chat Area */}
      <div className="flex-1 flex flex-col w-full lg:w-auto">
        {/* Error banner */}
        {error && (
          <div className="bg-red-50 border-b border-red-200 px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <svg
                  className="h-5 w-5 text-red-600 flex-shrink-0"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm text-red-800">{error}</p>
              </div>
              <div className="flex items-center space-x-2 flex-shrink-0">
                <button
                  onClick={retry}
                  className="text-sm text-red-600 hover:text-red-800 font-medium"
                >
                  Retry
                </button>
                <button
                  onClick={clearError}
                  className="text-sm text-red-600 hover:text-red-800"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Message list */}
        <MessageList
          messages={messages}
          streamingMessage={streamingMessage}
          isStreaming={isStreaming}
        />

        {/* Chat input */}
        <ChatInput onSend={handleSendMessage} disabled={isSending || isStreaming} />
      </div>
    </div>
  );
}
