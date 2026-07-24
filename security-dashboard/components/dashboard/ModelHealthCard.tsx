'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Progress } from '@/components/ui/Progress';
import { formatRelativeTime } from '@/lib/utils';

interface ModelHealthCardProps {
  modelVersion: string;
  lastTrained: string;
  driftStatus: string;
  accuracy: number;
  falsePositiveRate: number;
  className?: string;
}

export function ModelHealthCard({
  modelVersion,
  lastTrained,
  driftStatus,
  accuracy,
  falsePositiveRate,
  className,
}: ModelHealthCardProps) {
  const driftColor = driftStatus === 'STABLE' ? 'success' : driftStatus === 'WARNING' ? 'warning' : 'danger';
  const driftLabel = driftStatus === 'STABLE' ? 'Stable' : driftStatus === 'WARNING' ? 'Warning' : 'Drifted';

  return (
    <Card className={className}>
      <CardTitle>Model Health</CardTitle>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-gray-500 mb-1">Model Version</p>
            <p className="text-sm font-mono text-gray-200">{modelVersion}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Drift Status</p>
            <Badge variant={driftColor}>{driftLabel}</Badge>
          </div>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Last Trained</p>
          <p className="text-sm text-gray-300">{formatRelativeTime(lastTrained)}</p>
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Accuracy</span>
            <span className="font-mono text-gray-300">{accuracy.toFixed(1)}%</span>
          </div>
          <Progress value={accuracy} variant="success" size="sm" />
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">False Positive Rate</span>
            <span className={cn('font-mono', falsePositiveRate > 3 ? 'text-red-400' : 'text-gray-300')}>
              {falsePositiveRate.toFixed(2)}%
            </span>
          </div>
          <Progress value={Math.min(falsePositiveRate * 20, 100)} variant="risk" size="sm" />
        </div>
      </CardContent>
    </Card>
  );
}
