import { useState, useEffect } from 'react';

export const useSidebarToggle = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Check window size on initial render and when resizing
  useEffect(() => {
    const handleResize = () => {
      // On mobile devices, sidebar should be collapsed by default
      if (window.innerWidth < 768) {
        setIsCollapsed(true);
      } else {
        // For larger screens, use the default state (false = expanded)
        setIsCollapsed(false);
      }
    };

    // Run once on mount
    handleResize();

    // Add resize listener
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const expandSidebar = () => {
    setIsCollapsed(false);
  };

  const collapseSidebar = () => {
    setIsCollapsed(true);
  };

  return {
    isCollapsed,
    toggleSidebar,
    expandSidebar,
    collapseSidebar
  };
};