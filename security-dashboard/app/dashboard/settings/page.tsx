'use client';

import React, { useState, useEffect } from 'react';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { Switch } from '@/components/ui/Switch';
import { Tabs } from '@/components/ui/Tabs';
import { CardSkeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/components/ui/Toast';
import { fetchRiskThresholds, fetchNotificationSettings } from '@/lib/api';
import type { RiskThreshold, NotificationSetting } from '@/lib/types';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('users');
  const [thresholds, setThresholds] = useState<RiskThreshold[]>([]);
  const [notifications, setNotifications] = useState<NotificationSetting[]>([]);
  const [loading, setLoading] = useState(true);
  const { addToast } = useToast();

  useEffect(() => {
    Promise.all([
      fetchRiskThresholds(),
      fetchNotificationSettings(),
    ]).then(([t, n]) => {
      setThresholds(t);
      setNotifications(n);
    }).finally(() => setLoading(false));
  }, []);

  const tabs = [
    { id: 'users', label: 'User Management' },
    { id: 'thresholds', label: 'Risk Thresholds' },
    { id: 'ml', label: 'ML Settings' },
    { id: 'notifications', label: 'Notifications' },
    { id: 'health', label: 'System Health' },
  ];

  const systemHealthItems = [
    { name: 'API Server', status: 'healthy', latency: '12ms' },
    { name: 'ML Inference', status: 'healthy', latency: '45ms' },
    { name: 'Database', status: 'healthy', latency: '3ms' },
    { name: 'Redis Cache', status: 'healthy', latency: '1ms' },
    { name: 'Message Queue', status: 'degraded', latency: '120ms' },
    { name: 'WebSocket Server', status: 'healthy', latency: '8ms' },
  ];

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-navy-700/50 rounded animate-pulse" />
        <CardSkeleton />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Admin Settings" description="System configuration and management" />

      <Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === 'users' && (
        <Card>
          <CardTitle>Analyst & Admin Management</CardTitle>
          <CardContent>
            <div className="space-y-4">
              <div className="flex gap-3">
                <Input placeholder="Email address" className="max-w-xs" />
                <Button>Add User</Button>
              </div>
              <div className="space-y-2">
                {[
                  { name: 'Sarah Chen', email: 'sarah.chen@bank.com', role: 'admin', status: 'active' },
                  { name: 'Marcus Jones', email: 'marcus.jones@bank.com', role: 'analyst', status: 'active' },
                  { name: 'Elena Kovac', email: 'elena.kovac@bank.com', role: 'analyst', status: 'active' },
                ].map((user) => (
                  <div key={user.email} className="flex items-center justify-between p-3 rounded-lg bg-navy-800/50">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-cyber-600/20 flex items-center justify-center text-cyber-400 font-semibold text-sm">
                        {user.name.charAt(0)}
                      </div>
                      <div>
                        <p className="text-sm text-gray-200">{user.name}</p>
                        <p className="text-xs text-gray-500">{user.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant={user.role === 'admin' ? 'info' : 'default'}>{user.role}</Badge>
                      <Badge variant="success">{user.status}</Badge>
                      <button className="text-gray-500 hover:text-red-400 transition-colors">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === 'thresholds' && (
        <Card>
          <CardTitle>Risk Threshold Configuration</CardTitle>
          <CardContent>
            <div className="space-y-4">
              {thresholds.map((t) => (
                <div key={t.band} className="flex items-center gap-4 p-3 rounded-lg bg-navy-800/50">
                  <Badge
                    variant={t.band === 'CRITICAL' ? 'danger' : t.band === 'HIGH' ? 'warning' : t.band === 'MEDIUM' ? 'warning' : 'info'}
                    className="w-20 justify-center"
                  >
                    {t.band}
                  </Badge>
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      value={t.min}
                      className="w-20"
                      onChange={() => {}}
                    />
                    <span className="text-gray-500">to</span>
                    <Input
                      type="number"
                      value={t.max}
                      className="w-20"
                      onChange={() => {}}
                    />
                  </div>
                  <Button size="sm" variant="ghost" className="ml-auto">Save</Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === 'ml' && (
        <div className="space-y-6">
          <Card>
            <CardTitle>ML Model Settings</CardTitle>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-200">Auto-retrain interval</p>
                  <p className="text-xs text-gray-500">How often models are retrained</p>
                </div>
                <select className="cyber-input w-32">
                  <option>6 hours</option>
                  <option>12 hours</option>
                  <option selected>24 hours</option>
                  <option>48 hours</option>
                </select>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-200">Cold start sessions</p>
                  <p className="text-xs text-gray-500">Minimum sessions before model is active</p>
                </div>
                <select className="cyber-input w-32">
                  <option>5</option>
                  <option selected>10</option>
                  <option>20</option>
                  <option>50</option>
                </select>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-200">Drift detection sensitivity</p>
                  <p className="text-xs text-gray-500">Threshold for triggering drift alerts</p>
                </div>
                <select className="cyber-input w-32">
                  <option>Low</option>
                  <option selected>Medium</option>
                  <option>High</option>
                </select>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-200">Batch inference enabled</p>
                  <p className="text-xs text-gray-500">Process predictions in batches</p>
                </div>
                <Switch checked={true} onChange={() => {}} />
              </div>
              <Button>Save Settings</Button>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'notifications' && (
        <Card>
          <CardTitle>Notification Settings</CardTitle>
          <CardContent>
            <div className="space-y-4">
              {notifications.map((n) => (
                <div key={n.id} className="flex items-center justify-between p-3 rounded-lg bg-navy-800/50">
                  <div>
                    <p className="text-sm text-gray-200">{n.channel}</p>
                    <p className="text-xs text-gray-500">{n.events.join(', ')}</p>
                    {n.webhookUrl && <p className="text-xs font-mono text-gray-600 mt-0.5">{n.webhookUrl}</p>}
                  </div>
                  <Switch
                    checked={n.enabled}
                    onChange={() => addToast(`${n.channel} ${n.enabled ? 'disabled' : 'enabled'}`, 'success')}
                  />
                </div>
              ))}
              <div className="flex gap-3 pt-2">
                <Input placeholder="Webhook URL" className="max-w-md" />
                <Button variant="secondary">Add Webhook</Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === 'health' && (
        <Card>
          <CardTitle>System Health Check</CardTitle>
          <CardContent>
            <div className="space-y-3">
              {systemHealthItems.map((item) => (
                <div key={item.name} className="flex items-center justify-between p-3 rounded-lg bg-navy-800/50">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      item.status === 'healthy' ? 'bg-emerald-500' : 'bg-alert-medium'
                    }`} />
                    <span className="text-sm text-gray-200">{item.name}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-xs text-gray-500">Latency: {item.latency}</span>
                    <Badge variant={item.status === 'healthy' ? 'success' : 'warning'}>
                      {item.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-6">
              <Button variant="secondary">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Run Full Diagnostics
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
