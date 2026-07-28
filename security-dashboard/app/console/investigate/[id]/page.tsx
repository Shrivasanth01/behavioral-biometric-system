'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { SeverityBadge, StatusBadge } from '@/components/ui/Badge';
import { RadarChart } from '@/components/dashboard/RadarChart';
import { LineChart } from '@/components/dashboard/LineChart';
import { useToast } from '@/components/ui/Toast';

interface BiometricFeatureSHAP {
  featureName: string;
  measuredValue: string;
  userBaseline: string;
  shapContribution: number;
  anomalyDegree: string;
}

export default function SecOpsInvestigateIdPage() {
  const params = useParams();
  const router = useRouter();
  const { addToast } = useToast();
  const alertId = (params.id as string) || 'SEC-ALT-884';

  const [isLocked, setIsLocked] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'BIOMETRIC_DEEP_DIVE' | 'DEVICE_INTELLIGENCE' | 'AUDIT_TRAIL'>('BIOMETRIC_DEEP_DIVE');
  const [selectedAction, setSelectedAction] = useState<string | null>(null);

  const mockTargetUser = {
    userId: 'USR-77102',
    name: 'Jonathan Sterling',
    email: 'j.sterling@enterprise-holdings.ch',
    riskTier: 'CRITICAL THREAT (98.4%)',
    accountBalance: '€485,290.00',
    trustedDevice: 'iPhone 15 Pro Max (Secure Enclave Verified)',
    currentAttackDevice: 'MacBook Pro / Chrome (Spoofed Audio Canvas Hash)',
    sessionTimestamp: new Date().toUTCString(),
  };

  const shapFeatures: BiometricFeatureSHAP[] = [
    {
      featureName: 'Keystroke Flight Time (Key-to-Key Transitions)',
      measuredValue: '38ms (Zero variance)',
      userBaseline: '124ms (±28ms)',
      shapContribution: 38.5,
      anomalyDegree: '+4.2σ (Automated Script / Bot Engine)',
    },
    {
      featureName: 'Mouse Trajectory Polynomial Curvature',
      measuredValue: '1.000 (Euclidean straight linear paths)',
      userBaseline: '0.742 (Natural human hand micro-tremors)',
      shapContribution: 29.8,
      anomalyDegree: '+3.8σ (Synthetic Mouse Injection)',
    },
    {
      featureName: 'Touch & Click Dwell Time Duration',
      measuredValue: '45.0ms exactly on every DOM target',
      userBaseline: '92.4ms (±18.5ms)',
      shapContribution: 18.2,
      anomalyDegree: '+3.1σ (Programmatic Event Dispatch)',
    },
    {
      featureName: 'UI Navigation & Form Field Acceleration',
      measuredValue: '4 fields completed in 320ms',
      userBaseline: 'Average 4.2s per form phase',
      shapContribution: 11.9,
      anomalyDegree: '+2.9σ (Autofill Attack Pattern)',
    },
  ];

  const radarData = [
    { feature: 'Flight Timings', user: 98, population: 42 },
    { feature: 'Dwell Duration', user: 95, population: 48 },
    { feature: 'Spline Curvature', user: 99, population: 55 },
    { feature: 'Swipe Acceleration', user: 88, population: 50 },
    { feature: 'Touch Contact Area', user: 92, population: 45 },
    { feature: 'Sensor Stability', user: 90, population: 52 },
  ];

  const riskHistoryData = [
    { name: '10:00', score: 12 },
    { name: '10:05', score: 14 },
    { name: '10:10', score: 15 },
    { name: '10:15 (Login)', score: 18 },
    { name: '10:17 (Nav)', score: 45 },
    { name: '10:18 (Wire Setup)', score: 88 },
    { name: '10:19 (Trigger)', score: 98.4 },
  ];

  const handleDefensiveAction = (action: string, variant: 'error' | 'success' | 'warning' = 'success') => {
    setSelectedAction(action);
    if (action.includes('Freeze') || action.includes('Kill')) {
      setIsLocked(true);
      addToast(`🚨 SECURE CONTAINMENT EXECUTED: Account ${mockTargetUser.userId} has been frozen & JWTs revoked!`, 'error');
    } else {
      addToast(`🛡️ COMMAND DISPATCHED: ${action} applied to Target ${mockTargetUser.userId}`, variant);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in font-sans">
      {/* Navigation Breadcrumbs */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => router.push('/console/alerts')}
          className="flex items-center gap-2 text-sm text-cyber-400 hover:text-cyber-300 font-mono font-bold transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span>BACK TO REAL-TIME SECOPS TRIAGE</span>
        </button>
        <div className="flex items-center gap-2 font-mono text-xs text-gray-500">
          <span>INVESTIGATION CASE:</span>
          <span className="text-gray-200 font-bold px-2 py-0.5 bg-navy-800 rounded border border-navy-700">{alertId}</span>
        </div>
      </div>

      <PageHeader
        title={`Forensic Biometric Investigation: ${alertId}`}
        description="Deep anomaly decomposition, explainable AI SHAP attribution, and active containment controls"
        actions={
          <div className="flex items-center gap-3">
            {isLocked ? (
              <div className="px-4 py-2 rounded-lg bg-red-600 font-mono text-xs font-bold text-white uppercase animate-bounce shadow-lg shadow-red-500/50 flex items-center gap-2">
                <span>🔒 TARGET ACCOUNT CONTAINED & LOCKED</span>
              </div>
            ) : (
              <Button
                variant="danger"
                size="sm"
                onClick={() => handleDefensiveAction('Instant Force Freeze & Session Kill', 'error')}
              >
                🚨 Instant Contain & Freeze
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleDefensiveAction('Push Step-Up Challenge (Biometric Face Auth)', 'warning')}
            >
              📲 Enforce Step-Up Challenge
            </Button>
          </div>
        }
      />

      {/* Target Subject Identity Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 border-red-500/40 bg-gradient-to-br from-navy-900 via-navy-900 to-red-950/20 shadow-2xl">
          <CardTitle className="border-b border-navy-800 pb-3 flex items-center justify-between">
            <span className="text-gray-200 font-mono flex items-center gap-2">
              <span className="text-red-400">👤</span> SUBJECT TARGET PROFILE & THREAT ATTRITION
            </span>
            <SeverityBadge severity="CRITICAL" />
          </CardTitle>
          <CardContent className="space-y-4 pt-4 text-sm font-mono">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-3 bg-navy-950 rounded-lg border border-navy-800">
                <div className="text-[11px] text-gray-400">CUSTOMER ID</div>
                <div className="text-base font-bold text-cyber-400 mt-0.5">{mockTargetUser.userId}</div>
              </div>
              <div className="p-3 bg-navy-950 rounded-lg border border-navy-800">
                <div className="text-[11px] text-gray-400">SUBJECT NAME</div>
                <div className="text-sm font-bold text-gray-100 mt-0.5">{mockTargetUser.name}</div>
              </div>
              <div className="p-3 bg-navy-950 rounded-lg border border-navy-800">
                <div className="text-[11px] text-gray-400">ACCOUNT VALUE</div>
                <div className="text-base font-bold text-green-400 mt-0.5">{mockTargetUser.accountBalance}</div>
              </div>
              <div className="p-3 bg-navy-950 rounded-lg border border-red-500/30 bg-red-950/20">
                <div className="text-[11px] text-red-400">AI RISK CONFIDENCE</div>
                <div className="text-base font-bold text-red-400 mt-0.5">98.4% ANOMALY</div>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-navy-950/90 border border-navy-800 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">TRUSTED BIOMETRIC IDENTITY DEVICE:</span>
                <span className="text-green-400 font-bold">✅ {mockTargetUser.trustedDevice}</span>
              </div>
              <div className="flex items-center justify-between text-xs border-t border-navy-800 pt-2">
                <span className="text-red-400 font-bold animate-pulse">⚠️ ACTIVE ATTACK TELEMETRY ORIGIN:</span>
                <span className="text-red-300 font-bold">🔴 {mockTargetUser.currentAttackDevice}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Defense Center */}
        <Card className="border-cyber-500/30 bg-navy-900 shadow-xl flex flex-col justify-between">
          <div>
            <CardTitle className="border-b border-navy-800 pb-3 text-cyber-400 font-mono text-sm">
              🛡️ ACTIVE DEFENSE COUNTERMEASURES
            </CardTitle>
            <CardContent className="pt-4 space-y-3 font-sans">
              <p className="text-xs text-gray-400 font-mono leading-relaxed">
                Select defensive containment protocols. Actions execute instantaneously across banking API API gateways via Redis Pub/Sub events.
              </p>
              <div className="space-y-2.5">
                <button
                  onClick={() => handleDefensiveAction('Instant Account Freeze & JWT Token Revocation', 'error')}
                  className="w-full py-2.5 px-4 rounded-lg bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white border border-red-500/40 text-left text-xs font-mono font-bold transition-all flex items-center justify-between shadow-lg"
                >
                  <span>1. FORCE KILL & FREEZE ACCOUNT</span>
                  <span>⚡ INSTANT</span>
                </button>
                <button
                  onClick={() => handleDefensiveAction('Step-Up Challenge: Live Selfie Liveness Auth', 'warning')}
                  className="w-full py-2.5 px-4 rounded-lg bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 border border-yellow-500/40 text-left text-xs font-mono font-bold transition-all flex items-center justify-between"
                >
                  <span>2. ENFORCE STEP-UP MFA LIVENESS</span>
                  <span>📲 CHALLENGE</span>
                </button>
                <button
                  onClick={() => handleDefensiveAction('Mark as False Positive & Retrain Profile', 'success')}
                  className="w-full py-2.5 px-4 rounded-lg bg-green-600/20 hover:bg-green-600/30 text-green-400 border border-green-500/40 text-left text-xs font-mono font-bold transition-all flex items-center justify-between"
                >
                  <span>3. VERIFY VARIANCE & RETRAIN ML</span>
                  <span>✓ SAFEGUARD</span>
                </button>
              </div>
            </CardContent>
          </div>
          {selectedAction && (
            <div className="mx-6 mb-6 p-3 bg-navy-950 rounded border border-cyber-500/40 text-[11px] font-mono text-gray-300">
              <span className="text-cyber-400 font-bold">LAST EXECUTED COMMAND:</span> {selectedAction}
            </div>
          )}
        </Card>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-navy-800 font-mono text-xs">
        {[
          { id: 'BIOMETRIC_DEEP_DIVE', label: '🧬 Explainable AI: Biometric SHAP Attribution' },
          { id: 'DEVICE_INTELLIGENCE', label: '💻 Device Telemetry & Spline Analytics' },
          { id: 'AUDIT_TRAIL', label: '📜 Live Session Timeline Event Log' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`py-3 px-6 font-bold border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-cyber-500 text-cyber-400 bg-cyber-500/10'
                : 'border-transparent text-gray-400 hover:text-gray-200 hover:bg-navy-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Biometric Deep Dive (SHAP Values & Charts) */}
      {activeTab === 'BIOMETRIC_DEEP_DIVE' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">
          <Card className="lg:col-span-2 border-navy-700/80">
            <CardTitle className="text-sm font-mono text-gray-200 border-b border-navy-800 pb-3">
              🎯 SHAP Feature Attribution (Why ML Model Flagged This Session)
            </CardTitle>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-left font-mono text-xs">
                  <thead>
                    <tr className="bg-navy-950 text-gray-400 uppercase border-b border-navy-800">
                      <th className="py-3 px-4">Behavioral Biometric Feature</th>
                      <th className="py-3 px-4">Live Measured Vector</th>
                      <th className="py-3 px-4">Subject Learned Baseline</th>
                      <th className="py-3 px-4">SHAP Impact (%)</th>
                      <th className="py-3 px-4 text-right">Statistical Deviation</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-navy-800/60">
                    {shapFeatures.map((f, i) => (
                      <tr key={i} className="hover:bg-navy-800/40 transition-colors">
                        <td className="py-3.5 px-4 font-bold text-gray-200">{f.featureName}</td>
                        <td className="py-3.5 px-4 text-red-400 font-bold">{f.measuredValue}</td>
                        <td className="py-3.5 px-4 text-green-400">{f.userBaseline}</td>
                        <td className="py-3.5 px-4">
                          <div className="flex items-center gap-2">
                            <div className="w-24 bg-navy-800 rounded-full h-2 overflow-hidden">
                              <div className="bg-red-500 h-full rounded-full" style={{ width: `${f.shapContribution * 2}%` }} />
                            </div>
                            <span className="font-bold text-gray-200">{f.shapContribution}%</span>
                          </div>
                        </td>
                        <td className="py-3.5 px-4 text-right font-bold text-red-400">{f.anomalyDegree}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <Card className="border-navy-700/80 bg-navy-900/90">
              <CardTitle className="text-xs font-mono text-cyber-400 border-b border-navy-800 pb-2">
                📡 BIOMETRIC PROFILE DEVIATION RADAR
              </CardTitle>
              <CardContent className="p-2 h-72 flex items-center justify-center">
                <RadarChart data={radarData} title="Biometric Feature Drift vs Baseline" height={260} />
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Tab 2: Device Intelligence & Telemetry */}
      {activeTab === 'DEVICE_INTELLIGENCE' && (
        <Card className="border-navy-700/80 animate-fade-in">
          <CardTitle className="text-sm font-mono border-b border-navy-800 pb-3 text-cyber-400">
            💻 Hardware Fingerprinting & Mouse Trajectory B-Spline Diagnostics
          </CardTitle>
          <CardContent className="p-6 space-y-6 font-mono text-xs">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-4 rounded-xl bg-navy-950 border border-navy-800 space-y-3">
                <div className="text-sm font-bold text-gray-200 pb-2 border-b border-navy-800 flex items-center justify-between">
                  <span>🖥️ BROWSER & HARDWARE ATTLL/TELEMETRY</span>
                  <span className="text-red-400 text-[10px]">SPOOFING DETECTED</span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between"><span className="text-gray-400">User Agent:</span> <span className="text-gray-200">Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/122.0.0.0</span></div>
                  <div className="flex justify-between"><span className="text-gray-400">AudioContext Canvas Hash:</span> <span className="text-red-400 font-bold">88f2a1b9c4 (Known Proxy Headless Node)</span></div>
                  <div className="flex justify-between"><span className="text-gray-400">WebGL Vendor / Renderer:</span> <span className="text-yellow-400">Google Inc. / Apple GPU (Simulated)</span></div>
                  <div className="flex justify-between"><span className="text-gray-400">WebRTC Local / Public IP:</span> <span className="text-red-400">10.0.0.2 / 185.220.101.4 (TOR / Proxy Exit)</span></div>
                  <div className="flex justify-between"><span className="text-gray-400">Screen Resolution & Color Depth:</span> <span className="text-gray-200">2560x1600 / 24-bit</span></div>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-navy-950 border border-navy-800 space-y-3">
                <div className="text-sm font-bold text-gray-200 pb-2 border-b border-navy-800">
                  <span>🖱️ MOUSE CURVATURE SPLINE VERIFICATION</span>
                </div>
                <p className="text-gray-400 leading-relaxed">
                  Human mouse mechanics exhibit parabolic curvature with micro-tremor deceleration on click approach.
                  In this session, trajectory vector coefficient is <strong className="text-red-400">1.000 (Euclidean linear path)</strong>, confirming automated programmatic JavaScript event injection (Puppeteer / Playwright attack script).
                </p>
                <div className="p-3 bg-navy-900 rounded border border-red-500/30 flex items-center justify-between text-red-400 font-bold">
                  <span>🚨 AUTOMATED BOT CONFIDENCE:</span>
                  <span>99.8% CERTAINTY</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab 3: Audit Trail & Session Timeline */}
      {activeTab === 'AUDIT_TRAIL' && (
        <Card className="border-navy-700/80 animate-fade-in">
          <CardTitle className="text-sm font-mono border-b border-navy-800 pb-3 text-cyber-400">
            📜 Real-Time Biometric Session Event Logs & Escalation Timeline
          </CardTitle>
          <CardContent className="p-6">
            <div className="space-y-6 font-mono text-xs">
              {[
                { time: '10:19:42 UTC', type: '🚨 CRITICAL AI THREAT TRIGGER', detail: 'Keystroke Flight Time Variance hit +4.2σ during IBAN wire transfer validation.', status: 'CRITICAL', color: 'text-red-400 bg-red-950/40 border-red-500/40' },
                { time: '10:19:35 UTC', type: '⚠️ HIGH RISK ACTION INIT', detail: 'POST /api/banking/wire-transfer requested amount €125,000 to offshore IBAN.', status: 'FLAGGED', color: 'text-yellow-400 bg-yellow-950/40 border-yellow-500/40' },
                { time: '10:18:10 UTC', type: '👁️ BEHAVIORAL DRIFT DETECTED', detail: 'Mouse motion switched from human parabolic curve to straight line Euclidean injection.', status: 'ANOMALY', color: 'text-purple-400 bg-purple-950/40 border-purple-500/40' },
                { time: '10:15:02 UTC', type: '🔐 SESSION INITIALIZED', detail: 'Valid login via OAuth/JWT token exchange. Biometric telemetry stream initialized.', status: 'OK', color: 'text-green-400 bg-green-950/40 border-green-500/40' },
              ].map((ev, i) => (
                <div key={i} className="flex gap-4 items-start border-l-2 border-navy-700 pl-4 relative">
                  <div className="w-2.5 h-2.5 rounded-full bg-cyber-500 absolute -left-[7px] top-1.5" />
                  <div className="w-32 text-gray-400 font-bold">{ev.time}</div>
                  <div className={`flex-1 p-3.5 rounded-lg border ${ev.color}`}>
                    <div className="font-bold mb-1 flex items-center justify-between">
                      <span>{ev.type}</span>
                      <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-navy-950 border border-navy-800">{ev.status}</span>
                    </div>
                    <div className="text-gray-300 text-xs font-sans">{ev.detail}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Real-Time Risk Trend Over Session Progression */}
      <Card className="border-navy-700/80">
        <CardTitle className="text-sm font-mono text-gray-200 border-b border-navy-800 pb-3">
          📈 Session Risk Score Progression Over Time
        </CardTitle>
        <CardContent className="p-4 h-64">
          <LineChart data={riskHistoryData} lines={[{ dataKey: 'score', color: '#ef4444', name: 'AI Risk Anomaly Score' }]} xKey="name" />
        </CardContent>
      </Card>
    </div>
  );
}
