import { useState, useEffect } from 'react';

export const useBreakpoint = () => {
  const [breakpoint, setBreakpoint] = useState<string>('mobile');
  const [screenSize, setScreenSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const updateBreakpoint = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;

      setScreenSize({ width, height });

      if (width < 640) {
        setBreakpoint('mobile');
      } else if (width >= 640 && width < 768) {
        setBreakpoint('mobile-lg');
      } else if (width >= 768 && width < 1024) {
        setBreakpoint('tablet');
      } else if (width >= 1024 && width < 1280) {
        setBreakpoint('desktop');
      } else if (width >= 1280 && width < 1536) {
        setBreakpoint('desktop-lg');
      } else {
        setBreakpoint('ultra-wide');
      }
    };

    // Initial check
    updateBreakpoint();

    // Add resize listener
    window.addEventListener('resize', updateBreakpoint);

    // Cleanup
    return () => window.removeEventListener('resize', updateBreakpoint);
  }, []);

  return {
    breakpoint,
    screenSize,
    isMobile: breakpoint === 'mobile' || breakpoint === 'mobile-lg',
    isTablet: breakpoint === 'tablet',
    isDesktop: breakpoint === 'desktop' || breakpoint === 'desktop-lg',
    isUltraWide: breakpoint === 'ultra-wide',
    isMobileUp: breakpoint !== 'mobile',
    isTabletUp: ['tablet', 'desktop', 'desktop-lg', 'ultra-wide'].includes(breakpoint),
    isDesktopUp: ['desktop', 'desktop-lg', 'ultra-wide'].includes(breakpoint),
  };
};