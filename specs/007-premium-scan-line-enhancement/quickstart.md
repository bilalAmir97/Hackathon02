# Quickstart: Premium Futuristic Scan-Line Enhancement

## Overview
This guide will help you set up and run the premium futuristic scan-line enhancement feature in your development environment.

## Prerequisites
- Node.js 18+ (for Next.js 16+)
- Yarn or npm package manager
- Modern browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <your-repo-url>
   cd <repo-directory>
   ```

2. **Navigate to the frontend directory**:
   ```bash
   cd Phase-II/frontend
   ```

3. **Install dependencies**:
   ```bash
   npm install
   # or
   yarn install
   ```

4. **Install GSAP animation library** (if not already installed):
   ```bash
   npm install gsap
   # or
   yarn add gsap
   ```

## Running the Development Server

1. **Start the Next.js development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

2. **Open your browser** to:
   ```
   http://localhost:3000
   ```

## Key Files for Scan-Line Enhancement

The scan-line enhancement feature is implemented in these key files:

- `Phase-II/frontend/src/components/AdvancedScanline.tsx` - Main enhanced scan line component
- `Phase-II/frontend/src/components/LayoutWithScanline.tsx` - Layout wrapper with scan line integration
- `Phase-II/frontend/src/lib/gsap-animations.ts` - GSAP animation utilities
- `Phase-II/frontend/src/lib/animations/scanLineController.ts` - Centralized animation controller
- `Phase-II/frontend/src/styles/globals.css` - Global styles including scan line styles
- `Phase-II/frontend/src/hooks/useAccessibilitySettings.ts` - Motion sensitivity detection
- `Phase-II/frontend/src/types/scanLine.d.ts` - Scan line related type definitions

## Testing the Feature

1. **Verify ambient scan lines**: Look for subtle horizontal bands moving slowly across the background
2. **Test event scan lines**: Trigger key interactions (login success, dashboard navigation, CTA clicks) to see bright streaks with glow effect
3. **Test reduced motion**: Enable "Reduced motion" in your OS settings to verify fallback behavior
4. **Test theme adaptation**: Switch between light/dark mode to see scan line adaptation

## Configuration

The scan-line behavior can be customized by adjusting these parameters in `Phase-II/frontend/src/config/scanLines.ts`:

- `ambientOpacity`: Opacity range for ambient scan lines (0.02-0.06)
- `ambientDuration`: Duration range for ambient animations (8-14 seconds)
- `eventDuration`: Duration for event scan lines (0.6-1.2 seconds)
- `glowIntensity`: Intensity of the soft glow effect
- `themeAdaptation`: Whether scan lines adapt to light/dark mode

## Troubleshooting

- **Scan lines not appearing**: Check that `ScanLineOverlay` component is properly included in your layout
- **Poor performance**: Verify that only transform and opacity properties are being animated
- **Reduced motion not working**: Confirm that `prefers-reduced-motion` media query is properly detected
- **Theme adaptation not working**: Check that CSS custom properties are properly defined for both themes

## Performance Monitoring

To monitor performance during development:

1. Open Chrome DevTools
2. Navigate to the Performance tab
3. Record a session while using the application
4. Verify that frame rate remains consistently at 60fps
5. Check that animation renders are GPU-accelerated (look for "Composite" in flame chart)