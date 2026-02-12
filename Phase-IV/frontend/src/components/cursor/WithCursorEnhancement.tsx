'use client';

import React, { forwardRef } from 'react';
import { useCursor } from './CursorContext';

interface WithCursorEnhancementProps {
  children: React.ReactElement;
  disabled?: boolean;
}

const WithCursorEnhancement = forwardRef<HTMLDivElement, WithCursorEnhancementProps>(
  ({ children, disabled = false }, ref) => {
    const { setIsHovering, setIsActive } = useCursor();

    if (disabled) {
      return children;
    }

    const enhancedChildren = React.cloneElement(children, {
      onMouseEnter: (e: React.MouseEvent) => {
        setIsHovering(true);
        const existingHandler = (children.props as any)?.onMouseEnter;
        if (existingHandler) {
          existingHandler(e);
        }
      },
      onMouseLeave: (e: React.MouseEvent) => {
        setIsHovering(false);
        const existingHandler = (children.props as any)?.onMouseLeave;
        if (existingHandler) {
          existingHandler(e);
        }
      },
      onMouseDown: (e: React.MouseEvent) => {
        setIsActive(true);
        const existingHandler = (children.props as any)?.onMouseDown;
        if (existingHandler) {
          existingHandler(e);
        }
      },
      onMouseUp: (e: React.MouseEvent) => {
        setIsActive(false);
        const existingHandler = (children.props as any)?.onMouseUp;
        if (existingHandler) {
          existingHandler(e);
        }
      },
      onTouchStart: (e: React.TouchEvent) => {
        setIsActive(true);
        const existingHandler = (children.props as any)?.onTouchStart;
        if (existingHandler) {
          existingHandler(e);
        }
      },
      onTouchEnd: (e: React.TouchEvent) => {
        setIsActive(false);
        const existingHandler = (children.props as any)?.onTouchEnd;
        if (existingHandler) {
          existingHandler(e);
        }
      },
      ...(children.props as any || {}),
    } as React.Attributes);

    return <div ref={ref}>{enhancedChildren}</div>;
  }
);

WithCursorEnhancement.displayName = 'WithCursorEnhancement';

export default WithCursorEnhancement;