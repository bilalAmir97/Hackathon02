'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';

export const UserProfileMenu: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuth();

  const toggleMenu = () => setIsOpen(!isOpen);

  const handleClickOutside = (event: MouseEvent) => {
    if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
      setIsOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Function to generate initials from email
  const getUserInitials = (email: string) => {
    const emailParts = email.split('@')[0].split('.');
    if (emailParts.length >= 2) {
      return (emailParts[0][0] + emailParts[1][0]).toUpperCase();
    } else {
      return emailParts[0].substring(0, 2).toUpperCase();
    }
  };

  // Function to get display name from email (fallback)
  const getUserDisplayName = (email: string) => {
    const emailPrefix = email.split('@')[0];
    const parts = emailPrefix.split('.');
    if (parts.length >= 2) {
      const firstName = parts[0].charAt(0).toUpperCase() + parts[0].slice(1);
      const lastName = parts[1].charAt(0).toUpperCase() + parts[1].slice(1);
      return `${firstName} ${lastName}`;
    } else {
      // If no dots, capitalize the first letter and add the rest
      return emailPrefix.charAt(0).toUpperCase() + emailPrefix.slice(1);
    }
  };

  const handleLogout = () => {
    logout();
  };

  // Use user data if available, fallback to default values
  const displayName = user ? getUserDisplayName(user.email) : 'User';
  const userEmail = user ? user.email : 'user@example.com';
  const initials = user ? getUserInitials(user.email) : 'UN';

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={toggleMenu}
        className="flex items-center text-sm rounded-full focus:outline-none"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <span className="sr-only">Open user menu</span>
        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] flex items-center justify-center text-white font-medium">
          {initials}
        </div>
      </button>

      {isOpen && (
        <div
          className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-[var(--soft-dark-bg)] ring-1 ring-[var(--glass-border)] divide-y divide-[var(--glass-border)] focus:outline-none"
          role="menu"
          aria-orientation="vertical"
          aria-labelledby="user-menu"
        >
          <div className="px-4 py-3">
            <p className="text-sm font-medium text-[var(--text-primary)]">{displayName}</p>
            <p className="text-xs text-[var(--text-secondary)]">{userEmail}</p>
          </div>
          <div className="py-1" role="none">
            <a
              href="#"
              className="block px-4 py-2 text-sm text-[var(--text-primary)] hover:bg-[var(--soft-dark-bg-secondary)]"
              role="menuitem"
            >
              Your Profile
            </a>
            <a
              href="#"
              className="block px-4 py-2 text-sm text-[var(--text-primary)] hover:bg-[var(--soft-dark-bg-secondary)]"
              role="menuitem"
            >
              Settings
            </a>
            <a
              href="#"
              className="block px-4 py-2 text-sm text-[var(--text-primary)] hover:bg-[var(--soft-dark-bg-secondary)]"
              role="menuitem"
            >
              Billing
            </a>
          </div>
          <div className="py-1" role="none">
            <button
              onClick={handleLogout}
              className="w-full text-left block px-4 py-2 text-sm text-[var(--color-danger)] hover:bg-[var(--soft-dark-bg-secondary)]"
              role="menuitem"
            >
              Sign out
            </button>
          </div>
        </div>
      )}
    </div>
  );
};