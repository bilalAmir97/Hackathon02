'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode, useMemo, useCallback } from 'react';
import { getStoredUser, isAuthenticated as checkIsAuthenticated, clearAuth, authApi } from '@/lib/api-client';

interface AuthContextType {
  user: { id: string; email: string } | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  getToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<{ id: string; email: string } | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Check authentication status on mount
    const checkAuthStatus = async () => {
      try {
        const isAuthenticatedResult = await checkIsAuthenticated();
        if (isAuthenticatedResult) {
          const storedUser = await getStoredUser();
          if (storedUser) {
            setUser(storedUser);
            setIsAuthenticated(true);
          }
        }
      } catch (error) {
        console.error("Auth status check failed:", error);
        // Clear auth data if validation fails
        try {
          await clearAuth();
        } catch (clearError) {
          console.error("Failed to clear auth:", clearError);
        }
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const getToken = useCallback(async (): Promise<string | null> => {
    if (typeof window === 'undefined') {
      return null;
    }
    return localStorage.getItem('jwt_token');
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await authApi.login({ email, password });
      setUser(response.user);
      setIsAuthenticated(true);
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await authApi.register({ email, password });
      setUser(response.user);
      setIsAuthenticated(true);
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    await authApi.logout();
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  const value = useMemo(() => ({
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
    getToken,
  }), [user, isAuthenticated, loading, login, register, logout, getToken]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};