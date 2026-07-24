'use client';

import React, { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react';
import type { User } from './types';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string, mfaCode?: string) => Promise<boolean>;
  logout: () => void;
  hasPermission: (requiredRole: 'analyst' | 'admin') => boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  login: async () => false,
  logout: () => {},
  hasPermission: () => false,
});

const MOCK_CREDENTIALS: Record<string, { password: string; user: User }> = {
  'sarah.chen@bank.com': {
    password: 'admin123',
    user: {
      id: 'USR-001',
      email: 'sarah.chen@bank.com',
      name: 'Sarah Chen',
      role: 'admin',
      lastLogin: new Date().toISOString(),
      mfaEnabled: true,
      ipRestricted: true,
    },
  },
  'marcus.jones@bank.com': {
    password: 'analyst123',
    user: {
      id: 'USR-002',
      email: 'marcus.jones@bank.com',
      name: 'Marcus Jones',
      role: 'analyst',
      lastLogin: new Date().toISOString(),
      mfaEnabled: true,
      ipRestricted: true,
    },
  },
  'elena.kovac@bank.com': {
    password: 'analyst123',
    user: {
      id: 'USR-003',
      email: 'elena.kovac@bank.com',
      name: 'Elena Kovac',
      role: 'analyst',
      lastLogin: new Date().toISOString(),
      mfaEnabled: true,
      ipRestricted: true,
    },
  },
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem('auth_user');
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch {
        localStorage.removeItem('auth_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string, _mfaCode?: string): Promise<boolean> => {
    await new Promise((r) => setTimeout(r, 800));
    const entry = MOCK_CREDENTIALS[email.toLowerCase()];
    if (!entry || entry.password !== password) return false;
    localStorage.setItem('auth_user', JSON.stringify(entry.user));
    setUser(entry.user);
    return true;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('auth_user');
    setUser(null);
  }, []);

  const hasPermission = useCallback(
    (requiredRole: 'analyst' | 'admin') => {
      if (!user) return false;
      if (requiredRole === 'analyst') return true;
      return user.role === 'admin';
    },
    [user]
  );

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
        hasPermission,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
