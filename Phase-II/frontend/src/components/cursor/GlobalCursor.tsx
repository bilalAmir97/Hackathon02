'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useCursor } from './CursorContext';

interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  opacity: number;
  life: number;
  speedX: number;
  speedY: number;
}

const GlobalCursor: React.FC = () => {
  const cursorContext = useCursor();
  const isHovering = cursorContext?.isHovering || false;
  const isActive = cursorContext?.isActive || false;
  const cursorRef = useRef<HTMLDivElement>(null);
  const trailRef = useRef<HTMLDivElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const animationFrameRef = useRef<number>(0);
  const lastPositionRef = useRef({ x: 0, y: 0 });
  const particleIdCounter = useRef(0);
  const [isVisible, setIsVisible] = useState(true);

  // Check for reduced motion preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    const handleMotionChange = (e: MediaQueryListEvent) => {
      setIsVisible(!e.matches);
    };

    setIsVisible(!mediaQuery.matches);

    mediaQuery.addEventListener('change', handleMotionChange);

    return () => {
      mediaQuery.removeEventListener('change', handleMotionChange);
    };
  }, []);

  // Mouse move handler
  useEffect(() => {
    if (!isVisible) return;

    const handleMouseMove = (e: MouseEvent) => {
      const cursor = cursorRef.current;
      const trail = trailRef.current;

      if (cursor) {
        cursor.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`;
      }

      if (trail) {
        // Add delay to trail
        setTimeout(() => {
          if (trail) {
            trail.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`;
          }
        }, 50);
      }

      // Update last position for particles
      lastPositionRef.current = { x: e.clientX, y: e.clientY };

      // Add particles occasionally for trail effect
      if (Math.random() < 0.3) {
        particleIdCounter.current += 1;
        const newParticle: Particle = {
          id: particleIdCounter.current,
          x: e.clientX,
          y: e.clientY,
          size: Math.random() * 3 + 1,
          opacity: 1,
          life: 30,
          speedX: (Math.random() - 0.5) * 2,
          speedY: (Math.random() - 0.5) * 2,
        };
        particlesRef.current.push(newParticle);
      }
    };

    const handleClick = () => {
      // Trigger ripple effect
      const cursor = cursorRef.current;
      if (cursor) {
        cursor.classList.add('animate-ripple');
        setTimeout(() => {
          cursor.classList.remove('animate-ripple');
        }, 600);
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('click', handleClick);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('click', handleClick);
      cancelAnimationFrame(animationFrameRef.current);
    };
  }, [isVisible]);

  // Animation loop for particles
  useEffect(() => {
    if (!isVisible) return;

    const animateParticles = () => {
      particlesRef.current = particlesRef.current
        .map(particle => ({
          ...particle,
          x: particle.x + particle.speedX,
          y: particle.y + particle.speedY,
          opacity: particle.opacity - 0.03,
          life: particle.life - 1,
        }))
        .filter(particle => particle.life > 0 && particle.opacity > 0);

      animationFrameRef.current = requestAnimationFrame(animateParticles);
    };

    animationFrameRef.current = requestAnimationFrame(animateParticles);

    return () => {
      cancelAnimationFrame(animationFrameRef.current);
    };
  }, [isVisible]);

  if (!isVisible) {
    return null;
  }

  return (
    <>
      {/* Main cursor */}
      <div
        ref={cursorRef}
        className={`fixed top-0 left-0 w-4 h-4 rounded-full pointer-events-none z-[9999] transition-all duration-200 ease-out ${
          isActive
            ? 'bg-purple-500 scale-150 shadow-[0_0_20px_5px_rgba(139,92,246,0.6)]'
            : isHovering
              ? 'bg-blue-500 scale-125 shadow-[0_0_15px_3px_rgba(59,130,246,0.5)]'
              : 'bg-blue-400 shadow-[0_0_10px_2px_rgba(59,130,246,0.3)]'
        }`}
      />

      {/* Trail */}
      <div
        ref={trailRef}
        className="fixed top-0 left-0 w-2 h-2 rounded-full bg-blue-300 opacity-60 pointer-events-none z-[9998] transition-opacity duration-300"
      />

      {/* Particles */}
      {particlesRef.current.map((particle) => (
        <div
          key={particle.id}
          className="fixed w-1 h-1 rounded-full pointer-events-none z-[9997]"
          style={{
            left: particle.x,
            top: particle.y,
            width: particle.size,
            height: particle.size,
            backgroundColor: '#8b5cf6',
            opacity: particle.opacity,
            transform: 'translate(-50%, -50%)',
          }}
        />
      ))}

      {/* Ripple effect container */}
      <style jsx global>{`
        @keyframes ripple {
          0% {
            box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.7);
            transform: translate(-50%, -50%) scale(1);
          }
          70% {
            box-shadow: 0 0 0 10px rgba(139, 92, 246, 0);
            transform: translate(-50%, -50%) scale(1.5);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(139, 92, 246, 0);
            transform: translate(-50%, -50%) scale(1);
          }
        }

        .animate-ripple {
          animation: ripple 0.6s linear;
        }
      `}</style>
    </>
  );
};

export default GlobalCursor;