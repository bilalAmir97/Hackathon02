/**
 * NewChatButton Component
 *
 * Premium button to create a new conversation with gradient and animations.
 */

'use client';

import { motion } from 'framer-motion';

interface NewChatButtonProps {
  onClick: () => void;
}

/**
 * NewChatButton component with premium styling
 */
export function NewChatButton({ onClick }: NewChatButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] hover:opacity-90 text-white rounded-xl font-medium transition-all shadow-lg hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-[var(--primary-accent)] focus:ring-offset-2 focus:ring-offset-[var(--soft-dark-bg)]"
      aria-label="Start new conversation"
    >
      <svg
        className="h-5 w-5"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path d="M12 4v16m8-8H4" />
      </svg>
      New Chat
    </motion.button>
  );
}
