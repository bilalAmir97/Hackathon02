'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';

interface ThemeContextType {
  theme: 'light' | 'dark' | 'soft-dark';
  setTheme: (theme: 'light' | 'dark' | 'soft-dark') => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark' | 'soft-dark'>('soft-dark');

  useEffect(() => {
    // Check for saved theme preference or default to soft-dark
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'soft-dark' | null;
    if (savedTheme) {
      setTheme(savedTheme);
    } else {
      setTheme('soft-dark'); // Default to soft-dark theme
    }
  }, []);

  useEffect(() => {
    // Apply theme to document
    document.documentElement.classList.remove('light', 'dark', 'soft-dark');
    document.documentElement.classList.add(theme);

    // Update meta theme color
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      if (theme === 'soft-dark') {
        metaThemeColor.setAttribute('content', '#0f172a');
      } else if (theme === 'dark') {
        metaThemeColor.setAttribute('content', '#0a0a0a');
      } else {
        metaThemeColor.setAttribute('content', '#f0f0f0');
      }
    }

    // Save theme preference
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => {
      if (prev === 'light') return 'dark';
      if (prev === 'dark') return 'soft-dark';
      return 'light';
    });
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};