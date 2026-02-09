'use client';

import React, { useEffect, useRef } from 'react';

interface ScanlineProps {
  speed?: number;
  height?: string;
  color?: string;
  opacity?: number;
}

const Scanline: React.FC<ScanlineProps> = ({
  speed = 4000,
  height = '100%',
  color = 'transparent',
  opacity = 0.7
}) => {
  const scanlineRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!scanlineRef.current) return;

    let animationFrameId: number;
    let startTime: number | null = null;
    const element = scanlineRef.current;

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;

      const elapsed = timestamp - startTime;
      const progress = (elapsed % speed) / speed;
      const translateX = `${progress * 100}%`;

      element.style.transform = `translateX(${translateX})`;

      animationFrameId = requestAnimationFrame(animate);
    };

    animationFrameId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [speed]);

  return (
    <div
      className="scanline-container fixed top-0 left-0 w-full h-full pointer-events-none z-[9999]"
      style={{ zIndex: 9999, overflow: 'hidden' }}
    >
      <div
        ref={scanlineRef}
        className="scanline absolute top-0 w-[200%]"
        style={{
          height: height,
          background: `linear-gradient(90deg, transparent 0%, ${color || 'rgba(100, 200, 255, 0.3)'} 25%, rgba(0, 100, 255, 0.15) 50%, transparent 100%)`,
          opacity,
          mixBlendMode: 'screen',
          filter: 'brightness(1.2) contrast(1.3)',
          willChange: 'transform',
        }}
      />
    </div>
  );
};

export default Scanline;