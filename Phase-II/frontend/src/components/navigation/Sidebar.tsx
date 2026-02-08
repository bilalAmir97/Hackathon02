'use client';

import React, { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { SoftDarkButton } from '@/components/ui/SoftDarkButton';
import { ThemeToggle } from '@/components/navigation/ThemeToggle';
import { useAuth } from '@/hooks/useAuth';

interface SidebarItemProps {
  href: string;
  icon: React.ReactNode;
  label: string;
  isActive?: boolean;
  showLabels?: boolean;
  isCollapsed?: boolean;
}

const SidebarItem: React.FC<SidebarItemProps> = ({ href, icon, label, isActive = false, showLabels = true }) => {
  return (
    <a
      href={href}
      className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
        isActive
          ? 'bg-[var(--soft-dark-bg-secondary)] text-[var(--primary-accent)]'
          : 'text-[var(--text-secondary)] hover:bg-[var(--soft-dark-bg-secondary)] hover:text-[var(--text-primary)]'
      }`}
    >
      <span className="mr-3">{icon}</span>
      {showLabels && <span>{label}</span>}
    </a>
  );
};

interface SoftDarkSidebarProps {
  isCollapsed?: boolean;
  onCollapseToggle?: () => void;
  isMobileMenuOpen?: boolean;
  onMobileMenuToggle?: () => void;
}

export const SoftDarkSidebar: React.FC<SoftDarkSidebarProps> = ({
  isCollapsed: controlledCollapsed,
  onCollapseToggle,
  isMobileMenuOpen: controlledMobileMenuOpen,
  onMobileMenuToggle
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [internalMobileMenuOpen, setInternalMobileMenuOpen] = useState(false);
  const pathname = usePathname();
  const { user } = useAuth();

  // Use controlled state if provided, otherwise manage internally
  const effectiveCollapsed = controlledCollapsed !== undefined ? controlledCollapsed : isCollapsed;
  const effectiveMobileMenuOpen = controlledMobileMenuOpen !== undefined ? controlledMobileMenuOpen : internalMobileMenuOpen;

  const toggleCollapse = () => {
    if (onCollapseToggle) {
      // If using controlled state, just call the parent's handler
      onCollapseToggle();
    } else {
      // Otherwise, use internal state
      setIsCollapsed(!effectiveCollapsed);
    }
  };

  const toggleMobileMenu = () => {
    if (onMobileMenuToggle) {
      // If using controlled state, just call the parent's handler
      onMobileMenuToggle();
    } else {
      // Otherwise, use internal state
      setInternalMobileMenuOpen(!effectiveMobileMenuOpen);
    }
  };

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

  useEffect(() => {
    // Close sidebar on mobile when navigating
    if (window.innerWidth < 768) {
      setIsCollapsed(true);
      if (onMobileMenuToggle) {
        // If using controlled state, let parent manage mobile menu state
        // Don't automatically close the mobile menu on navigation
      } else {
        // Otherwise, use internal state
        setInternalMobileMenuOpen(false);
      }
    } else {
      if (!onMobileMenuToggle) {
        setInternalMobileMenuOpen(false);
      }
    }
  }, [pathname, onMobileMenuToggle]);

  // Handle window resize to manage mobile/desktop states
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        if (onMobileMenuToggle) {
          // If using controlled state, let parent manage mobile menu state
          // Don't automatically close on resize
        } else {
          setInternalMobileMenuOpen(false);
        }
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [onMobileMenuToggle]);

  return (
    <>
      {/* Mobile overlay */}
      {effectiveMobileMenuOpen && (
        <div
          className="fixed inset-0 z-30 bg-black bg-opacity-50 md:hidden"
          onClick={toggleMobileMenu}
        ></div>
      )}

      <aside
        className={`inset-y-0 left-0 z-40 ${
          effectiveCollapsed ? 'w-64' : 'w-16'
        } bg-[var(--soft-dark-bg)] border-r border-[var(--glass-border)] transition-all duration-300 ease-in-out ${
          effectiveMobileMenuOpen ? 'fixed translate-x-0 z-50' : '-translate-x-full md:static md:translate-x-0'
        }`}
      >
        <div className="flex flex-col h-full pt-8 pb-4">
          {/* Logo/Brand */}
          <div className="px-6 mb-8">
            <h1 className="text-xl font-bold bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] bg-clip-text text-transparent">
              {effectiveCollapsed && 'Todo App'}
              {!effectiveCollapsed && 'T'}
            </h1>
          </div>

          {/* Navigation Items */}
          <nav className="flex-1 px-4 space-y-2">
            <SidebarItem
              href="/dashboard"
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
              }
              label="Dashboard"
              isActive={pathname === '/dashboard'}
              showLabels={effectiveCollapsed}
            />
            <SidebarItem
              href="/dashboard/tasks"
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              }
              label="Tasks"
              isActive={pathname === '/dashboard/tasks'}
              showLabels={effectiveCollapsed}
            />
            <SidebarItem
              href="/dashboard/analytics"
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              }
              label="Analytics"
              isActive={pathname === '/dashboard/analytics'}
              showLabels={effectiveCollapsed}
            />
            <SidebarItem
              href="/dashboard/settings"
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              }
              label="Settings"
              isActive={pathname === '/dashboard/settings'}
              showLabels={effectiveCollapsed}
            />
          </nav>

          {/* Bottom section with theme toggle and user profile */}
          <div className="mt-auto px-4 pt-4 border-t border-[var(--glass-border)]">
            <div className="mb-4">
              <ThemeToggle />
            </div>

            <div className="flex items-center p-3 bg-[var(--soft-dark-bg-secondary)] rounded-lg">
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] flex items-center justify-center text-white font-medium text-sm">
                {user && user.email ? getUserInitials(user.email) : 'U'}
              </div>
              {effectiveCollapsed && (
                <div className="ml-3 overflow-hidden">
                  <p className="text-sm font-medium text-[var(--text-primary)] truncate max-w-[100px]">
                    {user && user.email ? getUserDisplayName(user.email) : 'User'}
                  </p>
                  <p className="text-xs text-[var(--text-secondary)] truncate max-w-[100px]">
                    {user ? user.email : 'user@example.com'}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Collapse button for desktop */}
        <button
          onClick={toggleCollapse}
          className="absolute right-[-12px] top-20 z-50 hidden md:flex items-center justify-center w-6 h-12 bg-[var(--soft-dark-bg-secondary)] border border-[var(--glass-border)] rounded-r-lg shadow-md hover:bg-[var(--soft-dark-bg-tertiary)] transition-colors"
          aria-label={effectiveCollapsed ? "Collapse sidebar" : "Expand sidebar"}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={`h-4 w-4 text-[var(--text-secondary)] transition-transform ${effectiveCollapsed ? '' : 'rotate-180'}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      </aside>
    </>
  );
};