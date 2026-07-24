'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';

interface TabsProps {
  tabs: { id: string; label: string; count?: number }[];
  activeTab: string;
  onTabChange: (id: string) => void;
  className?: string;
}

export function Tabs({ tabs, activeTab, onTabChange, className }: TabsProps) {
  return (
    <div className={cn('flex border-b border-navy-700/50 overflow-x-auto', className)}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={cn(
            'flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-all duration-200',
            activeTab === tab.id
              ? 'border-cyber-500 text-cyber-400'
              : 'border-transparent text-gray-500 hover:text-gray-300 hover:border-navy-600'
          )}
        >
          {tab.label}
          {tab.count !== undefined && (
            <span className="inline-flex items-center justify-center w-5 h-5 text-xs rounded-full bg-navy-700/50 text-gray-400">
              {tab.count}
            </span>
          )}
        </button>
      ))}
    </div>
  );
}
