/**
 * useChat Hook
 *
 * Main state management hook for chat functionality.
 * Manages messages, streaming, sending, and error handling.
 */

'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { Message, ChatError, AuthenticationError, ToolCall } from '@/types/chat';
import { ChatClient, createChatClient } from '@/lib/api/chat-client';
import { useAuth } from '@/hooks/useAuth';
import { useStreaming } from './useStreaming';

interface UseChatReturn {
  messages: Message[];
  streamingMessage: string;
  isStreaming: boolean;
  isSending: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<{ conversationId: number } | void>;
  clearError: () => void;
  retry: () => Promise<void>;
}

/**
 * useChat hook for managing chat state and operations
 */
export function useChat(conversationId: number | null): UseChatReturn {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  const [chatClient, setChatClient] = useState<ChatClient | null>(null);

  const {
    streamingMessage,
    isStreaming,
    toolCalls,
    startStreaming,
    stopStreaming,
    appendToken,
    addToolCall,
    reset: resetStreaming,
  } = useStreaming();

  // Use ref to capture current streaming message for onComplete callback
  const streamingMessageRef = useRef<string>('');
  const toolCallsRef = useRef<ToolCall[]>([]);

  // Update refs when streaming state changes
  useEffect(() => {
    streamingMessageRef.current = streamingMessage;
    toolCallsRef.current = toolCalls;
  }, [streamingMessage, toolCalls]);

  // Initialize chat client
  useEffect(() => {
    const client = createChatClient({
      baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      getToken,
    });
    setChatClient(client);
  }, [getToken]);

  /**
   * Load conversation messages
   */
  useEffect(() => {
    if (conversationId && chatClient) {
      console.log('[useChat] Effect triggered - loading messages for conversation:', conversationId);
      loadMessages();
    } else if (conversationId === null) {
      // Clear messages when conversation ID is explicitly set to null
      console.log('[useChat] Conversation ID is null, clearing messages');
      setMessages([]);

      // Clear all conversation caches
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith('chat_messages_')) {
          localStorage.removeItem(key);
        }
      });
      console.log('[useChat] Cleared conversation cache');
    } else {
      console.log('[useChat] Waiting for chatClient or conversationId', { conversationId, hasChatClient: !!chatClient });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [conversationId, chatClient]);

  /**
   * Load messages for current conversation
   */
  const loadMessages = useCallback(async () => {
    if (!conversationId || !chatClient) return;

    // Try to load from cache first for instant display
    const cacheKey = `chat_messages_${conversationId}`;
    const cachedData = localStorage.getItem(cacheKey);

    if (cachedData) {
      try {
        const cached = JSON.parse(cachedData);
        // Show cached messages immediately
        setMessages(cached.messages);
        console.log('[useChat] Loaded messages from cache instantly');
      } catch (err) {
        console.error('Failed to parse cached messages:', err);
      }
    }

    // Fetch fresh messages in the background
    try {
      const response = await chatClient.getMessages(conversationId);
      setMessages(response.messages);

      // Update cache with fresh data
      localStorage.setItem(cacheKey, JSON.stringify({
        messages: response.messages,
        timestamp: Date.now()
      }));
      console.log('[useChat] Loaded fresh messages from API');
    } catch (err) {
      console.error('Failed to load messages:', err);
      // Only show error if we don't have cached data
      if (!cachedData) {
        setError('Failed to load conversation history');
      }
    }
  }, [conversationId, chatClient]);

  /**
   * Send a message
   */
  const sendMessage = useCallback(
    async (content: string): Promise<{ conversationId: number } | void> => {
      if (!chatClient || isSending) return;

      setIsSending(true);
      setError(null);
      setLastMessage(content);

      // Optimistic update: add user message immediately
      const optimisticMessage: Message = {
        id: Date.now(), // Temporary ID
        conversation_id: conversationId || -1,
        role: 'user',
        content,
        tool_calls: null,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, optimisticMessage]);

      return new Promise((resolve, reject) => {
        (async () => {
          try {
            // Start streaming
            startStreaming();

            // Stream the response
            await chatClient.streamMessage(content, conversationId, {
              onToken: (token) => {
                appendToken(token);
              },
              onToolCall: (toolCall) => {
                addToolCall(toolCall);
              },
              onComplete: (newConversationId, messageId) => {
                // Stop streaming
                stopStreaming();

                // Use ref to get current streaming message value
                const finalMessage = streamingMessageRef.current;
                const finalToolCalls = toolCallsRef.current;

                // Create assistant message from streaming buffer
                const assistantMessage: Message = {
                  id: messageId || Date.now() + 1,
                  conversation_id: newConversationId,
                  role: 'assistant',
                  content: finalMessage,
                  tool_calls: finalToolCalls.length > 0 ? finalToolCalls : null,
                  created_at: new Date().toISOString(),
                };

                // Replace optimistic message with server response
                setMessages((prev) => {
                  // Remove optimistic message
                  const filtered = prev.filter((m) => m.id !== optimisticMessage.id);
                  // Add both user and assistant messages
                  const updatedMessages = [...filtered, optimisticMessage, assistantMessage];

                  // Update cache with new messages
                  const cacheKey = `chat_messages_${newConversationId}`;
                  localStorage.setItem(cacheKey, JSON.stringify({
                    messages: updatedMessages,
                    timestamp: Date.now()
                  }));

                  return updatedMessages;
                });

                // Reset streaming state
                resetStreaming();
                setIsSending(false);

                // Resolve with the conversation ID
                resolve({ conversationId: newConversationId });
              },
              onError: (err) => {
                stopStreaming();
                resetStreaming();

                // Handle authentication errors
                if (err instanceof AuthenticationError) {
                  setError('Session expired. Please log in again.');
                  // Redirect to login after a delay
                  setTimeout(() => {
                    window.location.href = '/';
                  }, 2000);
                  reject(err);
                  return;
                }

                // Handle other errors
                setError(err.message || 'Failed to send message');

                // Rollback optimistic update
                setMessages((prev) => prev.filter((m) => m.id !== optimisticMessage.id));

                setIsSending(false);
                reject(err);
              },
            });
          } catch (err) {
            stopStreaming();
            resetStreaming();

            // Handle errors
            if (err instanceof AuthenticationError) {
              setError('Session expired. Please log in again.');
              setTimeout(() => {
                window.location.href = '/';
              }, 2000);
            } else if (err instanceof ChatError) {
              setError(err.message);
            } else {
              setError('Failed to send message. Please try again.');
            }

            // Rollback optimistic update
            setMessages((prev) => prev.filter((m) => m.id !== optimisticMessage.id));

            setIsSending(false);
            reject(err);
          }
        })();
      });
    },
    [
      chatClient,
      conversationId,
      isSending,
      startStreaming,
      stopStreaming,
      appendToken,
      addToolCall,
      resetStreaming,
      streamingMessage,
      toolCalls,
    ]
  );

  /**
   * Retry last message
   */
  const retry = useCallback(async () => {
    if (lastMessage) {
      await sendMessage(lastMessage);
    }
  }, [lastMessage, sendMessage]);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    messages,
    streamingMessage,
    isStreaming,
    isSending,
    error,
    sendMessage,
    clearError,
    retry,
  };
}
