import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';

interface DashboardEntranceProps {
  children: React.ReactNode;
  className?: string;
}

export const DashboardEntrance: React.FC<DashboardEntranceProps> = ({ children, className = '' }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      // Animate child elements on mount
      const childElements = containerRef.current.children;

      Array.from(childElements).forEach((child, index) => {
        gsap.from(child, {
          duration: 0.8,
          opacity: 0,
          y: 30,
          delay: index * 0.1, // Stagger the animation
          ease: 'power3.out'
        });
      });
    }
  }, []);

  return (
    <div ref={containerRef} className={className}>
      {children}
    </div>
  );
};