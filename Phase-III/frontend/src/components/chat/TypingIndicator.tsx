/**
 * TypingIndicator Component
 *
 * Premium animated indicator with glowing pulsing dots.
 */

'use client';

/**
 * TypingIndicator component with premium pulsing glow animation
 */
export function TypingIndicator() {
  return (
    <div className="flex w-full mb-4 justify-start" role="status" aria-live="polite" aria-label="AI is typing">
      <div className="bg-white text-gray-900 border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
        <div className="flex space-x-2 items-center">
          <style jsx>{`
            @keyframes glow-pulse {
              0%, 100% {
                opacity: 1;
                transform: scale(1);
              }
              50% {
                opacity: 0.5;
                transform: scale(1.2);
              }
            }
            .dot {
              width: 10px;
              height: 10px;
              background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
              border-radius: 50%;
              animation: glow-pulse 1.4s ease-in-out infinite;
              box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
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
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
        </div>
        <span className="sr-only">AI is typing a response</span>
      </div>
    </div>
  );
}
