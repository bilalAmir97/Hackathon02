# Quickstart: UI Fixes (Landing, Login, Register)

## Overview

This guide explains how to set up, run, and test the UI fixes for the landing, login, and register pages. The changes focus on stabilizing layouts, fixing card sizing issues, and resolving GSAP animation conflicts while preserving the premium futuristic design aesthetic.

## Prerequisites

- Node.js 18+ installed
- Yarn or npm package manager
- Access to Phase-II/frontend directory

## Setup

### 1. Navigate to the Frontend Directory
```bash
cd Phase-II/frontend
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
```

### 3. Environment Setup
Copy the environment file if it exists:
```bash
cp .env.local.example .env.local
# Update values as needed for your environment
```

## Development

### 1. Start the Development Server
```bash
npm run dev
# or
yarn dev
```

### 2. Access the Application
- Visit `http://localhost:3000` for the landing page
- Visit `http://localhost:3000/login` for the login page
- Visit `http://localhost:3000/register` for the register page

## Testing the UI Fixes

### 1. Visual Verification
Test the following on desktop, tablet, and mobile viewports:

#### Landing Page
- [ ] Hero section is centered and properly scaled
- [ ] Headline and CTA button are visible without clipping
- [ ] Scan-line animation runs smoothly without affecting layout
- [ ] No vertical stretching of content

#### Login Page
- [ ] Auth card renders at intended width/height
- [ ] Card is horizontally centered on desktop
- [ ] Border-radius and spacing are correct
- [ ] Card stacks properly on small viewports
- [ ] No layout shift during animations

#### Register Page
- [ ] Auth card renders at intended width/height
- [ ] Card is horizontally centered on desktop
- [ ] Border-radius and spacing are correct
- [ ] Card stacks properly on small viewports
- [ ] No layout shift during animations

### 2. Responsive Testing
Test at these specific breakpoints:
- Desktop: 1024px and above
- Tablet: 768px - 1023px
- Mobile: Below 768px

### 3. Animation Testing
- [ ] GSAP animations don't cause layout distortion
- [ ] Animations are interruptible during user interactions
- [ ] No permanent transforms affect layout flow
- [ ] Reduced motion preference is respected

### 4. Accessibility Testing
- [ ] Keyboard tab order remains intact
- [ ] Form labels remain visible
- [ ] Reduced motion preference is honored (inspect with dev tools)

## Playwright Visual Regression Tests

### 1. Install Playwright
```bash
npx playwright install
```

### 2. Run Visual Regression Tests
```bash
npm run test:visual
# or
yarn test:visual
```

### 3. Update Snapshots (if intentional changes made)
```bash
npm run test:visual:update
# or
yarn test:visual:update
```

## Troubleshooting

### Common Issues

#### Layout Issues Persist
1. Check that CSS changes were applied correctly
2. Verify responsive breakpoints are properly implemented
3. Clear browser cache and restart development server

#### Animations Still Cause Layout Shifts
1. Verify GSAP animations only use transform and opacity
2. Check for conflicting Framer Motion animations
3. Ensure `will-change` property is set appropriately

#### Cards Not Centering Properly
1. Verify flexbox centering classes are applied
2. Check for conflicting CSS that might override centering
3. Validate max-width constraints are appropriate

### Debugging Tips

#### Browser Developer Tools
1. Use the responsive design mode to test different breakpoints
2. Disable animations temporarily to isolate layout issues
3. Inspect computed styles to verify applied CSS

#### Animation Debugging
1. Use GSAP's `gsap.globalTimeline()` to inspect all animations
2. Check for conflicting CSS transforms
3. Verify scroll-triggered animations are properly cleaned up

## Performance Testing

### 1. Measure Page Load Times
- Use browser dev tools Performance tab
- Aim for pages to load in under 2 seconds
- Monitor for any performance regressions

### 2. Animation Performance
- Use browser dev tools Rendering tab
- Monitor for consistent 60fps during animations
- Look for dropped frames or jank

## Deployment

### Build for Production
```bash
npm run build
# This creates an optimized build in the .next/ directory
```

### Preview Production Build
```bash
npm run start
# Runs the built application in production mode
```

## Key Files to Review

### Landing Page
- `Phase-II/frontend/src/app/page.tsx` - Main landing page
- `Phase-II/frontend/src/app/globals.css` - Global styles including scan-line

### Login Page
- `Phase-II/frontend/src/app/(auth)/login/page.tsx` - Login page implementation

### Register Page
- `Phase-II/frontend/src/app/(auth)/register/page.tsx` - Register page implementation

### Global Styles
- `Phase-II/frontend/src/styles/globals.css` - Global styles and animations (if separate from app globals.css)

### Animation Utilities
- Any GSAP-related files in `Phase-II/frontend/src/lib/`
- Animation configuration in individual page files

### UI Components
- `Phase-II/frontend/src/components/ui/input.tsx` - Input component (if layout adjustments needed)
- `Phase-II/frontend/src/components/ui/button.tsx` - Button component (if layout adjustments needed)

## Rollback Plan

If issues arise after deployment:
1. Revert CSS changes in globals.css
2. Disable GSAP animations temporarily
3. Revert to previous component versions if needed
4. Test each change incrementally to identify the problematic code