import React from 'react';
import { useTheme } from '@/components/theme/ThemeProvider';

export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  // Choose the appropriate icon based on current theme
  const getIcon = () => {
    if (theme === 'light') {
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M4.95 4.95a7.04 7.04 0 010 9.9l-.707.707M19.05 4.95a7.04 7.04 0 000 9.9l-.707-.707M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      );
    } else if (theme === 'dark') {
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
      );
    } else { // soft-dark
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
        </svg>
      );
    }
  };

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-full text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--soft-dark-bg-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-accent)]"
      aria-label={`Switch to ${theme === 'light' ? 'dark' : theme === 'dark' ? 'soft dark' : 'light'} theme`}
    >
      {getIcon()}
    </button>
  );
};