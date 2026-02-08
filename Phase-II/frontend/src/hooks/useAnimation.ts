import { useEffect, useRef } from 'react';
import gsap from 'gsap';

export const useAnimation = () => {
  const animateOnMount = (selector: string, fromVars: gsap.TweenVars, toVars: gsap.TweenVars = {}) => {
    const elementRef = useRef<HTMLElement | null>(null);

    useEffect(() => {
      if (elementRef.current) {
        gsap.fromTo(elementRef.current, fromVars, { ...toVars, duration: toVars.duration || 0.8 });
      }

      return () => {
        // Cleanup animation if needed
      };
    }, []);

    return elementRef;
  };

  const animateSequence = (selector: string, staggerVars: gsap.TweenVars, options: { stagger?: number } = {}) => {
    useEffect(() => {
      const elements = document.querySelectorAll(selector);
      if (elements.length > 0) {
        gsap.from(elements, {
          ...staggerVars,
          stagger: options.stagger || 0.1,
          duration: staggerVars.duration || 0.8
        });
      }
    }, []);
  };

  const animateHover = (selector: string, hoverVars: gsap.TweenVars, leaveVars: gsap.TweenVars) => {
    useEffect(() => {
      const elements = document.querySelectorAll(selector);

      elements.forEach(el => {
        el.addEventListener('mouseenter', () => {
          gsap.to(el, { ...hoverVars, duration: hoverVars.duration || 0.3 });
        });

        el.addEventListener('mouseleave', () => {
          gsap.to(el, { ...leaveVars, duration: leaveVars.duration || 0.3 });
        });
      });

      return () => {
        elements.forEach(el => {
          el.removeEventListener('mouseenter', () => {});
          el.removeEventListener('mouseleave', () => {});
        });
      };
    }, []);
  };

  return {
    animateOnMount,
    animateSequence,
    animateHover
  };
};