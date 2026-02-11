'use client';

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useChat } from '@/lib/hooks/useChat';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';
import { ErrorRetry } from './ErrorRetry';
import { useTaskRefresh } from '@/context/TaskRefreshContext';

interface ChatWidgetProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * Chat Widget - Inline chat interface that appears as a popup
 *
 * A compact chat interface that overlays the current page without navigation.
 * Provides full chat functionality in a modal-style widget.
 */
export function ChatWidget({ isOpen, onClose }: ChatWidgetProps) {
  const { user, getToken } = useAuth();
  const { refreshTasks } = useTaskRefresh();
  const [conversationId, setConversationId] = useState<number | null>(() => {
    // Load conversation ID from localStorage on mount
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('chat_conversation_id');
      const id = stored ? parseInt(stored, 10) : null;
      console.log('[ChatWidget] Initializing conversationId from localStorage:', id);
      return id;
    }
    return null;
  });

  const {
    messages,
    streamingMessage,
    isStreaming,
    isSending,
    error,
    sendMessage,
    clearError,
  } = useChat(conversationId);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Debug: Log when conversationId or messages change
  useEffect(() => {
    console.log('[ChatWidget] State update:', { conversationId, messagesCount: messages.length });
  }, [conversationId, messages.length]);

  // Save conversation ID to localStorage when it changes
  useEffect(() => {
    if (conversationId !== null) {
      localStorage.setItem('chat_conversation_id', conversationId.toString());
    }
  }, [conversationId]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [messages, streamingMessage]);

  const handleSendMessage = async (content: string) => {
    if (!user?.id) return;

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Authentication required');
      }

      console.log('[ChatWidget] Sending message, current conversationId:', conversationId);

      // Send message and get the conversation ID back
      const result = await sendMessage(content);

      console.log('[ChatWidget] Message sent, result:', result);

      // Update conversation ID if this was the first message
      if (result?.conversationId && !conversationId) {
        console.log('[ChatWidget] Setting conversationId to:', result.conversationId);
        setConversationId(result.conversationId);
        // Save immediately to localStorage to ensure persistence
        localStorage.setItem('chat_conversation_id', result.conversationId.toString());
        console.log('[ChatWidget] Saved conversationId to localStorage');
      } else if (result?.conversationId) {
        console.log('[ChatWidget] ConversationId already set, not updating');
      } else {
        console.warn('[ChatWidget] No conversationId in result!');
      }

      // Refresh tasks after message completes (in case AI performed task operations)
      // Wait longer for the backend to complete the operation
      console.log('Chat message completed, scheduling task refresh in 2 seconds...');
      setTimeout(() => {
        console.log('Triggering task refresh now...');
        refreshTasks();
      }, 2000);
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  const handleClearConversation = () => {
    console.log('Clear conversation clicked!');

    // Show confirmation dialog
    const confirmed = window.confirm(
      'Are you sure you want to clear this conversation?\n\nThis will delete all messages and cannot be undone.'
    );

    if (!confirmed) {
      console.log('Clear conversation cancelled');
      return;
    }

    console.log('Clear conversation confirmed');
    // Clear conversation ID from state and localStorage
    setConversationId(null);
    localStorage.removeItem('chat_conversation_id');
    // Messages will be cleared automatically when conversationId becomes null
  };

  // Debug: Log messages length
  useEffect(() => {
    console.log('Messages count:', messages.length);
  }, [messages]);

  if (!isOpen) return null;

  return (
    <>
      <style jsx>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(20px) scale(0.95);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes shimmerHeader {
          0% {
            background-position: -200% center;
          }
          100% {
            background-position: 200% center;
          }
        }

        .chat-widget-enter {
          animation: slideInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .backdrop-enter {
          animation: fadeIn 0.3s ease-out;
        }

        .header-shimmer {
          background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(255, 255, 255, 0.1) 50%,
            transparent 100%
          );
          background-size: 200% 100%;
          animation: shimmerHeader 3s infinite;
        }

        /* Custom Scrollbar Styles */
        :global(.custom-scrollbar::-webkit-scrollbar) {
          width: 8px;
        }

        :global(.custom-scrollbar::-webkit-scrollbar-track) {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 10px;
          margin: 4px 0;
        }

        :global(.custom-scrollbar::-webkit-scrollbar-thumb) {
          background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
          border-radius: 10px;
          box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
          transition: all 0.3s ease;
        }

        :global(.custom-scrollbar::-webkit-scrollbar-thumb:hover) {
          background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
          box-shadow: 0 0 15px rgba(59, 130, 246, 0.8), 0 0 25px rgba(139, 92, 246, 0.4);
          transform: scaleX(1.2);
        }

        :global(.custom-scrollbar::-webkit-scrollbar-thumb:active) {
          background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
          box-shadow: 0 0 20px rgba(59, 130, 246, 1);
        }

        /* Firefox scrollbar styling */
        :global(.custom-scrollbar) {
          scrollbar-width: thin;
          scrollbar-color: #3b82f6 rgba(255, 255, 255, 0.05);
        }
      `}</style>

      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/30 backdrop-blur-md z-40 backdrop-enter"
        onClick={onClose}
      />

      {/* Chat Widget */}
      <div className="fixed bottom-24 right-6 w-[calc(100vw-3rem)] sm:w-96 max-w-[90vw] h-[600px] max-h-[80vh] bg-[var(--soft-dark-bg)]/95 backdrop-blur-xl border border-[var(--glass-border)] rounded-2xl shadow-2xl z-50 flex flex-col overflow-hidden chat-widget-enter"
           style={{
             boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1)'
           }}>
        {/* Header */}
        <div className="relative flex items-center justify-between p-4 border-b border-[var(--glass-border)] bg-gradient-to-r from-[var(--primary-accent)]/10 to-[var(--primary-accent-end)]/10 overflow-hidden">
          {/* Animated shimmer overlay */}
          <div className="absolute inset-0 header-shimmer pointer-events-none" />

          <div className="flex items-center space-x-3 relative z-10">
            {/* Animated AI Avatar */}
            <div className="relative">
              {/* Pulsing glow ring */}
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] opacity-30 blur-md animate-pulse" />

              {/* Avatar circle */}
              <div className="relative w-10 h-10 rounded-full bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] flex items-center justify-center shadow-lg"
                   style={{
                     animation: 'breathe 2s ease-in-out infinite',
                     boxShadow: '0 0 20px rgba(59, 130, 246, 0.5)'
                   }}>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-[var(--text-primary)]">
                AI Assistant
              </h3>
              <p className="text-xs text-[var(--text-secondary)] flex items-center space-x-1">
                {isStreaming ? (
                  <>
                    <span className="inline-block w-2 h-2 bg-[var(--primary-accent)] rounded-full animate-pulse" />
                    <span>Typing...</span>
                  </>
                ) : (
                  <>
                    <span className="inline-block w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    <span>Online</span>
                  </>
                )}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Clear conversation button */}
            {messages.length > 0 && (
              <button
                onClick={handleClearConversation}
                className="p-2 hover:bg-[var(--soft-dark-bg-secondary)] rounded-lg transition-colors cursor-pointer relative z-10"
                aria-label="Clear conversation"
                title="Start new conversation"
                type="button"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 text-[var(--text-secondary)] pointer-events-none"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            )}

            {/* Close button */}
            <button
              onClick={onClose}
              className="p-2 hover:bg-[var(--soft-dark-bg-secondary)] rounded-lg transition-colors"
              aria-label="Close chat"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 text-[var(--text-secondary)]"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-3 border-b border-[var(--glass-border)]">
            <ErrorRetry
              error={error}
              onRetry={() => {
                clearError();
                // Retry last message if needed
              }}
              onDismiss={clearError}
            />
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth custom-scrollbar" style={{ scrollBehavior: 'smooth' }}>
          {messages.length === 0 && !isStreaming && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 rounded-full bg-gradient-to-r from-[var(--primary-accent)]/20 to-[var(--primary-accent-end)]/20 flex items-center justify-center mb-4">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-8 w-8 text-[var(--primary-accent)]"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
              <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-2">
                Start a conversation
              </h4>
              <p className="text-xs text-[var(--text-secondary)]">
                Ask me anything or try managing your tasks
              </p>
            </div>
          )}

          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {/* Streaming message with typewriter effect */}
          {isStreaming && streamingMessage && (
            <div className="flex w-full mb-4 justify-start">
              <div className="max-w-[80%] rounded-lg px-4 py-3 bg-white text-gray-900 border border-gray-200">
                <div className="text-sm leading-relaxed whitespace-pre-wrap inline">
                  {streamingMessage}
                  <span className="inline-block w-0.5 h-4 bg-blue-600 ml-1 animate-pulse align-middle"></span>
                </div>
              </div>
            </div>
          )}

          {/* Typing indicator */}
          {isStreaming && !streamingMessage && (
            <TypingIndicator />
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-[var(--glass-border)] p-4 bg-[var(--soft-dark-bg-secondary)]">
          <ChatInput
            onSend={handleSendMessage}
            disabled={isStreaming || isSending}
          />
        </div>
      </div>
    </>
  );
}
