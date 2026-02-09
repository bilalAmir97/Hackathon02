# Global Custom Cursor System

A holographic cursor system with particle trail effects for the TaskFlow application. This system provides an enhanced user experience with visual feedback for interactive elements while respecting accessibility preferences.

## Features

- **Holographic Cursor**: Glowing dot with blue/purple gradient colors matching the brand theme
- **Particle Trail**: Subtle trail of particles following the cursor movement
- **Interactive Feedback**: Enhanced glow when hovering over buttons/links
- **Click Animations**: Ripple effect on mouse clicks
- **Magnetic Effect**: Slight attraction to interactive elements
- **Accessibility Support**: Respects `prefers-reduced-motion` settings
- **Performance Optimized**: Uses `requestAnimationFrame` for smooth animations

## Components

### CursorProvider
Provides cursor state to the application via React Context.

```tsx
import { CursorProvider } from '@/components/cursor/CursorContext';

export default function MyApp({ children }: { children: React.ReactNode }) {
  return (
    <CursorProvider>
      {children}
    </CursorProvider>
  );
}
```

### GlobalCursor
The main cursor component that renders the holographic cursor and manages its animations.

```tsx
import GlobalCursor from '@/components/cursor/GlobalCursor';

// Automatically included in ClientWrapper
<CursorProvider>
  <GlobalCursor />
  {children}
</CursorProvider>
```

### CursorEnhancedElement
A wrapper component to apply cursor enhancements to interactive elements.

```tsx
import CursorEnhancedElement from '@/components/cursor/CursorEnhancedElement';

function MyButton() {
  return (
    <CursorEnhancedElement>
      <button className="px-4 py-2 bg-blue-500 text-white rounded">
        Click me
      </button>
    </CursorEnhancedElement>
  );
}
```

### WithCursorEnhancement
A higher-order component to wrap existing components with cursor enhancements.

```tsx
import WithCursorEnhancement from '@/components/cursor/WithCursorEnhancement';

function MyComponent() {
  return (
    <WithCursorEnhancement>
      <button>Enhanced Button</button>
    </WithCursorEnhancement>
  );
}
```

### useCursorEnhancement
Custom hook for programmatic cursor enhancement control.

```tsx
import { useCursorEnhancement } from '@/components/cursor/useCursorEnhancement';

function MyCustomComponent() {
  const { enhanceInteractiveElement } = useCursorEnhancement();

  return (
    <button ref={enhanceInteractiveElement}>
      Enhanced Button
    </button>
  );
}
```

## Cursor States

- **Default**: Small glowing dot with subtle pulsation
- **Hover**: Expands slightly with enhanced glow when over interactive elements
- **Active**: Creates ripple effect on click
- **Trail**: Leaves a faint trail of particles as it moves

## Accessibility

The cursor system automatically detects and respects the user's `prefers-reduced-motion` setting. When this preference is enabled:

- All cursor animations are disabled
- The cursor becomes invisible to avoid motion triggers
- Interactive elements continue to work normally

## Integration

The cursor system is automatically integrated into the application through the `ClientWrapper` component. No additional setup is required for global functionality.

## Performance

The cursor system is optimized for performance:

- Uses `requestAnimationFrame` for smooth animations
- Efficient particle system with automatic cleanup
- Proper cleanup of event listeners
- Memoized state updates

## Brand Colors

The cursor uses the following brand colors:
- Primary: Blue (`#3b82f6`)
- Secondary: Purple (`#8b5cf6`)
- Gradient: Blue to purple transition

These colors match the existing brand theme of the application.