'use client';

import React from 'react';
import { GlassCard } from '../ui/glass-card';
import { useAuth } from '@/hooks/useAuth';

export const TopNavigation: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-20 bg-transparent">
      <GlassCard className="flex items-center justify-between p-4 md:p-5 border-white/10 backdrop-blur-md">
        <div className="flex items-center gap-2">
          {/* Search Bar */}
          <div className="relative flex-1 max-w-md">
            <input
              type="text"
              placeholder="Search..."
              className="w-full px-4 py-2 pl-10 bg-black/20 border border-white/10 rounded-lg text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-transparent backdrop-blur-sm"
            />
            <svg
              className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Notification Bell */}
          <button className="relative p-2 rounded-lg hover:bg-white/10 transition-colors glow-element">
            <svg
              className="w-5 h-5 text-slate-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H6"
              />
            </svg>
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* User Profile Dropdown */}
          <div className="relative group">
            <button className="flex items-center gap-2 p-1 rounded-lg hover:bg-white/10 transition-colors glow-element">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center text-white text-sm font-medium">
                {user?.email?.charAt(0).toUpperCase() || 'U'}
              </div>
              <span className="hidden md:inline text-slate-300 text-sm font-medium max-w-[100px] truncate">
                {user?.email?.split('@')[0] || 'User'}
              </span>
              <svg
                className="hidden md:block w-4 h-4 text-slate-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {/* Dropdown Menu */}
            <div className="absolute right-0 mt-2 w-48 origin-top-right rounded-lg glass-effect backdrop-blur-md border border-white/10 opacity-0 invisible group-hover:visible group-hover:opacity-100 transition-all duration-200 z-50">
              <div className="py-2">
                <div className="px-4 py-2 border-b border-white/10">
                  <p className="text-slate-300 text-sm font-medium truncate">
                    {user?.email || 'User Account'}
                  </p>
                  <p className="text-slate-400 text-xs truncate">
                    {user?.id || 'ID: Unknown'}
                  </p>
                </div>
                <button
                  onClick={logout}
                  className="w-full text-left px-4 py-2 text-slate-300 hover:bg-white/10 transition-colors text-sm flex items-center gap-2"
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                    />
                  </svg>
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </GlassCard>
    </header>
  );
};