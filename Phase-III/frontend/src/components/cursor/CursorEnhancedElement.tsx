'use client';

import React, { forwardRef } from 'react';
import { useCursor } from './CursorContext';

interface CursorEnhancedElementProps {
  children: React.ReactElement;
  asChild?: boolean;
  disabled?: boolean;
}

const CursorEnhancedElement = forwardRef<HTMLSpanElement, CursorEnhancedElementProps>(
  ({ children, asChild = false, disabled = false }, ref) => {
    const { setIsHovering, setIsActive } = useCursor();

    if (disabled) {
      return <span ref={ref}>{children}</span>;
    }

    const enhancedProps = {
      onMouseEnter: () => typeof setIsHovering === 'function' && setIsHovering(true),
      onMouseLeave: () => typeof setIsHovering === 'function' && setIsHovering(false),
      onMouseDown: () => typeof setIsActive === 'function' && setIsActive(true),
      onMouseUp: () => typeof setIsActive === 'function' && setIsActive(false),
      onTouchStart: () => typeof setIsActive === 'function' && setIsActive(true),
      onTouchEnd: () => typeof setIsActive === 'function' && setIsActive(false),
    };

    if (asChild) {
      return React.cloneElement(children, {
        ...(children.props || {}),
        ...enhancedProps,
      });
    }

    return (
      <span
        ref={ref}
        {...enhancedProps}
        style={{ display: 'contents' }}
      >
        {children}
      </span>
    );
  }
);

CursorEnhancedElement.displayName = 'CursorEnhancedElement';

export default CursorEnhancedElement;