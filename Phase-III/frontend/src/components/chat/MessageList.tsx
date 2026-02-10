/**
 * MessageList Component
 *
 * Displays the list of messages in a conversation with auto-scroll
 * and support for streaming messages.
 */

'use client';

import { useEffect, useRef } from 'react';
import { Message } from '@/types/chat';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';

interface MessageListProps {
  messages: Message[];
  streamingMessage?: string;
  isStreaming?: boolean;
}

/**
 * MessageList component for displaying chat messages
 */
export function MessageList({
  messages,
  streamingMessage,
  isStreaming = false,
}: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive or streaming updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      {messages.length === 0 && !streamingMessage && (
        <div className="flex h-full items-center justify-center">
          <div className="text-center text-gray-500">
            <p className="text-lg font-medium mb-2">Start a conversation</p>
            <p className="text-sm">
              Send a message to begin chatting with the AI assistant
            </p>
          </div>
        </div>
      )}

      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {streamingMessage && (
        <MessageBubble
          message={{
            id: -1,
            conversation_id: -1,
            role: 'assistant',
            content: streamingMessage,
            tool_calls: null,
            created_at: new Date().toISOString(),
          }}
          isStreaming={true}
        />
      )}

      {isStreaming && !streamingMessage && <TypingIndicator />}

      <div ref={messagesEndRef} />
    </div>
  );
}
