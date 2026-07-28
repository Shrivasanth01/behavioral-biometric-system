'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { SeverityBadge, StatusBadge } from '@/components/ui/Badge';
import { useToast } from '@/components/ui/Toast';
import { formatTimestamp } from '@/lib/utils';
import type { FraudAlert } from '@/lib/types';

interface SecOpsAlert extends FraudAlert {
  biometricVector: string;
  deviceHash: string;
  location: string;
  confidenceScore: number;
}

const INITIAL_ALERTS: SecOpsAlert[] = [
  {
    id: 'SEC-ALT-884',
    userId: 'USR-77102',
    userName: 'Jonathan Sterling',
    userEmail: 'j.sterling@enterprise.ch',
    timestamp: new Date().toISOString(),
    severity: 'CRITICAL',
    status: 'OPEN',
    type: 'behavioral_anomaly',
    riskScore: 98,
    assignedTo: 'Automated AI Containment',
    sessionId: 'SESS-99214-GB',
    description: 'Keystroke flight timings 4.2σ outside user behavioral baseline during high-value wire transfer.',
    biometricVector: 'Keystroke Dynamics (Flight Time & Dwell Variance)',
    deviceHash: 'MacBook Pro / Chrome / AudioCanvas:88f2a1',
    location: 'London, UK (VPN Endpoint Detected)',
    confidenceScore: 98.4,
    riskBreakdown: { overall: 98, ml: 99, rules: 95, heuristic: 97 },
    reasons: ['Keystroke cadence anomaly', 'VPN proxy endpoint detected'],
    modelVersion: 'v2.4-Transformer',
  },
  {
    id: 'SEC-ALT-883',
    userId: 'USR-30491',
    userName: 'Eleanor Vance',
    userEmail: 'e.vance@banking.com',
    timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
    severity: 'CRITICAL',
    status: 'OPEN',
    type: 'velocity_anomaly',
    riskScore: 99,
    assignedTo: null,
    sessionId: 'SESS-44102-DE',
    description: 'Mouse spline curvature coefficient = 1.0 (Zero human hand tremor / Bot Automated Scripting).',
    biometricVector: 'Mouse Trajectory & Accelerometer Telemetry',
    deviceHash: 'Windows 11 / Edge / WebGL:041e8c',
    location: 'Frankfurt, Germany',
    confidenceScore: 99.1,
    riskBreakdown: { overall: 99, ml: 99, rules: 98, heuristic: 99 },
    reasons: ['Zero human micro-tremor detected', 'Linear B-Spline motion trajectory'],
    modelVersion: 'v2.4-Transformer',
  },
  {
    id: 'SEC-ALT-882',
    userId: 'USR-51928',
    userName: 'Marco Rossi',
    userEmail: 'm.rossi@fintech.ch',
    timestamp: new Date(Date.now() - 12 * 60000).toISOString(),
    severity: 'HIGH',
    status: 'INVESTIGATING',
    type: 'device_anomaly',
    riskScore: 87,
    assignedTo: 'Sarah Chen (Senior Analyst)',
    sessionId: 'SESS-88120-CH',
    description: 'Concurrent session initialization with anomalous touch swipe speed (1800 px/s vs normal 450 px/s).',
    biometricVector: 'Touch Swipe Velocity & Contact Area',
    deviceHash: 'iPhone 15 Pro / Safari Mobile',
    location: 'Zurich, Switzerland',
    confidenceScore: 86.7,
    riskBreakdown: { overall: 87, ml: 89, rules: 82, heuristic: 88 },
    reasons: ['Abnormal swipe speed (1800 px/s)', 'Concurrent device token'],
    modelVersion: 'v2.4-Transformer',
  },
  {
    id: 'SEC-ALT-881',
    userId: 'USR-12940',
    userName: 'Avery Clark',
    userEmail: 'avery.c@globalwealth.fr',
    timestamp: new Date(Date.now() - 25 * 60000).toISOString(),
    severity: 'MEDIUM',
    status: 'OPEN',
    type: 'behavioral_anomaly',
    riskScore: 68,
    assignedTo: null,
    sessionId: 'SESS-33912-FR',
    description: 'Sudden change in navigation pattern pacing during password recovery challenge.',
    biometricVector: 'UI Navigation Transitions & Dwell',
    deviceHash: 'iPad OS 17 / Safari',
    location: 'Paris, France',
    confidenceScore: 68.2,
    riskBreakdown: { overall: 68, ml: 72, rules: 60, heuristic: 70 },
    reasons: ['Navigation pacing deviation during password recovery'],
    modelVersion: 'v2.4-Transformer',
  },
  {
    id: 'SEC-ALT-880',
    userId: 'USR-90211',
    userName: 'Hassan Al-Zani',
    userEmail: 'hassan@techgroup.ae',
    timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
    severity: 'LOW',
    status: 'RESOLVED',
    type: 'behavioral_anomaly',
    riskScore: 41,
    assignedTo: 'Automated Step-Up MFA',
    sessionId: 'SESS-10294-DE',
    description: 'Minor deviation in scroll rhythm; resolved after successful biometric touch verification.',
    biometricVector: 'Scroll Rhythm & Acceleration',
    deviceHash: 'Pixel 8 / Android Chrome',
    location: 'Berlin, Germany',
    confidenceScore: 41.0,
    riskBreakdown: { overall: 41, ml: 44, rules: 35, heuristic: 40 },
    reasons: ['Scroll speed variance (+1.4σ)'],
    modelVersion: 'v2.4-Transformer',
  }
];

