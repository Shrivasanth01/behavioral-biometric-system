'use client';

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';

interface DonutChartProps {
  data: { name: string; value: number; color: string }[];
  title?: string;
  className?: string;
}

export function DonutChart({ data, title, className }: DonutChartProps) {
  const total = data.reduce((sum, d) => sum + d.value, 0);

  return (
    <Card className={className}>
      {title && <CardTitle>{title}</CardTitle>}
      <CardContent>
        <div className="flex items-center justify-center h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={3}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={index} fill={entry.color} stroke="rgba(0,0,0,0.2)" strokeWidth={1} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: 'rgba(10,10,26,0.95)',
                  border: '1px solid rgba(99,102,241,0.2)',
                  borderRadius: '8px',
                  color: '#e5e7eb',
                  fontSize: '12px',
                }}
                formatter={(value: number) => [value.toLocaleString(), 'Sessions']}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="grid grid-cols-2 gap-2 mt-2">
          {data.map((item) => (
            <div key={item.name} className="flex items-center gap-2 text-xs text-gray-400">
              <div className="w-2.5 h-2.5 rounded-full" style={{ background: item.color }} />
              <span>{item.name}</span>
              <span className="font-mono ml-auto">{((item.value / total) * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
