'use client';

import React, { useState, useEffect } from 'react';
import { useTheme } from '@/components/theme/ThemeProvider';
import { SoftDarkCard } from '@/components/ui/SoftDarkCard';
import { SoftDarkButton } from '@/components/ui/SoftDarkButton';
import Link from 'next/link';

const HomePageContent = () => {
  const [isMounted, setIsMounted] = useState(false);
  // Initialize with a default theme to avoid hydration issues
  const [localTheme, setLocalTheme] = useState<'light' | 'dark' | 'soft-dark'>('soft-dark');
  const [hasThemeContext, setHasThemeContext] = useState(false);
  const [contextTheme, setContextTheme] = useState<{theme: 'light' | 'dark' | 'soft-dark', toggleTheme: () => void} | null>(null);

  // Check for theme context availability after mounting
  useEffect(() => {
    // Since we can't directly check for context existence without calling the hook,
    // we'll implement a strategy where we attempt to render a child component
    // that uses the context, and if it fails, we'll catch it with an error boundary
    // For now, we'll try to access the context in a safer way
    try {
      // Try to dynamically import and use the hook
      const loadThemeWithFallback = async () => {
        if (typeof window !== 'undefined') {
          try {
            // Try to access the theme context if available
            const themeModule = await import('@/components/theme/ThemeProvider');
            // We'll try to call useTheme in a controlled way
            // For now, let's just set up a global listener for theme changes if possible
            const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'soft-dark' | null;
            if (savedTheme) {
              setLocalTheme(savedTheme);
            }
          } catch (e) {
            console.warn('Theme context not available, using fallback');
            setHasThemeContext(false);
            // Load theme from localStorage if context is not available
            try {
              const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'soft-dark' | null;
              if (savedTheme) {
                setLocalTheme(savedTheme);
              }
            } catch (e) {
              console.error('Could not read theme from localStorage:', e);
            }
          }
        }
      };

      loadThemeWithFallback();
    } catch (error) {
      console.warn('Theme context not available, using fallback');
      setHasThemeContext(false);
    }
  }, []);

  // For now, we'll just use the local theme and simulate the toggle
  const theme = localTheme;
  const toggleTheme = () => {
    const newTheme = localTheme === 'light' ? 'dark' : localTheme === 'dark' ? 'soft-dark' : 'light';
    setLocalTheme(newTheme);
    // Attempt to update localStorage if possible
    try {
      localStorage.setItem('theme', newTheme);
    } catch (e) {
      console.error('Could not save theme to localStorage:', e);
    }
  };

  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    setIsMounted(true);

    // Set initial theme from localStorage if context is not available
    if (!hasThemeContext) {
      try {
        const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'soft-dark' | null;
        if (savedTheme) {
          setLocalTheme(savedTheme);
        }
      } catch (e) {
        console.error('Could not read theme from localStorage:', e);
      }
    }

    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [hasThemeContext]);

  // Show a minimal loading state until mounted to avoid hydration issues
  if (!isMounted) {
    return <div className="min-h-screen bg-gray-50" />;
  }

  return (
    <div className={`min-h-screen transition-colors duration-300 ${theme === 'dark' || theme === 'soft-dark' ? 'bg-[var(--soft-dark-bg)]' : 'bg-gray-50'}`}>
      {/* Navbar */}
      <nav className={`fixed w-full z-50 transition-all duration-300 ${scrolled ? 'py-3 bg-opacity-90 backdrop-blur-md' : 'py-5'} ${theme === 'dark' || theme === 'soft-dark' ? 'bg-[var(--soft-dark-bg)]' : 'bg-white'}`}>
        <div className="container mx-auto px-4 md:px-8 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] flex items-center justify-center">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <span className={`text-xl font-bold ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>TaskFlow</span>
          </div>

          <div className="hidden md:flex items-center space-x-8">
            <a href="#features" className={`transition-colors hover:text-[var(--primary-accent)] ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>Features</a>
            <a href="#how-it-works" className={`transition-colors hover:text-[var(--primary-accent)] ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>How It Works</a>
            <a href="#testimonials" className={`transition-colors hover:text-[var(--primary-accent)] ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>Testimonials</a>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={toggleTheme}
              className={`p-2 rounded-lg ${theme === 'dark' || theme === 'soft-dark' ? 'bg-[var(--soft-dark-bg-secondary)] text-[var(--text-primary)]' : 'bg-gray-100 text-gray-700'}`}
              aria-label="Toggle theme"
            >
              {theme === 'light' ? (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
              )}
            </button>

            <Link href="/login">
              <SoftDarkButton variant="outline">
                Sign In
              </SoftDarkButton>
            </Link>
            <Link href="/register">
              <SoftDarkButton>
                Get Started
              </SoftDarkButton>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 relative overflow-hidden">
        <div className="absolute inset-0 z-0">
          <div className={`absolute inset-0 ${theme === 'dark' || theme === 'soft-dark' ? 'bg-[var(--soft-dark-bg)]' : 'bg-gray-50'}`} />
          <div className="absolute top-0 left-0 w-full h-full opacity-50">
            <div className="absolute top-20 left-10 w-72 h-72 bg-[var(--primary-accent)] rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
            <div className="absolute top-40 right-10 w-72 h-72 bg-[var(--primary-accent-end)] rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
            <div className="absolute -bottom-8 left-1/2 w-72 h-72 bg-indigo-400 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>
          </div>
        </div>

        <div className="container mx-auto px-4 md:px-8 relative z-10">
          <div className="max-w-5xl mx-auto text-center">
            <h1 className={`text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r ${theme === 'dark' || theme === 'soft-dark' ? 'from-white to-[var(--text-secondary)]' : 'from-gray-900 to-gray-600'} bg-clip-text text-transparent`}>
              Transform Your Productivity
            </h1>
            <p className={`text-xl mb-10 max-w-4xl mx-auto text-left md:text-center ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>
              A futuristic, full-featured todo application with advanced UI/UX that helps you manage tasks efficiently and achieve your goals faster.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link href="/register">
                <SoftDarkButton size="lg">
                  Start Free Trial
                </SoftDarkButton>
              </Link>
              <Link href="/dashboard">
                <SoftDarkButton variant="outline" size="lg">
                  Live Demo
                </SoftDarkButton>
              </Link>
            </div>
          </div>

          <div className="mt-16 max-w-6xl mx-auto">
            <div className={`rounded-2xl overflow-hidden border ${theme === 'dark' || theme === 'soft-dark' ? 'border-[var(--glass-border)]' : 'border-gray-200'} shadow-xl bg-white dark:bg-[var(--soft-dark-bg-secondary)] relative`}>
              {/* Scanning overlay */}
              <div className="scanning-overlay absolute inset-0 pointer-events-none z-10"></div>

              <style jsx>{`
                .scanning-overlay {
                  background: linear-gradient(
                    to bottom,
                    transparent 0%,
                    rgba(59, 130, 246, 0.1) 50%,
                    transparent 100%
                  );
                  animation: scan 4s linear infinite;
                  mask: linear-gradient(black, black) content-box, linear-gradient(black, black);
                  mask-composite: exclude;
                  -webkit-mask-composite: xor;
                }

                @keyframes scan {
                  0% { transform: translateY(-100%); }
                  100% { transform: translateY(100%); }
                }

                .typing-effect {
                  display: inline-block;
                  overflow: hidden;
                  border-right: 0.1em solid;
                  white-space: nowrap;
                  animation: typing 3.5s steps(40, end), blink-caret 0.75s step-end infinite;
                }

                @keyframes typing {
                  from { width: 0 }
                  to { width: 100% }
                }

                @keyframes blink-caret {
                  from, to { border-color: transparent }
                  50% { border-color: #10b981; }
                }

                .feed-content {
                  animation: scrollUp 20s linear infinite;
                }

                @keyframes scrollUp {
                  from { transform: translateY(0); }
                  to { transform: translateY(-50%); }
                }

                .progress-bar {
                  animation: fillProgress 10s ease-in-out infinite alternate;
                }

                .percentage {
                  animation: changePercentage 10s ease-in-out infinite alternate;
                }

                .countdown {
                  animation: countdownTimer 10s ease-in-out infinite alternate;
                }

                @keyframes fillProgress {
                  0% { content: "[░░░░░░░░░░░░░░░░░░░░]"; }
                  25% { content: "[███████░░░░░░░░░░░░░]"; }
                  50% { content: "[█████████████░░░░░░░]"; }
                  75% { content: "[██████████████████░░]"; }
                  100% { content: "[████████████████████]"; }
                }

                @keyframes changePercentage {
                  0% { content: "32%"; }
                  25% { content: "56%"; }
                  50% { content: "78%"; }
                  75% { content: "89%"; }
                  100% { content: "94%"; }
                }

                @keyframes countdownTimer {
                  0% { content: "5m 30s"; }
                  25% { content: "4m 15s"; }
                  50% { content: "3m 05s"; }
                  75% { content: "2m 35s"; }
                  100% { content: "2m 14s"; }
                }

                div::-webkit-scrollbar {
                  display: none;
                }
              `}</style>

              {/* Fake Browser Window */}
              <div className="bg-gray-100 dark:bg-[var(--soft-dark-bg)] p-4 border-b border-gray-200 dark:border-[var(--glass-border)]">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-red-400"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                  <div className="w-3 h-3 rounded-full bg-green-400"></div>
                  <div className="ml-4 text-xs text-gray-500 dark:text-[var(--text-secondary)] font-mono">
                    app.taskflow.ai/dashboard
                  </div>
                </div>
              </div>

              <div className="flex h-96">
                {/* Sidebar */}
                <div className={`w-64 border-r ${theme === 'dark' || theme === 'soft-dark' ? 'border-[var(--glass-border)] bg-[var(--soft-dark-bg-secondary)]' : 'border-gray-200 bg-gray-50'} p-4`}>
                  <div className="mb-6">
                    <h3 className={`text-sm font-semibold mb-3 ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-primary)]' : 'text-gray-900'}`}>AI AGENTS</h3>
                    <div className="space-y-3">
                      {['Research Agent', 'Writing Agent', 'Analysis Agent', 'Planning Agent'].map((agent, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <span className={`text-xs ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>{agent}</span>
                          <div className="relative">
                            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                            <div className="absolute inset-0 w-2 h-2 bg-green-400 rounded-full animate-ping opacity-75"></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mb-6">
                    <h3 className={`text-sm font-semibold mb-3 ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-primary)]' : 'text-gray-900'}`}>STATUS</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs">
                        <span className={theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}>Tasks</span>
                        <span className={theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-primary)]' : 'text-gray-900'}>24/42</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className={theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}>Efficiency</span>
                        <span className={theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-primary)]' : 'text-gray-900'}>94%</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className={`text-sm font-semibold mb-3 ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-primary)]' : 'text-gray-900'}`}>WORKFLOW OPTIMIZATION</h3>
                    <div className="w-full bg-gray-200 dark:bg-[var(--soft-dark-bg)] rounded-full h-2">
                      <div className="bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] h-2 rounded-full w-3/4 animate-pulse"></div>
                    </div>
                    <div className="text-xs mt-1 text-right">
                      <span className={theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}>Optimizing...</span>
                    </div>
                  </div>

                  {/* Current Action with typing effect */}
                  <div className="mt-6">
                    <h3 className={`text-sm font-semibold mb-2 ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-primary)]' : 'text-gray-900'}`}>CURRENT ACTION</h3>
                    <div className={`p-3 rounded font-mono text-xs ${theme === 'dark' || theme === 'soft-dark' ? 'bg-black/20 text-green-400' : 'bg-gray-200 text-gray-700'}`}>
                      <span className="typing-effect">Analyzing user workflow patterns...</span>
                    </div>
                  </div>
                </div>

                {/* Main Content */}
                <div className="flex-1 p-6 overflow-y-hidden" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
                  <div className="mb-6">
                    <h2 className={`text-lg font-semibold mb-4 ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>Task Feed</h2>

                    {/* Auto-scrolling container with hidden scrollbar */}
                    <div className="h-64 overflow-y-auto relative" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
                      <div className="feed-content pb-20">
                        {/* Duplicate content to create seamless infinite scroll */}
                        <div className="space-y-4">
                          {[
                            { task: 'Analyzing market trends', status: 'COMPLETED', time: '2 min ago' },
                            { task: 'Generating report', status: 'PROCESSING', time: 'Just now' },
                            { task: 'Scheduling meetings', status: 'PENDING', time: '1 min ago' },
                            { task: 'Researching competitors', status: 'THINKING', time: '3 min ago' },
                            { task: 'Updating user preferences', status: 'PROCESSING', time: 'Just now' },
                            { task: 'Syncing data across platforms', status: 'COMPLETED', time: '4 min ago' },
                            { task: 'Optimizing workflow algorithms', status: 'THINKING', time: '5 min ago' },
                            { task: 'Preparing weekly summary', status: 'PENDING', time: '6 min ago' },
                            { task: 'Learning user patterns', status: 'PROCESSING', time: '7 min ago' },
                            { task: 'Generating insights', status: 'COMPLETED', time: '8 min ago' }
                          ].map((item, index) => (
                            <div
                              key={`${index}-duplicate`}
                              className={`p-4 rounded-lg border ${theme === 'dark' || theme === 'soft-dark' ? 'border-[var(--glass-border)] bg-[var(--soft-dark-bg-secondary)]' : 'border-gray-200 bg-gray-50'} transition-all duration-300 hover:scale-[1.02]`}
                            >
                              <div className="flex justify-between items-start">
                                <div className="flex-1">
                                  <div className="flex items-center mb-2">
                                    <div className={`w-2 h-2 rounded-full mr-2 ${
                                      item.status === 'COMPLETED' ? 'bg-green-400' :
                                      item.status === 'PROCESSING' ? 'bg-blue-400 animate-pulse' :
                                      item.status === 'THINKING' ? 'bg-yellow-400 animate-pulse' :
                                      'bg-gray-400'
                                    }`}></div>
                                    <span className={`text-sm font-medium ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>
                                      {item.task}
                                    </span>
                                  </div>
                                  <div className="flex justify-between text-xs">
                                    <span className={`px-2 py-1 rounded-full ${
                                      item.status === 'COMPLETED' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                                      item.status === 'PROCESSING' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' :
                                      item.status === 'THINKING' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' :
                                      'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                                    }`}>
                                      {item.status}
                                    </span>
                                    <span className={theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-500'}>
                                      {item.time}
                                    </span>
                                  </div>
                                </div>
                              </div>

                              {/* Skeleton loader for task details */}
                              {item.status !== 'COMPLETED' && (
                                <div className="mt-3 space-y-2">
                                  <div className="h-2 bg-gray-200 dark:bg-[var(--soft-dark-bg)] rounded animate-pulse"></div>
                                  <div className="h-2 bg-gray-200 dark:bg-[var(--soft-dark-bg)] rounded animate-pulse w-5/6"></div>
                                  <div className="h-2 bg-gray-200 dark:bg-[var(--soft-dark-bg)] rounded animate-pulse w-3/4"></div>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>

                        {/* Duplicate the content to create seamless infinite scroll */}
                        <div className="space-y-4">
                          {[
                            { task: 'Analyzing market trends', status: 'COMPLETED', time: '2 min ago' },
                            { task: 'Generating report', status: 'PROCESSING', time: 'Just now' },
                            { task: 'Scheduling meetings', status: 'PENDING', time: '1 min ago' },
                            { task: 'Researching competitors', status: 'THINKING', time: '3 min ago' },
                            { task: 'Updating user preferences', status: 'PROCESSING', time: 'Just now' },
                            { task: 'Syncing data across platforms', status: 'COMPLETED', time: '4 min ago' },
                            { task: 'Optimizing workflow algorithms', status: 'THINKING', time: '5 min ago' },
                            { task: 'Preparing weekly summary', status: 'PENDING', time: '6 min ago' },
                            { task: 'Learning user patterns', status: 'PROCESSING', time: '7 min ago' },
                            { task: 'Generating insights', status: 'COMPLETED', time: '8 min ago' }
                          ].map((item, index) => (
                            <div
                              key={`${index}-duplicate-2`}
                              className={`p-4 rounded-lg border ${theme === 'dark' || theme === 'soft-dark' ? 'border-[var(--glass-border)] bg-[var(--soft-dark-bg-secondary)]' : 'border-gray-200 bg-gray-50'} transition-all duration-300 hover:scale-[1.02]`}
                            >
                              <div className="flex justify-between items-start">
                                <div className="flex-1">
                                  <div className="flex items-center mb-2">
                                    <div className={`w-2 h-2 rounded-full mr-2 ${
                                      item.status === 'COMPLETED' ? 'bg-green-400' :
                                      item.status === 'PROCESSING' ? 'bg-blue-400 animate-pulse' :
                                      item.status === 'THINKING' ? 'bg-yellow-400 animate-pulse' :
                                      'bg-gray-400'
                                    }`}></div>
                                    <span className={`text-sm font-medium ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>
                                      {item.task}
                                    </span>
                                  </div>
                                  <div className="flex justify-between text-xs">
                                    <span className={`px-2 py-1 rounded-full ${
                                      item.status === 'COMPLETED' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                                      item.status === 'PROCESSING' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' :
                                      item.status === 'THINKING' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' :
                                      'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                                    }`}>
                                      {item.status}
                                    </span>
                                    <span className={theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-500'}>
                                      {item.time}
                                    </span>
                                  </div>
                                </div>
                              </div>

                              {/* Skeleton loader for task details */}
                              {item.status !== 'COMPLETED' && (
                                <div className="mt-3 space-y-2">
                                  <div className="h-2 bg-gray-200 dark:bg-[var(--soft-dark-bg)] rounded animate-pulse"></div>
                                  <div className="h-2 bg-gray-200 dark:bg-[var(--soft-dark-bg)] rounded animate-pulse w-5/6"></div>
                                  <div className="h-2 bg-gray-200 dark:bg-[var(--soft-dark-bg)] rounded animate-pulse w-3/4"></div>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Terminal-like command log with animated progress */}
                  <div className={`p-4 rounded-lg font-mono text-xs ${theme === 'dark' || theme === 'soft-dark' ? 'bg-black/20 text-green-400 border border-[var(--glass-border)]' : 'bg-gray-900 text-green-400 text-gray-100'}`}>
                    <div className="flex items-center mb-2">
                      <span className="text-green-400">&gt;</span>
                      <span className={`ml-2 ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-400'}`}>Last command:</span>
                    </div>
                    <div className={theme === 'dark' || theme === 'soft-dark' ? 'text-green-400' : 'text-green-300'}>
                      $ optimizing_workflow --deep-learning --neural-network<br/>
                      <span className={theme === 'dark' || theme === 'soft-dark' ? 'text-yellow-400' : 'text-yellow-300'}>
                        <span className="progress-bar">[████████████████████]</span> <span className="percentage">94%</span> complete
                      </span><br/>
                      <span className={theme === 'dark' || theme === 'soft-dark' ? 'text-blue-400' : 'text-blue-300'}>
                        Estimated time remaining: <span className="countdown">2m 14s</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20">
        <div className="container mx-auto px-4 md:px-8">
          <div className="text-center mb-16">
            <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>
              Powerful Features
            </h2>
            <p className={`text-lg max-w-4xl mx-auto text-left md:text-center ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>
              Everything you need to organize your tasks and boost productivity
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                title: "Smart Organization",
                description: "Intelligent categorization and tagging system to keep your tasks organized.",
                icon: (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                )
              },
              {
                title: "Real-time Sync",
                description: "All your tasks sync instantly across all devices for seamless access.",
                icon: (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                )
              },
              {
                title: "Team Collaboration",
                description: "Share tasks and collaborate with your team in real-time.",
                icon: (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                )
              },
              {
                title: "Advanced Analytics",
                description: "Gain insights into your productivity with detailed analytics and reports.",
                icon: (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                )
              },
              {
                title: "Custom Workflows",
                description: "Create personalized workflows that match your unique productivity style.",
                icon: (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                  </svg>
                )
              },
              {
                title: "Privacy Focused",
                description: "Your data is encrypted and never shared with third parties.",
                icon: (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                )
              }
            ].map((feature, index) => (
              <SoftDarkCard key={index} className="p-6 hover:scale-[1.02] transition-all duration-300 hover:shadow-lg hover:shadow-[var(--glass-shadow)]">
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] flex items-center justify-center mb-4 ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-white'}`}>
                  {feature.icon}
                </div>
                <h3 className={`text-xl font-semibold mb-2 ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>
                  {feature.title}
                </h3>
                <p className={`${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>
                  {feature.description}
                </p>
              </SoftDarkCard>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20">
        <div className="container mx-auto px-4 md:px-8">
          <div className="text-center mb-16">
            <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>
              How It Works
            </h2>
            <p className={`text-lg max-w-4xl mx-auto text-left md:text-center ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>
              Get started in just a few simple steps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: 1,
                title: "Sign Up",
                description: "Create your account in seconds with your email or social login."
              },
              {
                step: 2,
                title: "Organize",
                description: "Add your tasks, set priorities, and organize them into projects."
              },
              {
                step: 3,
                title: "Achieve",
                description: "Track your progress and accomplish your goals efficiently."
              }
            ].map((item, index) => (
              <div key={index} className="text-center">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] text-white font-bold text-xl`}>
                  {item.step}
                </div>
                <h3 className={`text-xl font-semibold mb-2 ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>
                  {item.title}
                </h3>
                <p className={`${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20">
        <div className="container mx-auto px-4 md:px-8">
          <div className="text-center mb-16">
            <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>
              What Our Users Say
            </h2>
            <p className={`text-lg max-w-4xl mx-auto text-left md:text-center ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>
              Join thousands of satisfied users who transformed their productivity
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                name: "Sarah Johnson",
                role: "Product Manager",
                quote: "TaskFlow helped me organize my team's workflow and increased our productivity by 40%."
              },
              {
                name: "Michael Chen",
                role: "Software Engineer",
                quote: "The intuitive interface and powerful features make TaskFlow indispensable for my daily tasks."
              },
              {
                name: "Emma Rodriguez",
                role: "Freelance Designer",
                quote: "Finally, a task manager that understands how creative professionals work. Highly recommended!"
              }
            ].map((testimonial, index) => (
              <SoftDarkCard key={index} className="p-6">
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <svg key={i} xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461c.969 0 1.371-1.24.588-1.81l-1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <p className={`italic mb-4 ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>
                  "{testimonial.quote}"
                </p>
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] flex items-center justify-center text-white font-medium text-sm mr-3">
                    {testimonial.name.charAt(0)}
                  </div>
                  <div>
                    <p className={`font-medium ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>
                      {testimonial.name}
                    </p>
                    <p className={`text-sm ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>
                      {testimonial.role}
                    </p>
                  </div>
                </div>
              </SoftDarkCard>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20">
        <div className="container mx-auto px-4 md:px-8">
          <SoftDarkCard className="p-12 text-center">
            <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>
              Ready to Transform Your Productivity?
            </h2>
            <p className={`text-xl mb-8 max-w-4xl mx-auto text-left md:text-center ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>
              Join thousands of users who have already revolutionized their task management
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link href="/register">
                <SoftDarkButton size="lg">
                  Get Started Free
                </SoftDarkButton>
              </Link>
              <Link href="/pricing">
                <SoftDarkButton variant="outline" size="lg">
                  View Pricing
                </SoftDarkButton>
              </Link>
            </div>
          </SoftDarkCard>
        </div>
      </section>

      {/* Footer */}
      <footer className={`py-12 ${theme === 'dark' || theme === 'soft-dark' ? 'bg-[var(--soft-dark-bg-secondary)]' : 'bg-gray-100'}`}>
        <div className="container mx-auto px-4 md:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] flex items-center justify-center">
                  <span className="text-white font-bold text-sm">T</span>
                </div>
                <span className={`text-xl font-bold ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>TaskFlow</span>
              </div>
              <p className={`${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>
                A futuristic, full-featured todo application with advanced UI/UX.
              </p>
            </div>

            <div>
              <h3 className={`font-semibold mb-4 ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>Product</h3>
              <ul className={`space-y-2 ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>
                <li><a href="#" className="hover:text-[var(--primary-accent)] transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-[var(--primary-accent)] transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-[var(--primary-accent)] transition-colors">Integrations</a></li>
                <li><a href="#" className="hover:text-[var(--primary-accent)] transition-colors">Roadmap</a></li>
              </ul>
            </div>

            <div>
              <h3 className={`font-semibold mb-4 ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>Resources</h3>
              <ul className={`space-y-2 ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>
                <li><a href="#" className="hover:text-[var(--primary-accent)] transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-[var(--primary-accent)] transition-colors">Tutorials</a></li>
                <li><a href="#" className="hover:text-[var(--primary-accent)] transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-[var(--primary-accent)] transition-colors">Support</a></li>
              </ul>
            </div>

            <div>
              <h3 className={`font-semibold mb-4 ${theme === 'dark' || theme === 'soft-dark' ? 'text-white' : 'text-gray-900'}`}>Company</h3>
              <ul className={`space-y-2 ${theme === 'dark' || theme === 'soft-dark' ? 'text-[var(--text-secondary)]' : 'text-gray-600'}`}>
                <li><a href="#" className="hover:text-[var(--primary-accent)] transition-colors">About</a></li>
                <li><a href="#" className="hover:text-[var(--primary-accent)] transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-[var(--primary-accent)] transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-[var(--primary-accent)] transition-colors">Legal</a></li>
              </ul>
            </div>
          </div>

          <div className={`border-t mt-12 pt-8 text-center ${theme === 'dark' || theme === 'soft-dark' ? 'border-[var(--glass-border)] text-[var(--text-secondary)]' : 'border-gray-200 text-gray-600'}`}>
            <p>© {new Date().getFullYear()} TaskFlow. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePageContent;