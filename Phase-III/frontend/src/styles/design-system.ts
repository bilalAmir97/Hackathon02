/**
 * Design System for Future-Ready UI
 *
 * This file defines the visual design system with glassmorphism and neumorphism aesthetics
 * following futuristic UI principles.
 */

// Color palette
export const colors = {
  primary: {
    light: '#667eea',
    dark: '#764ba2',
  },
  glass: {
    background: 'rgba(255, 255, 255, 0.15)',
    border: 'rgba(255, 255, 255, 0.2)',
  },
  neumorphism: {
    light: '#ffffff',
    dark: '#d1d9e6',
  },
  text: {
    primary: '#171717',
    secondary: '#6b7280',
    inverted: '#ffffff',
  },
  status: {
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
  },
};

// Typography
export const typography = {
  heading: {
    xl: 'text-4xl font-bold',
    lg: 'text-3xl font-bold',
    md: 'text-2xl font-semibold',
    sm: 'text-xl font-medium',
  },
  body: {
    lg: 'text-lg',
    md: 'text-base',
    sm: 'text-sm',
    xs: 'text-xs',
  },
  weight: {
    light: 'font-light',
    normal: 'font-normal',
    medium: 'font-medium',
    semibold: 'font-semibold',
    bold: 'font-bold',
  },
};

// Spacing
export const spacing = {
  xxs: '0.25rem', // 4px
  xs: '0.5rem',   // 8px
  sm: '0.75rem',  // 12px
  md: '1rem',     // 16px
  lg: '1.5rem',   // 24px
  xl: '2rem',     // 32px
  xxl: '3rem',    // 48px
};

// Border radius
export const borderRadius = {
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '24px',
  full: '9999px',
};

// Shadows
export const shadows = {
  glass: '0 8px 32px rgba(31, 38, 135, 0.2)',
  neumorphism: 'inset 5px 5px 10px #c3cbd5, inset -5px -5px 10px #ffffff',
  neumorphismPressed: 'inset 2px 2px 5px #c3cbd5, inset -2px -2px 5px #ffffff',
  floating: '0 10px 25px rgba(0, 0, 0, 0.1)',
  hover: '0 12px 24px rgba(0, 0, 0, 0.15)',
};

// Transitions
export const transitions = {
  quick: 'all 0.2s ease',
  standard: 'all 0.3s ease',
  slow: 'all 0.5s ease',
};

// Breakpoints
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

// Component variants
export const componentVariants = {
  card: {
    base: 'rounded-xl border transition-all duration-300',
    glass: 'glass-effect bg-opacity-10',
    neumorphism: 'neumorphism',
    futuristic: 'futuristic-card',
  },
  button: {
    primary: 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg hover:shadow-xl',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    ghost: 'bg-transparent text-gray-600 hover:bg-gray-100',
  },
};

export default {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  transitions,
  breakpoints,
  componentVariants,
};