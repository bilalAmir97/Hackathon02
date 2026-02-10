import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register plugins
gsap.registerPlugin(ScrollTrigger);

/**
 * Optimized animations for 60fps performance
 * Uses transform and opacity properties which are GPU-accelerated
 */

/**
 * Page Transition Animations
 */
export const animatePageLoad = () => {
  // Animate elements with data-animate attribute
  gsap.from('[data-animate]', {
    duration: 0.6, // Reduced duration for better performance
    opacity: 0,
    y: 30,
    stagger: 0.1,
    ease: 'power2.out', // Simpler easing for better performance
    scrollTrigger: {
      trigger: '[data-animate]',
      start: 'top 90%',
    }
  });
};

/**
 * Fade In Animation
 */
export const fadeIn = (element: HTMLElement | null, delay: number = 0) => {
  if (!element) return;

  // Use transform3d to promote to GPU layer for better performance
  gsap.set(element, {
    transformStyle: 'preserve-3d',
    perspective: 1000,
    force3D: true
  });

  gsap.fromTo(element,
    { opacity: 0, y: 20, scale: 0.98 },
    {
      opacity: 1,
      y: 0,
      scale: 1,
      duration: 0.4, // Reduced duration
      delay,
      ease: 'power2.out', // Simpler easing
      overwrite: 'auto', // Prevent memory leaks
      clearProps: 'transform' // Clean up transform properties after animation
    }
  );
};

/**
 * Slide In From Left
 */
export const slideInFromLeft = (element: HTMLElement | null, delay: number = 0) => {
  if (!element) return;

  gsap.set(element, {
    transformStyle: 'preserve-3d',
    perspective: 1000,
    force3D: true
  });

  gsap.fromTo(element,
    { opacity: 0, x: -50, scale: 0.98 },
    {
      opacity: 1,
      x: 0,
      scale: 1,
      duration: 0.4, // Reduced duration
      delay,
      ease: 'power2.out', // Simpler easing
      overwrite: 'auto',
      clearProps: 'transform'
    }
  );
};

/**
 * Slide In From Right
 */
export const slideInFromRight = (element: HTMLElement | null, delay: number = 0) => {
  if (!element) return;

  gsap.set(element, {
    transformStyle: 'preserve-3d',
    perspective: 1000,
    force3D: true
  });

  gsap.fromTo(element,
    { opacity: 0, x: 50, scale: 0.98 },
    {
      opacity: 1,
      x: 0,
      scale: 1,
      duration: 0.4, // Reduced duration
      delay,
      ease: 'power2.out', // Simpler easing
      overwrite: 'auto',
      clearProps: 'transform'
    }
  );
};

/**
 * Task Item Animation
 */
export const animateTaskItem = (element: HTMLElement | null, index: number = 0) => {
  if (!element) return;

  gsap.set(element, {
    transformStyle: 'preserve-3d',
    perspective: 1000,
    force3D: true
  });

  gsap.fromTo(element,
    { opacity: 0, scale: 0.95, y: 15, rotationX: 15 }, // Added subtle 3D rotation
    {
      opacity: 1,
      scale: 1,
      y: 0,
      rotationX: 0,
      duration: 0.3, // Reduced duration
      delay: Math.min(index * 0.03, 0.2), // Cap the delay to prevent long waits
      ease: 'back.out(1.4)', // Slightly simplified
      overwrite: 'auto',
      clearProps: 'transform'
    }
  );
};

/**
 * Staggered Task List Animation
 */
export const animateTaskList = (elements: NodeListOf<Element> | Element[] | null) => {
  if (!elements) return;

  // Convert to array and limit to prevent too many animations
  const limitedElements = Array.from(elements).slice(0, 20); // Limit to 20 elements

  gsap.fromTo(limitedElements,
    { opacity: 0, y: 15, scale: 0.98 },
    {
      opacity: 1,
      y: 0,
      scale: 1,
      duration: 0.4, // Reduced duration
      stagger: 0.05, // Faster stagger
      ease: 'power2.out', // Simpler easing
      overwrite: 'auto',
      clearProps: 'transform'
    }
  );
};

/**
 * Button Hover Animation - Optimized
 */
export const addButtonHoverAnimation = (element: HTMLElement | null) => {
  if (!element) return;

  // Store original scale to prevent accumulation
  let originalScale = 1;

  const mouseEnterHandler = () => {
    gsap.to(element, {
      scale: 1.03, // Reduced scale for better performance
      duration: 0.15, // Faster animation
      ease: 'power2.out',
      overwrite: 'auto'
    });
  };

  const mouseLeaveHandler = () => {
    gsap.to(element, {
      scale: originalScale,
      duration: 0.15, // Faster animation
      ease: 'power2.out',
      overwrite: 'auto'
    });
  };

  // Add event listeners
  element.addEventListener('mouseenter', mouseEnterHandler);
  element.addEventListener('mouseleave', mouseLeaveHandler);

  // Store handlers for potential cleanup
  (element as any).__hoverHandlers = { mouseEnterHandler, mouseLeaveHandler };
};

/**
 * Remove hover animation handlers
 */
export const removeButtonHoverAnimation = (element: HTMLElement | null) => {
  if (!element || !(element as any).__hoverHandlers) return;

  const { mouseEnterHandler, mouseLeaveHandler } = (element as any).__hoverHandlers;

  element.removeEventListener('mouseenter', mouseEnterHandler);
  element.removeEventListener('mouseleave', mouseLeaveHandler);

  // Clean up stored handlers
  delete (element as any).__hoverHandlers;
};

/**
 * Cleanup function to kill all animations
 */
export const killAllAnimations = () => {
  gsap.killTweensOf('*');
  ScrollTrigger.getAll().forEach(trigger => trigger.kill());

  // Clean up any leftover hover animations
  document.querySelectorAll('[data-hover-animation]').forEach(el => {
    removeButtonHoverAnimation(el as HTMLElement);
  });
};

/**
 * Performance-optimized animation for frequently triggered animations
 */
export const quickAnimation = (element: HTMLElement | null, properties: any) => {
  if (!element) return;

  gsap.to(element, {
    ...properties,
    duration: 0.2, // Very fast for frequent triggers
    ease: 'power1.out',
    overwrite: 'auto',
    onComplete: () => {
      // Clean up any temporary properties
      if (properties.clearProps) {
        gsap.set(element, { clearProps: properties.clearProps });
      }
    }
  });
};