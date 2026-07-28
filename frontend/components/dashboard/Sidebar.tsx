'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, Landmark, ArrowRightLeft, CreditCard, Users,
  Coins as HandCoins, ArrowUpDown, UserCircle, ChevronLeft, ChevronRight,
  Building2, LogOut, Shield,
} from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { APP_NAME } from '@/lib/constants';
import { cn } from '@/lib/utils';

const NAV_ITEMS = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Accounts', href: '/dashboard/accounts', icon: Landmark },
  { label: 'Transfer', href: '/dashboard/transfer', icon: ArrowRightLeft },
  { label: 'Payments', href: '/dashboard/payments', icon: CreditCard },
  { label: 'Beneficiaries', href: '/dashboard/beneficiaries', icon: Users },
  { label: 'Cards', href: '/dashboard/cards', icon: CreditCard },
  { label: 'Loans', href: '/dashboard/loans', icon: HandCoins },
  { label: 'Transactions', href: '/dashboard/transactions', icon: ArrowUpDown },
  { label: 'Profile', href: '/dashboard/profile', icon: UserCircle },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 h-full bg-navy-900 text-white flex flex-col transition-all duration-300 z-30',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className={cn('flex items-center h-16 px-4 border-b border-navy-700/50', collapsed ? 'justify-center' : 'gap-3')}>
        <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center shrink-0">
          <Building2 className="w-5 h-5 text-white" />
        </div>
        {!collapsed && <span className="font-bold text-lg">{APP_NAME}</span>}
      </div>

      <nav className="flex-1 py-4 overflow-y-auto">
        {NAV_ITEMS.map(item => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center mx-2 px-3 py-2.5 rounded-lg transition-all duration-200 group',
                collapsed && 'justify-center',
                isActive
                  ? 'bg-primary-600/20 text-primary-400'
                  : 'text-navy-200 hover:bg-navy-800 hover:text-white'
              )}
              title={collapsed ? item.label : undefined}
            >
              <item.icon className={cn('w-5 h-5 shrink-0', collapsed ? '' : 'mr-3')} />
              {!collapsed && <span className="text-sm font-medium">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      <div className={cn('p-4 border-t border-navy-700/50', collapsed && 'px-2')}>
        {!collapsed && user && (
          <div className="flex items-center gap-3 mb-3 px-2">
            <div className="w-8 h-8 bg-primary-500/20 rounded-full flex items-center justify-center">
              <span className="text-sm font-semibold text-primary-400">
                {user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user.name}</p>
              <p className="text-xs text-navy-400 truncate">{user.email}</p>
            </div>
          </div>
        )}
        <div className={cn('flex gap-1', collapsed && 'flex-col')}>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex items-center justify-center p-2 text-navy-400 hover:text-white hover:bg-navy-800 rounded-lg transition-colors"
            title={collapsed ? 'Expand' : 'Collapse'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
          <button
            onClick={logout}
            className="flex items-center justify-center p-2 text-navy-400 hover:text-danger-400 hover:bg-navy-800 rounded-lg transition-colors"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}

export function SidebarSkeleton() {
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
