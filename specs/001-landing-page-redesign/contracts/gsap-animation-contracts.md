# GSAP Animation Contracts: Landing Page UI Redesign

## Overview
This document defines the animation contracts for the landing page redesign project. It specifies the GSAP animation functions, their parameters, expected behavior, and accessibility requirements.

## Animation Functions

### 1. animatePageLoad()
**Purpose**: Handles the initial page entrance animations for elements with data-animate attribute.

**Signature**:
```typescript
animatePageLoad(): void
```

**Parameters**: None

**Behavior**:
- Animates elements with `data-animate` attribute
- Applies fade-in with subtle vertical movement
- Duration: 0.6 seconds
- Easing: power2.out
- Stagger: 0.1 seconds between elements
- Trigger: ScrollTrigger when element enters viewport (top 90%)

**Constraints**:
- Must respect `prefers-reduced-motion` setting
- Should not cause layout shifts
- Must clean up any ScrollTrigger instances on page unload

**Error Handling**: None (silent failure acceptable)

### 2. fadeIn(element: HTMLElement | null, delay: number = 0)
**Purpose**: Creates a fade-in animation with subtle scale and vertical movement.

**Signature**:
```typescript
fadeIn(element: HTMLElement | null, delay: number = 0): void
```

**Parameters**:
- `element`: HTMLElement to animate (nullable)
- `delay`: Delay in seconds before animation starts (default: 0)

**Behavior**:
- Opacity: 0 → 1
- Vertical position: y: 20px → 0px
- Scale: 0.98 → 1
- Duration: 0.4 seconds
- Easing: power2.out
- Forces 3D acceleration for performance

**Constraints**:
- Must check if element exists before animating
- Should respect `prefers-reduced-motion` setting
- Must use transform and opacity properties only (GPU-accelerated)

**Error Handling**:
- If element is null, function exits silently
- If animation fails, no error is thrown

### 3. slideInFromLeft(element: HTMLElement | null, delay: number = 0)
**Purpose**: Slides an element in from the left side with fade-in effect.

**Signature**:
```typescript
slideInFromLeft(element: HTMLElement | null, delay: number = 0): void
```

**Parameters**:
- `element`: HTMLElement to animate (nullable)
- `delay`: Delay in seconds before animation starts (default: 0)

**Behavior**:
- Opacity: 0 → 1
- Horizontal position: x: -50px → 0px
- Scale: 0.98 → 1
- Duration: 0.4 seconds
- Easing: power2.out
- Forces 3D acceleration for performance

**Constraints**:
- Must check if element exists before animating
- Should respect `prefers-reduced-motion` setting
- Must use transform and opacity properties only (GPU-accelerated)

**Error Handling**:
- If element is null, function exits silently
- If animation fails, no error is thrown

### 4. slideInFromRight(element: HTMLElement | null, delay: number = 0)
**Purpose**: Slides an element in from the right side with fade-in effect.

**Signature**:
```typescript
slideInFromRight(element: HTMLElement | null, delay: number = 0): void
```

**Parameters**:
- `element`: HTMLElement to animate (nullable)
- `delay`: Delay in seconds before animation starts (default: 0)

**Behavior**:
- Opacity: 0 → 1
- Horizontal position: x: 50px → 0px
- Scale: 0.98 → 1
- Duration: 0.4 seconds
- Easing: power2.out
- Forces 3D acceleration for performance

**Constraints**:
- Must check if element exists before animating
- Should respect `prefers-reduced-motion` setting
- Must use transform and opacity properties only (GPU-accelerated)

**Error Handling**:
- If element is null, function exits silently
- If animation fails, no error is thrown

### 5. animateTaskItem(element: HTMLElement | null, index: number = 0)
**Purpose**: Animates individual task items with staggered delays.

**Signature**:
```typescript
animateTaskItem(element: HTMLElement | null, index: number = 0): void
```

**Parameters**:
- `element`: HTMLElement to animate (nullable)
- `index`: Position in list to calculate delay (default: 0)

**Behavior**:
- Opacity: 0 → 1
- Scale: 0.95 → 1
- Vertical position: y: 15px → 0px
- Rotation: rotationX: 15deg → 0deg
- Duration: 0.3 seconds
- Delay: Math.min(index * 0.03, 0.2) - capped at 0.2 seconds
- Easing: back.out(1.4)

**Constraints**:
- Must cap delay to prevent excessively long animations
- Should respect `prefers-reduced-motion` setting
- Must use transform and opacity properties only (GPU-accelerated)

**Error Handling**:
- If element is null, function exits silently
- If animation fails, no error is thrown

### 6. animateTaskList(elements: NodeListOf<Element> | Element[] | null)
**Purpose**: Animates a list of task elements with staggered entrance.

**Signature**:
```typescript
animateTaskList(elements: NodeListOf<Element> | Element[] | null): void
```

