'use client';

import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { ChatWidget } from './ChatWidget';
import { useAuth } from '@/hooks/useAuth';

/**
 * Floating Chat Button
 *
 * A fixed button in the bottom-right corner that opens an inline chat widget
 * without navigating away from the current page.
 * Features premium animations: breathing effect, rotating gradient, pulsing dots
 * Only visible to authenticated users.
 */
export function FloatingChatButton() {
  const pathname = usePathname();
  const [isHovered, setIsHovered] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  // Only render after client-side mount to ensure AuthProvider is available
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Don't render until mounted (prevents SSR issues with AuthProvider)
  if (!isMounted) {
    return null;
  }

  // Now we can safely use useAuth after mount
  return <FloatingChatButtonInner
    pathname={pathname}
    isHovered={isHovered}
    setIsHovered={setIsHovered}
    isChatOpen={isChatOpen}
    setIsChatOpen={setIsChatOpen}
  />;
}

function FloatingChatButtonInner({
  pathname,
  isHovered,
  setIsHovered,
  isChatOpen,
  setIsChatOpen
}: {
  pathname: string;
  isHovered: boolean;
  setIsHovered: (value: boolean) => void;
  isChatOpen: boolean;
  setIsChatOpen: (value: boolean) => void;
}) {
  const { user, loading } = useAuth();

  // Only show chat button to authenticated users
  if (loading) {
    return null; // Don't show while checking auth status
  }

  if (!user) {
    return null; // Hide from unauthenticated users
  }

  // Hide the button on the chat page itself to avoid redundancy
  if (pathname === '/chat') {
    return null;
  }

  const handleClick = () => {
    setIsChatOpen(true);
  };

  const handleClose = () => {
    setIsChatOpen(false);
  };

  return (
    <>
      <style jsx>{`
        @keyframes breathe {
          0%, 100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.05);
          }
        }

        @keyframes rotate-gradient {
          0% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
          100% {
            background-position: 0% 50%;
          }
        }

        @keyframes pulse-dot {
          0%, 100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.5;
            transform: scale(1.3);
          }
        }

        @keyframes shimmer {
          0% {
            transform: translateX(-100%) rotate(45deg);
          }
          100% {
            transform: translateX(200%) rotate(45deg);
          }
        }

        .chat-button {
          animation: breathe 3s ease-in-out infinite;
        }

        .chat-button:hover {
          animation: breathe 1.5s ease-in-out infinite;
        }

        .gradient-bg {
          background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899, #3b82f6);
          background-size: 300% 300%;
          animation: rotate-gradient 6s ease infinite;
        }

        .shimmer-effect {
          position: absolute;
          top: -50%;
          left: -50%;
          width: 200%;
          height: 200%;
          background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.3),
            transparent
          );
          animation: shimmer 3s infinite;
        }

        .dot {
          width: 4px;
          height: 4px;
          background: white;
          border-radius: 50%;
          animation: pulse-dot 1.5s ease-in-out infinite;
        }

        .dot:nth-child(1) {
          animation-delay: 0s;
        }

        .dot:nth-child(2) {
          animation-delay: 0.2s;
        }

        .dot:nth-child(3) {
          animation-delay: 0.4s;
        }
      `}</style>

      <button
        onClick={handleClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className="fixed bottom-6 right-6 z-50 group"
        aria-label="Open AI Chat"
      >
        {/* Main button circle */}
        <div className="relative chat-button">
          {/* Outer glow rings */}
          <div className="absolute inset-0 rounded-full">
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] opacity-20 blur-xl animate-pulse" />
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] opacity-30 blur-lg"
                 style={{ animation: 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite' }} />
          </div>

          {/* Enhanced glow effect on hover */}
          <div
            className={`absolute inset-0 rounded-full bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] blur-xl transition-all duration-500 ${
              isHovered ? 'opacity-90 scale-110' : 'opacity-0 scale-100'
            }`}
          />

          {/* Button with animated gradient */}
          <div className="relative w-14 h-14 sm:w-16 sm:h-16 rounded-full gradient-bg flex items-center justify-center shadow-2xl hover:shadow-3xl transition-all duration-300 overflow-hidden">
            {/* Shimmer effect */}
            <div className="shimmer-effect" />

            {/* Pulsing dots icon (instead of static chat icon) */}
            <div className="relative flex items-center space-x-1.5 z-10">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
          </div>
        </div>

        {/* Enhanced tooltip on hover */}
        <div
          className={`absolute bottom-full right-0 mb-3 px-4 py-2.5 bg-[var(--soft-dark-bg)] backdrop-blur-xl border border-[var(--glass-border)] rounded-xl shadow-2xl whitespace-nowrap transition-all duration-300 ${
            isHovered ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-2 scale-95 pointer-events-none'
          }`}
          style={{
            background: 'rgba(17, 24, 39, 0.95)',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)'
          }}
        >
          <span className="text-sm text-[var(--text-primary)] font-medium bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] bg-clip-text text-transparent">
            Chat with AI Assistant
          </span>
          {/* Tooltip arrow */}
          <div className="absolute top-full right-6 w-0 h-0 border-l-[6px] border-r-[6px] border-t-[6px] border-transparent border-t-[var(--glass-border)]" />
        </div>
      </button>

      {/* Chat Widget - only render when open */}
      {isChatOpen && <ChatWidget isOpen={isChatOpen} onClose={handleClose} />}
    </>
  );
}
