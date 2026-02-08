'use client';

import React, { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { SoftDarkCard } from '@/components/ui/SoftDarkCard';
import { TaskCard } from '@/components/tasks/TaskCard';
import { useAuth } from '@/hooks/useAuth';
import { useTaskManager } from '@/hooks/useTaskManager';
import TaskForm from '@/components/tasks/task-form';

// Register GSAP plugins
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

export default function DashboardPage() {
  const { user, loading: authLoading, logout } = useAuth();
  const {
    tasks,
    loading: tasksLoading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete
  } = useTaskManager();
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [editingTask, setEditingTask] = useState<any>(null);
  const [previousStats, setPreviousStats] = useState({ totalTasks: 0, completedTasks: 0, pendingTasks: 0 });

  const heroRef = useRef<HTMLDivElement>(null);
  const statsRef = useRef<HTMLDivElement>(null);
  const taskSectionRef = useRef<HTMLDivElement>(null);

  // Fetch tasks when user is authenticated and auth loading is complete
  useEffect(() => {
    if (user?.id && !authLoading) {
      fetchTasks();
    }
  }, [user?.id, authLoading, fetchTasks]);

  // Initialize GSAP animations when component mounts
  useEffect(() => {
    // Ensure animations only run once after initial load
    if (authLoading || !user) return;

    const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });

    // Animate hero section with refined entrance
    tl.fromTo(heroRef.current?.querySelectorAll('.hero-item') || [],
      {
        opacity: 0,
        y: 30,
        scale: 0.95,
      },
      {
        opacity: 1,
        y: 0,
        scale: 1,
        stagger: 0.15,
        duration: 0.8,
      }
    ).fromTo(
      heroRef.current,
      {
        filter: 'blur(2px)'
      },
      {
        filter: 'blur(0px)',
        duration: 0.6,
      },
      "<" // Start at same time as previous animation
    );

    // Animate stats section with subtle entrance
    tl.fromTo(statsRef.current?.children || [],
      {
        opacity: 0,
        y: 25,
      },
      {
        opacity: 1,
        y: 0,
        stagger: 0.1,
        duration: 0.6,
        // Add gentle pulse after initial animation
        onComplete: () => {
          gsap.to(statsRef.current?.children || [], {
            scale: 1.02,
            duration: 1.5,
            repeat: -1,
            yoyo: true,
            ease: 'sine.inOut',
            stagger: 0.2,
            paused: false
          });
        }
      }
    , 0.2); // Short delay from previous animation

    // Animate task section entrance
    tl.fromTo(taskSectionRef.current,
      {
        opacity: 0,
        y: 20,
      },
      {
        opacity: 1,
        y: 0,
        duration: 0.7,
      }
    , 0.3);

    // Animate individual task cards with refined timing
    if (tasks.length > 0) {
      tl.fromTo('.task-card',
        {
          opacity: 0,
          y: 15,
        },
        {
          opacity: 1,
          y: 0,
          stagger: 0.05,
          duration: 0.4,
          ease: 'power2.out'
        }
      , 0.2);
    }

    // Cleanup timeline on unmount
    return () => {
      tl.kill();
    };
  }, [authLoading, user, tasks.length]);

  // Calculate task statistics with memoization to prevent unnecessary recalculations
  const { totalTasks, completedTasks, pendingTasks } = React.useMemo(() => {
    const total = tasks.length;
    const completed = tasks.filter(task => task.completed).length;
    const pending = total - completed;
    return { totalTasks: total, completedTasks: completed, pendingTasks: pending };
  }, [tasks]);

  // Update previous stats when tasks change and not loading
  useEffect(() => {
    if (!tasksLoading) {
      setPreviousStats({
        totalTasks: totalTasks,
        completedTasks: completedTasks,
        pendingTasks: pendingTasks
      });
    }
  }, [tasksLoading, totalTasks, completedTasks, pendingTasks]); // Include individual stats in dependency array

  const handleAddTask = () => {
    setEditingTask(null);
    setShowTaskForm(true);
  };

  const handleCancelForm = () => {
    setShowTaskForm(false);
    setEditingTask(null);
  };

  const handleTaskSubmit = async (taskData: any) => {
    try {
      if (editingTask) {
        await updateTask(editingTask.id, taskData);
      } else {
        await createTask(taskData);
      }
      setShowTaskForm(false);
      setEditingTask(null);

      // Scroll to the "Your Tasks" section after successful task creation/update
      setTimeout(() => {
        if (taskSectionRef.current) {
          taskSectionRef.current.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
            inline: 'nearest'
          });

          // Additional adjustment to account for header height
          const offsetPosition = taskSectionRef.current.offsetTop - 100;
          window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
          });
        }
      }, 100); // Small delay to ensure DOM updates
    } catch (err) {
      console.error('Error saving task:', err);
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6 md:space-y-8">
      {/* Error Message */}
      {error && (
        <SoftDarkCard className="p-4 text-sm text-[var(--color-danger)] border border-[var(--color-danger)]/30 hover:scale-[1.01] transition-transform duration-300 hover:shadow-lg hover:shadow-[var(--color-danger)]/20">
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="break-words">{error}</span>
          </div>
        </SoftDarkCard>
      )}


      {/* Task Form */}
      {showTaskForm && (
        <SoftDarkCard className="p-4 sm:p-6 mb-4 sm:mb-6">
          <h2 className="text-lg sm:text-xl font-semibold text-[var(--text-primary)] mb-4">
            {editingTask ? "Edit Task" : "Create New Task"}
          </h2>
          <TaskForm
            task={editingTask || undefined}
            onSubmit={handleTaskSubmit}
            onCancel={handleCancelForm}
            submitLabel={editingTask ? "Update Task" : "Create Task"}
            cancelLabel="Cancel"
            disabled={tasksLoading}
          />
        </SoftDarkCard>
      )}

      {/* Hero Section */}
      <div ref={heroRef}>
        <SoftDarkCard className="p-4 sm:p-6 md:p-8 hover:scale-[1.01] transition-transform duration-500 hover:shadow-xl hover:shadow-[var(--glass-shadow)]">
          <div className="text-center">
            <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold mb-2 sm:mb-4 hero-item bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] bg-clip-text text-transparent min-h-[1.2em] leading-tight">
              {authLoading ? 'Loading...' : (user?.email ? `Welcome, ${user.email.split('@')[0]}!` : 'Welcome to Your Dashboard')}
            </h1>
            <p className="text-[var(--text-secondary)] text-base sm:text-lg hero-item min-h-[1.2em]">
              {authLoading ? 'Verifying your session...' : 'Manage your tasks with premium soft dark UI elements'}
            </p>
          </div>
        </SoftDarkCard>
      </div>

      {/* Stats Section */}
      <div ref={statsRef}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          <SoftDarkCard className="p-3 sm:p-4 text-center min-h-[68px] sm:min-h-[72px] hover:scale-[1.02] transition-transform duration-300 hover:shadow-lg hover:shadow-[var(--glass-shadow)]">
            <div className="text-xl sm:text-2xl font-bold text-[var(--primary-accent)] min-h-[1.2em] flex items-center justify-center">
              {tasksLoading ? `${previousStats.totalTasks}*` : totalTasks}
            </div>
            <div className="text-xs sm:text-sm text-[var(--text-secondary)]">Total Tasks {!tasksLoading ? '' : '(updating)'}</div>
          </SoftDarkCard>

          <SoftDarkCard className="p-3 sm:p-4 text-center min-h-[68px] sm:min-h-[72px] hover:scale-[1.02] transition-transform duration-300 hover:shadow-lg hover:shadow-[var(--glass-shadow)]">
            <div className="text-xl sm:text-2xl font-bold text-[var(--color-success)] min-h-[1.2em] flex items-center justify-center">
              {tasksLoading ? `${previousStats.completedTasks}*` : completedTasks}
            </div>
            <div className="text-xs sm:text-sm text-[var(--text-secondary)]">Completed {!tasksLoading ? '' : '(updating)'}</div>
          </SoftDarkCard>

          <SoftDarkCard className="p-3 sm:p-4 text-center min-h-[68px] sm:min-h-[72px] hover:scale-[1.02] transition-transform duration-300 hover:shadow-lg hover:shadow-[var(--glass-shadow)]">
            <div className="text-xl sm:text-2xl font-bold text-[var(--color-warning)] min-h-[1.2em] flex items-center justify-center">
              {tasksLoading ? `${previousStats.pendingTasks}*` : pendingTasks}
            </div>
            <div className="text-xs sm:text-sm text-[var(--text-secondary)]">Incomplete {!tasksLoading ? '' : '(updating)'}</div>
          </SoftDarkCard>
        </div>
      </div>

      {/* Task Section */}
      <div ref={taskSectionRef}>
        <SoftDarkCard className="p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-4 sm:mb-6">
            <h2 id="your-tasks-section" className="text-lg sm:text-xl md:text-2xl font-semibold text-[var(--text-primary)]">Your Tasks</h2>
            <button
              className="px-4 py-2 bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] rounded-lg text-white hover:opacity-90 transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-[var(--primary-accent)]/20 cursor-pointer whitespace-nowrap"
              onClick={handleAddTask}
              disabled={tasksLoading}
            >
              Add Task
            </button>
          </div>

          <div className="space-y-3 sm:space-y-4">
            {tasksLoading ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-[var(--primary-accent)] mb-4"></div>
                <p className="text-[var(--text-secondary)]">Loading your tasks...</p>
              </div>
            ) : (
              <>
                {tasks.map((task, index) => (
                  <div key={task.id} className="task-card" data-index={index}>
                    <TaskCard
                      task={{
                        ...task,
                        description: task.description || undefined,
                        createdAt: task.created_at,
                        updatedAt: task.updated_at,
                      }}
                      onToggleComplete={(task) => {
                        const originalTask = tasks.find(t => t.id === task.id);
                        if (originalTask) {
                          toggleComplete(originalTask);
                        }
                      }}
                      onDelete={deleteTask}
                      onEdit={(task) => {
                        const originalTask = tasks.find(t => t.id === task.id);
                        if (originalTask) {
                          setEditingTask(originalTask);
                          setShowTaskForm(true);

                          // Subtle highlight animation when editing
                          const element = document.getElementById(`task-${originalTask.id}`);
                          if (element) {
                            gsap.to(element, {
                              scale: 1.02,
                              duration: 0.3,
                              ease: 'power1.out',
                              yoyo: true,
                              repeat: 1,
                              repeatDelay: 0.1
                            });
                          }
                        }
                      }}
                    />
                  </div>
                ))}

                {tasks.length === 0 && !tasksLoading && (
                  <div className="text-center py-8 sm:py-12">
                    <div className="mx-auto w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-gradient-to-r from-[var(--primary-accent)]/20 to-[var(--primary-accent-end)]/20 flex items-center justify-center mb-4 sm:mb-6">
                      <svg className="w-10 h-10 sm:w-12 sm:h-12 text-[var(--primary-accent)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </div>
                    <h3 className="text-lg sm:text-xl font-semibold text-[var(--text-primary)] mb-2">No tasks yet</h3>
                    <p className="text-[var(--text-secondary)] mb-4 sm:mb-6">Get started by creating your first task</p>
                    <button
                      className="px-4 py-2 sm:px-6 sm:py-3 bg-gradient-to-r from-[var(--primary-accent)] to-[var(--primary-accent-end)] rounded-lg text-white hover:opacity-90 transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-[var(--primary-accent)]/20 cursor-pointer"
                      onClick={handleAddTask}
                    >
                      Create Your First Task
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </SoftDarkCard>
      </div>
    </div>
  );
}