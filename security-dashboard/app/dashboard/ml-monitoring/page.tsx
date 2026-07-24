'use client';

import React, { useState, useEffect } from 'react';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { StatCard } from '@/components/dashboard/StatCard';
import { LineChart } from '@/components/dashboard/LineChart';
import { BarChart } from '@/components/dashboard/BarChart';
import { Badge, SeverityBadge } from '@/components/ui/Badge';
import { ModelHealthCard } from '@/components/dashboard/ModelHealthCard';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { DataTable } from '@/components/dashboard/DataTable';
import { CardSkeleton, ChartSkeleton } from '@/components/ui/Skeleton';
import { Progress } from '@/components/ui/Progress';
import { fetchModelInfo, fetchUserModelHealth } from '@/lib/api';
import { formatRelativeTime, getRiskColor } from '@/lib/utils';
import type { ModelInfo, UserModelHealth } from '@/lib/types';

export default function MLMonitoringPage() {
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [userHealth, setUserHealth] = useState<UserModelHealth[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchModelInfo(),
      fetchUserModelHealth(),
    ]).then(([model, health]) => {
      setModelInfo(model);
      setUserHealth(health);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-navy-700/50 rounded animate-pulse" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
        <ChartSkeleton />
      </div>
    );
  }

  const driftBarData = modelInfo
    ? Object.entries(modelInfo.featureDriftScores).map(([feature, score]) => ({
        name: feature.replace(/_/g, ' '),
        value: score * 100,
        fill: score > 0.3 ? '#ef4444' : score > 0.15 ? '#f97316' : '#06b6d4',
      }))
    : [];

  const modelAccuracyData = Array.from({ length: 14 }, (_, i) => ({
    date: `Day ${i + 1}`,
    accuracy: 92 + Math.random() * 7,
    fpRate: 0.5 + Math.random() * 4,
  }));

  const driftedUsers = userHealth.filter((u) => u.driftStatus !== 'STABLE').length;
  const warningUsers = userHealth.filter((u) => u.driftStatus === 'WARNING').length;

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="ML Model Monitoring" description="Real-time model performance, drift detection, and user health" />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Active Models"
          value="3"
          icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>}
        />
        <StatCard
          title="Cold Start Users"
          value={userHealth.filter((u) => u.sessionCount < 30).length}
          icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          variant="warning"
        />
        <StatCard
          title="Drifted Users"
          value={driftedUsers}
          icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>}
          variant={driftedUsers > 5 ? 'danger' : 'warning'}
          trend={warningUsers}
          trendLabel="in warning"
        />
        <StatCard
          title="Retraining Queue"
          value={userHealth.length - driftedUsers > 0 ? 'Ready' : 'Idle'}
          icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ModelHealthCard
          modelVersion={modelInfo?.modelVersion || '-'}
          lastTrained={modelInfo?.lastTrained || '-'}
          driftStatus={modelInfo?.driftStatus || 'STABLE'}
          accuracy={modelInfo?.accuracy || 0}
          falsePositiveRate={modelInfo?.falsePositiveRate || 0}
        />
        <Card>
          <CardTitle>Anomaly Score Distribution</CardTitle>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Average Anomaly Score</span>
                <span className="font-mono text-gray-200">{modelInfo?.avgAnomalyScore.toFixed(1) || '-'}</span>
              </div>
              <Progress value={modelInfo?.avgAnomalyScore || 0} variant="risk" size="md" />
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="p-2 rounded bg-navy-800/50">
                <p className="text-xs text-gray-500">Low</p>
                <p className="text-sm font-mono text-gray-200">65%</p>
              </div>
              <div className="p-2 rounded bg-navy-800/50">
                <p className="text-xs text-gray-500">Medium</p>
                <p className="text-sm font-mono text-gray-200">22%</p>
              </div>
              <div className="p-2 rounded bg-navy-800/50">
                <p className="text-xs text-gray-500">High+</p>
                <p className="text-sm font-mono text-alert-high">13%</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardTitle>Model Health Summary</CardTitle>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">Total Users Tracked</span>
              <span className="text-sm font-mono text-gray-200">{userHealth.length}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">Stable Models</span>
              <span className="text-sm font-mono text-emerald-400">{userHealth.filter((u) => u.driftStatus === 'STABLE').length}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">Warning</span>
              <span className="text-sm font-mono text-alert-high">{warningUsers}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">Drifted</span>
              <span className="text-sm font-mono text-red-400">{driftedUsers}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">Avg Sessions/User</span>
              <span className="text-sm font-mono text-gray-200">
                {(userHealth.reduce((s, u) => s + u.sessionCount, 0) / userHealth.length).toFixed(0)}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LineChart
          data={modelAccuracyData}
          title="Model Accuracy Trend"
          lines={[
            { dataKey: 'accuracy', color: '#10b981', name: 'Accuracy (%)' },
          ]}
          height={280}
        />
        <LineChart
          data={modelAccuracyData}
          title="False Positive Rate Trend"
          lines={[
            { dataKey: 'fpRate', color: '#ef4444', name: 'FP Rate (%)' },
          ]}
          height={280}
        />
      </div>

      <BarChart
        data={driftBarData}
        title="Feature Drift Scores"
        height={240}
      />

      <Card>
        <CardTitle>User Model Health</CardTitle>
        <CardContent>
          <DataTable
            columns={[
              { key: 'userId', label: 'User ID', sortable: true, render: (u: UserModelHealth) => <span className="font-mono text-xs text-gray-300">{u.userId}</span> },
              { key: 'sessionCount', label: 'Sessions', sortable: true, render: (u: UserModelHealth) => <span className="font-mono">{u.sessionCount}</span> },
              { key: 'lastTrained', label: 'Last Trained', sortable: true, render: (u: UserModelHealth) => <span className="text-xs text-gray-400">{formatRelativeTime(u.lastTrained)}</span> },
              { key: 'driftStatus', label: 'Drift Status', sortable: true, render: (u: UserModelHealth) => (
                <Badge variant={u.driftStatus === 'STABLE' ? 'success' : u.driftStatus === 'WARNING' ? 'warning' : 'danger'}>
                  {u.driftStatus}
                </Badge>
              )},
              { key: 'modelVersion', label: 'Version', render: (u: UserModelHealth) => <span className="text-xs font-mono text-gray-400">{u.modelVersion}</span> },
              { key: 'threshold', label: 'Threshold', render: (u: UserModelHealth) => <span className="font-mono text-xs">{(u.threshold * 100).toFixed(0)}%</span> },
              { key: 'avgRiskScore', label: 'Avg Risk', sortable: true, render: (u: UserModelHealth) => (
                <span className="font-mono text-xs" style={{ color: getRiskColor(u.avgRiskScore) }}>{u.avgRiskScore.toFixed(1)}</span>
              )},
            ]}
            data={userHealth}
            keyExtractor={(u: UserModelHealth) => u.userId}
            searchable
            searchKeys={['userId']}
            pageSize={10}
          />
        </CardContent>
      </Card>
    </div>
  );
}
