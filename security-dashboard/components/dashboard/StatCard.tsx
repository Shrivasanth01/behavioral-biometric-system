'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { Card } from '@/components/ui/Card';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: number;
  trendLabel?: string;
  variant?: 'default' | 'warning' | 'danger';
  className?: string;
}

export function StatCard({ title, value, icon, trend, trendLabel, variant = 'default', className }: StatCardProps) {
  const variants = {
    default: 'border-cyber-500/20',
    warning: 'border-alert-medium/30',
    danger: 'border-alert-critical/30',
  };

  return (
    <Card className={cn('relative overflow-hidden', variants[variant], className)}>
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">{title}</p>
          <p className="text-2xl md:text-3xl font-bold font-mono text-gray-100">{value}</p>
          {trend !== undefined && (
            <div className="flex items-center gap-1.5">
              <span className={cn('text-xs font-medium', trend >= 0 ? 'text-emerald-400' : 'text-red-400')}>
                {trend >= 0 ? '+' : ''}{trend}%
              </span>
              {trendLabel && <span className="text-xs text-gray-500">{trendLabel}</span>}
            </div>
          )}
        </div>
        <div className={cn(
          'p-3 rounded-lg',
          variant === 'default' ? 'bg-cyber-500/10 text-cyber-400' :
          variant === 'warning' ? 'bg-alert-medium/10 text-alert-medium' :
          'bg-alert-critical/10 text-alert-critical'
        )}>
          {icon}
        </div>
      </div>
    </Card>
  );
}
