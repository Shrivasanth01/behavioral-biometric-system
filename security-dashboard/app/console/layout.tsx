'use client';

import React from 'react';
import { AuthProvider, useAuth } from '@/lib/auth';
import { ToastProvider } from '@/components/ui/Toast';
import { Sidebar } from '@/components/layout/Sidebar';
import { TopBar } from '@/components/layout/TopBar';
import { useRouter } from 'next/navigation';

function SecOpsLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  React.useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-navy-950">
        <div className="flex flex-col items-center gap-3">
          <svg className="animate-spin h-8 w-8 text-cyber-500" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-sm text-gray-500 font-mono">Initializing SecOps Command Center...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-navy-950 text-gray-100">
      <Sidebar />
      <div className="lg:pl-64">
        <TopBar />
        <div className="bg-gradient-to-r from-red-950/20 via-navy-900/50 to-cyber-950/20 border-b border-red-500/20 px-6 py-2 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
            <span className="text-xs font-bold uppercase tracking-widest text-red-400 font-mono">SecOps Active Defense Console</span>
          </div>
          <div className="text-xs font-mono text-gray-400 flex items-center gap-4">
            <span>AI ENGINE: <span className="text-green-400">ONLINE</span></span>
            <span>STREAM: <span className="text-cyber-400">240 EVT/SEC</span></span>
          </div>
        </div>
        <main className="p-4 md:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}

export default function ConsoleLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <ToastProvider>
        <SecOpsLayout>
          {children}
        </SecOpsLayout>
      </ToastProvider>
    </AuthProvider>
  );
}
