"use client";

/**
 * Enhanced Premium Dashboard Page
 *
 * Main dashboard view for authenticated users with advanced task management features.
 * Features premium futuristic Neo-Glass AI SaaS design with enhanced glassmorphism,
 * sophisticated animations, and refined visual hierarchy.
 */

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useTaskManager } from "@/hooks/useTaskManager";
import { TaskList } from "@/components/tasks/task-list";
import { TaskForm } from "@/components/tasks/task-form";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DashboardHeaderSkeleton, TaskItemSkeleton } from "@/components/ui/loading-skeleton";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete
  } = useTaskManager();
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [editingTask, setEditingTask] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredTasks, setFilteredTasks] = useState<any[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // Filter tasks based on search query
  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredTasks(tasks);
    } else {
      const filtered = tasks.filter(task =>
        task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (task.description && task.description.toLowerCase().includes(searchQuery.toLowerCase()))
      );
      setFilteredTasks(filtered);
    }
  }, [searchQuery, tasks]);

  useEffect(() => {
    if (user?.id) {
      fetchTasks();
    }
  }, [user?.id]);

  const handleCreateTask = async (taskData: any) => {
    try {
      await createTask(taskData);
      setShowTaskForm(false);
      setSuccessMessage('Task created successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Error creating task:', err);
    }
  };

  const handleUpdateTask = async (taskData: any) => {
    if (editingTask) {
      try {
        await updateTask(editingTask.id, taskData);
        setEditingTask(null);
        setSuccessMessage('Task updated successfully!');
        setTimeout(() => setSuccessMessage(''), 3000);
      } catch (err) {
        console.error('Error updating task:', err);
      }
    }
  };

  const handleTaskFormSubmit = (taskData: any) => {
    if (editingTask) {
      handleUpdateTask(taskData);
    } else {
      handleCreateTask(taskData);
    }
  };

  const handleEditTask = (task: any) => {
    setEditingTask(task);
    setShowTaskForm(true);
  };

  const handleCancelEdit = () => {
    setEditingTask(null);
    setShowTaskForm(false);
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await fetchTasks();
    } finally {
      setIsRefreshing(false);
    }
  };

  // Render skeleton while loading user data
  if (!user && loading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="premium-glass-container relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10"></div>
          <div className="relative z-10">
            <DashboardHeaderSkeleton />

            <Card className="glass-effect backdrop-blur-xl bg-white/20 dark:bg-black/20 border border-white/30 dark:border-white/10 p-6 mb-8 animate-hover-lift shadow-xl">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="h-3 bg-gradient-to-r from-blue-400/30 to-purple-400/30 rounded w-16 mb-2 animate-pulse"></div>
                  <div className="h-4 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded w-32 animate-pulse"></div>
                </div>
                <div className="space-y-2">
                  <div className="h-3 bg-gradient-to-r from-purple-400/30 to-pink-400/30 rounded w-20 mb-2 animate-pulse"></div>
                  <div className="h-4 bg-gradient-to-r from-purple-400/20 to-pink-400/20 rounded w-40 animate-pulse"></div>
                </div>
              </div>
            </Card>

            <div className="glass-effect backdrop-blur-xl bg-white/20 dark:bg-black/20 border border-white/30 dark:border-white/10 p-6 rounded-2xl animate-hover-lift shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
                <div className="h-8 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded w-48 mb-4 sm:mb-0 animate-pulse"></div>
                <div className="flex flex-col sm:flex-row gap-3">
                  <div className="h-10 bg-gradient-to-r from-gray-400/20 to-gray-500/20 rounded-lg w-40 animate-pulse"></div>
                  <div className="h-10 bg-gradient-to-r from-gray-400/20 to-gray-500/20 rounded-lg w-24 animate-pulse"></div>
                </div>
              </div>

              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <TaskItemSkeleton key={i} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 relative overflow-hidden">
      <style jsx global>{`
        .dashboard-glass-effect {
          background: linear-gradient(135deg, rgba(51, 65, 85, 0.4) 0%, rgba(15, 23, 42, 0.4) 100%) !important;
          backdrop-filter: blur(12px) !important;
          -webkit-backdrop-filter: blur(12px) !important;
          border: 1px solid rgba(94, 234, 212, 0.1) !important;
          box-shadow: 0 8px 32px 0 rgba(2, 6, 23, 0.3), inset 0 0 2px rgba(94, 234, 212, 0.1) !important;
        }
        .dashboard-glass-effect:hover {
          background: linear-gradient(135deg, rgba(51, 65, 85, 0.5) 0%, rgba(15, 23, 42, 0.5) 100%) !important;
          box-shadow: 0 12px 48px 0 rgba(94, 234, 212, 0.2), inset 0 0 2px rgba(94, 234, 212, 0.2) !important;
        }
      `}</style>
      <div className="premium-glass-container relative overflow-hidden">
        {/* Ambient Lighting Effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-800/10 via-indigo-600/10 to-emerald-600/10"></div>
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-slate-700/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-700/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        {/* Additional floating shapes for premium look */}
        <div className="absolute top-20 left-20 w-16 h-16 rounded-full blur-xl bg-slate-600/20 animate-pulse" style={{ filter: 'blur(60px)' }}></div>
        <div className="absolute top-1/3 right-1/4 w-12 h-12 rounded-full blur-xl bg-indigo-600/20 animate-pulse delay-2000" style={{ filter: 'blur(60px)' }}></div>
        <div className="absolute bottom-1/4 left-1/3 w-20 h-20 rounded-full blur-xl bg-emerald-600/20 animate-pulse delay-3000" style={{ filter: 'blur(60px)' }}></div>

        <div className="relative z-10">
          {/* Hero Section */}
          <div className="dashboard-glass-effect backdrop-blur-xl p-8 mb-8 rounded-2xl animate-hover-lift shadow-2xl hover:shadow-indigo-500/10 transition-all duration-500">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-3 h-3 bg-gradient-to-r from-emerald-400 to-indigo-500 rounded-full animate-pulse"></div>
                  <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-emerald-400 via-indigo-400 to-amber-400 bg-clip-text text-transparent">
                    Welcome Back!
                  </h1>
                </div>

                <div className="mb-4">
                  <h2 className="text-2xl md:text-3xl font-semibold text-white mb-2 font-extrabold tracking-tight">
                    {user?.email ? `Hello, ${user.email.split('@')[0]}` : 'Welcome to your dashboard'}
                  </h2>
                  <p className="text-lg text-slate-300 max-w-2xl">
                    Manage your tasks with <span className="bg-gradient-to-r from-emerald-400 to-indigo-400 bg-clip-text text-transparent font-medium">AI-powered</span> efficiency. Your personalized workspace for productivity and goal achievement.
                  </p>
                </div>

                <div className="flex flex-wrap gap-4 mt-6">
                  <div className="flex items-center gap-2 px-4 py-2 bg-gradient-to-br from-slate-700/50 to-slate-800/50 rounded-lg backdrop-blur-sm border border-slate-600/50">
                    <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-sm font-medium text-slate-300">
                      {tasks.filter(t => t.completed).length} Completed
                    </span>
                  </div>
                  <div className="flex items-center gap-2 px-4 py-2 bg-gradient-to-br from-slate-700/50 to-slate-800/50 rounded-lg backdrop-blur-sm border border-slate-600/50">
                    <svg className="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-sm font-medium text-slate-300">
                      {tasks.filter(t => !t.completed).length} Pending
                    </span>
                  </div>
                  <div className="flex items-center gap-2 px-4 py-2 bg-gradient-to-br from-slate-700/50 to-slate-800/50 rounded-lg backdrop-blur-sm border border-slate-600/50">
                    <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    <span className="text-sm font-medium text-slate-300">
                      {tasks.length} Total Tasks
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 lg:flex-col">
                <Button
                  variant="primary"
                  onClick={() => setShowTaskForm(!showTaskForm)}
                  className="whitespace-nowrap relative overflow-hidden group px-6 py-3 bg-gradient-to-r from-emerald-500 to-indigo-600 text-white font-semibold transition-all duration-300 transform hover:scale-105 shadow-2xl hover:shadow-emerald-500/25 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 focus:ring-offset-transparent"
                  disabled={loading}
                >
                  <span className="relative z-10 flex items-center">
                    <svg className={`w-5 h-5 mr-2 transition-transform duration-300 ${showTaskForm ? 'rotate-180' : 'rotate-0'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    {showTaskForm ? "Cancel" : "Add Task"}
                  </span>
                  <span className="absolute inset-0 bg-gradient-to-r from-emerald-600 to-indigo-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></span>
                </Button>

                <Button
                  variant="ghost"
                  onClick={logout}
                  className="relative border-2 border-slate-600/50 hover:border-slate-400/60 text-white px-6 py-3 whitespace-nowrap transition-all duration-300 hover:bg-slate-700/30 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 focus:ring-offset-transparent"
                  disabled={loading}
                >
                  <span className="relative z-10 flex items-center">
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Logout
                  </span>
                </Button>
              </div>
            </div>
          </div>

          {/* Success Message */}
          {successMessage && (
            <div className="mb-6 rounded-xl bg-green-100/80 dark:bg-green-900/30 p-4 text-sm text-green-800 dark:text-green-300 border border-green-200/50 dark:border-green-800/50 animate-fadeIn backdrop-blur-sm">
              <div className="flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                {successMessage}
              </div>
            </div>
          )}

          {/* User Info Card */}
          <Card className="dashboard-glass-effect backdrop-blur-xl p-6 mb-8 animate-hover-lift shadow-2xl hover:shadow-indigo-500/10 transition-all duration-500">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-2 h-2 bg-gradient-to-r from-emerald-400 to-indigo-500 rounded-full animate-pulse"></div>
              <h2 className="text-xl font-semibold text-white">Account Information</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <span className="text-sm font-medium text-slate-300 flex items-center">
                  <svg className="w-4 h-4 mr-2 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                  </svg>
                  Email
                </span>
                <p className="text-slate-400 mt-1 px-4 py-2 bg-gradient-to-br from-slate-700/50 to-slate-800/50 rounded-lg backdrop-blur-sm border border-slate-600/50">
                  {user?.email || "Loading..."}
                </p>
              </div>
              <div className="space-y-2">
                <span className="text-sm font-medium text-slate-300 flex items-center">
                  <svg className="w-4 h-4 mr-2 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                  </svg>
                  User ID
                </span>
                <p className="font-mono text-xs text-slate-400 mt-1 px-4 py-2 bg-gradient-to-br from-slate-700/50 to-slate-800/50 rounded-lg backdrop-blur-sm border border-slate-600/50 break-all">
                  {user?.id || "Loading..."}
                </p>
              </div>
            </div>
          </Card>

          {/* Task Form */}
          {showTaskForm && (
            <div className="mb-8 animate-fadeIn">
              <div className="dashboard-glass-effect backdrop-blur-xl p-6 rounded-2xl shadow-2xl hover:shadow-indigo-500/10 transition-all duration-500">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-2 h-2 bg-gradient-to-r from-amber-400 to-emerald-500 rounded-full animate-pulse"></div>
                  <h3 className="text-xl font-semibold text-white">
                    {editingTask ? "Edit Task" : "Create New Task"}
                  </h3>
                </div>
                <TaskForm
                  task={editingTask}
                  onSubmit={handleTaskFormSubmit}
                  onCancel={handleCancelEdit}
                  submitLabel={editingTask ? "Update Task" : "Create Task"}
                  cancelLabel="Cancel"
                  disabled={loading}
                />
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 rounded-xl bg-red-100/80 dark:bg-red-900/30 p-4 text-sm text-red-800 dark:text-red-300 border border-red-200/50 dark:border-red-800/50 animate-fadeIn backdrop-blur-sm">
              <div className="flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {error}
              </div>
            </div>
          )}

          {/* Task List */}
          <div className="dashboard-glass-effect backdrop-blur-xl p-6 rounded-2xl animate-hover-lift shadow-2xl hover:shadow-indigo-500/10 transition-all duration-500">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
              <div className="flex items-center gap-3 mb-4 sm:mb-0">
                <div className="w-2 h-2 bg-gradient-to-r from-emerald-400 to-indigo-500 rounded-full animate-pulse"></div>
                <h2 className="text-2xl font-bold text-white">
                  Your Tasks
                  <span className="ml-3 text-sm font-normal bg-gradient-to-br from-emerald-500/20 to-indigo-500/20 text-emerald-300 px-4 py-1.5 rounded-full border border-emerald-500/30">
                    {filteredTasks.length} {filteredTasks.length === 1 ? 'task' : 'tasks'}
                  </span>
                </h2>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
                <div className="relative group w-full sm:w-64 mb-2 sm:mb-0">
                  <input
                    type="text"
                    placeholder="Search tasks..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full px-4 py-3 pl-10 bg-gradient-to-br from-slate-700/50 to-slate-800/50 border border-slate-600/50 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-transparent transition-all duration-300 backdrop-blur-sm group-hover:bg-gradient-to-br from-slate-700/70 to-slate-800/70"
                    disabled={loading}
                  />
                  <svg
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400 group-hover:text-slate-300 transition-colors duration-300"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>

                <Button
                  variant="secondary"
                  onClick={handleRefresh}
                  className="whitespace-nowrap relative overflow-hidden group w-full sm:w-auto bg-gradient-to-r from-slate-600 to-slate-700 text-white hover:bg-gradient-to-r hover:from-slate-700 hover:to-slate-800 transition-all duration-300 shadow-lg hover:shadow-emerald-500/10"
                  disabled={loading || isRefreshing}
                >
                  <span className="relative z-10 flex items-center justify-center sm:justify-start">
                    <svg className={`w-4 h-4 mr-2 transition-transform duration-300 ${isRefreshing ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    {isRefreshing ? "Refreshing..." : "Refresh"}
                  </span>
                </Button>
              </div>
            </div>

            <TaskList
              tasks={filteredTasks}
              onToggleComplete={toggleComplete}
              onDelete={deleteTask}
              onUpdate={handleEditTask}
              loading={loading}
              emptyMessage={searchQuery ? "No tasks match your search. Try different keywords." : "No tasks found. Add a new task to get started."}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
