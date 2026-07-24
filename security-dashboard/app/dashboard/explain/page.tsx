'use client';

import React, { useState } from 'react';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge, SeverityBadge } from '@/components/ui/Badge';
import { RiskGauge } from '@/components/dashboard/RiskGauge';
import { FeatureContributions } from '@/components/dashboard/FeatureContributions';
import { RiskBreakdown } from '@/components/dashboard/RiskBreakdown';
import { Progress } from '@/components/ui/Progress';
import { useToast } from '@/components/ui/Toast';
import { fetchExplainability } from '@/lib/api';
import type { ExplainabilityResult } from '@/lib/types';

export default function ExplainabilityPage() {
  const [sessionQuery, setSessionQuery] = useState('');
  const [result, setResult] = useState<ExplainabilityResult | null>(null);
  const [loading, setLoading] = useState(false);
  const { addToast } = useToast();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sessionQuery.trim()) return;
    setLoading(true);
    try {
      const data = await fetchExplainability(sessionQuery.trim());
      setResult(data);
    } catch {
      addToast('Failed to load explainability result', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Explainability Dashboard" description="Understand why a session was flagged as risky" />

      <Card>
        <CardContent>
          <form onSubmit={handleSearch} className="flex gap-3">
            <input
              type="text"
              value={sessionQuery}
              onChange={(e) => setSessionQuery(e.target.value)}
              placeholder="Enter Session ID or User ID..."
              className="cyber-input flex-1"
            />
            <Button type="submit" isLoading={loading}>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Analyze
            </Button>
          </form>
        </CardContent>
      </Card>

      {result && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <div className="lg:col-span-1 flex items-center justify-center">
              <div className="relative">
                <RiskGauge score={result.riskScore.overall} size={180} />
              </div>
            </div>
            <div className="lg:col-span-3">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg bg-navy-800/50 text-center">
                  <p className="text-xs text-gray-500 mb-1">Risk Band</p>
                  <SeverityBadge severity={result.riskBand} />
                </div>
                <div className="p-4 rounded-lg bg-navy-800/50 text-center">
                  <p className="text-xs text-gray-500 mb-1">ML Score</p>
                  <p className="text-lg font-mono" style={{ color: result.riskScore.ml >= 60 ? '#f97316' : '#06b6d4' }}>
                    {result.riskScore.ml.toFixed(1)}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-navy-800/50 text-center">
                  <p className="text-xs text-gray-500 mb-1">Model Confidence</p>
                  <p className="text-lg font-mono text-emerald-400">{result.modelConfidence.toFixed(0)}%</p>
                </div>
                <div className="p-4 rounded-lg bg-navy-800/50 text-center">
                  <p className="text-xs text-gray-500 mb-1">Model Version</p>
                  <p className="text-sm font-mono text-gray-300">{result.modelVersion}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RiskBreakdown riskScore={result.riskScore} />
            <FeatureContributions contributions={result.contributions} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardTitle>Human-Readable Reasons</CardTitle>
              <CardContent>
                <ul className="space-y-3">
                  {result.reasons.map((reason, i) => (
                    <li key={i} className="flex items-start gap-3 p-3 rounded-lg bg-navy-800/50">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${
                        i < 2 ? 'bg-red-500/10 text-red-400' : 'bg-amber-500/10 text-amber-400'
                      }`}>
                        <span className="text-xs font-mono">{i + 1}</span>
                      </div>
                      <p className="text-sm text-gray-300">{reason}</p>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardTitle>Comparison to Baseline</CardTitle>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-400">This Session</span>
                      <span className="font-mono font-semibold" style={{ color: result.riskScore.overall >= 60 ? '#f97316' : '#06b6d4' }}>
                        {result.riskScore.overall.toFixed(1)}
                      </span>
                    </div>
                    <Progress value={result.riskScore.overall} variant="risk" size="lg" />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-400">User Baseline</span>
                      <span className="font-mono text-gray-300">{result.baselineComparison.toFixed(1)}</span>
                    </div>
                    <Progress value={result.baselineComparison} variant="default" size="lg" />
                  </div>
                  <div className="pt-2 border-t border-navy-700/50">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Deviation</span>
                      <span className={`font-mono font-bold ${
                        result.riskScore.overall - result.baselineComparison > 20 ? 'text-red-400' : 'text-emerald-400'
                      }`}>
                        {(result.riskScore.overall - result.baselineComparison).toFixed(1)} pts
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardTitle>Session Information</CardTitle>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-3 rounded-lg bg-navy-800/50">
                  <p className="text-xs text-gray-500">Session ID</p>
                  <p className="text-sm font-mono text-gray-200">{result.sessionId}</p>
                </div>
                <div className="p-3 rounded-lg bg-navy-800/50">
                  <p className="text-xs text-gray-500">User ID</p>
                  <p className="text-sm font-mono text-gray-200">{result.userId}</p>
                </div>
                <div className="p-3 rounded-lg bg-navy-800/50">
                  <p className="text-xs text-gray-500">Timestamp</p>
                  <p className="text-sm text-gray-200">{new Date(result.timestamp).toLocaleString()}</p>
                </div>
                <div className="p-3 rounded-lg bg-navy-800/50">
                  <p className="text-xs text-gray-500">Device</p>
                  <p className="text-sm text-gray-200">Desktop / Windows</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
