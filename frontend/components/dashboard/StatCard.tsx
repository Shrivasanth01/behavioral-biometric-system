'use client';

import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { Card, CardBody } from '@/components/ui/Card';
import { cn } from '@/lib/utils';

interface StatCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: string;
  className?: string;
}

export function StatCard({ title, value, subtitle, icon, trend, color = 'primary', className }: StatCardProps) {
  const colorClasses: Record<string, string> = {
    primary: 'bg-primary-50 text-primary-600',
    success: 'bg-success-50 text-success-600',
    warning: 'bg-warning-50 text-warning-600',
    danger: 'bg-danger-50 text-danger-600',
  };

  return (
    <Card className={cn('relative overflow-hidden', className)}>
      <CardBody>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-sm text-gray-500">{title}</p>
            <p className="text-2xl font-bold text-navy-900">{value}</p>
            {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
            {trend && (
              <div className={cn('flex items-center gap-1 text-xs font-medium', trend.isPositive ? 'text-success-600' : 'text-danger-600')}>
                {trend.isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                {Math.abs(trend.value)}%
              </div>
            )}
          </div>
          {icon && (
            <div className={cn('p-3 rounded-lg', colorClasses[color] || colorClasses.primary)}>
              {icon}
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
}
