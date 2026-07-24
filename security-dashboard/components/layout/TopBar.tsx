'use client';

import React from 'react';
import { useAuth } from '@/lib/auth';
import { Avatar } from '@/components/ui/Avatar';
import { Dropdown } from '@/components/ui/Dropdown';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';

export function TopBar() {
  const { user, logout } = useAuth();
  const router = useRouter();

  return (
    <header className="sticky top-0 z-30 h-16 bg-navy-900/90 backdrop-blur-md border-b border-navy-700/50">
      <div className="flex items-center justify-end h-full px-6 gap-4">
        <div className="flex items-center gap-4">
          <button className="relative p-2 text-gray-500 hover:text-gray-300 transition-colors rounded-lg hover:bg-navy-800">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
          <button className="relative p-2 text-gray-500 hover:text-gray-300 transition-colors rounded-lg hover:bg-navy-800">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 rounded-full text-[10px] font-bold text-white flex items-center justify-center">
              3
            </span>
          </button>
          {user && (
            <Dropdown
              trigger={
                <button className="flex items-center gap-2 px-2 py-1 rounded-lg hover:bg-navy-800 transition-colors">
                  <Avatar name={user.name} size="sm" />
                  <div className="hidden md:block text-left">
                    <p className="text-sm font-medium text-gray-200">{user.name}</p>
                    <p className="text-[10px] text-gray-500 uppercase">{user.role}</p>
                  </div>
                </button>
              }
              items={[
                { label: 'Profile', onClick: () => {} },
                { label: 'Change Password', onClick: () => {} },
                { label: 'Sign Out', onClick: () => { logout(); router.push('/login'); }, variant: 'danger' },
              ]}
              align="right"
            />
          )}
        </div>
      </div>
    </header>
  );
}
