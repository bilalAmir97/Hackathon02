/**
 * Authentication Layout
 *
 * Provides consistent layout for authentication pages (login, register).
 * Centers content and applies consistent styling.
 */

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Authentication - Todo App",
  description: "Login or register to access your tasks",
};

interface AuthLayoutProps {
  children: React.ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-zinc-50 to-zinc-100 dark:from-zinc-900 dark:to-black px-4 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/10 dark:bg-purple-500/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/10 dark:bg-blue-500/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-500/5 dark:bg-indigo-500/3 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      <div className="w-full max-w-sm sm:max-w-md z-10 narrow-column-guard">
        {/* Logo/Brand */}
        <div className="mb-6 sm:mb-8 text-center">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight bg-gradient-to-r from-blue-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
            Todo App
          </h1>
          <p className="mt-2 text-xs sm:text-sm text-zinc-600 dark:text-zinc-400">
            Manage your tasks efficiently
          </p>
        </div>

        {/* Auth Form Container */}
        {children}

        {/* Footer */}
        <p className="mt-6 sm:mt-8 text-center text-xs text-zinc-500 dark:text-zinc-500">
          Secured with Better Auth and JWT tokens
        </p>
      </div>
    </div>
  );
}