**Parameters**:
- `elements`: Collection of elements to animate (nullable)

**Behavior**:
- Limits animation to maximum 20 elements to prevent performance issues
- Opacity: 0 → 1
- Vertical position: y: 15px → 0px
- Scale: 0.98 → 1
- Duration: 0.4 seconds
- Stagger: 0.05 seconds between elements
- Easing: power2.out

**Constraints**:
- Must limit elements to prevent performance degradation
- Should respect `prefers-reduced-motion` setting
- Must use transform and opacity properties only (GPU-accelerated)

**Error Handling**:
- If elements is null, function exits silently
- If animation fails, no error is thrown

### 7. addButtonHoverAnimation(element: HTMLElement | null)
**Purpose**: Adds hover animation effects to buttons.

**Signature**:
```typescript
addButtonHoverAnimation(element: HTMLElement | null): void
```

**Parameters**:
- `element`: HTMLElement to add hover effects to (nullable)

**Behavior**:
- On mouse enter: scale to 1.03 (3% increase)
- On mouse leave: scale back to original
- Duration: 0.15 seconds each
- Easing: power2.out

**Constraints**:
- Must prevent animation accumulation on rapid hovering
- Should respect `prefers-reduced-motion` setting
- Must clean up event listeners when component unmounts

**Error Handling**:
- If element is null, function exits silently
- Stores event handlers for proper cleanup

### 8. removeButtonHoverAnimation(element: HTMLElement | null)
**Purpose**: Removes hover animation effects and cleans up event listeners.

**Signature**:
```typescript
removeButtonHoverAnimation(element: HTMLElement | null): void
```

**Parameters**:
- `element`: HTMLElement to remove hover effects from (nullable)

**Behavior**:
- Removes mouseenter and mouseleave event listeners
- Cleans up stored handler references

**Constraints**:
- Must only run if handlers were previously stored
- Should not throw errors if no handlers exist

**Error Handling**:
- If element is null or has no stored handlers, function exits silently

### 9. killAllAnimations()
**Purpose**: Cleans up all GSAP animations and ScrollTrigger instances.

**Signature**:
```typescript
killAllAnimations(): void
```

**Parameters**: None

**Behavior**:
- Kills all active GSAP tweens
- Kills all ScrollTrigger instances
- Cleans up hover animation event listeners

**Constraints**:
- Should be called on page transitions or component unmounts
- Must not cause errors if no animations exist

**Error Handling**: Silent failure acceptable

### 10. quickAnimation(element: HTMLElement | null, properties: any)
**Purpose**: Performs a quick animation with specified properties.

**Signature**:
```typescript
quickAnimation(element: HTMLElement | null, properties: any): void
```

**Parameters**:
- `element`: HTMLElement to animate (nullable)
- `properties`: Object containing animation properties

**Behavior**:
- Duration: 0.2 seconds
- Easing: power1.out
- Overwrite: 'auto' to prevent conflicts
- Clears specified properties on completion if provided

**Constraints**:
- Should respect `prefers-reduced-motion` setting
- Must use transform and opacity properties only (GPU-accelerated) when possible

**Error Handling**:
- If element is null, function exits silently

## Accessibility Requirements

### 1. Reduced Motion Support
All animations must respect the `prefers-reduced-motion` media query:
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

### 2. Performance Requirements
- All animations must maintain 60fps performance
- Use only transform and opacity properties for hardware acceleration
- Limit complex animations to prevent jank
- Ensure animations don't cause layout shifts

### 3. Interruption Handling
- Animations should be interruptible
- Use `overwrite: 'auto'` to prevent animation conflicts
- Clean up animations properly to prevent memory leaks

## Testing Requirements

### 1. Unit Tests
- Verify animation functions are called with correct parameters
- Test null element handling
- Verify delay calculations are correct
- Confirm event listener cleanup

### 2. Integration Tests
- Test animations work correctly with React components
- Verify ScrollTrigger integration
- Confirm performance metrics are met
- Validate accessibility compliance

### 3. Visual Regression Tests
- Capture snapshots of animated states
- Compare across different breakpoints
- Verify animations don't cause layout shifts
- Confirm consistent behavior across browsers

## Performance Benchmarks

### 1. Frame Rate
- Target: 60fps on mid-range devices
- Minimum acceptable: 30fps on low-end devices

### 2. Animation Duration
- Entrance animations: 0.4-0.6 seconds
- Hover effects: 0.15-0.2 seconds
- Transitions: Under 0.5 seconds

### 3. Memory Usage
- Prevent memory leaks from uncleared animations
- Proper cleanup of ScrollTrigger instances
- Efficient event listener management

## Browser Compatibility
- Modern browsers supporting CSS transforms and opacity
- IE11+ support if required (with appropriate fallbacks)
- Mobile browser compatibility for touch interactions