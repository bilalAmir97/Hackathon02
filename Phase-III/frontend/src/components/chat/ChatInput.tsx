/**
 * ChatInput Component
 *
 * Premium chat input with glassmorphism, auto-resize, and smooth animations.
 * Includes keyboard shortcuts and accessibility support.
 */

'use client';

import { useState, KeyboardEvent, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

/**
 * ChatInput component for message input
 */
export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea as user types
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const newHeight = Math.min(textarea.scrollHeight, 200);
      textarea.style.height = `${newHeight}px`;
    }
  }, [message]);

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-[var(--glass-border)] bg-[var(--soft-dark-bg)]/80 backdrop-blur-xl">
      <div className="max-w-4xl mx-auto px-4 md:px-6 lg:px-8 py-4">
        <motion.div
          animate={{
            boxShadow: isFocused
              ? '0 0 0 2px var(--primary-accent)'
              : '0 0 0 1px var(--glass-border)',
          }}
          transition={{ duration: 0.2 }}
          className="relative rounded-2xl bg-[var(--glass-bg)] backdrop-blur-xl overflow-hidden"
        >
          <div className="flex items-end gap-2 p-3">
            <label htmlFor="chat-message-input" className="sr-only">
              Type your message
            </label>
            <textarea
              ref={textareaRef}
              id="chat-message-input"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              disabled={disabled}
              placeholder={disabled ? 'AI is thinking...' : 'Type your message...'}
              aria-label="Message input"
              aria-describedby="chat-input-help"
              className="flex-1 resize-none bg-transparent text-[var(--text-primary)] px-3 py-2 focus:outline-none disabled:cursor-not-allowed placeholder:text-[var(--text-secondary)] min-h-[44px] max-h-[200px] overflow-y-auto"
              rows={1}
            />
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleSend}
              disabled={disabled || !message.trim()}
              aria-label="Send message"
              className="flex-shrink-0 rounded-xl bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] p-3 text-white font-medium hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-[var(--primary-accent)] focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg"
            >
              {disabled ? (
                <svg
                  className="w-5 h-5 animate-spin"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
              ) : (
                <svg
                  className="w-5 h-5"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </motion.button>
          </div>
        </motion.div>

        <p id="chat-input-help" className="mt-2 text-xs text-[var(--text-secondary)] text-center">
          Press <kbd className="px-1.5 py-0.5 text-xs font-semibold bg-[var(--soft-dark-bg-secondary)] border border-[var(--glass-border)] rounded">Enter</kbd> to send, <kbd className="px-1.5 py-0.5 text-xs font-semibold bg-[var(--soft-dark-bg-secondary)] border border-[var(--glass-border)] rounded">Shift+Enter</kbd> for new line
        </p>
      </div>
    </div>
  );
}
