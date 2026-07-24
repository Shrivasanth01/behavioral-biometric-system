'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { StatCard } from '@/components/dashboard/StatCard';
import { DonutChart } from '@/components/dashboard/DonutChart';
import { LineChart } from '@/components/dashboard/LineChart';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { SeverityBadge, StatusBadge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { CardSkeleton, ChartSkeleton, TableSkeleton } from '@/components/ui/Skeleton';
import { fetchKPI, fetchRiskDistribution, fetchDailyTrends, fetchFraudAlerts } from '@/lib/api';
import { formatTimestamp, getRiskColor } from '@/lib/utils';
import type { KPI, RiskDistribution, DailyTrend, FraudAlert } from '@/lib/types';

export default function ExecutiveOverviewPage() {
  const [kpi, setKpi] = useState<KPI | null>(null);
  const [riskDist, setRiskDist] = useState<RiskDistribution | null>(null);
  const [trends, setTrends] = useState<DailyTrend[]>([]);
  const [alerts, setAlerts] = useState<FraudAlert[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [kpiData, riskData, trendData, alertData] = await Promise.all([
        fetchKPI(),
        fetchRiskDistribution(),
        fetchDailyTrends(7),
        fetchFraudAlerts(10),
      ]);
      setKpi(kpiData);
      setRiskDist(riskData);
      setTrends(trendData);
      setAlerts(alertData);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-navy-700/50 rounded animate-pulse" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
        <ChartSkeleton />
      </div>
    );
  }

  const donutData = riskDist ? [
    { name: 'Low Risk', value: riskDist.low, color: '#3b82f6' },
    { name: 'Medium Risk', value: riskDist.medium, color: '#eab308' },
    { name: 'High Risk', value: riskDist.high, color: '#f97316' },
    { name: 'Critical', value: riskDist.critical, color: '#ef4444' },
  ] : [];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Executive Overview"
        description="Real-time fraud monitoring dashboard"
        actions={
          <Button variant="outline" size="sm" onClick={loadData}>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </Button>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard
          title="Active Users"
          value={kpi?.activeUsers?.toLocaleString() || '-'}
          icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" /></svg>}
          trend={3.2}
          trendLabel="vs yesterday"
        />
        <StatCard
          title="Active Sessions"
          value={kpi?.activeSessions?.toLocaleString() || '-'}
          icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>}
          trend={-1.5}
          trendLabel="vs yesterday"
        />
        <StatCard
          title="Transactions Today"
          value={kpi?.transactionsToday?.toLocaleString() || '-'}
          icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" /></svg>}
          trend={5.8}
          trendLabel="vs yesterday"
        />
        <StatCard
          title="Fraud Alerts"
          value={kpi?.fraudAlerts ?? '-'}
          icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>}
          trend={-8.3}
          trendLabel="vs yesterday"
          variant={kpi && kpi.fraudAlerts > 20 ? 'danger' : kpi && kpi.fraudAlerts > 10 ? 'warning' : 'default'}
        />
        <StatCard
          title="Avg Risk Score"
          value={kpi?.avgRiskScore?.toFixed(1) ?? '-'}
          icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>}
          trend={kpi && kpi.avgRiskScore > 30 ? 2.1 : -1.2}
          trendLabel="vs yesterday"
          variant={kpi && kpi.avgRiskScore > 40 ? 'danger' : kpi && kpi.avgRiskScore > 25 ? 'warning' : 'default'}
        />
        <StatCard
          title="Blocked Sessions"
          value={kpi?.blockedSessions ?? '-'}
          icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" /></svg>}
          trend={kpi && kpi.blockedSessions > 10 ? 12.5 : -5.0}
          trendLabel="vs yesterday"
          variant={kpi && kpi.blockedSessions > 15 ? 'danger' : 'default'}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DonutChart data={donutData} title="Session Risk Distribution" />
        <LineChart
          data={trends}
          title="Daily Risk Trend (7 Days)"
          lines={[
            { dataKey: 'avgRisk', color: '#06b6d4', name: 'Avg Risk Score' },
            { dataKey: 'alerts', color: '#ef4444', name: 'Fraud Alerts' },
          ]}
          area
        />
      </div>

      <Card>
        <CardTitle>Recent Fraud Alerts</CardTitle>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-navy-700/50">
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Assigned</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-700/30">
                {alerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-navy-800/50 transition-colors">
                    <td className="px-4 py-3 text-xs text-gray-400 font-mono">{formatTimestamp(alert.timestamp)}</td>
                    <td className="px-4 py-3 text-sm text-gray-200">{alert.userName}</td>
                    <td className="px-4 py-3 text-xs text-gray-400">{alert.type.replace(/_/g, ' ')}</td>
                    <td className="px-4 py-3"><SeverityBadge severity={alert.severity} /></td>
                    <td className="px-4 py-3">
                      <span className="font-mono text-xs" style={{ color: getRiskColor(alert.riskScore) }}>
                        {alert.riskScore.toFixed(0)}
                      </span>
                    </td>
                    <td className="px-4 py-3"><StatusBadge status={alert.status} /></td>
                    <td className="px-4 py-3 text-xs text-gray-400">{alert.assignedTo || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
