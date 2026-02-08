"use client";

/**
 * Protected Dashboard Layout
 *
 * Ensures user is authenticated before accessing dashboard routes.
 * Redirects to login if no valid JWT token is found.
 * Provides navigation header with logout functionality.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated, getStoredUser, authApi } from "@/lib/api-client";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<{ id: string; email: string } | null>(null);

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
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-zinc-900">
        <div className="text-center">
          <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-zinc-300 border-t-zinc-900 dark:border-zinc-700 dark:border-t-zinc-50"></div>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900">
      {/* Navigation Header */}
      <header className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Logo/Brand */}
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
                Todo App
              </h1>
            </div>

            {/* User Info and Logout */}
            <div className="flex items-center gap-4">
              <div className="hidden text-sm sm:block">
                <span className="text-zinc-600 dark:text-zinc-400">
                  {user?.email}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:ring-offset-2 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200 dark:focus:ring-zinc-50"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
