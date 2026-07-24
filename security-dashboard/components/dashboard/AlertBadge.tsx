'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { SeverityBadge } from '@/components/ui/Badge';
import { ALERT_TYPES } from '@/lib/constants';
import type { FraudAlert } from '@/lib/types';

interface AlertBadgeProps {
  severity: string;
  type?: string;
}

export function AlertBadge({ severity, type }: AlertBadgeProps) {
  return <SeverityBadge severity={severity} />;
}

export function AlertTypeBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    behavioral_anomaly: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    location_anomaly: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    device_anomaly: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    transaction_anomaly: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    velocity_anomaly: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
  };

  return (
    <span className={cn('inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium', colors[type] || 'bg-navy-700/50 text-gray-300')}>
      {ALERT_TYPES[type as keyof typeof ALERT_TYPES] || type}
    </span>
  );
}

export function AlertRow({ alert, onClick }: { alert: FraudAlert; onClick?: () => void }) {
  return (
    <tr className="hover:bg-navy-800/50 transition-colors cursor-pointer" onClick={onClick}>
      <td className="px-4 py-3 text-xs text-gray-400 font-mono">{alert.id}</td>
      <td className="px-4 py-3 text-sm text-gray-200">{alert.userName}</td>
      <td className="px-4 py-3"><AlertTypeBadge type={alert.type} /></td>
      <td className="px-4 py-3"><SeverityBadge severity={alert.severity} /></td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <div className={cn(
            'w-16 h-1.5 rounded-full bg-navy-700',
          )}>
            <div
              className={cn(
                'h-full rounded-full transition-all',
                alert.riskScore >= 80 ? 'bg-red-500' :
                alert.riskScore >= 60 ? 'bg-orange-500' :
                alert.riskScore >= 30 ? 'bg-yellow-500' : 'bg-blue-500'
              )}
              style={{ width: `${alert.riskScore}%` }}
            />
          </div>
          <span className="text-xs font-mono text-gray-400">{alert.riskScore.toFixed(0)}</span>
        </div>
      </td>
      <td className="px-4 py-3">
        <span className={cn(
          'inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium',
          alert.status === 'OPEN' ? 'text-cyber-400 bg-cyber-500/10 border-cyber-500/30' :
          alert.status === 'INVESTIGATING' ? 'text-orange-400 bg-orange-500/10 border-orange-500/30' :
          alert.status === 'RESOLVED' ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' :
          'text-gray-500 bg-gray-500/10 border-gray-500/30'
        )}>
          {alert.status}
        </span>
      </td>
      <td className="px-4 py-3 text-xs text-gray-400">{alert.assignedTo || '-'}</td>
    </tr>
  );
}
