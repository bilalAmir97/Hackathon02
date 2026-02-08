# ScanLine Component API Contract

## Component: AdvancedScanline (enhancement to existing Scanline component)

### Description
An enhanced React component that extends the existing scan-line system to provide a two-layer scan-line overlay system with ambient and event scan-lines for premium visual effects. This component builds upon the existing `Scanline.tsx` and `AdvancedScanline.tsx` components.

### Props Interface

```typescript
interface ScanLineConfig {
  // Ambient scan line settings
  ambientOpacity?: number;        // Range: 0.02-0.06, default: 0.04
  ambientDuration?: number;       // Range: 8-14 seconds, default: 10
  ambientEnabled?: boolean;       // Whether ambient scan lines are enabled

  // Event scan line settings
  eventDuration?: number;         // Range: 0.6-1.2 seconds, default: 0.8
  eventEnabled?: boolean;         // Whether event scan lines are enabled

  // Visual settings
  colorGradient?: string;         // CSS gradient string, default: "linear-gradient(to right, #00f7ff, #6a00ff)"
  glowIntensity?: number;         // Range: 0-1, default: 0.3
  blurIntensity?: number;         // Range: 0-10px, default: 4

  // Accessibility settings
  reducedMotionFallback?: 'static-gradient' | 'subtle-pulse' | 'none'; // default: 'static-gradient'

  // Theme settings
  themeAdaptation?: boolean;      // Whether to adapt to light/dark mode, default: true

  // Integration settings for existing codebase
  integrationType?: 'overlay' | 'background' | 'hybrid'; // How to integrate with existing scanline system
  compatibilityMode?: boolean;    // Whether to maintain compatibility with existing scanline props
}

interface AdvancedScanlineProps {
  config?: ScanLineConfig;
  className?: string;             // Additional CSS classes
  zIndex?: number;                // Z-index for the overlay, default: 9999
  // Inherits additional props from existing Scanline component
}
```

### Component Methods/Functions

```typescript
// Trigger an event scan line programmatically
function triggerEventScanLine(options?: {
  position?: 'top' | 'bottom' | 'left' | 'right';
  color?: string;
  duration?: number;
}): void;

// Pause all animations
function pauseAnimations(): void;

// Resume all animations
function resumeAnimations(): void;

// Check if reduced motion is preferred by user
function getReducedMotionPreference(): boolean;

// Update configuration dynamically
function updateConfig(newConfig: Partial<ScanLineConfig>): void;

// Integration with existing GSAP animation utilities from gsap-animations.ts
function syncWithExistingAnimations(): void;

// Cleanup resources when component unmounts
function cleanup(): void;
```

### Events

```typescript
interface ScanLineEvents {
  // Emitted when an event scan line is triggered
  onEventScanLineTrigger: (event: {
    id: string;
    timestamp: Date;
    position: 'top' | 'bottom' | 'left' | 'right';
  }) => void;

  // Emitted when animations are paused/resumed
  onAnimationToggle: (event: {
    isPaused: boolean;
  }) => void;

  // Emitted when accessibility settings change
  onAccessibilityChange: (event: {
    reducedMotion: boolean;
  }) => void;

  // Emitted when integrated with existing scanline system
  onIntegrationComplete: () => void;
}
```

### CSS Classes

The component extends existing CSS classes from the current implementation:

- `.scanline-container` - Base container (extends existing class)
- `.scanline-ambient` - Ambient scan line layer (new class)
- `.scanline-event` - Event scan line layer (new class)
- `.scanline-enhanced` - Premium visual effect indicator (new class)
- `.scanline-hidden` - Applied when animations are disabled
- `.scanline-reduced-motion` - Applied when reduced motion is enabled

### CSS Custom Properties (CSS Variables)

The component extends CSS custom properties defined in globals.css:

```css
/* Existing properties from globals.css */
--scanline-base-opacity: 0.04;
--scanline-base-color: #00f7ff;

/* New properties for enhanced functionality */
--scanline-ambient-opacity: 0.04;
--scanline-event-opacity: 0.8;
--scanline-color-gradient: linear-gradient(to right, #00f7ff, #6a00ff);
--scanline-glow-intensity: 0.3;
--scanline-blur-intensity: 4px;
--scanline-theme-adaptation: true;
```

### Integration with Existing Codebase

- Compatible with existing `Scanline.tsx` and `AdvancedScanline.tsx` components
- Leverages existing `gsap-animations.ts` utilities
- Integrates with current layout system via `LayoutWithScanline.tsx`
- Maintains compatibility with existing accessibility patterns
- Extends existing type definitions in `types/scanLine.d.ts`

### Accessibility Compliance

- Respects `prefers-reduced-motion` media query (extends existing implementation)
- Proper contrast ratios maintained in all themes
- No animation-induced seizures (minimal motion when reduced motion enabled)
- Keyboard navigable (uses `pointer-events: none` so doesn't interfere with focus)
- Maintains existing accessibility features from current implementation

### Performance Requirements

- Maintains 60fps during animations
- Uses GPU-accelerated transforms only (translateX, translateY, opacity)
- Limits paint area to minimal bounds
- Uses `will-change` property appropriately
- <16ms frame render time target
- <50ms input delay target
- Integrates efficiently with existing GSAP animation system

### Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- With graceful degradation for older browsers
- Maintains compatibility with existing browser support matrix