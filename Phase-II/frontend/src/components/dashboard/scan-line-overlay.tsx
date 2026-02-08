'use client';

import React from 'react';

export const ScanLineOverlay: React.FC = () => {
  return (
    <div className="fixed inset-0 pointer-events-none z-50 opacity-20">
      <div className="scanline-container">
        <div className="scanline"></div>
      </div>

      {/* Additional electric zap effects for premium futuristic feel */}
      <div className="electric-zap">
        <div className="electric-bolt" style={{ '--zap-delay': '1s' } as React.CSSProperties}></div>
        <div className="electric-bolt" style={{ '--zap-delay': '2.5s' } as React.CSSProperties}></div>
        <div className="electric-bolt" style={{ '--zap-delay': '4s' } as React.CSSProperties}></div>
      </div>
    </div>
  );
};