'use client';

import React, { useState } from 'react';
import { PageHeader } from '@/components/layout/PageHeader';
import { UserSearchCard } from '@/components/dashboard/UserSearchCard';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge, SeverityBadge, StatusBadge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { SessionTimeline } from '@/components/dashboard/SessionTimeline';
import { RadarChart } from '@/components/dashboard/RadarChart';
import { LineChart } from '@/components/dashboard/LineChart';
import { CardSkeleton, ChartSkeleton } from '@/components/ui/Skeleton';
import { Progress } from '@/components/ui/Progress';
import { DataTable } from '@/components/dashboard/DataTable';
import { useToast } from '@/components/ui/Toast';
import {
  fetchUserDetails,
  fetchSessionsForUser,
  fetchBehavioralProfile,
  fetchUserRiskHistory,
  fetchUserAlerts,
  fetchUserDeviceHistory,
  fetchUserTransactions,
} from '@/lib/api';
import { formatTimestamp, formatRiskScore, getRiskColor, getRiskBand } from '@/lib/utils';
import type { UserDetails, Session, BehavioralProfile, FraudAlert } from '@/lib/types';

export default function InvestigatePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [user, setUser] = useState<UserDetails | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [profile, setProfile] = useState<BehavioralProfile | null>(null);
  const [riskHistory, setRiskHistory] = useState<{ date: string; score: number }[]>([]);
  const [alerts, setAlerts] = useState<FraudAlert[]>([]);
  const [devices, setDevices] = useState<{ fingerprint: string; deviceType: string; firstSeen: string; lastSeen: string; riskScore: number }[]>([]);
  const [transactions, setTransactions] = useState<{ id: string; amount: number; timestamp: string; riskScore: number; status: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const { addToast } = useToast();

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    setLoading(true);
    setHasSearched(true);
    try {
      const userData = await fetchUserDetails(query);
      if (!userData) {
        addToast('User not found', 'error');
        setLoading(false);
        return;
      }
      setUser(userData);
      const [sessionsData, profileData, riskData, alertsData, devicesData, txnData] = await Promise.all([
        fetchSessionsForUser(userData.id),
        fetchBehavioralProfile(userData.id),
        fetchUserRiskHistory(userData.id),
        fetchUserAlerts(userData.id),
        fetchUserDeviceHistory(userData.id),
        fetchUserTransactions(userData.id),
      ]);
      setSessions(sessionsData);
      setProfile(profileData);
      setRiskHistory(riskData);
      setAlerts(alertsData);
      setDevices(devicesData);
      setTransactions(txnData);
    } catch (err) {
      addToast('Failed to load user data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const radarData = profile
    ? Object.entries(profile.features).map(([key, val]) => ({
        feature: key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
        user: val,
        population: 50 + Math.random() * 20,
      }))
    : [];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="User Investigation" description="Deep-dive into user behavior, risk, and session history" />

      <UserSearchCard onSearch={handleSearch} isLoading={loading} />

      {loading && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
      )}

      {hasSearched && !loading && !user && (
        <Card>
          <CardContent className="py-12 text-center">
            <svg className="w-12 h-12 mx-auto text-gray-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <p className="text-gray-500">No user found matching &quot;{searchQuery}&quot;</p>
            <p className="text-xs text-gray-600 mt-1">Try searching by User ID (e.g. USR-001), email, or phone number</p>
          </CardContent>
        </Card>
      )}

      {user && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardTitle>User Details</CardTitle>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500 font-mono">{user.id}</span>
                  <StatusBadge status={user.status} />
                </div>
                <div>
                  <p className="text-sm text-gray-200">{user.name}</p>
                  <p className="text-xs text-gray-500">{user.email}</p>
                  <p className="text-xs text-gray-500">{user.phone}</p>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-500">Joined</span>
                    <p className="text-gray-300">{formatTimestamp(user.accountCreated)}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Last Login</span>
                    <p className="text-gray-300">{formatTimestamp(user.lastLogin)}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Total Sessions</span>
                    <p className="text-gray-300">{user.totalSessions}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Avg Risk</span>
                    <p className="text-gray-300 font-mono" style={{ color: getRiskColor(user.avgSessionRisk) }}>
                      {user.avgSessionRisk.toFixed(1)}
                    </p>
                  </div>
                </div>
                <div className="flex gap-2 pt-2">
                  <Badge variant={user.mfaEnabled ? 'success' : 'danger'}>
                    {user.mfaEnabled ? 'MFA Enabled' : 'MFA Disabled'}
                  </Badge>
                  <Badge variant={user.ipRestricted ? 'info' : 'default'}>
                    {user.ipRestricted ? 'IP Restricted' : 'No IP Restriction'}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardTitle>Model Status</CardTitle>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Model Version</span>
                  <span className="text-sm font-mono text-gray-200">v3.2.1</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Last Trained</span>
                  <span className="text-sm text-gray-300">2h ago</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Drift Status</span>
                  <Badge variant="success">Stable</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Session Count</span>
                  <span className="text-sm font-mono text-gray-200">{user.totalSessions}</span>
                </div>
                <Progress value={profile?.features.typing_speed || 50} variant="default" size="sm" showLabel />
              </CardContent>
            </Card>

            <Card>
              <CardTitle>Recent Alerts</CardTitle>
              <CardContent className="space-y-2 max-h-48 overflow-y-auto">
                {alerts.slice(0, 5).map((alert) => (
                  <div key={alert.id} className="flex items-center justify-between p-2 rounded bg-navy-800/50">
                    <div>
                      <p className="text-xs text-gray-300 font-mono">{alert.id}</p>
                      <p className="text-[10px] text-gray-500">{alert.type.replace(/_/g, ' ')}</p>
                    </div>
                    <SeverityBadge severity={alert.severity} />
                  </div>
                ))}
                {alerts.length === 0 && <p className="text-xs text-gray-500">No recent alerts</p>}
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardTitle>Session Timeline</CardTitle>
              <CardContent className="max-h-80 overflow-y-auto cyber-scrollbar">
                <SessionTimeline sessions={sessions} />
              </CardContent>
            </Card>

            <RadarChart
              data={radarData}
              title="Behavioral Profile vs Population"
              height={320}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <LineChart
              data={riskHistory}
              title="Risk Score History (30 Days)"
              lines={[
                { dataKey: 'score', color: '#06b6d4', name: 'Risk Score' },
              ]}
              height={280}
            />

            <Card>
              <CardTitle>Device Fingerprint History</CardTitle>
              <CardContent>
                <div className="space-y-3">
                  {devices.map((d, i) => (
                    <div key={i} className="flex items-center justify-between p-2 rounded bg-navy-800/50">
                      <div>
                        <p className="text-xs text-gray-200 font-mono">{d.fingerprint}</p>
                        <p className="text-[10px] text-gray-500">{d.deviceType}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs font-mono" style={{ color: getRiskColor(d.riskScore) }}>
                          {d.riskScore.toFixed(0)}
                        </p>
                        <p className="text-[10px] text-gray-500">{formatTimestamp(d.lastSeen)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardTitle>Recent Transactions</CardTitle>
            <CardContent>
              <DataTable
                columns={[
                  { key: 'id', label: 'ID', render: (t: any) => <span className="font-mono text-xs text-gray-400">{t.id}</span> },
                  { key: 'amount', label: 'Amount', sortable: true, render: (t: any) => <span className="font-mono">${t.amount.toFixed(2)}</span> },
                  { key: 'timestamp', label: 'Time', sortable: true, render: (t: any) => <span className="text-xs text-gray-400">{formatTimestamp(t.timestamp)}</span> },
                  { key: 'riskScore', label: 'Risk Score', sortable: true, render: (t: any) => <span className="font-mono text-xs" style={{ color: getRiskColor(t.riskScore) }}>{t.riskScore.toFixed(0)}</span> },
                  { key: 'status', label: 'Status', render: (t: any) => <StatusBadge status={t.status} /> },
                ]}
                data={transactions}
                keyExtractor={(t: any) => t.id}
                pageSize={5}
              />
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
