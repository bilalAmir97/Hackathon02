/**
 * useConversations Hook
 *
 * Manages conversation list state and operations.
 * Fetches conversations, creates new conversations, and handles selection.
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import { Conversation, ChatError } from '@/types/chat';
import { ChatClient, createChatClient } from '@/lib/api/chat-client';
import { useAuth } from '@/hooks/useAuth';

interface UseConversationsReturn {
  conversations: Conversation[];
  activeConversationId: number | null;
  isLoading: boolean;
  error: string | null;
  selectConversation: (id: number) => void;
  createNewConversation: () => void;
  refreshConversations: () => Promise<void>;
}

/**
 * useConversations hook for managing conversation list
 */
export function useConversations(): UseConversationsReturn {
  const { getToken } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chatClient, setChatClient] = useState<ChatClient | null>(null);

  // Initialize chat client
  useEffect(() => {
    const client = createChatClient({
      baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      getToken,
    });
    setChatClient(client);
  }, [getToken]);

  // Load conversations on mount
  useEffect(() => {
    if (chatClient) {
      loadConversations();
    }
  }, [chatClient]);

  /**
   * Load conversations from backend
   */
  const loadConversations = useCallback(async () => {
    if (!chatClient) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await chatClient.getConversations();
      setConversations(response.conversations);

      // If no active conversation and conversations exist, select the first one
      if (!activeConversationId && response.conversations.length > 0) {
        setActiveConversationId(response.conversations[0].id);
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
      if (err instanceof ChatError) {
        setError(err.message);
      } else {
        setError('Failed to load conversations');
      }
    } finally {
      setIsLoading(false);
    }
  }, [chatClient, activeConversationId]);

  /**
   * Select a conversation
   */
  const selectConversation = useCallback((id: number) => {
    setActiveConversationId(id);
  }, []);

  /**
   * Create a new conversation
   */
  const createNewConversation = useCallback(() => {
    // Set active conversation to null to start a new one
    setActiveConversationId(null);
  }, []);

  /**
   * Refresh conversations list
   */
  const refreshConversations = useCallback(async () => {
    await loadConversations();
  }, [loadConversations]);

  return {
    conversations,
    activeConversationId,
    isLoading,
    error,
    selectConversation,
    createNewConversation,
    refreshConversations,
  };
}
