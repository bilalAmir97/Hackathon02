/**
 * NewChatButton Component
 *
 * Button to create a new conversation.
 */

'use client';

interface NewChatButtonProps {
  onClick: () => void;
}

/**
 * NewChatButton component
 */
export function NewChatButton({ onClick }: NewChatButtonProps) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
    >
      <svg
        className="h-5 w-5"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path d="M12 4v16m8-8H4" />
      </svg>
      <span className="font-medium">New Chat</span>
    </button>
  );
}
