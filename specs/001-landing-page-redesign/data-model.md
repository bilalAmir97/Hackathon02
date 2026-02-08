# Data Model: Landing Page UI Redesign & Visual System Overhaul

## Overview
This document defines the layout primitives, container width strategy, and component specifications for the landing page UI redesign. The goal is to establish stable, responsive layout foundations while preserving the premium futuristic design.

## Layout Primitives

### 1. Container System
Defines the foundational layout containers with appropriate max-widths for different screen sizes.

#### Main Content Container
- **Mobile**: `w-full` with `px-4` padding
- **Tablet**: `w-full` with `px-6` padding
- **Desktop**: `max-w-6xl` (7xl = 80rem = 1280px) with `px-8` padding
- **Ultra-Wide**: `max-w-7xl` (896px) with `px-12` padding

#### Authentication Card Container
- **Mobile**: `w-full` with `p-4` padding
- **Tablet**: `max-w-md` (2xl = 28rem = 448px) with `p-6` padding
- **Desktop**: `max-w-lg` (32rem = 512px) with `p-8` padding
- **Constraint**: Minimum width of `sm:min-w-[320px]` to prevent narrow columns

### 2. Grid and Flexbox Specifications

#### Landing Page Grid System
```html
<!-- Hero Section -->
<div class="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 pt-16">
  <div class="max-w-6xl mx-auto text-center relative z-20">
    <!-- Content here -->
  </div>
</div>

<!-- Feature Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-20">
  <!-- Feature cards -->
</div>
```

#### Authentication Form Grid
```html
<!-- Auth Card -->
<div class="max-w-md w-full mx-auto p-6 sm:p-8 relative overflow-hidden z-10">
  <div class="relative z-10 space-y-5 sm:space-y-6">
    <!-- Form elements -->
  </div>
</div>
```

### 3. Spacing System
Consistent spacing using Tailwind's spacing scale with specific values:

- **xs**: `0.5rem` (2)
- **sm**: `1rem` (4)
- **md**: `1.5rem` (6)
- **lg**: `2rem` (8)
- **xl**: `3rem` (12)
- **2xl**: `4rem` (16)

Applied consistently to margins and padding around components.

## Container Width Strategy

### 1. Fixed vs Fluid Approach
- **Fixed**: Content containers use max-width constraints to prevent overly wide elements on large screens
- **Fluid**: Background elements and full-width sections remain fluid to fill available space
- **Responsive**: Max-width values scale appropriately across breakpoints

### 2. Specific Width Values
- **Auth Cards**: `max-w-md` (28rem = 448px) on tablet → `max-w-lg` (32rem = 512px) on desktop
- **Main Content**: `max-w-6xl` (1280px) for feature sections, `max-w-7xl` (896px) for hero
- **Cards**: `max-w-2xl` (42rem = 672px) for feature cards on desktop

### 3. Breakpoint Strategy
- **Mobile**: `<640px` - Full width with padding
- **Tablet**: `640px - 768px` - Limited width containers
- **Desktop**: `768px - 1024px` - Expanded containers
- **Large Desktop**: `1024px - 1280px` - Maximum width containers
- **Ultra-Wide**: `>1280px` - Maintains maximum width with generous side spacing

## Component Specifications

### 1. Scan-Line Implementation
- **Positioning**: Absolute positioned with `z-0` to stay behind content
- **Animation**: Transform-based vertical movement using `translateY` only
- **Reduced Motion**: Disabled via `@media (prefers-reduced-motion: reduce)`
- **Performance**: Hardware accelerated with `will-change: transform`

```html
<div class="absolute inset-0 z-0 pointer-events-none">
  <div class="scan-line absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-blue-500 to-transparent animate-scan-line">
    <!-- Animated via CSS or GSAP -->
  </div>
</div>
```

### 2. Glassmorphism Elements
- **Backface Visibility**: `backface-visibility: hidden` for smoother transitions
- **Backdrop Blur**: `backdrop-blur-md` with fallbacks
- **Border**: `border border-white/10` for subtle definition
- **Background**: `bg-white/10` or `bg-black/20` depending on theme

### 3. Floating Elements (Decorative)
- **Positioning**: Absolute positioned with percentage-based coordinates
- **Animation**: Transform-based movement (translateX/Y, scale) only
- **Performance**: Limited to 6 elements max per view to prevent performance issues
- **Responsiveness**: Disabled or reduced on mobile devices

## Animation Specifications

### 1. Safe Animation Properties
Only properties that don't trigger layout or paint:
- `transform` (translate, scale, rotate)
- `opacity`
- `filter` (blur, brightness) - with caution as can be expensive

### 2. Animation Timing
- **Entrance Animations**: 0.4-0.6 seconds duration
- **Hover Effects**: 0.15-0.2 seconds duration
- **Stagger Delays**: Maximum 0.1 seconds between elements
- **Safe Timing**: All animations should complete after component paint

### 3. Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Responsive Behavior Specifications

### 1. Typography Scaling
- **Mobile**: Base font sizes with clamp() for fluid scaling
- **Desktop**: Larger font sizes with maximum limits
- **Line Height**: Consistent ratios (1.5 for body text, 1.25 for headings)

### 2. Element Scaling
- **Buttons**: Maintain minimum touch target size (44px) on mobile
- **Inputs**: Adequate spacing for accessibility
- **Images**: Responsive with appropriate aspect ratios

### 3. Navigation Behavior
- **Mobile**: Hamburger menu or stacked layout
- **Desktop**: Horizontal layout with adequate spacing
- **Transitions**: Smooth, non-distracting animations

## Accessibility Considerations

### 1. Focus Management
- Visible focus indicators for all interactive elements
- Logical tab order that follows visual sequence
- Proper labeling for form elements

### 2. Color Contrast
- Minimum 4.5:1 ratio for normal text, 3:1 for large text
- Sufficient contrast maintained during animations
- Alternative indicators beyond color alone

### 3. Motion Sensitivity
- All animations respect `prefers-reduced-motion` setting
- No flashing or rapidly changing content
- Option to pause animations where appropriate

## Performance Benchmarks

### 1. Animation Performance
- Target: 60fps on mid-range devices
- Use of `will-change` for elements that will animate
- Off-main-thread animations where possible

### 2. Layout Stability
- No layout shift during animations
- Containment applied to animated elements
- Proper sizing applied before animations begin

### 3. Bundle Size
- Animation libraries loaded efficiently
- Unused animations tree-shaken from bundle
- Performance budget maintained

## Implementation Checklist

### Pre-Implementation
- [ ] Define container max-widths for all breakpoints
- [ ] Establish spacing system and apply consistently
- [ ] Plan z-index layering strategy
- [ ] Define reduced-motion support approach

### During Implementation
- [ ] Use transform/opacity only for animations
- [ ] Apply proper z-index values for layering
- [ ] Test on all target devices and screen sizes
- [ ] Verify accessibility compliance

### Post-Implementation
- [ ] Performance testing across devices
- [ ] Cross-browser compatibility check
- [ ] Accessibility audit
- [ ] Animation performance measurement