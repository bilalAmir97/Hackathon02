'use client';

import React, { ReactNode } from 'react';
import { useScanline } from '@/context/scanline-context';
import Scanline from '@/components/Scanline';

interface LayoutWithScanlineProps {
  children: ReactNode;
}

const LayoutWithScanline: React.FC<LayoutWithScanlineProps> = ({ children }) => {
  const { isEnabled } = useScanline();

  return (
    <>
      {children}
      {isEnabled && <Scanline />}
    </>
  );
};

export default LayoutWithScanline;