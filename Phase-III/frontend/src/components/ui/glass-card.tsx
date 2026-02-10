'use client';

import React, { forwardRef } from 'react';
import { motion } from 'framer-motion';

export interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
  className?: string;
  variant?: 'default' | 'elevated' | 'floating';
  animate?: boolean;
  delay?: number;
}

const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  ({ children, className = '', variant = 'default', animate = false, delay = 0, ...props }, ref) => {
    const baseClasses = 'futuristic-glass-card rounded-xl border border-white/10 backdrop-blur-md bg-black/10 shadow-lg';

    const variantClasses = {
      default: '',
      elevated: 'shadow-xl',
      floating: 'shadow-2xl hover:shadow-3xl transition-all duration-300 hover:-translate-y-1'
    };

    const combinedClasses = `${baseClasses} ${variantClasses[variant]} ${className}`;

    if (animate) {
      return (
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.5,
            delay: delay * 0.1,
            ease: "easeOut"
          }}
          className={combinedClasses}
          {...props}
        >
          {children}
        </motion.div>
      );
    }

    return (
      <div
        ref={ref}
        className={combinedClasses}
        {...props}
      >
        {children}
      </div>
    );
  }
);

GlassCard.displayName = 'GlassCard';

export { GlassCard };