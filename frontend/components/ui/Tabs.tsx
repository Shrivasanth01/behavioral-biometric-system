'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';

interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  badge?: string | number;
  disabled?: boolean;
}

interface TabsProps {
  tabs: Tab[];
  activeTab?: string;
  onChange?: (tabId: string) => void;
  variant?: 'default' | 'pills' | 'underline';
  className?: string;
}

export function Tabs({ tabs, activeTab, onChange, variant = 'default', className }: TabsProps) {
  const [internalActive, setInternalActive] = useState(tabs[0]?.id || '');
  const currentTab = activeTab || internalActive;

  const handleChange = (tabId: string) => {
    setInternalActive(tabId);
    onChange?.(tabId);
  };

  const variants = {
    default: {
      container: 'border-b border-gray-200',
      tab: 'px-4 py-3 text-sm font-medium border-b-2 border-transparent -mb-px',
      active: 'text-primary-600 border-primary-600',
      inactive: 'text-gray-500 hover:text-gray-700 hover:border-gray-300',
    },
    pills: {
      container: 'bg-gray-100 p-1 rounded-lg',
      tab: 'px-4 py-2 text-sm font-medium rounded-md',
      active: 'bg-white text-primary-700 shadow-sm',
      inactive: 'text-gray-500 hover:text-gray-700',
    },
    underline: {
      container: 'border-b border-gray-200',
      tab: 'px-4 py-3 text-sm font-medium border-b-2 border-transparent -mb-px',
      active: 'text-primary-600 border-primary-600',
      inactive: 'text-gray-500 hover:text-gray-700',
    },
  };

  return (
    <div className={cn('flex gap-1', variants[variant].container, className)}>
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => !tab.disabled && handleChange(tab.id)}
          disabled={tab.disabled}
          className={cn(
            variants[variant].tab,
            currentTab === tab.id ? variants[variant].active : variants[variant].inactive,
            tab.disabled && 'opacity-50 cursor-not-allowed',
            'transition-all duration-200 whitespace-nowrap'
          )}
        >
          <span className="flex items-center gap-2">
            {tab.icon}
            {tab.label}
            {tab.badge !== undefined && (
              <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-medium rounded-full bg-primary-100 text-primary-700">
                {tab.badge}
              </span>
            )}
          </span>
        </button>
      ))}
    </div>
  );
}