export default function SecOpsAlertsPage() {
  const [alerts, setAlerts] = useState<SecOpsAlert[]>(INITIAL_ALERTS);
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isLiveStream, setIsLiveStream] = useState<boolean>(true);
  const [selectedAlerts, setSelectedAlerts] = useState<Set<string>>(new Set());
  const router = useRouter();
  const { addToast } = useToast();

  useEffect(() => {
    if (!isLiveStream) return;
    const interval = setInterval(() => {
      const randomId = `SEC-ALT-${Math.floor(885 + Math.random() * 100)}`;
      const vectors = [
        'Keystroke Dwell Zero-Variance (Script Attack)',
        'Touch Pressure Deviation +3.8σ (Remote Access Tool)',
        'Mouse Telemetry Spoofing / Linear B-Spline',
        'Gyroscope / Accelerometer Sensor Desync'
      ];
      const newAlert: SecOpsAlert = {
        id: randomId,
        userId: `USR-${Math.floor(10000 + Math.random() * 89999)}`,
        userName: 'Detected Session Target',
        userEmail: 'alert-target@biobank.com',
        timestamp: new Date().toISOString(),
        severity: Math.random() > 0.4 ? 'CRITICAL' : 'HIGH',
        status: 'OPEN',
        type: 'behavioral_anomaly',
        riskScore: Math.floor(85 + Math.random() * 14),
        assignedTo: null,
        sessionId: `SESS-${Math.floor(10000 + Math.random() * 89999)}-LIVE`,
        description: `Active anomaly detected: ${vectors[Math.floor(Math.random() * vectors.length)]}`,
        biometricVector: vectors[Math.floor(Math.random() * vectors.length)],
        deviceHash: `DeviceHash:${Math.random().toString(36).substring(2, 8).toUpperCase()}`,
        location: 'Detected via Zero-Trust Edge Monitor',
        confidenceScore: parseFloat((85 + Math.random() * 14).toFixed(1)),
        riskBreakdown: { overall: 90, ml: 92, rules: 88, heuristic: 91 },
        reasons: ['Real-time streaming anomaly detection'],
        modelVersion: 'v2.4-Transformer',
      };
      setAlerts((prev) => [newAlert, ...prev]);
      addToast(`🚨 New High-Confidence Threat Detected: ${newAlert.id}`, 'warning');
    }, 15000);

    return () => clearInterval(interval);
  }, [isLiveStream, addToast]);

  const toggleSelect = (id: string) => {
    setSelectedAlerts((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleBulkAction = (action: string) => {
    addToast(`⚡ Executed "${action}" on ${selectedAlerts.size} high-risk target(s)`, 'success');
    setAlerts((prev) =>
      prev.map((a) => (selectedAlerts.has(a.id) ? { ...a, status: action === 'Resolve' ? 'RESOLVED' : a.status } : a))
    );
    setSelectedAlerts(new Set());
  };

  const filteredAlerts = alerts.filter((a) => {
    if (filterSeverity !== 'ALL' && a.severity !== filterSeverity) return false;
    if (searchQuery && !a.id.toLowerCase().includes(searchQuery.toLowerCase()) && !a.userId.toLowerCase().includes(searchQuery.toLowerCase()) && !a.biometricVector.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="SecOps Real-Time Behavioral Threat Console"
        description="Continuous ingestion of AI-driven biometric fraud anomalies and automated defensive containment"
        actions={
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsLiveStream(!isLiveStream)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${
                isLiveStream
                  ? 'bg-green-500/20 text-green-400 border border-green-500/40 shadow-lg shadow-green-500/10'
                  : 'bg-navy-800 text-gray-400 border border-navy-700'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${isLiveStream ? 'bg-green-400 animate-ping' : 'bg-gray-500'}`} />
              {isLiveStream ? 'LIVE INGESTION: ON' : 'STREAM PAUSED'}
            </button>
            <Button variant="outline" size="sm" onClick={() => setAlerts(INITIAL_ALERTS)}>
              Reset Stream
            </Button>
          </div>
        }
      />

      {/* KPI Command Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-navy-900/90 border border-red-500/30 backdrop-blur-md shadow-lg shadow-red-950/20">
          <div className="text-xs font-mono uppercase text-gray-400">Active Critical Anomaly Threads</div>
          <div className="text-3xl font-bold text-red-400 font-mono mt-1">
            {alerts.filter((a) => a.severity === 'CRITICAL' && a.status === 'OPEN').length}
            <span className="text-xs text-red-500 ml-2 font-normal">↑ +14% vs avg</span>
          </div>
        </div>
        <div className="p-4 rounded-xl bg-navy-900/90 border border-cyber-500/30 backdrop-blur-md">
          <div className="text-xs font-mono uppercase text-gray-400">Mean Triage & Lockout Latency</div>
          <div className="text-3xl font-bold text-cyber-400 font-mono mt-1">142ms</div>
        </div>
        <div className="p-4 rounded-xl bg-navy-900/90 border border-green-500/30 backdrop-blur-md">
          <div className="text-xs font-mono uppercase text-gray-400">Auto-Contained Sessions (24h)</div>
          <div className="text-3xl font-bold text-green-400 font-mono mt-1">1,489</div>
        </div>
        <div className="p-4 rounded-xl bg-navy-900/90 border border-purple-500/30 backdrop-blur-md">
          <div className="text-xs font-mono uppercase text-gray-400">ML False Positive Rate</div>
          <div className="text-3xl font-bold text-purple-400 font-mono mt-1">0.18%</div>
        </div>
      </div>

      {/* Control & Search Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-navy-900/80 p-4 rounded-xl border border-navy-700/60">
        <div className="flex items-center gap-2 flex-1 max-w-md">
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search Alert ID, User ID, or Biometric Vector..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-navy-950/80 border border-navy-700 rounded-lg px-3 py-1.5 text-sm text-gray-200 focus:outline-none focus:border-cyber-500 font-mono"
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-gray-400">SEVERITY FILTER:</span>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-3 py-1 rounded text-xs font-mono font-bold transition-all ${
                filterSeverity === sev
                  ? 'bg-cyber-600 text-white shadow-md shadow-cyber-500/30'
                  : 'bg-navy-800 text-gray-400 hover:text-gray-200 hover:bg-navy-700'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Bulk action header */}
      {selectedAlerts.size > 0 && (
        <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-red-950/40 border border-red-500/50 animate-pulse">
          <div className="flex items-center gap-2">
            <span className="text-sm font-mono text-red-400 font-bold">⚠️ {selectedAlerts.size} THREAT THREADS SELECTED</span>
          </div>
          <div className="flex gap-2">
            <Button size="sm" variant="danger" onClick={() => handleBulkAction('Instant Account Freeze & Token Revoke')}>
              🔒 Instant Force Freeze
            </Button>
            <Button size="sm" variant="secondary" onClick={() => handleBulkAction('Enforce Step-Up Biometric Challenge')}>
              📲 Push Step-Up Challenge
            </Button>
            <Button size="sm" variant="outline" onClick={() => handleBulkAction('Resolve')}>
              ✓ Mark False Positive & Retrain
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setSelectedAlerts(new Set())}>
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Real-time Threat Stream Table */}
      <Card className="border-navy-700/80 shadow-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse font-sans">
            <thead>
              <tr className="bg-navy-950 text-gray-400 text-xs font-mono uppercase border-b border-navy-700/80">
                <th className="py-3.5 px-4 w-12">
                  <input
                    type="checkbox"
                    onChange={(e) => {
                      if (e.target.checked) setSelectedAlerts(new Set(alerts.map((a) => a.id)));
                      else setSelectedAlerts(new Set());
                    }}
                    checked={selectedAlerts.size === alerts.length && alerts.length > 0}
                    className="rounded border-navy-600 bg-navy-800 text-cyber-500 focus:ring-cyber-500"
                  />
                </th>
                <th className="py-3.5 px-4">Threat ID & Target</th>
                <th className="py-3.5 px-4">AI Severity & Risk</th>
                <th className="py-3.5 px-4">Behavioral Anomaly Vector</th>
                <th className="py-3.5 px-4">Telemetry Hash & Location</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-right">Forensic Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-800/60 text-sm">
              {filteredAlerts.map((alert) => (
                <tr
                  key={alert.id}
                  className={`hover:bg-navy-800/40 transition-colors duration-150 ${
                    selectedAlerts.has(alert.id) ? 'bg-cyber-900/20 border-l-4 border-cyber-500' : ''
                  }`}
                >
                  <td className="py-4 px-4">
                    <input
                      type="checkbox"
                      checked={selectedAlerts.has(alert.id)}
                      onChange={() => toggleSelect(alert.id)}
                      className="rounded border-navy-600 bg-navy-800 text-cyber-500 focus:ring-cyber-500"
                    />
                  </td>
                  <td className="py-4 px-4 font-mono">
                    <div className="font-bold text-cyber-400">{alert.id}</div>
                    <div className="text-xs text-gray-400 mt-0.5">USR: <span className="text-gray-200">{alert.userId}</span> ({alert.userName})</div>
                    <div className="text-[10px] text-gray-500 mt-1">{formatTimestamp(alert.timestamp)}</div>
                  </td>
                  <td className="py-4 px-4">
                    <SeverityBadge severity={alert.severity} />
                    <div className="mt-2 text-xs font-mono">
                      <span className="text-gray-400">AI Conf: </span>
                      <span className={alert.confidenceScore > 90 ? 'text-red-400 font-bold' : 'text-yellow-400 font-bold'}>
                        {alert.confidenceScore}%
                      </span>
                    </div>
                  </td>
                  <td className="py-4 px-4 max-w-sm">
                    <div className="font-medium text-gray-200 text-xs font-mono bg-navy-950 px-2 py-1 rounded border border-navy-700/50 inline-block">
                      {alert.biometricVector}
                    </div>
                    <p className="text-xs text-gray-400 mt-1.5 line-clamp-2 leading-relaxed">{alert.description}</p>
                  </td>
                  <td className="py-4 px-4 text-xs font-mono">
                    <div className="text-gray-300 truncate max-w-[180px]" title={alert.deviceHash}>
                      💻 {alert.deviceHash}
                    </div>
                    <div className="text-gray-500 mt-1 flex items-center gap-1">
                      📍 {alert.location}
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <StatusBadge status={alert.status} />
                  </td>
                  <td className="py-4 px-4 text-right">
                    <button
                      onClick={() => router.push(`/console/investigate/${alert.id}`)}
                      className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-cyber-600 to-navy-700 hover:from-cyber-500 hover:to-cyber-600 text-white font-mono text-xs font-bold transition-all shadow-md shadow-cyber-950/50 flex items-center gap-1.5 ml-auto"
                    >
                      <span>Deep Forensic Triage</span>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                      </svg>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
