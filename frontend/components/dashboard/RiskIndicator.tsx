'use client';

import React from 'react';
import { Shield, ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react';
import { Progress } from '@/components/ui/Progress';
import { cn, getRiskLevel } from '@/lib/utils';

interface RiskIndicatorProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showDetails?: boolean;
}

export function RiskIndicator({ score, size = 'md', showDetails = true }: RiskIndicatorProps) {
  const risk = getRiskLevel(score);

  const icons = {
    'High Risk': ShieldX,
    'Medium Risk': ShieldAlert,
    'Low Risk': ShieldCheck,
    'Trusted': ShieldCheck,
  };

  const Icon = icons[risk.label as keyof typeof icons] || Shield;

  const sizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  };

  const progressVariants = {
    'High Risk': 'danger' as const,
    'Medium Risk': 'warning' as const,
    'Low Risk': 'primary' as const,
    'Trusted': 'success' as const,
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className={cn('w-4 h-4', risk.color)} />
          <span className={cn('font-medium', risk.color, sizeClasses[size])}>
            {risk.label}
          </span>
        </div>
        <span className={cn('font-bold', risk.color, size === 'lg' ? 'text-2xl' : 'text-lg')}>
          {Math.round(score)}%
        </span>
      </div>
      <Progress
        value={score}
        variant={progressVariants[risk.label as keyof typeof progressVariants]}
        size="sm"
      />
      {showDetails && (
        <p className="text-xs text-gray-500">
          {score >= 80
            ? 'Your behavior matches your profile. No unusual patterns detected.'
            : score >= 60
              ? 'Minor deviations detected. Routine monitoring active.'
              : score >= 30
                ? 'Unusual behavior patterns. Additional verification may be required.'
                : 'Significant behavioral anomalies. Transactions may be restricted.'}
        </p>
      )}
    </div>
  );
}
