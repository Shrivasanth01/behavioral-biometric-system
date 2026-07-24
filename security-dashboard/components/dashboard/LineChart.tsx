'use client';

import React from 'react';
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ChartData = Record<string, any>;

interface LineChartProps {
  data: ChartData[];
  lines: { dataKey: string; color: string; name: string }[];
  title?: string;
  xKey?: string;
  area?: boolean;
  className?: string;
  height?: number;
}

export function LineChart({ data, lines, title, xKey = 'date', area, className, height = 300 }: LineChartProps) {
  const tooltipStyle = {
    background: 'rgba(10,10,26,0.95)',
    border: '1px solid rgba(99,102,241,0.2)',
    borderRadius: '8px',
    color: '#e5e7eb',
    fontSize: '12px',
  };

  return (
    <Card className={className}>
      {title && <CardTitle>{title}</CardTitle>}
      <CardContent>
        <div style={{ height }}>
          <ResponsiveContainer width="100%" height="100%">
            {area ? (
              <AreaChart data={data}>
                <defs>
                  {lines.map((l) => (
                    <linearGradient key={l.dataKey} id={`gradient-${l.dataKey}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={l.color} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={l.color} stopOpacity={0} />
                    </linearGradient>
                  ))}
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
                <XAxis dataKey={xKey} stroke="#6b7280" fontSize={11} tickMargin={8} />
                <YAxis stroke="#6b7280" fontSize={11} tickMargin={8} />
                <Tooltip contentStyle={tooltipStyle} />
                {lines.map((l) => (
                  <Area
                    key={l.dataKey}
                    type="monotone"
                    dataKey={l.dataKey}
                    stroke={l.color}
                    fill={`url(#gradient-${l.dataKey})`}
                    strokeWidth={2}
                    name={l.name}
                  />
                ))}
              </AreaChart>
            ) : (
              <RechartsLineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
                <XAxis dataKey={xKey} stroke="#6b7280" fontSize={11} tickMargin={8} />
                <YAxis stroke="#6b7280" fontSize={11} tickMargin={8} />
                <Tooltip contentStyle={tooltipStyle} />
                {lines.map((l) => (
                  <Line
                    key={l.dataKey}
                    type="monotone"
                    dataKey={l.dataKey}
                    stroke={l.color}
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4, fill: l.color }}
                    name={l.name}
                  />
                ))}
              </RechartsLineChart>
            )}
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
