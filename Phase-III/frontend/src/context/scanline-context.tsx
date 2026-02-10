'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface ScanlineContextType {
  isEnabled: boolean;
  setIsEnabled: (enabled: boolean) => void;
  speed: number;
  setSpeed: (speed: number) => void;
  height: string;
  setHeight: (height: string) => void;
  color: string;
  setColor: (color: string) => void;
  opacity: number;
  setOpacity: (opacity: number) => void;
}

const ScanlineContext = createContext<ScanlineContextType | undefined>(undefined);

export const ScanlineProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isEnabled, setIsEnabled] = useState(true);
  const [speed, setSpeed] = useState(4000); // 4 seconds
  const [height, setHeight] = useState('2px');
  const [color, setColor] = useState('rgba(0, 255, 255, 0.8)');
  const [opacity, setOpacity] = useState(0.8);

  return (
    <ScanlineContext.Provider
      value={{
        isEnabled,
        setIsEnabled,
        speed,
        setSpeed,
        height,
        setHeight,
        color,
        setColor,
        opacity,
        setOpacity,
      }}
    >
      {children}
    </ScanlineContext.Provider>
  );
};

export const useScanline = (): ScanlineContextType => {
  const context = useContext(ScanlineContext);
  if (!context) {
    throw new Error('useScanline must be used within a ScanlineProvider');
  }
  return context;
};