import { useEffect, useRef } from 'react';
import {
  animatePageLoad,
  fadeIn,
  slideInFromLeft,
  slideInFromRight,
  animateTaskItem,
  animateTaskList,
  addButtonHoverAnimation,
  removeButtonHoverAnimation,
  quickAnimation
} from '@/lib/gsap-animations';

export const useGsapAnimations = () => {
  // Hook to handle page load animations
  useEffect(() => {
    animatePageLoad();
  }, []);

  // Hook to animate a single element
  const useFadeIn = (delay: number = 0) => {
    const elementRef = useRef<HTMLElement>(null);

    useEffect(() => {
      fadeIn(elementRef.current, delay);

      // Cleanup function to kill animations on unmount
      return () => {
        if (elementRef.current) {
          // No need to manually kill this animation as it's handled by GSAP's overwrite property
        }
      };
    }, [delay]);

    return elementRef;
  };

  // Hook to animate element sliding in from left
  const useSlideInFromLeft = (delay: number = 0) => {
    const elementRef = useRef<HTMLElement>(null);

    useEffect(() => {
      slideInFromLeft(elementRef.current, delay);

      // Cleanup function
      return () => {
        if (elementRef.current) {
          // No need to manually kill this animation as it's handled by GSAP's overwrite property
        }
      };
    }, [delay]);

    return elementRef;
  };

  // Hook to animate element sliding in from right
  const useSlideInFromRight = (delay: number = 0) => {
    const elementRef = useRef<HTMLElement>(null);

    useEffect(() => {
      slideInFromRight(elementRef.current, delay);

      // Cleanup function
      return () => {
        if (elementRef.current) {
          // No need to manually kill this animation as it's handled by GSAP's overwrite property
        }
      };
    }, [delay]);

    return elementRef;
  };

  // Hook to animate task items
  const useAnimateTaskItem = (index: number = 0) => {
    const elementRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
      animateTaskItem(elementRef.current, index);

      // Cleanup function
      return () => {
        if (elementRef.current) {
          // No need to manually kill this animation as it's handled by GSAP's overwrite property
        }
      };
    }, [index]);

    return elementRef;
  };

  // Hook to animate button hover effects
  const useButtonHoverAnimation = () => {
    const elementRef = useRef<HTMLButtonElement>(null);

    useEffect(() => {
      if (elementRef.current) {
        addButtonHoverAnimation(elementRef.current);

        // Store element for cleanup
        (elementRef.current as any).__cleanupAnimation = true;
      }

      // Cleanup function
      return () => {
        if (elementRef.current) {
          removeButtonHoverAnimation(elementRef.current);
        }
      };
    }, []);

    return elementRef;
  };

  return {
    useFadeIn,
    useSlideInFromLeft,
    useSlideInFromRight,
    useAnimateTaskItem,
    useButtonHoverAnimation,
    animateTaskList,
    quickAnimation,
  };
};