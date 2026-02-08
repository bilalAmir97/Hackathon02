'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { GlassCard } from '../ui/glass-card';
import gsap from 'gsap';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊', href: '/dashboard' },
  { id: 'tasks', label: 'Tasks', icon: '✅', href: '/dashboard' },
  { id: 'calendar', label: 'Calendar', icon: '📅', href: '/dashboard' },
  { id: 'analytics', label: 'Analytics', icon: '📈', href: '/dashboard' },
  { id: 'settings', label: 'Settings', icon: '⚙️', href: '/dashboard' },
];

export const FuturisticSidebar: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [activeItem, setActiveItem] = useState('dashboard');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Initialize GSAP animations for sidebar interactions
  useEffect(() => {
    // Animate navigation items when they appear
    gsap.from('.nav-item', {
      duration: 0.5,
      opacity: 0,
      x: -20,
      stagger: 0.1,
      ease: 'power2.out',
      delay: 0.2
    });

    // Animate sidebar expansion/collapse
    gsap.set('.sidebar-item', { opacity: 1 });
  }, [isCollapsed]);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);

    // Animate collapse/expand with GSAP
    if (isCollapsed) {
      gsap.to('.sidebar-item', {
        duration: 0.3,
        opacity: 1,
        x: 0,
        stagger: 0.05,
        ease: 'power2.out'
      });
    } else {
      gsap.to('.sidebar-item', {
        duration: 0.2,
        opacity: 0,
        x: -10,
        stagger: 0.02,
        ease: 'power2.in'
      });
    }
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <>
      {/* Mobile menu button */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <button
          onClick={toggleMobileMenu}
          className="p-2 rounded-lg glass-effect backdrop-blur-md bg-black/10 border border-white/10 hover:bg-white/10 transition-colors"
          aria-label="Toggle navigation menu"
        >
          <svg
            className="w-6 h-6 text-slate-300"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            {isMobileMenuOpen ? (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            ) : (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 z-40 md:hidden"
              onClick={toggleMobileMenu}
            />
            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="fixed top-0 left-0 h-full w-64 z-50"
            >
              <GlassCard className="h-full flex flex-col border-white/10 backdrop-blur-md">
                <div className="p-5 border-b border-white/10">
                  <div className="flex items-center justify-between">
                    <h2 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
                      Menu
                    </h2>
                    <button
                      onClick={toggleMobileMenu}
                      className="p-1 rounded-lg hover:bg-white/10 transition-colors"
                    >
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
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </button>
                  </div>
                </div>

                <nav className="flex-1 p-2">
                  <ul className="space-y-1">
                    {NAV_ITEMS.map((item) => (
                      <li key={item.id} className="nav-item">
                        <Link
                          href={item.href}
                          onClick={() => {
                            setActiveItem(item.id);
                            setIsMobileMenuOpen(false);
                          }}
                          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                            activeItem === item.id
                              ? 'bg-gradient-to-r from-blue-500/20 to-indigo-500/20 text-blue-300 glow-element'
                              : 'text-slate-300 hover:bg-white/10'
                          }`}
                        >
                          <span className="text-lg">{item.icon}</span>
                          <span className="font-medium">{item.label}</span>
                        </Link>
                      </li>
                    ))}
                  </ul>
                </nav>
              </GlassCard>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Desktop sidebar */}
      <aside className="hidden md:block fixed left-0 top-0 h-full z-30">
        <GlassCard
          variant={isCollapsed ? 'default' : 'elevated'}
          className={`h-screen flex flex-col border-white/10 backdrop-blur-md min-w-[240px] ${
            isCollapsed ? 'w-20' : 'w-64'
          } transition-all duration-300`}
        >
          <div className="p-5 border-b border-white/10">
            <div className="flex items-center justify-between">
              <AnimatePresence>
                {!isCollapsed && (
                  <motion.h1
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: 'auto' }}
                    exit={{ opacity: 0, width: 0 }}
                    className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent whitespace-nowrap"
                  >
                    Futuristic UI
                  </motion.h1>
                )}
              </AnimatePresence>

              <button
                onClick={toggleSidebar}
                className="p-1.5 rounded-lg hover:bg-white/10 transition-colors glow-element"
                aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
              >
                <svg
                  className={`w-5 h-5 text-slate-300 transition-transform duration-300 ${
                    isCollapsed ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
              </button>
            </div>
          </div>

          <nav className="flex-1 p-2 overflow-y-auto">
            <ul className="space-y-1">
              {NAV_ITEMS.map((item) => (
                <li key={item.id} className={`nav-item sidebar-item ${isCollapsed ? 'justify-center' : ''}`}>
                  <Link
                    href={item.href}
                    onClick={() => setActiveItem(item.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                      activeItem === item.id
                        ? 'bg-gradient-to-r from-blue-500/20 to-indigo-500/20 text-blue-300 glow-element'
                        : 'text-slate-300 hover:bg-white/10'
                    }`}
                  >
                    <span className="text-lg">{item.icon}</span>
                    <AnimatePresence>
                      {!isCollapsed && (
                        <motion.span
                          initial={{ opacity: 0, width: 0 }}
                          animate={{ opacity: 1, width: 'auto' }}
                          exit={{ opacity: 0, width: 0 }}
                          className="font-medium whitespace-nowrap"
                        >
                          {item.label}
                        </motion.span>
                      )}
                    </AnimatePresence>
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          <div className="p-4 border-t border-white/10">
            <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-slate-300 hover:bg-white/10 transition-colors">
              <span className="text-lg">🚪</span>
              <AnimatePresence>
                {!isCollapsed && (
                  <motion.span
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: 'auto' }}
                    exit={{ opacity: 0, width: 0 }}
                    className="font-medium whitespace-nowrap"
                  >
                    Logout
                  </motion.span>
                )}
              </AnimatePresence>
            </button>
          </div>
        </GlassCard>
      </aside>

      {/* Spacer for desktop sidebar */}
      <div className={`hidden md:block ${isCollapsed ? 'ml-20' : 'ml-64'} transition-all duration-300`} />
    </>
  );
};