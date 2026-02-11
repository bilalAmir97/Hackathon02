/**
 * ChatInterface Component
 *
 * Clean grid-based chat interface with proper layout.
 * Uses CSS Grid for desktop layout, overlay sidebar for mobile.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { ConversationSidebar } from './ConversationSidebar';
import { useChat } from '@/lib/hooks/useChat';
import { useConversations } from '@/lib/hooks/useConversations';

/**
 * ChatInterface component - grid-based layout
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

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        handleNewChat();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleNewChat = useCallback(() => {
    createNewConversation();
    setIsSidebarOpen(false);
  }, [createNewConversation]);

  const handleSelectConversation = useCallback((id: number) => {
    selectConversation(id);
    setIsSidebarOpen(false);
  }, [selectConversation]);

  const handleSendMessage = useCallback(async (content: string) => {
    const result = await sendMessage(content);
    if (result) {
      await refreshConversations();
    }
  }, [sendMessage, refreshConversations]);

  return (
    <div className="grid lg:grid-cols-[320px_1fr] h-screen w-full bg-[var(--soft-dark-bg)] overflow-hidden">
      {/* Mobile menu button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-3 bg-[var(--glass-bg)] backdrop-blur-xl rounded-xl shadow-lg border border-[var(--glass-border)] hover:border-[var(--primary-accent)]/50 focus:outline-none focus:ring-2 focus:ring-[var(--primary-accent)] transition-all"
        aria-label="Toggle conversation list"
      >
        <svg
          className="h-5 w-5 text-[var(--text-primary)]"
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
      </motion.button>

      {/* Desktop Sidebar - Grid handles width */}
      <div className="hidden lg:block">
        <ConversationSidebar
          activeId={activeConversationId}
          onSelect={handleSelectConversation}
          onNewChat={handleNewChat}
        />
      </div>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {isSidebarOpen && (
          <>
            <motion.div
              initial={{ x: -320 }}
              animate={{ x: 0 }}
              exit={{ x: -320 }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="fixed inset-y-0 left-0 z-40 w-80"
            >
              <ConversationSidebar
                activeId={activeConversationId}
                onSelect={handleSelectConversation}
                onNewChat={handleNewChat}
              />
            </motion.div>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30"
              onClick={() => setIsSidebarOpen(false)}
              aria-hidden="true"
            />
          </>
        )}
      </AnimatePresence>

      {/* Chat Area - Grid handles width automatically */}
      <div className="flex flex-col overflow-hidden">
        {/* Error banner */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ y: -100, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: -100, opacity: 0 }}
              className="bg-red-500/10 border-b border-red-500/20 backdrop-blur-xl px-4 md:px-6 py-3"
            >
              <div className="max-w-4xl mx-auto flex items-center justify-between gap-4">
                <div className="flex items-center gap-3 min-w-0">
                  <svg
                    className="h-5 w-5 text-red-400 flex-shrink-0"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-sm text-red-300 truncate">{error}</p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    onClick={retry}
                    className="text-sm text-red-300 hover:text-red-200 font-medium px-3 py-1 rounded-lg hover:bg-red-500/10 transition-colors"
                  >
                    Retry
                  </button>
                  <button
                    onClick={clearError}
                    className="text-sm text-red-300 hover:text-red-200 p-1 rounded-lg hover:bg-red-500/10 transition-colors"
                    aria-label="Dismiss error"
                  >
                    <svg className="w-4 h-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Message list */}
        <MessageList
          messages={messages}
          streamingMessage={streamingMessage}
          isStreaming={isStreaming}
          onSendMessage={handleSendMessage}
          onRegenerate={retry}
        />

        {/* Chat input */}
        <ChatInput onSend={handleSendMessage} disabled={isSending || isStreaming} />
      </div>
    </div>
  );
}
