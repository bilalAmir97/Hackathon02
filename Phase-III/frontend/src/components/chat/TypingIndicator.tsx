/**
 * TypingIndicator Component
 *
 * Premium animated indicator with glowing pulsing dots matching the theme.
 */

'use client';

import { motion } from 'framer-motion';

/**
 * TypingIndicator component with premium pulsing glow animation
 */
export function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex w-full mb-6 justify-start"
      role="status"
      aria-live="polite"
      aria-label="AI is typing"
    >
      <div className="bg-[var(--glass-bg)] backdrop-blur-xl border border-[var(--glass-border)] text-[var(--text-primary)] rounded-2xl px-5 py-3.5 shadow-md">
        <div className="flex space-x-1.5 items-center">
          {[0, 1, 2].map((index) => (
            <motion.div
              key={index}
              className="w-2 h-2 rounded-full bg-gradient-to-br from-[var(--primary-accent)] to-[var(--primary-accent-end)]"
              animate={{
                scale: [1, 1.3, 1],
                opacity: [0.5, 1, 0.5],
              }}
              transition={{
                duration: 1.4,
                repeat: Infinity,
                delay: index * 0.2,
                ease: 'easeInOut',
              }}
              style={{
                boxShadow: '0 0 10px rgba(56, 189, 248, 0.5)',
              }}
            />
          ))}
        </div>
        <span className="sr-only">AI is typing a response</span>
      </div>
    </motion.div>
  );
}
