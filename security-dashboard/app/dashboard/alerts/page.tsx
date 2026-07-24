'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge, SeverityBadge, StatusBadge } from '@/components/ui/Badge';
import { AlertTypeBadge } from '@/components/dashboard/AlertBadge';
import { DataTable } from '@/components/dashboard/DataTable';
import { TableSkeleton, CardSkeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/components/ui/Toast';
import { fetchFraudAlerts } from '@/lib/api';
import { formatTimestamp, getRiskColor } from '@/lib/utils';
import type { FraudAlert } from '@/lib/types';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<FraudAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAlerts, setSelectedAlerts] = useState<Set<string>>(new Set());
  const router = useRouter();
  const { addToast } = useToast();

  useEffect(() => {
    fetchFraudAlerts(50).then((data) => {
      setAlerts(data);
    }).finally(() => setLoading(false));
  }, []);

  const openAlerts = alerts.filter((a) => a.status === 'OPEN').length;
  const criticalAlerts = alerts.filter((a) => a.severity === 'CRITICAL' && a.status !== 'RESOLVED' && a.status !== 'DISMISSED').length;

  const toggleSelect = (id: string) => {
    setSelectedAlerts((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleBulkAction = (action: string) => {
    addToast(`Bulk action "${action}" applied to ${selectedAlerts.size} alerts`, 'success');
    setSelectedAlerts(new Set());
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Fraud Alerts"
        description={`${openAlerts} open alerts, ${criticalAlerts} critical`}
        actions={
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-navy-800/80 text-sm">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              <span className="text-gray-400 font-mono">{criticalAlerts}</span>
              <span className="text-gray-500">critical</span>
            </div>
            <Button variant="outline" size="sm" onClick={() => fetchFraudAlerts(50).then(setAlerts)}>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </Button>
          </div>
        }
      />

      {selectedAlerts.size > 0 && (
        <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-cyber-600/10 border border-cyber-500/30">
          <span className="text-sm text-cyber-400">{selectedAlerts.size} selected</span>
          <div className="flex gap-2 ml-auto">
            <Button size="sm" variant="secondary" onClick={() => handleBulkAction('Assign')}>Assign</Button>
            <Button size="sm" variant="secondary" onClick={() => handleBulkAction('Resolve')}>Resolve</Button>
            <Button size="sm" variant="ghost" onClick={() => handleBulkAction('Dismiss')}>Dismiss</Button>
            <Button size="sm" variant="ghost" onClick={() => setSelectedAlerts(new Set())}>Clear</Button>
          </div>
        </div>
      )}

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-6">
              <TableSkeleton rows={8} cols={7} />
            </div>
          ) : (
            <DataTable
              columns={[
                {
                  key: 'select',
                  label: '',
                  render: (alert: FraudAlert) => (
                    <input
                      type="checkbox"
                      checked={selectedAlerts.has(alert.id)}
                      onChange={() => toggleSelect(alert.id)}
                      className="rounded border-navy-600 bg-navy-800 text-cyber-500 focus:ring-cyber-500"
                    />
                  ),
                },
                { key: 'id', label: 'Alert ID', sortable: true, render: (a: FraudAlert) => <span className="font-mono text-xs text-gray-400">{a.id}</span> },
                { key: 'timestamp', label: 'Time', sortable: true, render: (a: FraudAlert) => <span className="text-xs text-gray-400">{formatTimestamp(a.timestamp)}</span> },
                { key: 'userName', label: 'User', sortable: true, render: (a: FraudAlert) => <span className="text-sm text-gray-200">{a.userName}</span> },
                { key: 'type', label: 'Type', render: (a: FraudAlert) => <AlertTypeBadge type={a.type} /> },
                { key: 'severity', label: 'Severity', sortable: true, render: (a: FraudAlert) => <SeverityBadge severity={a.severity} /> },
                { key: 'riskScore', label: 'Risk Score', sortable: true, render: (a: FraudAlert) => (
                  <span className="font-mono text-xs" style={{ color: getRiskColor(a.riskScore) }}>{a.riskScore.toFixed(0)}</span>
                )},
                { key: 'status', label: 'Status', sortable: true, render: (a: FraudAlert) => <StatusBadge status={a.status} /> },
                { key: 'assignedTo', label: 'Assigned To', render: (a: FraudAlert) => <span className="text-xs text-gray-400">{a.assignedTo || '-'}</span> },
              ]}
              data={alerts}
              keyExtractor={(a: FraudAlert) => a.id}
              onRowClick={(a: FraudAlert) => router.push(`/dashboard/alerts/${a.id}`)}
              pageSize={15}
              searchable
              searchKeys={['userName', 'userEmail', 'id', 'description']}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
