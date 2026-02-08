'use client';

import { useCallback } from 'react';
import { useCursor } from './CursorContext';

// Custom hook to provide cursor enhancement functions
export const useCursorEnhancement = () => {
  const { setIsHovering, setIsActive } = useCursor();

  const enhanceInteractiveElement = useCallback(
    (element: HTMLElement | null) => {
      if (!element) return;

      const handleMouseEnter = () => setIsHovering(true);
      const handleMouseLeave = () => setIsHovering(false);
      const handleMouseDown = () => setIsActive(true);
      const handleMouseUp = () => setIsActive(false);

      element.addEventListener('mouseenter', handleMouseEnter);
      element.addEventListener('mouseleave', handleMouseLeave);
      element.addEventListener('mousedown', handleMouseDown);
      element.addEventListener('mouseup', handleMouseUp);

      // Cleanup function
      return () => {
        element.removeEventListener('mouseenter', handleMouseEnter);
        element.removeEventListener('mouseleave', handleMouseLeave);
        element.removeEventListener('mousedown', handleMouseDown);
        element.removeEventListener('mouseup', handleMouseUp);
      };
    },
    [setIsHovering, setIsActive]
  );

  return { enhanceInteractiveElement };
};