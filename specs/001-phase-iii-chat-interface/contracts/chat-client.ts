/**
 * Chat API Client Interface
 *
 * TypeScript interface for frontend-backend communication.
 * Provides type-safe methods for chat streaming, conversation management,
 * and message history retrieval.
 */

// ============================================================================
// Types
// ============================================================================

export interface Conversation {
  id: number;
  created_at: string;
  updated_at: string;
  preview: string;
  message_count: number;
}

export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  tool_calls: ToolCall[] | null;
  created_at: string;
}

export interface ToolCall {
  tool_name: string;
  input_parameters: Record<string, any>;
  output_result: Record<string, any>;
  execution_status: 'success' | 'error';
  error_message: string | null;
  timestamp: string;
}

export interface StreamChunk {
  type: 'token' | 'tool_call' | 'done';
  content?: string;
  data?: ToolCallData;
  conversation_id?: number;
}

export interface ToolCallData {
  tool_name: string;
  status: 'pending' | 'success' | 'error';
  input_parameters?: Record<string, any>;
  output_result?: Record<string, any>;
  error_message?: string | null;
  timestamp?: string;
}

export interface StreamCallbacks {
  onToken: (token: string) => void;
  onToolCall: (toolCall: ToolCallData) => void;
  onComplete: (conversationId: number) => void;
  onError: (error: Error) => void;
}

export interface ChatClientConfig {
  baseUrl: string;
  getToken: () => Promise<string>;
}

// ============================================================================
// Chat Client Interface
// ============================================================================

export interface IChatClient {
  /**
   * Stream a chat message and receive real-time response
   *
   * @param message - User's message text
   * @param conversationId - Optional conversation ID to resume (null for new)
   * @param callbacks - Callbacks for streaming events
   * @returns Promise that resolves when stream completes
   */
  streamMessage(
    message: string,
    conversationId: number | null,
    callbacks: StreamCallbacks
  ): Promise<void>;

  /**
   * Get list of user's conversations
   *
   * @param userId - User ID
   * @param limit - Maximum conversations to return (default: 100)
   * @param offset - Pagination offset (default: 0)
   * @returns Promise with conversation list
   */
  getConversations(
    userId: string,
    limit?: number,
    offset?: number
  ): Promise<Conversation[]>;

  /**
   * Get message history for a conversation
   *
   * @param userId - User ID
   * @param conversationId - Conversation ID
   * @param limit - Maximum messages to return (default: 100)
   * @param offset - Pagination offset (default: 0)
   * @returns Promise with message list
   */
  getMessages(
    userId: string,
    conversationId: number,
    limit?: number,
    offset?: number
  ): Promise<Message[]>;
}

// ============================================================================
// Chat Client Implementation
// ============================================================================

export class ChatClient implements IChatClient {
  private baseUrl: string;
  private getToken: () => Promise<string>;

  constructor(config: ChatClientConfig) {
    this.baseUrl = config.baseUrl;
    this.getToken = config.getToken;
  }

  /**
   * Extract user ID from JWT token
   */
  private getUserIdFromToken(token: string): string {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.sub || payload.user_id;
    } catch (error) {
      throw new Error('Invalid JWT token');
    }
  }

  /**
   * Stream a chat message
   */
  async streamMessage(
    message: string,
    conversationId: number | null,
    callbacks: StreamCallbacks
  ): Promise<void> {
    const token = await this.getToken();
    const userId = this.getUserIdFromToken(token);

    const response = await fetch(`${this.baseUrl}/api/${userId}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId
      })
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Authentication expired. Please log in again.');
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Response body is not readable');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            const chunk: StreamChunk = JSON.parse(line);

            if (chunk.type === 'token' && chunk.content) {
              callbacks.onToken(chunk.content);
            } else if (chunk.type === 'tool_call' && chunk.data) {
              callbacks.onToolCall(chunk.data);
            } else if (chunk.type === 'done' && chunk.conversation_id) {
              callbacks.onComplete(chunk.conversation_id);
            }
          } catch (parseError) {
            console.error('Failed to parse chunk:', line, parseError);
          }
        }
      }
    } catch (error) {
      callbacks.onError(error as Error);
      throw error;
    }
  }

  /**
   * Get list of conversations
   */
  async getConversations(
    userId: string,
    limit: number = 100,
    offset: number = 0
  ): Promise<Conversation[]> {
    const token = await this.getToken();

    const response = await fetch(
      `${this.baseUrl}/api/${userId}/conversations?limit=${limit}&offset=${offset}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Authentication expired. Please log in again.');
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return data.conversations;
  }

  /**
   * Get message history
   */
  async getMessages(
    userId: string,
    conversationId: number,
    limit: number = 100,
    offset: number = 0
  ): Promise<Message[]> {
    const token = await this.getToken();

    const response = await fetch(
      `${this.baseUrl}/api/${userId}/conversations/${conversationId}/messages?limit=${limit}&offset=${offset}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Authentication expired. Please log in again.');
      }
      if (response.status === 403) {
        throw new Error('You do not have access to this conversation.');
      }
      if (response.status === 404) {
        throw new Error('Conversation not found.');
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return data.messages;
  }
}

// ============================================================================
// Usage Example
// ============================================================================

/**
 * Example usage in a React component:
 *
 * ```typescript
 * import { ChatClient } from '@/lib/api/chat-client';
 * import { useAuth } from '@/lib/hooks/useAuth';
 *
 * function ChatComponent() {
 *   const { getToken } = useAuth();
 *   const chatClient = new ChatClient({
 *     baseUrl: process.env.NEXT_PUBLIC_API_URL,
 *     getToken
 *   });
 *
 *   async function sendMessage(message: string) {
 *     await chatClient.streamMessage(message, null, {
 *       onToken: (token) => console.log('Token:', token),
 *       onToolCall: (toolCall) => console.log('Tool call:', toolCall),
 *       onComplete: (conversationId) => console.log('Done:', conversationId),
 *       onError: (error) => console.error('Error:', error)
 *     });
 *   }
 *
 *   return <div>...</div>;
 * }
 * ```
 */
