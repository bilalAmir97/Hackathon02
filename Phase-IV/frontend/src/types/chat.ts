/**
 * Chat types for Phase-III AI Chat Interface
 *
 * These types define the structure of conversations, messages, and streaming
 * responses based on the API contracts defined in the specification.
 */

/**
 * Tool call execution details for transparency
 */
export interface ToolCall {
  tool_name: string;
  input_parameters: Record<string, unknown>;
  output_result: Record<string, unknown> | null;
  execution_status: 'pending' | 'success' | 'error';
  error_message?: string | null;
  timestamp: string;
}

/**
 * Message in a conversation
 */
export interface Message {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant';
  content: string;
  tool_calls: ToolCall[] | null;
  created_at: string;
}

/**
 * Conversation metadata
 */
export interface Conversation {
  id: number;
  user_id: string;
  created_at: string;
  updated_at: string;
  preview?: string;
  message_count?: number;
}

/**
 * Streaming chunk types from backend
 */
export type StreamChunkType = 'token' | 'tool_call' | 'done' | 'error';

/**
 * Token chunk during streaming
 */
export interface TokenChunk {
  type: 'token';
  content: string;
}

/**
 * Tool call chunk during streaming
 */
export interface ToolCallChunk {
  type: 'tool_call';
  data: ToolCall;
}

/**
 * Done chunk signaling stream completion
 */
export interface DoneChunk {
  type: 'done';
  conversation_id: number;
  message_id?: number;
}

/**
 * Error chunk during streaming
 */
export interface ErrorChunk {
  type: 'error';
  message: string;
  code?: string;
}

/**
 * Union type for all streaming chunks
 */
export type StreamChunk = TokenChunk | ToolCallChunk | DoneChunk | ErrorChunk;

/**
 * Chat request payload
 */
export interface ChatRequest {
  message: string;
  conversation_id?: number | null;
}

/**
 * Chat response (non-streaming)
 */
export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: ToolCall[];
}

/**
 * Conversation list response
 */
export interface ConversationListResponse {
  conversations: Conversation[];
}

/**
 * Message history response
 */
export interface MessageHistoryResponse {
  conversation_id: number;
  messages: Message[];
}

/**
 * Streaming callbacks for handling different chunk types
 */
export interface StreamingCallbacks {
  onToken: (token: string) => void;
  onToolCall: (toolCall: ToolCall) => void;
  onComplete: (conversationId: number, messageId?: number) => void;
  onError: (error: Error) => void;
}

/**
 * Chat client configuration
 */
export interface ChatClientConfig {
  baseUrl: string;
  getToken: () => Promise<string | null>;
}

/**
 * Error types for chat operations
 */
export class ChatError extends Error {
  constructor(
    message: string,
    public code?: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = 'ChatError';
  }
}

export class AuthenticationError extends ChatError {
  constructor(message: string = 'Authentication expired. Please log in again.') {
    super(message, 'AUTH_EXPIRED', 401);
    this.name = 'AuthenticationError';
  }
}

export class NetworkError extends ChatError {
  constructor(message: string = 'Network error. Please check your connection.') {
    super(message, 'NETWORK_ERROR');
    this.name = 'NetworkError';
  }
}

export class StreamInterruptedError extends ChatError {
  constructor(message: string = 'Stream was interrupted. Please retry.') {
    super(message, 'STREAM_INTERRUPTED');
    this.name = 'StreamInterruptedError';
  }
}
