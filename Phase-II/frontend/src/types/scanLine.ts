/**
 * Accessibility settings for scanline features
 */
export interface AccessibilitySettings {
  userId?: string;
  prefersReducedMotion: boolean;
  ambientFallbackStyle: 'static-gradient' | 'dotted-line' | 'solid-bar' | 'none';
  eventFallbackEnabled: boolean;
  existingScanlineIntegration: boolean;
}

/**
 * Configuration options for scanline component
 */
export interface ScanlineConfig {
  speed?: number;
  height?: number;
  color?: string;
  className?: string;
  ambientOpacity?: number;
  eventOpacity?: number;
  enableEventTriggers?: boolean;
  enableAmbientScanlines?: boolean;
}

/**
 * Scanline event data
 */
export interface ScanlineEventData {
  id: number;
  x: number;
  y: number;
  timestamp: number;
}