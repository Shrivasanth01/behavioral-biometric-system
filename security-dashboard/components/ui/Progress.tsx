'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface ProgressProps {
  value: number;
  max?: number;
  variant?: 'default' | 'risk' | 'success';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export function Progress({ value, max = 100, variant = 'default', size = 'md', showLabel, className }: ProgressProps) {
  const pct = Math.min(Math.max((value / max) * 100, 0), 100);

  const variants = {
    default: 'bg-cyber-500',
    risk: pct >= 80 ? 'bg-alert-critical' : pct >= 60 ? 'bg-alert-high' : pct >= 30 ? 'bg-alert-medium' : 'bg-alert-low',
    success: 'bg-emerald-500',
  };

  const sizes = {
    sm: 'h-1.5',
    md: 'h-2',
    lg: 'h-3',
  };

  return (
    <div className={cn('flex items-center gap-3', className)}>
      <div className={cn('flex-1 rounded-full bg-navy-700/50 overflow-hidden', sizes[size])}>
        <div
          className={cn('h-full rounded-full transition-all duration-500 ease-out', variants[variant])}
          style={{ width: `${pct}%` }}
        />
      </div>
      {showLabel && <span className="text-xs text-gray-400 font-mono w-10 text-right">{Math.round(pct)}%</span>}
    </div>
  );
}
