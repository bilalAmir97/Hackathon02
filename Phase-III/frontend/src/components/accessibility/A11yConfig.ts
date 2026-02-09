// Accessibility configuration and utility functions

/**
 * Ensures proper contrast ratios for WCAG 2.1 AA compliance
 * - Large text: minimum 3:1 ratio
 * - Normal text: minimum 4.5:1 ratio
 */
export const ensureContrastRatio = (foregroundColor: string, backgroundColor: string): boolean => {
  const fg = hexToRgb(foregroundColor);
  const bg = hexToRgb(backgroundColor);

  if (!fg || !bg) return false;

  const fgLuminance = calculateLuminance(fg);
  const bgLuminance = calculateLuminance(bg);

  const ratio = bgLuminance > fgLuminance
    ? (bgLuminance + 0.05) / (fgLuminance + 0.05)
    : (fgLuminance + 0.05) / (bgLuminance + 0.05);

  // For AA compliance: normal text needs 4.5:1, large text needs 3:1
  return ratio >= 4.5;
};

/**
 * Converts hex color to RGB
 */
const hexToRgb = (hex: string): { r: number; g: number; b: number } | null => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      }
    : null;
};

/**
 * Calculates luminance for contrast ratio calculation
 */
const calculateLuminance = (rgb: { r: number; g: number; b: number }): number => {
  const a = [rgb.r, rgb.g, rgb.b].map(v => {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });
  return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
};

/**
 * Configuration for reduced motion support
 */
export const reducedMotionConfig = {
  /**
   * Applies reduced motion settings when user prefers reduced motion
   */
  applyReducedMotion: () => {
    // Check if user has requested reduced motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      // Disable animations
      document.documentElement.classList.add('motion-reduce');

      // Update CSS variables to disable transitions
      document.documentElement.style.setProperty('--motion-duration-fast', '0.01ms');
      document.documentElement.style.setProperty('--motion-duration-normal', '0.01ms');
      document.documentElement.style.setProperty('--motion-duration-slow', '0.01ms');
    } else {
      // Remove reduced motion class if present
      document.documentElement.classList.remove('motion-reduce');

      // Reset CSS variables to normal values
      document.documentElement.style.setProperty('--motion-duration-fast', '150ms');
      document.documentElement.style.setProperty('--motion-duration-normal', '200ms');
      document.documentElement.style.setProperty('--motion-duration-slow', '300ms');
    }
  },

  /**
   * Initializes reduced motion listeners
   */
  initReducedMotionListener: () => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    mediaQuery.addEventListener('change', () => {
      reducedMotionConfig.applyReducedMotion();
    });

    // Apply initial setting
    reducedMotionConfig.applyReducedMotion();
  }
};

/**
 * Focus management utilities for keyboard navigation
 */
export const focusManagement = {
  /**
   * Adds focus trap to a modal or dialog
   */
  trapFocus: (element: HTMLElement) => {
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) as NodeListOf<HTMLElement>;

    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey && document.activeElement === firstElement) {
        lastElement.focus();
        e.preventDefault();
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        firstElement.focus();
        e.preventDefault();
      }
    };

    element.addEventListener('keydown', handleKeyDown);

    // Focus first element initially
    firstElement.focus();

    return () => {
      element.removeEventListener('keydown', handleKeyDown);
    };
  },

  /**
   * Manages focus when components mount/unmount
   */
  manageFocusOnMount: (element: HTMLElement | null) => {
    if (element) {
      element.focus({ preventScroll: true });
    }
  }
};

/**
 * ARIA live region utility for announcements
 */
export class AriaLiveRegion {
  private region: HTMLDivElement | null = null;

  constructor() {
    this.createRegion();
  }

  private createRegion() {
    this.region = document.createElement('div');
    this.region.setAttribute('aria-live', 'polite');
    this.region.setAttribute('aria-atomic', 'true');
    this.region.className = 'sr-only'; // Visually hidden but accessible to screen readers
    this.region.setAttribute('role', 'status');

    document.body.appendChild(this.region);
  }

  announce(message: string) {
    if (this.region) {
      // Clear previous message and set new one
      this.region.textContent = '';
      // Use a small delay to ensure the screen reader picks up the change
      setTimeout(() => {
        this.region!.textContent = message;
      }, 100);
    }
  }

  destroy() {
    if (this.region) {
      document.body.removeChild(this.region);
      this.region = null;
    }
  }
}