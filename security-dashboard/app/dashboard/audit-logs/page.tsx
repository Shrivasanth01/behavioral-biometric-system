'use client';

import React, { useState, useEffect } from 'react';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { DataTable } from '@/components/dashboard/DataTable';
import { TableSkeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/components/ui/Toast';
import { fetchAuditLogs } from '@/lib/api';
import { formatTimestamp, downloadCSV } from '@/lib/utils';
import type { AuditLog } from '@/lib/types';

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [actionFilter, setActionFilter] = useState('');
  const { addToast } = useToast();

  useEffect(() => {
    fetchAuditLogs().then(setLogs).finally(() => setLoading(false));
  }, []);

  const filteredLogs = actionFilter
    ? logs.filter((l) => l.action === actionFilter)
    : logs;

  const uniqueActions = [...new Set(logs.map((l) => l.action))];

  const handleExport = () => {
    downloadCSV(filteredLogs as unknown as Record<string, unknown>[], 'audit-logs-export');
    addToast('Audit logs exported to CSV', 'success');
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Audit Logs"
        description="Track all system actions and changes"
        actions={
          <Button variant="outline" size="sm" onClick={handleExport}>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export CSV
          </Button>
        }
      />

      <Card>
        <CardContent>
          <div className="flex flex-wrap gap-3 mb-4">
            <Select
              options={[
                { value: '', label: 'All Actions' },
                ...uniqueActions.map((a) => ({ value: a, label: a.replace(/\./g, ' ') })),
              ]}
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="w-48"
            />
            <input
              type="date"
              className="cyber-input w-40"
              placeholder="Start date"
            />
            <input
              type="date"
              className="cyber-input w-40"
              placeholder="End date"
            />
            <input
              type="text"
              placeholder="Search by user or resource..."
              className="cyber-input flex-1 min-w-[200px]"
            />
          </div>

          {loading ? (
            <TableSkeleton rows={10} cols={6} />
          ) : (
            <DataTable
              columns={[
                { key: 'timestamp', label: 'Timestamp', sortable: true, render: (l: AuditLog) => <span className="text-xs text-gray-400">{formatTimestamp(l.timestamp)}</span> },
                { key: 'action', label: 'Action', sortable: true, render: (l: AuditLog) => (
                  <Badge variant={l.action.includes('alert') ? 'warning' : l.action.includes('blocked') ? 'danger' : l.action.includes('settings') ? 'info' : 'default'}>
                    {l.action.replace(/\./g, ' ')}
                  </Badge>
                )},
                { key: 'actorName', label: 'Actor', sortable: true, render: (l: AuditLog) => <span className="text-sm text-gray-200">{l.actorName}</span> },
                { key: 'resourceType', label: 'Resource', render: (l: AuditLog) => <span className="text-xs text-gray-400">{l.resourceType}</span> },
                { key: 'resourceId', label: 'Resource ID', render: (l: AuditLog) => <span className="text-xs font-mono text-gray-500">{l.resourceId}</span> },
                { key: 'ipAddress', label: 'IP Address', render: (l: AuditLog) => <span className="text-xs font-mono text-gray-500">{l.ipAddress}</span> },
              ]}
              data={filteredLogs}
              keyExtractor={(l: AuditLog) => l.id}
              onRowClick={(l: AuditLog) => setSelectedLog(l)}
              pageSize={20}
              searchable
              searchKeys={['actorName', 'action', 'resourceId', 'resourceType']}
            />
          )}
        </CardContent>
      </Card>

      <Modal
        isOpen={!!selectedLog}
        onClose={() => setSelectedLog(null)}
        title="Audit Log Details"
        size="lg"
      >
        {selectedLog && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500">Log ID</p>
                <p className="text-sm font-mono text-gray-200">{selectedLog.id}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Timestamp</p>
                <p className="text-sm text-gray-200">{formatTimestamp(selectedLog.timestamp)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Action</p>
                <Badge>{selectedLog.action.replace(/\./g, ' ')}</Badge>
              </div>
              <div>
                <p className="text-xs text-gray-500">Actor</p>
                <p className="text-sm text-gray-200">{selectedLog.actorName}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Resource</p>
                <p className="text-sm text-gray-200">{selectedLog.resourceType}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Resource ID</p>
                <p className="text-sm font-mono text-gray-200">{selectedLog.resourceId}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">IP Address</p>
                <p className="text-sm font-mono text-gray-200">{selectedLog.ipAddress}</p>
              </div>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-2">Details (JSON)</p>
              <pre className="cyber-input p-3 text-xs font-mono text-gray-300 overflow-auto max-h-64">
                {JSON.stringify(selectedLog.details, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
