'use client';

import React from 'react';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { Progress } from '@/components/ui/Progress';
import type { RiskScore } from '@/lib/types';
import { getRiskColor } from '@/lib/utils';

interface RiskBreakdownProps {
  riskScore: RiskScore;
  className?: string;
}

export function RiskBreakdown({ riskScore, className }: RiskBreakdownProps) {
  return (
    <Card className={className}>
      <CardTitle>Risk Score Breakdown</CardTitle>
      <CardContent className="space-y-4">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-400">ML Model Score</span>
            <span className="font-mono font-semibold" style={{ color: getRiskColor(riskScore.ml) }}>
              {riskScore.ml.toFixed(1)}
            </span>
          </div>
          <Progress value={riskScore.ml} variant="risk" size="md" />
        </div>
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-400">Rules Engine Score</span>
            <span className="font-mono font-semibold" style={{ color: getRiskColor(riskScore.rules) }}>
              {riskScore.rules.toFixed(1)}
            </span>
          </div>
          <Progress value={riskScore.rules} variant="risk" size="md" />
        </div>
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-400">Heuristic Score</span>
            <span className="font-mono font-semibold" style={{ color: getRiskColor(riskScore.heuristic) }}>
              {riskScore.heuristic.toFixed(1)}
            </span>
          </div>
          <Progress value={riskScore.heuristic} variant="risk" size="md" />
        </div>
        <div className="pt-2 border-t border-navy-700/50">
          <div className="flex justify-between text-sm">
            <span className="text-gray-300 font-medium">Overall Risk</span>
            <span className="font-mono font-bold text-lg" style={{ color: getRiskColor(riskScore.overall) }}>
              {riskScore.overall.toFixed(1)}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
