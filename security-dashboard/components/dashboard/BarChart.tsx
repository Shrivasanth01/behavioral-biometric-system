'use client';

import React from 'react';
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Legend,
} from 'recharts';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';

interface BarConfig {
  dataKey: string;
  color: string;
  name?: string;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ChartData = Record<string, any>;

interface BarChartProps {
  data: ChartData[];
  title?: string;
  horizontal?: boolean;
  className?: string;
  height?: number;
  bars?: BarConfig[];
}

const defaultColors = ['#06b6d4', '#ef4444', '#10b981', '#eab308', '#8b5cf6'];

export function BarChart({ data, title, horizontal, className, height = 300, bars }: BarChartProps) {
  const tooltipStyle = {
    background: 'rgba(10,10,26,0.95)',
    border: '1px solid rgba(99,102,241,0.2)',
    borderRadius: '8px',
    color: '#e5e7eb',
    fontSize: '12px',
  };

  const hasSingleValue = data.length > 0 && 'value' in data[0];
  const maxVal = hasSingleValue
    ? Math.max(...data.map((d: any) => Math.abs(d.value)))
    : data.length > 0
      ? Math.max(...data.flatMap((d: any) => (bars || []).map((b) => Math.abs(Number(d[b.dataKey]) || 0))))
      : 100;

  return (
    <Card className={className}>
      {title && <CardTitle>{title}</CardTitle>}
      <CardContent>
        <div style={{ height }}>
          <ResponsiveContainer width="100%" height="100%">
            <RechartsBarChart
              data={data as any[]}
              layout={horizontal ? 'vertical' : 'horizontal'}
              margin={{ top: 5, right: 20, left: horizontal ? 80 : 0, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
              {horizontal ? (
                <>
                  <XAxis type="number" stroke="#6b7280" fontSize={11} domain={[-maxVal * 1.1, maxVal * 1.1]} />
                  <YAxis type="category" dataKey="name" stroke="#6b7280" fontSize={11} tickMargin={8} />
                </>
              ) : (
                <>
                  <XAxis dataKey="name" stroke="#6b7280" fontSize={11} tickMargin={8} />
                  <YAxis stroke="#6b7280" fontSize={11} tickMargin={8} />
                </>
              )}
              <Tooltip contentStyle={tooltipStyle} />
              {bars && !hasSingleValue ? (
                <>
                  <Legend wrapperStyle={{ fontSize: '12px', color: '#9ca3af' }} />
                  {bars.map((bar, i) => (
                    <Bar
                      key={bar.dataKey}
                      dataKey={bar.dataKey}
                      name={bar.name || bar.dataKey}
                      fill={bar.color || defaultColors[i % defaultColors.length]}
                      radius={[4, 4, 0, 0]}
                      maxBarSize={horizontal ? 20 : 30}
                    />
                  ))}
                </>
              ) : (
                <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={horizontal ? 20 : 40}>
                  {(data as any[]).map((entry: any, index: number) => (
                    <Cell
                      key={index}
                      fill={entry.fill || (entry.value >= 0 ? '#06b6d4' : '#ef4444')}
                      opacity={0.85}
                    />
                  ))}
                </Bar>
              )}
            </RechartsBarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
