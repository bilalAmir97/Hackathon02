import { useState, useEffect } from 'react';
import { AccessibilitySettings } from '@/types/scanLine';

/**
 * Custom hook for managing accessibility settings, particularly for scanline features
 * This hook detects and manages user preferences like reduced motion
 */
export const useAccessibilitySettings = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(false);
  const [isClient, setIsClient] = useState<boolean>(false);

  useEffect(() => {
    setIsClient(true);

    // Check for reduced motion preference
    if (typeof window !== 'undefined') {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

      // Set initial value
      setPrefersReducedMotion(mediaQuery.matches);

      // Listen for changes
      const handleChange = (e: MediaQueryListEvent) => {
        setPrefersReducedMotion(e.matches);
      };

      // Add listener
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleChange);
      } else {
        // Fallback for older browsers
        (mediaQuery as any).addListener(handleChange);
      }

      // Cleanup function
      return () => {
        if (mediaQuery.removeEventListener) {
          mediaQuery.removeEventListener('change', handleChange);
        } else {
          // Fallback for older browsers
          (mediaQuery as any).removeListener(handleChange);
        }
      };
    }
  }, []);

  /**
   * Get the current accessibility settings
   */
  const getAccessibilitySettings = (): AccessibilitySettings => {
    return {
      userId: undefined, // Not implemented in this basic version
      prefersReducedMotion,
      ambientFallbackStyle: 'static-gradient', // Default fallback style
      eventFallbackEnabled: false, // Disable event scan lines when reduced motion is enabled
      existingScanlineIntegration: true, // Integrate with existing scanline implementation
    };
  };

  return {
    prefersReducedMotion,
    getAccessibilitySettings,
    isClient, // Useful for server-side rendering considerations
  };
};