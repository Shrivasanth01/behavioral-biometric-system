'use client';

import React, { useState, useEffect } from 'react';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { LineChart } from '@/components/dashboard/LineChart';
import { BarChart } from '@/components/dashboard/BarChart';
import { HeatMap } from '@/components/dashboard/HeatMap';
import { ChartSkeleton } from '@/components/ui/Skeleton';
import { fetchDailyTrends, fetchDeviceRisks, fetchTimeHeatmap } from '@/lib/api';
import type { DailyTrend, DeviceRisk, TimeHeatmapData } from '@/lib/types';

export default function RiskTrendsPage() {
  const [trends, setTrends] = useState<DailyTrend[]>([]);
  const [deviceRisks, setDeviceRisks] = useState<DeviceRisk[]>([]);
  const [heatmap, setHeatmap] = useState<TimeHeatmapData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchDailyTrends(30),
      fetchDeviceRisks(),
      fetchTimeHeatmap(),
    ]).then(([t, d, h]) => {
      setTrends(t);
      setDeviceRisks(d);
      setHeatmap(h);
    }).finally(() => setLoading(false));
  }, []);

  const bandTrend = trends.map((t) => ({
    date: t.date,
    Low: Math.max(0, t.avgRisk - 15 + Math.random() * 10),
    Medium: Math.max(0, t.avgRisk - 5 + Math.random() * 8),
    High: Math.max(0, t.avgRisk * 0.3 + Math.random() * 5),
    Critical: Math.max(0, t.avgRisk * 0.1 + Math.random() * 3),
  }));

  const topRiskUsers = Array.from({ length: 10 }, (_, i) => ({
    name: `USR-${String(i + 1).padStart(3, '0')}`,
    risk: 60 + Math.random() * 35,
    sessions: Math.floor(20 + Math.random() * 100),
  })).sort((a, b) => b.risk - a.risk);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-navy-700/50 rounded animate-pulse" />
        <ChartSkeleton />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Risk Trends" description="Long-term risk analysis and patterns" />

      <LineChart
        data={trends}
        title="Daily Risk Trend (30 Days)"
        lines={[
          { dataKey: 'avgRisk', color: '#06b6d4', name: 'Avg Risk Score' },
          { dataKey: 'alerts', color: '#ef4444', name: 'Fraud Alerts' },
          { dataKey: 'blocked', color: '#f97316', name: 'Blocked Sessions' },
        ]}
        area
      />

      <Card>
        <CardTitle>Risk Band Distribution Over Time</CardTitle>
        <CardContent>
          <div style={{ height: 300 }}>
            <svg viewBox="0 0 1000 300" className="w-full h-full">
              {bandTrend.map((d, i) => {
                const x = (i / bandTrend.length) * 950 + 25;
                const total = d.Low + d.Medium + d.High + d.Critical;
                const scale = 250 / Math.max(...bandTrend.map((b) => b.Low + b.Medium + b.High + b.Critical));
                const lowH = d.Low * scale;
                const medH = d.Medium * scale;
                const highH = d.High * scale;
                const critH = d.Critical * scale;
                const w = Math.max(6, 900 / bandTrend.length - 2);
                return (
                  <g key={i}>
                    <rect x={x} y={300 - lowH} width={w} height={lowH} fill="#3b82f6" opacity={0.8} rx={1} />
                    <rect x={x} y={300 - lowH - medH} width={w} height={medH} fill="#eab308" opacity={0.8} rx={1} />
                    <rect x={x} y={300 - lowH - medH - highH} width={w} height={highH} fill="#f97316" opacity={0.8} rx={1} />
                    <rect x={x} y={300 - lowH - medH - highH - critH} width={w} height={critH} fill="#ef4444" opacity={0.8} rx={1} />
                  </g>
                );
              })}
            </svg>
          </div>
          <div className="flex items-center justify-center gap-6 mt-4">
            <span className="flex items-center gap-2 text-xs text-gray-400"><span className="w-3 h-3 rounded bg-blue-500" /> Low</span>
            <span className="flex items-center gap-2 text-xs text-gray-400"><span className="w-3 h-3 rounded bg-yellow-500" /> Medium</span>
            <span className="flex items-center gap-2 text-xs text-gray-400"><span className="w-3 h-3 rounded bg-orange-500" /> High</span>
            <span className="flex items-center gap-2 text-xs text-gray-400"><span className="w-3 h-3 rounded bg-red-500" /> Critical</span>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BarChart
          data={topRiskUsers.map((u) => ({ name: u.name, value: u.risk, fill: u.risk >= 80 ? '#ef4444' : u.risk >= 60 ? '#f97316' : '#eab308' }))}
          title="Top 10 Highest Risk Users"
          height={300}
        />
        <BarChart
          data={deviceRisks.map((d) => ({ name: d.deviceType, value: d.riskScore, fill: d.riskScore >= 50 ? '#ef4444' : '#06b6d4' }))}
          title="Device Risk by Type"
          height={300}
        />
      </div>

      <HeatMap
        data={heatmap.map((h) => ({ ...h, value: h.riskLevel }))}
        title="Time-of-Day Risk Heatmap (Risk Level by Hour/Day)"
      />
    </div>
  );
}
