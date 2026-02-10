/**
 * MessageBubble Component
 *
 * Displays a single message in the chat interface with role-based styling.
 * Supports user and assistant messages with timestamps and tool call transparency.
 * Optimized with React.memo to prevent unnecessary re-renders.
 */

'use client';

import { memo } from 'react';
import { Message } from '@/types/chat';
import { ToolCallIndicator } from './ToolCallIndicator';

interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
}

/**
 * MessageBubble component for displaying chat messages
 */
export const MessageBubble = memo(function MessageBubble({ message, isStreaming = false }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={`flex w-full mb-4 ${
        isUser ? 'justify-end' : 'justify-start'
      }`}
      role="article"
      aria-label={`${isUser ? 'Your' : 'AI'} message`}
    >
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-white text-gray-900 border border-gray-200'
        } ${isStreaming ? 'motion-safe:animate-pulse' : ''}`}
      >
        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>

        {/* Tool calls for assistant messages */}
        {!isUser && message.tool_calls && message.tool_calls.length > 0 && (
          <div className="mt-3 space-y-2" role="region" aria-label="Tool executions">
            {message.tool_calls.map((toolCall, index) => (
              <ToolCallIndicator key={`${toolCall.tool_name}-${index}`} toolCall={toolCall} />
            ))}
          </div>
        )}

        {message.created_at && (
          <div
            className={`text-xs mt-2 ${
              isUser ? 'text-blue-100' : 'text-gray-500'
            }`}
          >
            <time dateTime={message.created_at}>
              {new Date(message.created_at).toLocaleTimeString()}
            </time>
          </div>
        )}
      </div>
    </div>
  );
});
