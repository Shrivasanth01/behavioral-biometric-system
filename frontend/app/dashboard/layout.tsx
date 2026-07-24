'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { useBehavioralTracker } from '@/hooks/useBehavioralTracker';
import { Sidebar } from '@/components/dashboard/Sidebar';
import { TopBar } from '@/components/dashboard/TopBar';
import { SESSION_TIMEOUT } from '@/lib/constants';
import { generateSessionId } from '@/lib/utils';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const sessionId = generateSessionId();

  useBehavioralTracker({
    sessionId,
    enabled: isAuthenticated,
  });

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    let lastActivity = Date.now();

    const handleActivity = () => {
      lastActivity = Date.now();
    };

    const checkSession = setInterval(() => {
      if (Date.now() - lastActivity > SESSION_TIMEOUT) {
        router.push('/');
      }
    }, 60000);

    window.addEventListener('mousemove', handleActivity);
    window.addEventListener('keydown', handleActivity);
    window.addEventListener('click', handleActivity);
    window.addEventListener('scroll', handleActivity);

    return () => {
      clearInterval(checkSession);
      window.removeEventListener('mousemove', handleActivity);
      window.removeEventListener('keydown', handleActivity);
      window.removeEventListener('click', handleActivity);
      window.removeEventListener('scroll', handleActivity);
    };
  }, [router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex">
        <SidebarSkeleton />
        <main className="flex-1 ml-64">
          <div className="h-16 bg-white border-b border-gray-200 animate-pulse" />
          <div className="p-6 space-y-4">
            <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
            <div className="grid grid-cols-3 gap-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-32 bg-white rounded-xl border border-gray-200 animate-pulse" />
              ))}
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar />
      <div className="flex-1 ml-16 lg:ml-64 transition-all duration-300">
        <TopBar />
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
}

function SidebarSkeleton() {
  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-navy-900 z-30">
      <div className="h-16 flex items-center gap-3 px-4 border-b border-navy-700/50">
        <div className="w-8 h-8 bg-navy-700 rounded-lg animate-pulse" />
        <div className="h-5 w-24 bg-navy-700 rounded animate-pulse" />
      </div>
      <div className="p-4 space-y-2">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="h-10 bg-navy-800 rounded-lg animate-pulse" />
        ))}
      </div>
    </aside>
  );
}
