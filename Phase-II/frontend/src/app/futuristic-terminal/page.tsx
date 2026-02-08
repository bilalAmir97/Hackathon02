'use client';

import React, { useState } from 'react';
import Scanline from '@/components/Scanline';

const FuturisticTerminal = () => {
  const [terminalLines, setTerminalLines] = useState<string[]>([
    '> Initializing system...',
    '> Loading modules...',
    '> Connection established.',
    '> Ready for commands.'
  ]);
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      setTerminalLines(prev => [...prev, `$ ${input}`, 'Command executed.']);
      setInput('');
    }
  };

  return (
    <div className="relative min-h-screen bg-black text-green-400 font-mono overflow-hidden">
      {/* Scanline effect */}
      <Scanline
        speed={4000}
        opacity={0.7}
      />

      {/* Terminal UI */}
      <div className="container mx-auto px-4 py-8 relative z-10">
        <div className="border border-green-600 rounded-lg p-6 max-w-4xl mx-auto bg-gray-900 bg-opacity-50 backdrop-blur-sm">
          <div className="flex items-center mb-4">
            <div className="flex space-x-2 mr-4">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
            <div className="text-sm text-green-600">system@terminal:~</div>
          </div>

          <div className="h-96 overflow-y-auto mb-4 font-mono text-sm">
            {terminalLines.map((line, index) => (
              <div key={index} className="mb-1">
                {line}
              </div>
            ))}
            <form onSubmit={handleSubmit} className="flex items-center">
              <span className="text-green-500 mr-2">$</span>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="bg-transparent border-none outline-none flex-grow text-green-400 font-mono"
                autoFocus
              />
            </form>
          </div>

          <div className="text-xs text-green-700 text-right">
            SYSTEM STATUS: <span className="text-green-400">ONLINE</span>
          </div>
        </div>

        <div className="mt-8 text-center text-green-600 text-sm">
          <p>Futuristic Terminal Interface with Moving Scanline Effect</p>
          <p className="mt-2">The cyan line moving down represents a classic scanline effect</p>
        </div>
      </div>
    </div>
  );
};

export default FuturisticTerminal;