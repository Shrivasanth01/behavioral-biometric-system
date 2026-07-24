'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { formatTimestamp, getRiskColor } from '@/lib/utils';
import type { Session } from '@/lib/types';

interface SessionTimelineProps {
  sessions: Session[];
  className?: string;
}

export function SessionTimeline({ sessions, className }: SessionTimelineProps) {
  const sorted = [...sessions].sort(
    (a, b) => new Date(b.startTime).getTime() - new Date(a.startTime).getTime()
  );

  return (
    <div className={cn('space-y-2', className)}>
      {sorted.map((session, i) => (
        <div key={session.id} className="flex gap-3">
          <div className="flex flex-col items-center">
            <div
              className={cn(
                'w-3 h-3 rounded-full border-2 mt-1',
                session.riskBand === 'CRITICAL' ? 'border-red-500 bg-red-500/30' :
                session.riskBand === 'HIGH' ? 'border-orange-500 bg-orange-500/30' :
                session.riskBand === 'MEDIUM' ? 'border-yellow-500 bg-yellow-500/30' :
                'border-blue-500 bg-blue-500/30'
              )}
            />
            {i < sorted.length - 1 && <div className="w-px flex-1 bg-navy-700/50 mt-1" />}
          </div>
          <div className={cn(
            'flex-1 pb-4',
            'border-l border-navy-700/30 pl-4'
          )}>
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-gray-500">{session.id}</span>
              <div className="flex items-center gap-2">
                {session.isActive && (
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                )}
                <span
                  className="text-xs font-mono font-semibold"
                  style={{ color: getRiskColor(session.riskScore) }}
                >
                  {session.riskScore.toFixed(0)}
                </span>
              </div>
            </div>
            <div className="mt-1 text-xs text-gray-400">
              {formatTimestamp(session.startTime)}
              {session.endTime && ` → ${formatTimestamp(session.endTime)}`}
            </div>
            <div className="mt-1 flex flex-wrap gap-2 text-[11px] text-gray-500">
              <span>{session.deviceType}</span>
              <span>{session.location}</span>
              <span>{session.ipAddress}</span>
              <span>{session.actions} actions</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
