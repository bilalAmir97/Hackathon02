"use client";

/**
 * Protected Dashboard Layout
 *
 * Ensures user is authenticated before accessing dashboard routes.
 * Redirects to login if no valid JWT token is found.
 * Provides navigation with sidebar and top bar in soft dark theme.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated, getStoredUser, authApi } from "@/lib/api-client";
import { SoftDarkSidebar } from "@/components/navigation/Sidebar";
import { TopNavigation } from "@/components/navigation/TopNavigation";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<{ id: string; email: string } | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('sidebarCollapsed');
      return saved ? JSON.parse(saved) : false;
    }
    return false;
  });
  const [windowWidth, setWindowWidth] = useState<number | undefined>(undefined);

  // Track window width for responsive behavior
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const handleResize = () => {
        setWindowWidth(window.innerWidth);
      };

      // Set initial width
      setWindowWidth(window.innerWidth);

      // Add event listener
      window.addEventListener('resize', handleResize);

      // Cleanup
      return () => window.removeEventListener('resize', handleResize);
    }
  }, []);

  useEffect(() => {
    // Save sidebar collapse state to localStorage
    localStorage.setItem('sidebarCollapsed', JSON.stringify(isSidebarCollapsed));
  }, [isSidebarCollapsed]);

  useEffect(() => {
    const checkAuth = async () => {
      // Check authentication on mount
      const authenticated = await isAuthenticated();
      if (!authenticated) {
        router.push("/login?error=auth_required");
        return;
      }

      // Get user data
      const userData = await getStoredUser();
      if (!userData) {
        router.push("/login?error=auth_required");
        return;
      }

      // Verify that the token is still valid by making a simple API call
      try {
        // We can make a simple authenticated call to validate the token
        // For now, we'll just check if we can access user data
        setUser(userData);
        setIsLoading(false);
      } catch (error) {
        console.error("Token validation failed:", error);
        // Clear auth data and redirect to login
        authApi.logout();
      }
    };

    checkAuth();
  }, [router]);

  const handleLogout = () => {
    authApi.logout();
  };

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--soft-dark-bg)]">
        <div className="text-center">
          <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-[var(--primary-accent)] border-t-transparent"></div>
          <p className="text-sm text-[var(--text-secondary)]">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--soft-dark-bg)] flex">
      {/* Mobile menu button - always visible and not affected by sidebar transforms */}
      <button
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        className="fixed top-4 left-4 z-50 md:hidden p-2 rounded-lg bg-[var(--soft-dark-bg-secondary)] border border-[var(--glass-border)] text-[var(--text-primary)]"
        aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* Sidebar - passes desktop collapse state and mobile menu state */}
      {/* Now using relative positioning to take up actual space in document flow */}
      <div className={`${isMobileMenuOpen ? 'absolute inset-0 z-30 md:relative md:z-auto' : 'hidden md:block'} md:relative`}>
        <SoftDarkSidebar
          isCollapsed={isSidebarCollapsed}  // Control desktop collapse state
          onCollapseToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}  // Toggle desktop collapse
          isMobileMenuOpen={isMobileMenuOpen}
          onMobileMenuToggle={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        />
      </div>

      {/* Main content area - using flexbox to naturally shrink when sidebar expands */}
      <div className="flex-1 transition-all duration-300 min-h-screen">
        {/* Top Navigation */}
        <TopNavigation />

        {/* Main Content */}
        <main className="p-4 md:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
