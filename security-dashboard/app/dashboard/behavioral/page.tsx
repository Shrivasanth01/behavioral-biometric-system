'use client';

import React, { useState, useEffect } from 'react';
import { PageHeader } from '@/components/layout/PageHeader';
import { Tabs } from '@/components/ui/Tabs';
import { Card, CardTitle, CardContent } from '@/components/ui/Card';
import { BarChart } from '@/components/dashboard/BarChart';
import { LineChart } from '@/components/dashboard/LineChart';
import { CardSkeleton, ChartSkeleton } from '@/components/ui/Skeleton';
import { SeverityBadge } from '@/components/ui/Badge';
import { fetchTypingProfiles, fetchMouseProfiles, fetchTouchProfiles } from '@/lib/api';
import type { TypingProfile, MouseProfile, TouchProfile } from '@/lib/types';

export default function BehavioralAnalyticsPage() {
  const [activeTab, setActiveTab] = useState('typing');
  const [typingData, setTypingData] = useState<TypingProfile[]>([]);
  const [mouseData, setMouseData] = useState<MouseProfile[]>([]);
  const [touchData, setTouchData] = useState<TouchProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchTypingProfiles(),
      fetchMouseProfiles(),
      fetchTouchProfiles(),
    ]).then(([typing, mouse, touch]) => {
      setTypingData(typing);
      setMouseData(mouse);
      setTouchData(touch);
    }).finally(() => setLoading(false));
  }, []);

  const tabs = [
    { id: 'typing', label: 'Typing Profiles', count: typingData.length },
    { id: 'mouse', label: 'Mouse Profiles', count: mouseData.length },
    { id: 'touch', label: 'Mobile Touch Profiles', count: touchData.length },
  ];

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-64 bg-navy-700/50 rounded animate-pulse" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
      </div>
    );
  }

  const typingHistogram = () => {
    const bins = Array.from({ length: 8 }, (_, i) => ({
      range: `${20 + i * 10}-${29 + i * 10}`,
      normal: 0,
      anomalous: 0,
    }));
    typingData.forEach((p) => {
      const binIdx = Math.min(Math.floor((p.wpm - 20) / 10), 7);
      if (binIdx >= 0 && binIdx < bins.length) {
        if (p.isAnomalous) bins[binIdx].anomalous++;
        else bins[binIdx].normal++;
      }
    });
    return bins.map((b) => ({
      name: b.range,
      Normal: b.normal,
      Anomalous: b.anomalous,
    }));
  };

  const mouseScatterData = () => {
    return mouseData.map((m) => ({
      name: m.userId.slice(-4),
      speed: m.speed,
      acceleration: m.acceleration,
      isAnomalous: m.isAnomalous,
    }));
  };

  const touchPressureData = () => {
    const bins = Array.from({ length: 10 }, (_, i) => ({
      range: `${(i * 0.1).toFixed(1)}-${((i + 1) * 0.1).toFixed(1)}`,
      count: 0,
      anomalous: 0,
    }));
    touchData.forEach((t) => {
      const idx = Math.min(Math.floor(t.pressure / 0.1), 9);
      if (t.isAnomalous) bins[idx].anomalous++;
      else bins[idx].count++;
    });
    return bins.map((b) => ({ name: b.range, Normal: b.count, Anomalous: b.anomalous }));
  };

  const swipeVelocityData = () => {
    const bins = Array.from({ length: 8 }, (_, i) => ({
      range: `${i * 150}-${(i + 1) * 150 - 1}`,
      count: 0,
      anomalous: 0,
    }));
    touchData.forEach((t) => {
      const idx = Math.min(Math.floor(t.swipeVelocity / 150), 7);
      if (t.isAnomalous) bins[idx].anomalous++;
      else bins[idx].count++;
    });
    return bins.map((b) => ({ name: b.range, Normal: b.count, Anomalous: b.anomalous }));
  };

  const clusterData = () => {
    const clusters: Record<number, { total: number; anomalous: number }> = {};
    touchData.forEach((t) => {
      if (!clusters[t.gestureCluster]) clusters[t.gestureCluster] = { total: 0, anomalous: 0 };
      clusters[t.gestureCluster].total++;
      if (t.isAnomalous) clusters[t.gestureCluster].anomalous++;
    });
    return Object.entries(clusters).map(([cluster, data]) => ({
      name: `Cluster ${parseInt(cluster) + 1}`,
      Total: data.total,
      Anomalous: data.anomalous,
    }));
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Behavioral Analytics" description="User behavior profile distributions and anomaly detection" />

      <Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === 'typing' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <BarChart
              data={typingHistogram()}
              title="Typing Speed Distribution (WPM)"
              height={320}
              bars={[
                { dataKey: 'Normal', color: '#06b6d4', name: 'Normal' },
                { dataKey: 'Anomalous', color: '#ef4444', name: 'Anomalous' },
              ]}
            />
            <Card>
              <CardTitle>Anomalous Typing Patterns</CardTitle>
              <CardContent>
                <div className="space-y-2">
                  {typingData.filter((p) => p.isAnomalous).slice(0, 10).map((p) => (
                    <div
                      key={p.userId}
                      className="flex items-center justify-between p-2 rounded-lg bg-navy-800/50 cursor-pointer hover:bg-navy-800"
                      onClick={() => setSelectedUser(p.userId)}
                    >
                      <div>
                        <span className="text-sm text-gray-200 font-mono">{p.userId}</span>
                        <span className="text-xs text-gray-500 ml-2">{p.wpm.toFixed(0)} WPM</span>
                      </div>
                      <SeverityBadge severity="HIGH" />
                    </div>
                  ))}
                  {typingData.filter((p) => p.isAnomalous).length === 0 && (
                    <p className="text-sm text-gray-500">No anomalous patterns detected</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
          {selectedUser && (
            <Card>
              <CardTitle>User Drill-Down: {selectedUser}</CardTitle>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  {(() => {
                    const user = typingData.find((p) => p.userId === selectedUser);
                    if (!user) return null;
                    const avg = typingData.reduce((s, p) => s + p.wpm, 0) / typingData.length;
                    return (
                      <>
                        <div className="p-3 rounded-lg bg-navy-800/50">
                          <p className="text-xs text-gray-500">Typing Speed</p>
                          <p className="text-lg font-mono text-gray-200">{user.wpm.toFixed(0)} WPM</p>
                        </div>
                        <div className="p-3 rounded-lg bg-navy-800/50">
                          <p className="text-xs text-gray-500">Population Avg</p>
                          <p className="text-lg font-mono text-gray-200">{avg.toFixed(0)} WPM</p>
                        </div>
                        <div className="p-3 rounded-lg bg-navy-800/50">
                          <p className="text-xs text-gray-500">Deviation</p>
                          <p className="text-lg font-mono text-alert-high">
                            {((user.wpm - avg) / avg * 100).toFixed(1)}%
                          </p>
                        </div>
                      </>
                    );
                  })()}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {activeTab === 'mouse' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <BarChart
              data={(() => {
                const bins = Array.from({ length: 8 }, (_, i) => ({
                  name: `${i * 75}-${(i + 1) * 75 - 1}`,
                  Normal: 0,
                  Anomalous: 0,
                }));
                mouseData.forEach((m) => {
                  const idx = Math.min(Math.floor(m.speed / 75), 7);
                  if (m.isAnomalous) bins[idx].Anomalous++;
                  else bins[idx].Normal++;
                });
                return bins;
              })()}
              title="Mouse Speed Distribution"
              height={320}
              bars={[
                { dataKey: 'Normal', color: '#06b6d4', name: 'Normal' },
                { dataKey: 'Anomalous', color: '#ef4444', name: 'Anomalous' },
              ]}
            />
            <Card>
              <CardTitle>Anomalous Mouse Movements</CardTitle>
              <CardContent>
                <div className="space-y-2">
                  {mouseData.filter((m) => m.isAnomalous).slice(0, 10).map((m) => (
                    <div key={m.userId} className="flex items-center justify-between p-2 rounded-lg bg-navy-800/50">
                      <div>
                        <span className="text-sm text-gray-200 font-mono">{m.userId}</span>
                        <span className="text-xs text-gray-500 ml-2">{m.speed.toFixed(0)} px/s</span>
                      </div>
                      <SeverityBadge severity="HIGH" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
          <Card>
            <CardTitle>Mouse Speed vs Acceleration (All Users)</CardTitle>
            <CardContent>
              <div className="grid grid-cols-[repeat(auto-fill,minmax(8px,1fr))] gap-px h-64 items-end">
                {mouseScatterData().map((m, i) => (
                  <div
                    key={i}
                    className={`rounded-t ${m.isAnomalous ? 'bg-red-500' : 'bg-cyber-500'}`}
                    style={{ height: `${(m.speed / 600) * 100}%`, opacity: 0.6 }}
                    title={`${m.name}: ${m.speed.toFixed(0)} px/s`}
                  />
                ))}
              </div>
              <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-cyber-500" /> Normal</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-red-500" /> Anomalous</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'touch' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <BarChart
              data={touchPressureData()}
              title="Touch Pressure Distribution"
              height={320}
              bars={[
                { dataKey: 'Normal', color: '#06b6d4', name: 'Normal' },
                { dataKey: 'Anomalous', color: '#ef4444', name: 'Anomalous' },
              ]}
            />
            <BarChart
              data={swipeVelocityData()}
              title="Swipe Velocity Distribution"
              height={320}
              bars={[
                { dataKey: 'Normal', color: '#06b6d4', name: 'Normal' },
                { dataKey: 'Anomalous', color: '#ef4444', name: 'Anomalous' },
              ]}
            />
          </div>
          <BarChart
            data={clusterData()}
            title="Gesture Pattern Clusters"
            height={300}
            bars={[
              { dataKey: 'Total', color: '#06b6d4', name: 'Total Users' },
              { dataKey: 'Anomalous', color: '#ef4444', name: 'Anomalous' },
            ]}
          />
        </div>
      )}
    </div>
  );
}
