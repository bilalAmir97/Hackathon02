'use client';

import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { usePathname, useSearchParams } from 'next/navigation';
import { useGSAP } from '@gsap/react';

interface TransitionContextType {
  isTransitioning: boolean;
  triggerTransition: (callback: () => void) => void;
}

const TransitionContext = createContext<TransitionContextType | undefined>(undefined);

export const TransitionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [isTransitioning, setIsTransitioning] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const timelineRef = useRef<gsap.core.Timeline | null>(null);

  // Clean up GSAP timeline on unmount
  useEffect(() => {
    return () => {
      if (timelineRef.current) {
        timelineRef.current.kill();
      }
    };
  }, []);

  // Handle page transitions when route changes
  useEffect(() => {
    if (!containerRef.current) return;

    // Kill any existing timeline to prevent conflicts
    if (timelineRef.current) {
      timelineRef.current.kill();
    }

    // Create a new timeline for the transition
    timelineRef.current = gsap.timeline({
      onComplete: () => {
        setIsTransitioning(false);
      }
    });

    // Add fade out and fade in animations to the timeline
    timelineRef.current
      .to(containerRef.current, {
        opacity: 0,
        duration: 0.3,
        ease: 'power2.inOut',
      })
      .to(containerRef.current, {
        opacity: 1,
        duration: 0.3,
        ease: 'power2.inOut',
        onStart: () => setIsTransitioning(true),
      }, '-=0.15'); // Overlap slightly for smoother transition

  }, [pathname, searchParams]);

  const triggerTransition = (callback: () => void) => {
    if (containerRef.current) {
      setIsTransitioning(true);

      // Kill any existing timeline to prevent conflicts
      if (timelineRef.current) {
        timelineRef.current.kill();
      }

      // Create a new timeline for the custom transition
      timelineRef.current = gsap.timeline({
        onComplete: () => {
          callback();
          setIsTransitioning(false);

          // Fade in after callback
          gsap.to(containerRef.current, {
            opacity: 1,
            duration: 0.3,
            ease: 'power2.inOut',
          });
        }
      });

      // Fade out animation
      timelineRef.current.to(containerRef.current, {
        opacity: 0,
        duration: 0.3,
        ease: 'power2.inOut',
      });
    }
  };

  const value = {
    isTransitioning,
    triggerTransition,
  };

  return (
    <TransitionContext.Provider value={value}>
      <div ref={containerRef} className="opacity-100">
        {children}
      </div>
    </TransitionContext.Provider>
  );
};

export const useTransition = () => {
  const context = useContext(TransitionContext);
  if (context === undefined) {
    throw new Error('useTransition must be used within a TransitionProvider');
  }
  return context;
};