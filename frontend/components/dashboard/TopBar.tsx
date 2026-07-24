'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Search, Bell, Shield, ChevronDown, Settings, LogOut, User } from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { Avatar } from '@/components/ui/Avatar';
import { cn } from '@/lib/utils';

export function TopBar() {
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const notifications = [
    { id: 1, title: 'Salary credited', message: '₹45,000 credited to your account', time: '2 min ago', read: false },
    { id: 2, title: 'Bill payment due', message: 'Your electricity bill of ₹1,250 is due tomorrow', time: '1 hour ago', read: false },
    { id: 3, title: 'Low balance alert', message: 'Your current account balance is below ₹5,000', time: '3 hours ago', read: true },
  ];

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 sticky top-0 z-20">
      <div className="flex items-center flex-1 max-w-md">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search transactions, accounts..."
            className="w-full pl-10 pr-4 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all"
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden md:flex items-center gap-1 px-2 py-1 bg-success-50 rounded-full text-xs text-success-700">
          <Shield className="w-3 h-3" />
          Trust Score: 85
        </div>

        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 text-gray-500 hover:text-navy-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-danger-500 rounded-full" />
          </button>

          {showNotifications && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setShowNotifications(false)} />
              <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-xl shadow-lg border border-gray-200 z-20 animate-slide-down">
                <div className="px-4 py-3 border-b border-gray-100">
                  <h3 className="text-sm font-semibold text-navy-900">Notifications</h3>
                </div>
                <div className="max-h-72 overflow-y-auto">
                  {notifications.map(n => (
                    <div key={n.id} className={cn('px-4 py-3 border-b border-gray-50 hover:bg-gray-50 cursor-pointer', !n.read && 'bg-primary-50/50')}>
                      <div className="flex items-start gap-2">
                        <div className={cn('w-2 h-2 mt-1.5 rounded-full shrink-0', n.read ? 'bg-gray-300' : 'bg-primary-500')} />
                        <div>
                          <p className="text-sm font-medium text-navy-900">{n.title}</p>
                          <p className="text-xs text-gray-500 mt-0.5">{n.message}</p>
                          <p className="text-xs text-gray-400 mt-1">{n.time}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="px-4 py-2 border-t border-gray-100">
                  <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">View all notifications</button>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Avatar name={user?.name} size="sm" />
            <div className="hidden md:block text-left">
              <p className="text-sm font-medium text-navy-900 leading-tight">{user?.name}</p>
              <p className="text-xs text-gray-500">{user?.email}</p>
            </div>
            <ChevronDown className="w-4 h-4 text-gray-400 hidden md:block" />
          </button>

          {showUserMenu && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setShowUserMenu(false)} />
              <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-200 z-20 animate-slide-down">
                <div className="px-4 py-3 border-b border-gray-100">
                  <p className="text-sm font-medium text-navy-900">{user?.name}</p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                </div>
                <div className="py-1">
                  <Link href="/dashboard/profile" className="flex items-center gap-2 px-4 py-2 text-sm text-navy-700 hover:bg-gray-50">
                    <User className="w-4 h-4" /> Profile
                  </Link>
                  <Link href="/dashboard/profile" className="flex items-center gap-2 px-4 py-2 text-sm text-navy-700 hover:bg-gray-50">
                    <Settings className="w-4 h-4" /> Settings
                  </Link>
                </div>
                <div className="border-t border-gray-100 py-1">
                  <button onClick={logout} className="flex items-center gap-2 px-4 py-2 text-sm text-danger-600 hover:bg-gray-50 w-full">
                    <LogOut className="w-4 h-4" /> Sign Out
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
