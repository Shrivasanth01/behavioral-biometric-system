'use client';

import React from 'react';
import { BarChart } from '@/components/dashboard/BarChart';
import type { FeatureContribution } from '@/lib/types';

interface FeatureContributionsProps {
  contributions: FeatureContribution[];
  className?: string;
}

export function FeatureContributions({ contributions, className }: FeatureContributionsProps) {
  const data = contributions.map((c) => ({
    name: c.feature,
    value: c.direction === 'increases' ? c.contribution : -c.contribution,
    fill: c.direction === 'increases' ? '#ef4444' : '#3b82f6',
  }));

  return (
    <BarChart
      data={data}
      title="Feature Contributions to Risk"
      horizontal
      height={280}
      className={className}
    />
  );
}
