/**
 * WelcomeScreen Component
 *
 * Premium welcome screen shown when no conversation is active.
 * Features suggested prompts and a modern, inviting design.
 */

'use client';

import { motion } from 'framer-motion';

interface WelcomeScreenProps {
  onPromptClick: (prompt: string) => void;
}

const SUGGESTED_PROMPTS = [
  {
    icon: '💡',
    title: 'Get Ideas',
    prompt: 'Help me brainstorm ideas for a new project',
  },
  {
    icon: '📝',
    title: 'Write Content',
    prompt: 'Help me write a professional email',
  },
  {
    icon: '🔍',
    title: 'Research',
    prompt: 'Explain a complex topic in simple terms',
  },
  {
    icon: '🎯',
    title: 'Plan Tasks',
    prompt: 'Help me organize my tasks for the week',
  },
];

/**
 * WelcomeScreen component with suggested prompts
 */
export function WelcomeScreen({ onPromptClick }: WelcomeScreenProps) {
  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-3xl w-full"
      >
        {/* Header */}
        <div className="text-center mb-12">
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="mb-6"
          >
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-[var(--primary-accent)] to-[var(--primary-accent-end)] shadow-lg">
              <svg
                className="w-10 h-10 text-white"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-4xl font-bold text-[var(--text-primary)] mb-3"
          >
            How can I help you today?
          </motion.h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="text-lg text-[var(--text-secondary)]"
          >
            Start a conversation or choose a suggestion below
          </motion.p>
        </div>

        {/* Suggested Prompts Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="grid grid-cols-1 sm:grid-cols-2 gap-4"
        >
          {SUGGESTED_PROMPTS.map((suggestion, index) => (
            <motion.button
              key={suggestion.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onPromptClick(suggestion.prompt)}
              className="group relative p-6 rounded-2xl bg-[var(--glass-bg)] backdrop-blur-xl border border-[var(--glass-border)] hover:border-[var(--primary-accent)]/30 transition-all duration-300 text-left overflow-hidden"
            >
              {/* Gradient overlay on hover */}
              <div className="absolute inset-0 bg-gradient-to-br from-[var(--primary-accent)]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

              <div className="relative">
                <div className="text-3xl mb-3">{suggestion.icon}</div>
                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
                  {suggestion.title}
                </h3>
                <p className="text-sm text-[var(--text-secondary)] line-clamp-2">
                  {suggestion.prompt}
                </p>
              </div>

              {/* Arrow icon */}
              <div className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transform translate-x-2 group-hover:translate-x-0 transition-all duration-300">
                <svg
                  className="w-5 h-5 text-[var(--primary-accent)]"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
            </motion.button>
          ))}
        </motion.div>

        {/* Footer hint */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.9 }}
          className="mt-8 text-center"
        >
          <p className="text-sm text-[var(--text-secondary)]">
            Press{' '}
            <kbd className="px-2 py-1 text-xs font-semibold text-[var(--text-primary)] bg-[var(--soft-dark-bg-secondary)] border border-[var(--glass-border)] rounded">
              Cmd
            </kbd>{' '}
            +{' '}
            <kbd className="px-2 py-1 text-xs font-semibold text-[var(--text-primary)] bg-[var(--soft-dark-bg-secondary)] border border-[var(--glass-border)] rounded">
              K
            </kbd>{' '}
            for a new chat
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}
