'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge, SeverityBadge, StatusBadge } from '@/components/ui/Badge';
import { AlertTypeBadge } from '@/components/dashboard/AlertBadge';
import { RiskBreakdown } from '@/components/dashboard/RiskBreakdown';
import { FeatureContributions } from '@/components/dashboard/FeatureContributions';
import { CardSkeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/components/ui/Toast';
import { fetchAlertById } from '@/lib/api';
import { formatTimestamp } from '@/lib/utils';
import type { FraudAlert } from '@/lib/types';

export default function AlertDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { addToast } = useToast();
  const [alert, setAlert] = useState<FraudAlert | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      fetchAlertById(params.id as string).then((data) => {
        setAlert(data);
      }).finally(() => setLoading(false));
    }
  }, [params.id]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-64 bg-navy-700/50 rounded animate-pulse" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      </div>
    );
  }

  if (!alert) {
    return (
      <div className="space-y-6">
        <PageHeader title="Alert Not Found" />
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500">The requested alert could not be found.</p>
            <Button className="mt-4" variant="outline" onClick={() => router.push('/dashboard/alerts')}>
              Back to Alerts
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const handleAction = (action: string) => {
    addToast(`Alert ${action.toLowerCase()}d successfully`, 'success');
    router.push('/dashboard/alerts');
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title={`Alert ${alert.id}`}
        description={alert.description}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => router.push(`/dashboard/investigate?user=${alert.userId}`)}>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Investigate
            </Button>
            <Button size="sm" onClick={() => handleAction('Resolved')}>Resolve</Button>
            <Button variant="secondary" size="sm" onClick={() => handleAction('Dismissed')}>Dismiss</Button>
            <Button variant="danger" size="sm" onClick={() => handleAction('Block User')}>Block User</Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardTitle>Alert Details</CardTitle>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-xs text-gray-500">Alert ID</span>
              <span className="text-xs font-mono text-gray-300">{alert.id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-gray-500">Type</span>
              <AlertTypeBadge type={alert.type} />
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-gray-500">Severity</span>
              <SeverityBadge severity={alert.severity} />
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-gray-500">Status</span>
              <StatusBadge status={alert.status} />
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-gray-500">Timestamp</span>
              <span className="text-xs text-gray-300">{formatTimestamp(alert.timestamp)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-gray-500">Session</span>
              <span className="text-xs font-mono text-gray-300">{alert.sessionId}</span>
            </div>
            {alert.transactionId && (
              <div className="flex justify-between">
                <span className="text-xs text-gray-500">Transaction</span>
                <span className="text-xs font-mono text-gray-300">{alert.transactionId}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-xs text-gray-500">Model Version</span>
              <span className="text-xs font-mono text-gray-300">{alert.modelVersion}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardTitle>User Information</CardTitle>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-cyber-600/20 flex items-center justify-center text-cyber-400 font-semibold">
                {alert.userName.charAt(0)}
              </div>
              <div>
                <p className="text-sm font-medium text-gray-200">{alert.userName}</p>
                <p className="text-xs text-gray-500">{alert.userEmail}</p>
              </div>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-gray-500">User ID</span>
              <span className="text-xs font-mono text-gray-300">{alert.userId}</span>
            </div>
            <Button variant="outline" size="sm" className="w-full" onClick={() => router.push(`/dashboard/investigate?user=${alert.userId}`)}>
              View Full Profile
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardTitle>Assigned To</CardTitle>
          <CardContent className="space-y-3">
            <p className="text-sm text-gray-300">{alert.assignedTo || 'Unassigned'}</p>
            <p className="text-xs text-gray-500">Assign to analyst:</p>
            <div className="flex flex-wrap gap-2">
              {['Sarah Chen', 'Marcus Jones', 'Elena Kovac'].map((name) => (
                <Button
                  key={name}
                  size="sm"
                  variant={alert.assignedTo === name ? 'primary' : 'outline'}
                  onClick={() => addToast(`Assigned to ${name}`, 'success')}
                >
                  {name.split(' ')[0]}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RiskBreakdown riskScore={alert.riskBreakdown} />

        <FeatureContributions contributions={alert.reasons.map((r, i) => ({
          feature: r.split(':')[0],
          contribution: 20 + Math.random() * 30 * (i % 2 === 0 ? 1 : -1),
          direction: i % 2 === 0 ? 'increases' as const : 'decreases' as const,
        }))} />
      </div>

      <Card>
        <CardTitle>Explainability Reasons</CardTitle>
        <CardContent>
          <ul className="space-y-3">
            {alert.reasons.map((reason, i) => (
              <li key={i} className="flex items-start gap-3 p-3 rounded-lg bg-navy-800/50">
                <div className="w-6 h-6 rounded-full bg-cyber-500/10 flex items-center justify-center shrink-0 mt-0.5">
                  <span className="text-xs font-mono text-cyber-400">{i + 1}</span>
                </div>
                <p className="text-sm text-gray-300">{reason}</p>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardTitle>Transaction Details</CardTitle>
        <CardContent>
          {alert.transactionId ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-3 rounded-lg bg-navy-800/50">
                <p className="text-xs text-gray-500">Transaction ID</p>
                <p className="text-sm font-mono text-gray-200">{alert.transactionId}</p>
              </div>
              <div className="p-3 rounded-lg bg-navy-800/50">
                <p className="text-xs text-gray-500">Amount</p>
                <p className="text-sm font-mono text-gray-200">$2,450.00</p>
              </div>
              <div className="p-3 rounded-lg bg-navy-800/50">
                <p className="text-xs text-gray-500">Merchant</p>
                <p className="text-sm text-gray-200">Unknown</p>
              </div>
              <div className="p-3 rounded-lg bg-navy-800/50">
                <p className="text-xs text-gray-500">Status</p>
                <StatusBadge status="FLAGGED" />
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-500">No transaction associated with this alert.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
