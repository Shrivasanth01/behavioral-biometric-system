'use client';

import React from 'react';
import {
  RadarChart as RechartsRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';

interface RadarChartProps {
  data: { feature: string; user: number; population: number }[];
  title?: string;
  className?: string;
  height?: number;
}

export function RadarChart({ data, title, className, height = 300 }: RadarChartProps) {
  return (
    <Card className={className}>
      {title && <CardTitle>{title}</CardTitle>}
      <CardContent>
        <div style={{ height }}>
          <ResponsiveContainer width="100%" height="100%">
            <RechartsRadarChart data={data}>
              <PolarGrid stroke="rgba(99,102,241,0.15)" />
              <PolarAngleAxis dataKey="feature" tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 10 }} />
              <Radar
                name="User"
                dataKey="user"
                stroke="#06b6d4"
                fill="#06b6d4"
                fillOpacity={0.2}
                strokeWidth={2}
              />
              <Radar
                name="Population"
                dataKey="population"
                stroke="#6366f1"
                fill="#6366f1"
                fillOpacity={0.1}
                strokeWidth={2}
                strokeDasharray="4 4"
              />
              <Legend
                wrapperStyle={{ fontSize: '12px', color: '#9ca3af' }}
              />
            </RechartsRadarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
