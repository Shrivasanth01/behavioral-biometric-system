'use client';

import React, { useState } from 'react';
import { Bell } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Notification {
  id: string;
  title: string;
  message: string;
  time: string;
  read: boolean;
  type: 'info' | 'success' | 'warning' | 'error';
}

interface NotificationBellProps {
  notifications?: Notification[];
  onNotificationClick?: (notification: Notification) => void;
  onViewAll?: () => void;
}

export function NotificationBell({ notifications = [], onNotificationClick, onViewAll }: NotificationBellProps) {
  const [isOpen, setIsOpen] = useState(false);
  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-500 hover:text-navy-700 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1.5 right-1.5 flex items-center justify-center w-4 h-4 text-xs font-bold text-white bg-danger-500 rounded-full">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-xl shadow-lg border border-gray-200 z-20 animate-slide-down">
            <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-navy-900">Notifications</h3>
              {unreadCount > 0 && (
                <span className="text-xs text-primary-600 font-medium">{unreadCount} new</span>
              )}
            </div>
            <div className="max-h-72 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="px-4 py-8 text-center text-sm text-gray-500">
                  No notifications
                </div>
              ) : (
                notifications.map(n => (
                  <div
                    key={n.id}
                    onClick={() => onNotificationClick?.(n)}
                    className={cn(
                      'px-4 py-3 border-b border-gray-50 hover:bg-gray-50 cursor-pointer',
                      !n.read && 'bg-primary-50/30'
                    )}
                  >
                    <div className="flex items-start gap-2">
                      <div className={cn(
                        'w-2 h-2 mt-1.5 rounded-full shrink-0',
                        n.type === 'error' ? 'bg-danger-500' :
                        n.type === 'warning' ? 'bg-warning-500' :
                        n.type === 'success' ? 'bg-success-500' : 'bg-primary-500'
                      )} />
                      <div>
                        <p className="text-sm font-medium text-navy-900">{n.title}</p>
                        <p className="text-xs text-gray-500 mt-0.5">{n.message}</p>
                        <p className="text-xs text-gray-400 mt-1">{n.time}</p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
            {onViewAll && (
              <div className="px-4 py-2 border-t border-gray-100">
                <button
                  onClick={onViewAll}
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  View all notifications
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
