'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface RiskGaugeProps {
  score: number;
  size?: number;
  className?: string;
}

export function RiskGauge({ score, size = 120, className }: RiskGaugeProps) {
  const radius = (size - 20) / 2;
  const strokeWidth = 12;
  const normalizedRadius = radius - strokeWidth / 2;
  const circumference = 2 * Math.PI * normalizedRadius;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  const center = size / 2;

  const color = score >= 80 ? '#ef4444' : score >= 60 ? '#f97316' : score >= 30 ? '#eab308' : '#3b82f6';

  return (
    <div className={cn('flex flex-col items-center', className)}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={center}
          cy={center}
          r={normalizedRadius}
          fill="none"
          stroke="rgba(15,13,46,0.8)"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={center}
          cy={center}
          r={normalizedRadius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center" style={{ width: size, height: size }}>
        <span className="text-2xl font-bold font-mono" style={{ color }}>{Math.round(score)}</span>
        <span className="text-xs text-gray-500 mt-0.5">Risk Score</span>
      </div>
    </div>
  );
}
