/**
 * ChatClient - Authenticated API client for chat operations
 *
 * Provides methods for interacting with the chat backend API with
 * JWT authentication and error handling.
 */

import {
  ChatRequest,
  ChatResponse,
  ConversationListResponse,
  MessageHistoryResponse,
  ChatClientConfig,
  AuthenticationError,
  NetworkError,
  ChatError,
  StreamingCallbacks,
} from '@/types/chat';

/**
 * Decode JWT token to extract user_id
 * Note: This is a simple base64 decode, not cryptographic verification
 */
function decodeJWT(token: string): { user_id: string } {
  try {
    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));
    return { user_id: decoded.sub || decoded.user_id };
  } catch (error) {
    throw new AuthenticationError('Invalid JWT token format');
  }
}

/**
 * ChatClient class for all chat-related API operations
 */
export class ChatClient {
  private baseUrl: string;
  private getToken: () => Promise<string | null>;

  constructor(config: ChatClientConfig) {
    this.baseUrl = config.baseUrl;
    this.getToken = config.getToken;
  }

  /**
   * Get user ID from JWT token
   */
  private async getUserId(): Promise<string> {
    const token = await this.getToken();
    if (!token) {
      throw new AuthenticationError('No authentication token available');
    }
    const { user_id } = decodeJWT(token);
    return user_id;
  }

  /**
   * Make authenticated request with error handling
   */
  private async authenticatedFetch(
    url: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const token = await this.getToken();
    if (!token) {
      throw new AuthenticationError('No authentication token available');
    }

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
        ...options.headers,
      },
    });

    // Handle authentication errors
    if (response.status === 401) {
      throw new AuthenticationError();
    }

    // Handle other HTTP errors
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      throw new ChatError(
        `HTTP ${response.status}: ${errorText}`,
        'HTTP_ERROR',
        response.status
      );
    }

    return response;
  }

  /**
   * Send a chat message (non-streaming)
   */
  async sendMessage(
    message: string,
    conversationId?: number | null
  ): Promise<ChatResponse> {
    try {
      const userId = await this.getUserId();
      const url = `${this.baseUrl}/api/${userId}/chat`;

      const body: ChatRequest = {
        message,
        conversation_id: conversationId,
      };

      const response = await this.authenticatedFetch(url, {
        method: 'POST',
        body: JSON.stringify(body),
      });

      return await response.json();
    } catch (error) {
      if (error instanceof ChatError) {
        throw error;
      }
      throw new NetworkError(
        error instanceof Error ? error.message : 'Failed to send message'
      );
    }
  }

  /**
   * Stream a chat message with callbacks
   */
  async streamMessage(
    message: string,
    conversationId: number | null,
    callbacks: StreamingCallbacks
  ): Promise<void> {
    try {
      const userId = await this.getUserId();
      const url = `${this.baseUrl}/api/${userId}/chat/stream`;

      const body: ChatRequest = {
        message,
        conversation_id: conversationId,
      };

      const response = await this.authenticatedFetch(url, {
        method: 'POST',
        body: JSON.stringify(body),
      });

      // Process streaming response
      const reader = response.body?.getReader();
      if (!reader) {
        throw new ChatError('Response body is not readable');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Process complete lines (NDJSON format)
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            const chunk = JSON.parse(line);

            switch (chunk.type) {
              case 'token':
                callbacks.onToken(chunk.content);
                break;

              case 'tool_call':
                callbacks.onToolCall(chunk.data);
                break;

              case 'done':
                callbacks.onComplete(chunk.conversation_id, chunk.message_id);
                break;

              case 'error':
                callbacks.onError(
                  new ChatError(chunk.message, chunk.code)
                );
                break;

              default:
                console.warn('Unknown chunk type:', chunk);
            }
          } catch (parseError) {
            console.error('Failed to parse chunk:', line, parseError);
          }
        }
      }
    } catch (error) {
      if (error instanceof ChatError) {
        callbacks.onError(error);
        throw error;
      }
      const networkError = new NetworkError(
        error instanceof Error ? error.message : 'Stream failed'
      );
      callbacks.onError(networkError);
      throw networkError;
    }
  }

  /**
   * Get list of user's conversations
   */
  async getConversations(): Promise<ConversationListResponse> {
    try {
      const userId = await this.getUserId();
      const url = `${this.baseUrl}/api/${userId}/conversations`;

      const response = await this.authenticatedFetch(url, {
        method: 'GET',
      });

      return await response.json();
    } catch (error) {
      if (error instanceof ChatError) {
        throw error;
      }
      throw new NetworkError(
        error instanceof Error
          ? error.message
          : 'Failed to fetch conversations'
      );
    }
  }

  /**
   * Get message history for a conversation
   */
  async getMessages(
    conversationId: number,
    limit: number = 100,
    offset: number = 0
  ): Promise<MessageHistoryResponse> {
    try {
      const userId = await this.getUserId();
      const url = `${this.baseUrl}/api/${userId}/conversations/${conversationId}/messages?limit=${limit}&offset=${offset}`;

      const response = await this.authenticatedFetch(url, {
        method: 'GET',
      });

      return await response.json();
    } catch (error) {
      if (error instanceof ChatError) {
        throw error;
      }
      throw new NetworkError(
        error instanceof Error ? error.message : 'Failed to fetch messages'
      );
    }
  }

  /**
   * Create a new conversation (implicitly by sending first message)
   * This is a convenience method that sends a message with no conversation_id
   */
  async createConversation(firstMessage: string): Promise<ChatResponse> {
    return this.sendMessage(firstMessage, null);
  }
}

/**
 * Create a ChatClient instance with configuration
 */
export function createChatClient(config: ChatClientConfig): ChatClient {
  return new ChatClient(config);
}
