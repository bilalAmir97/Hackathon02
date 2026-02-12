import { useState, useEffect } from 'react';

export const useReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean | null>(null);

  useEffect(() => {
    // Check if the browser supports the media query
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

      // Set initial value
      setPrefersReducedMotion(mediaQuery.matches);

      // Listen for changes
      const handleChange = (e: MediaQueryListEvent) => {
        setPrefersReducedMotion(e.matches);
      };

      // Add listener
      mediaQuery.addEventListener('change', handleChange);

      // Cleanup
      return () => {
        mediaQuery.removeEventListener('change', handleChange);
      };
    } else {
      // Default to false if media queries are not supported
      setPrefersReducedMotion(false);
    }
  }, []);

  return prefersReducedMotion;
};