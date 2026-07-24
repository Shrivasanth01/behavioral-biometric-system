'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { SEVERITY_COLORS } from '@/lib/constants';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  const variants = {
    default: 'bg-navy-700/50 text-gray-300 border-navy-600/30',
    success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    warning: 'bg-alert-medium/10 text-alert-medium border-alert-medium/30',
    danger: 'bg-alert-critical/10 text-alert-critical border-alert-critical/30',
    info: 'bg-cyber-500/10 text-cyber-400 border-cyber-500/30',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium',
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

export function SeverityBadge({ severity }: { severity: string }) {
  const colorMap: Record<string, string> = {
    LOW: SEVERITY_COLORS.LOW,
    MEDIUM: SEVERITY_COLORS.MEDIUM,
    HIGH: SEVERITY_COLORS.HIGH,
    CRITICAL: SEVERITY_COLORS.CRITICAL,
  };

  return (
    <span className={cn('inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium', colorMap[severity] || colorMap.LOW)}>
      {severity}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const colorMap: Record<string, string> = {
    OPEN: 'text-cyber-400 bg-cyber-500/10 border-cyber-500/30',
    INVESTIGATING: 'text-alert-high bg-alert-high/10 border-alert-high/30',
    RESOLVED: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
    DISMISSED: 'text-gray-500 bg-gray-500/10 border-gray-500/30',
    ACTIVE: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
    BLOCKED: 'text-alert-critical bg-alert-critical/10 border-alert-critical/30',
    APPROVED: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
    FLAGGED: 'text-alert-high bg-alert-high/10 border-alert-high/30',
    PENDING: 'text-alert-medium bg-alert-medium/10 border-alert-medium/30',
  };

  return (
    <span className={cn('inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium', colorMap[status] || colorMap.OPEN)}>
      {status}
    </span>
  );
}
