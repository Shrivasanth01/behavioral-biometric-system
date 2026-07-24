'use client';

import React from 'react';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';

interface HeatMapProps {
  data: { hour: number; day: string; value: number; count?: number }[];
  title?: string;
  className?: string;
}

const HOURS = Array.from({ length: 24 }, (_, i) => i);
const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export function HeatMap({ data, title, className }: HeatMapProps) {
  const getColor = (value: number) => {
    if (value >= 70) return 'bg-red-500/80';
    if (value >= 50) return 'bg-orange-500/60';
    if (value >= 30) return 'bg-yellow-500/40';
    if (value >= 15) return 'bg-cyan-500/30';
    return 'bg-navy-700/30';
  };

  const getValue = (day: string, hour: number) => {
    const item = data.find((d) => d.day === day && d.hour === hour);
    return item?.value ?? 0;
  };

  return (
    <Card className={className}>
      {title && <CardTitle>{title}</CardTitle>}
      <CardContent>
        <div className="overflow-x-auto">
          <div className="grid grid-cols-[40px_repeat(24,1fr)] gap-0.5 min-w-[600px]">
            <div className="text-xs text-gray-500" />
            {HOURS.map((h) => (
              <div key={h} className="text-[10px] text-gray-500 text-center">
                {h.toString().padStart(2, '0')}
              </div>
            ))}
            {DAYS.map((day) => (
              <React.Fragment key={day}>
                <div className="text-xs text-gray-500 flex items-center">{day}</div>
                {HOURS.map((hour) => {
                  const val = getValue(day, hour);
                  return (
                    <div
                      key={`${day}-${hour}`}
                      className={`aspect-square rounded ${getColor(val)} hover:ring-1 hover:ring-cyber-400 cursor-pointer transition-all`}
                      title={`${day} ${hour}:00 - Risk: ${val.toFixed(1)}`}
                    />
                  );
                })}
              </React.Fragment>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-2 mt-3 justify-end">
          <span className="text-[10px] text-gray-500">Low</span>
          <div className="flex gap-0.5">
            <div className="w-3 h-3 rounded bg-navy-700/30" />
            <div className="w-3 h-3 rounded bg-cyan-500/30" />
            <div className="w-3 h-3 rounded bg-yellow-500/40" />
            <div className="w-3 h-3 rounded bg-orange-500/60" />
            <div className="w-3 h-3 rounded bg-red-500/80" />
          </div>
          <span className="text-[10px] text-gray-500">High</span>
        </div>
      </CardContent>
    </Card>
  );
}
