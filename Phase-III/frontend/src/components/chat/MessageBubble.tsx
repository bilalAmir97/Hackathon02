/**
 * MessageBubble Component
 *
 * Premium message bubble with glassmorphism, hover actions, and smooth animations.
 * Supports user and assistant messages with timestamps and tool call transparency.
 * Optimized with React.memo to prevent unnecessary re-renders.
 */

'use client';

import { memo, useState } from 'react';
import { motion } from 'framer-motion';
import { Message } from '@/types/chat';
import { ToolCallIndicator } from './ToolCallIndicator';
import { MessageActions } from './MessageActions';

interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
  onRegenerate?: () => void;
}

/**
 * MessageBubble component for displaying chat messages
 */
export const MessageBubble = memo(function MessageBubble({
  message,
  isStreaming = false,
  onRegenerate
}: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const [isHovered, setIsHovered] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}
      role="article"
      aria-label={`${isUser ? 'Your' : 'AI'} message`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-[85%] md:max-w-[75%]`}>
        {/* Message bubble */}
        <div
          className={`relative rounded-2xl px-5 py-3.5 ${
            isUser
              ? 'bg-gradient-to-br from-[var(--primary-accent)] to-[var(--primary-accent-end)] text-white shadow-lg'
              : 'bg-[var(--glass-bg)] backdrop-blur-xl border border-[var(--glass-border)] text-[var(--text-primary)] shadow-md'
          } ${isStreaming ? 'motion-safe:animate-pulse' : ''}`}
        >
          <div className="text-[15px] leading-relaxed whitespace-pre-wrap">
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
        </div>

        {/* Timestamp and actions */}
        <div className={`flex items-center gap-3 mt-2 px-1 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
          {message.created_at && (
            <time
              dateTime={message.created_at}
              className="text-xs text-[var(--text-secondary)]"
            >
              {new Date(message.created_at).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </time>
          )}

          {/* Action buttons on hover */}
          {isHovered && !isStreaming && (
            <MessageActions
              content={message.content}
              isAssistant={!isUser}
              onRegenerate={!isUser ? onRegenerate : undefined}
            />
          )}
        </div>
      </div>
    </motion.div>
  );
});
