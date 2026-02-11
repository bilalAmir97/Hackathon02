/**
 * MessageActions Component
 *
 * Action buttons for chat messages (copy, regenerate).
 * Appears on hover with smooth animations.
 */

'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface MessageActionsProps {
  content: string;
  isAssistant: boolean;
  onRegenerate?: () => void;
}

/**
 * MessageActions component with copy and regenerate functionality
 */
export function MessageActions({ content, isAssistant, onRegenerate }: MessageActionsProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="flex items-center gap-1"
    >
      {/* Copy button */}
      <button
        onClick={handleCopy}
        className="p-1.5 rounded-lg hover:bg-[var(--soft-dark-bg-secondary)] transition-colors duration-200 group relative"
        aria-label="Copy message"
        title="Copy message"
      >
        <AnimatePresence mode="wait">
          {copied ? (
            <motion.svg
              key="check"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              className="w-4 h-4 text-green-500"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M5 13l4 4L19 7" />
            </motion.svg>
          ) : (
            <motion.svg
              key="copy"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              className="w-4 h-4 text-[var(--text-secondary)] group-hover:text-[var(--text-primary)]"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </motion.svg>
          )}
        </AnimatePresence>
      </button>

      {/* Regenerate button (only for assistant messages) */}
      {isAssistant && onRegenerate && (
        <button
          onClick={onRegenerate}
          className="p-1.5 rounded-lg hover:bg-[var(--soft-dark-bg-secondary)] transition-colors duration-200 group"
          aria-label="Regenerate response"
          title="Regenerate response"
        >
          <svg
            className="w-4 h-4 text-[var(--text-secondary)] group-hover:text-[var(--text-primary)]"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      )}
    </motion.div>
  );
}
