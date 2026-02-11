/**
 * MessageList Component
 *
 * Premium message list with smooth scrolling, welcome screen, and animations.
 * Displays messages with auto-scroll and support for streaming.
 */

'use client';

import { useEffect, useRef } from 'react';
import { Message } from '@/types/chat';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';
import { WelcomeScreen } from './WelcomeScreen';

interface MessageListProps {
  messages: Message[];
  streamingMessage?: string;
  isStreaming?: boolean;
  onSendMessage?: (message: string) => void;
  onRegenerate?: () => void;
}

/**
 * MessageList component for displaying chat messages
 */
export function MessageList({
  messages,
  streamingMessage,
  isStreaming = false,
  onSendMessage,
  onRegenerate,
}: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive or streaming updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  // Show welcome screen if no messages
  if (messages.length === 0 && !streamingMessage) {
    return (
      <div className="flex-1 overflow-y-auto w-full">
        <WelcomeScreen onPromptClick={onSendMessage || (() => {})} />
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto px-4 md:px-6 lg:px-8 py-6 scroll-smooth"
    >
      <div className="max-w-4xl mx-auto">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onRegenerate={message.role === 'assistant' ? onRegenerate : undefined}
          />
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
    </div>
  );
}
