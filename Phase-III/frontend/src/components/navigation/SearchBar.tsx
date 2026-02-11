import React, { useState, useEffect, useRef } from 'react';

interface SearchBarProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = 'Search tasks, projects, or people...',
  onSearch
}) => {
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(query);
    }
  };

  const handleIconClick = () => {
    if (onSearch) {
      onSearch(query);
    }
  };

  // Handle keyboard shortcut for focusing search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Check if Cmd+K (Mac) or Ctrl+K (Windows/Linux) is pressed
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault(); // Stop default browser behavior

        // Set focus to the search input field
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }
    };

    // Add event listener to the document
    document.addEventListener('keydown', handleKeyDown);

    // Cleanup: remove event listener when component unmounts
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  return (
    <form onSubmit={handleSubmit} className="w-full relative z-10">
      <div className="relative z-10">
        <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none z-0">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-[var(--text-secondary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            console.log('Input changed:', e.target.value);
            setQuery(e.target.value);
          }}
          onFocus={() => console.log('Input focused')}
          onBlur={() => console.log('Input blurred')}
          onClick={() => console.log('Input clicked')}
          placeholder={placeholder}
          autoComplete="off"
          disabled={false}
          readOnly={false}
          className="relative z-20 w-full pl-10 pr-4 sm:pr-14 py-2 border border-[var(--glass-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--primary-accent)] focus:border-transparent cursor-text"
          style={{
            pointerEvents: 'auto',
            color: '#000000',
            backgroundColor: '#ffffff',
            caretColor: '#000000'
          }}
        />
        <div className="absolute inset-y-0 right-0 items-center pr-3 hidden sm:flex pointer-events-none z-0">
          <kbd className="px-2 py-1 text-xs font-semibold text-[var(--text-secondary)] bg-[var(--soft-dark-bg-secondary)] border border-[var(--glass-border)] rounded-md">
            ⌘K
          </kbd>
        </div>
      </div>
    </form>
  );
};