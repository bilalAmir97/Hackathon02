'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface CursorContextType {
  isHovering: boolean;
  setIsHovering: (hovering: boolean) => void;
  isActive: boolean;
  setIsActive: (active: boolean) => void;
}

const CursorContext = createContext<CursorContextType | undefined>(undefined);

export const useCursor = () => {
  const context = useContext(CursorContext);
  if (!context) {
    // Return default values during SSR or when context is not available
    return {
      isHovering: false,
      setIsHovering: () => {},
      isActive: false,
      setIsActive: () => {},
    };
  }
  return context;
};

interface CursorProviderProps {
  children: ReactNode;
}

export const CursorProvider: React.FC<CursorProviderProps> = ({ children }) => {
  const [isHovering, setIsHovering] = useState(false);
  const [isActive, setIsActive] = useState(false);

  return (
    <CursorContext.Provider value={{ isHovering, setIsHovering, isActive, setIsActive }}>
      {children}
    </CursorContext.Provider>
  );
};