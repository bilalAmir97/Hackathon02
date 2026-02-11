/**
 * ChatInput Component
 *
 * Input field for sending messages with send button.
 * Disables input during streaming to prevent duplicate sends.
 * Includes full accessibility support.
 */

'use client';

import { useState, KeyboardEvent, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

/**
 * ChatInput component for message input
 */
export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea as user types
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      // Reset height to auto to get the correct scrollHeight
      textarea.style.height = 'auto';
      // Set height to scrollHeight, but respect max-height
      const newHeight = Math.min(textarea.scrollHeight, 120);
      textarea.style.height = `${newHeight}px`;
    }
  }, [message]);

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="px-4 py-4">
      <div className="flex items-end space-x-2">
        <label htmlFor="chat-message-input" className="sr-only">
          Type your message
        </label>
        <textarea
          ref={textareaRef}
          id="chat-message-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={disabled ? 'Waiting for response...' : 'Type your message...'}
          aria-label="Message input"
          aria-describedby="chat-input-help"
          className="flex-1 resize-none rounded-lg border border-[var(--glass-border)] bg-[var(--soft-dark-bg)] text-[var(--text-primary)] px-4 py-3 focus:border-[var(--primary-accent)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-accent)]/50 disabled:bg-[var(--soft-dark-bg-secondary)] disabled:cursor-not-allowed placeholder:text-[var(--text-secondary)] min-h-[44px] max-h-[120px] overflow-hidden"
          rows={1}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          aria-label="Send message"
          className="rounded-lg bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] px-6 py-3 text-white font-medium hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-[var(--primary-accent)] focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          Send
        </button>
      </div>
      <p id="chat-input-help" className="mt-2 text-xs text-[var(--text-secondary)]">
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}
