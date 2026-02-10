import React from 'react';
import { useBreakpoint } from '@/hooks/useBreakpoint';

interface ResponsiveDashboardProps {
  children: React.ReactNode;
}

export const ResponsiveDashboard: React.FC<ResponsiveDashboardProps> = ({ children }) => {
  const { breakpoint, isMobile, isTablet, isDesktop, isUltraWide } = useBreakpoint();

  // Apply responsive classes based on breakpoint
  const getResponsiveClass = () => {
    if (isMobile) {
      return 'p-4'; // Smaller padding on mobile
    } else if (isTablet) {
      return 'p-6'; // Medium padding on tablet
    } else {
      return 'p-8'; // Larger padding on desktop and above
    }
  };

  return (
    <div className={`${getResponsiveClass()} ${isMobile ? 'max-w-full' : 'max-w-7xl'} mx-auto`}>
      {children}
    </div>
  );
};