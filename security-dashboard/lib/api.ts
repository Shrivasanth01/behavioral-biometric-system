import type {
  KPI,
  FraudAlert,
  Session,
  UserDetails,
  BehavioralProfile,
  ModelInfo,
  UserModelHealth,
  AuditLog,
  DailyTrend,
  RiskDistribution,
  ExplainabilityResult,
  FeatureContribution,
  TypingProfile,
  MouseProfile,
  TouchProfile,
  DeviceRisk,
  TimeHeatmapData,
  RiskThreshold,
  NotificationSetting,
} from './types';
import { generateId, getRiskBand } from './utils';
import { subDays, subHours, format } from 'date-fns';

function randomBetween(min: number, max: number): number {
  return Math.round((Math.random() * (max - min) + min) * 10) / 10;
}

function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

const deviceTypes = ['Desktop', 'Mobile', 'Tablet', 'API'];
const locations = ['US-East', 'US-West', 'EU-West', 'EU-Central', 'APAC', 'LATAM'];
const severityLevels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'] as const;
const alertTypes = ['behavioral_anomaly', 'location_anomaly', 'device_anomaly', 'transaction_anomaly', 'velocity_anomaly'] as const;
const modelVersions = ['v3.2.1', 'v3.2.0', 'v3.1.5', 'v3.1.0'];

const sampleUserIds = Array.from({ length: 50 }, (_, i) => `USR-${String(i + 1).padStart(3, '0')}`);
const sampleNames = [
  'Alice Johnson', 'Bob Smith', 'Carol White', 'David Brown', 'Eva Martinez',
  'Frank Lee', 'Grace Kim', 'Henry Davis', 'Iris Wang', 'Jack Wilson',
  'Karen Taylor', 'Leo Anderson', 'Maria Garcia', 'Nathan Thomas', 'Olivia Moore',
  'Paul Jackson', 'Quinn Harris', 'Rachel Martin', 'Sam Thompson', 'Tina Robinson',
  'Uma Patel', 'Victor Clark', 'Wendy Lewis', 'Xander Young', 'Yara King',
  'Zane Wright', 'Amy Scott', 'Ben Green', 'Cathy Adams', 'Dan Baker',
  'Ella Nelson', 'Fred Hill', 'Gina Carter', 'Hank Mitchell', 'Ivy Roberts',
  'Jake Turner', 'Kara Phillips', 'Liam Campbell', 'Mia Parker', 'Noah Evans',
  'Olivia Edwards', 'Peter Collins', 'Quincy Stewart', 'Rita Morris', 'Steve Rogers',
  'Tracy Murphy', 'Ulysses Cook', 'Vera Bailey', 'Will Howard', 'Xena Ward',
];

function generateUserName(userId: string): string {
  const idx = parseInt(userId.split('-')[1]) - 1;
  return sampleNames[idx % sampleNames.length];
}

function generateEmail(userName: string): string {
  return `${userName.toLowerCase().replace(' ', '.')}@email.com`;
}

function generateTimestamps(count: number, hoursBack: number): string[] {
  const now = Date.now();
  return Array.from({ length: count }, (_, i) => {
    const offset = Math.random() * hoursBack * 3600000;
    return new Date(now - offset).toISOString();
  });
}

export async function fetchKPI(): Promise<KPI> {
  await new Promise((r) => setTimeout(r, 200));
  return {
    activeUsers: randomInt(1200, 3500),
    activeSessions: randomInt(800, 2500),
    transactionsToday: randomInt(15000, 45000),
    fraudAlerts: randomInt(5, 45),
    avgRiskScore: randomBetween(12, 45),
    blockedSessions: randomInt(2, 25),
  };
}

export async function fetchRiskDistribution(): Promise<RiskDistribution> {
  await new Promise((r) => setTimeout(r, 150));
  return {
    low: randomInt(500, 1500),
    medium: randomInt(100, 400),
    high: randomInt(20, 80),
    critical: randomInt(2, 20),
  };
}

export async function fetchDailyTrends(days = 7): Promise<DailyTrend[]> {
  await new Promise((r) => setTimeout(r, 200));
  return Array.from({ length: days }, (_, i) => {
    const date = subDays(new Date(), days - 1 - i);
    return {
      date: format(date, 'yyyy-MM-dd'),
      avgRisk: randomBetween(15, 55),
      alerts: randomInt(5, 40),
      transactions: randomInt(15000, 45000),
      blocked: randomInt(1, 20),
    };
  });
}

export async function fetchFraudAlerts(limit = 50): Promise<FraudAlert[]> {
  await new Promise((r) => setTimeout(r, 250));
  const timestamps = generateTimestamps(limit, 48);
  return Array.from({ length: limit }, (_, i) => {
    const userId = sampleUserIds[randomInt(0, sampleUserIds.length - 1)];
    const userName = generateUserName(userId);
    const riskScore = randomBetween(10, 95);
    const severity = riskScore >= 80 ? 'CRITICAL' : riskScore >= 60 ? 'HIGH' : riskScore >= 30 ? 'MEDIUM' : 'LOW';
    return {
      id: `ALT-${String(i + 1).padStart(4, '0')}`,
      userId,
      userName,
      userEmail: generateEmail(userName),
      type: alertTypes[randomInt(0, alertTypes.length - 1)],
      severity: severity as typeof severity,
      riskScore,
      timestamp: timestamps[i],
      status: (['OPEN', 'INVESTIGATING', 'RESOLVED', 'DISMISSED'] as const)[randomInt(0, 3)],
      assignedTo: Math.random() > 0.5 ? null : ['Sarah Chen', 'Marcus Jones', 'Elena Kovac'][randomInt(0, 2)],
      description: `Suspicious ${alertTypes[randomInt(0, alertTypes.length - 1)].replace('_', ' ')} detected for user ${userName}`,
      sessionId: `SES-${generateId().toUpperCase()}`,
      transactionId: Math.random() > 0.5 ? `TXN-${generateId().toUpperCase()}` : undefined,
      riskBreakdown: {
        overall: riskScore,
        ml: randomBetween(5, 95),
        rules: randomBetween(5, 95),
        heuristic: randomBetween(5, 95),
      },
      reasons: [
        `Typing speed deviation: ${randomBetween(1.5, 5.0).toFixed(1)}σ`,
        `Mouse movement anomaly score: ${randomBetween(60, 95).toFixed(0)}%`,
        `Location mismatch with recent sessions`,
      ],
      modelVersion: modelVersions[randomInt(0, modelVersions.length - 1)],
    };
  });
}

export async function fetchAlertById(id: string): Promise<FraudAlert | null> {
  await new Promise((r) => setTimeout(r, 150));
  const alerts = await fetchFraudAlerts(1);
  return { ...alerts[0], id };
}

export async function fetchSessionsForUser(userId: string): Promise<Session[]> {
  await new Promise((r) => setTimeout(r, 200));
  const count = randomInt(5, 20);
  return Array.from({ length: count }, (_, i) => {
    const riskScore = randomBetween(5, 95);
    return {
      id: `SES-${generateId().toUpperCase()}`,
      userId,
      startTime: subHours(new Date(), randomInt(1, 720)).toISOString(),
      endTime: Math.random() > 0.3 ? subHours(new Date(), randomInt(0, 10)).toISOString() : undefined,
      riskScore,
      riskBand: getRiskBand(riskScore),
      deviceType: deviceTypes[randomInt(0, deviceTypes.length - 1)],
      deviceFingerprint: `FP-${generateId().toUpperCase()}`,
      ipAddress: `${randomInt(1, 255)}.${randomInt(0, 255)}.${randomInt(0, 255)}.${randomInt(1, 255)}`,
      location: locations[randomInt(0, locations.length - 1)],
      actions: randomInt(10, 500),
      isActive: i === 0 && Math.random() > 0.5,
    };
  });
}

export async function fetchBehavioralProfile(userId: string): Promise<BehavioralProfile> {
  await new Promise((r) => setTimeout(r, 150));
  return {
    userId,
    typingSpeed: randomBetween(30, 90),
    typingSpeedVariance: randomBetween(5, 30),
    mouseSpeed: randomBetween(100, 600),
    mouseAcceleration: randomBetween(500, 3000),
    touchPressure: randomBetween(0.1, 1.0),
    swipeVelocity: randomBetween(200, 1200),
    gesturePatternCluster: randomInt(0, 5),
    features: {
      typing_speed: randomBetween(20, 100),
      mouse_speed: randomBetween(20, 100),
      touch_pressure: randomBetween(20, 100),
      swipe_velocity: randomBetween(20, 100),
      navigation_pattern: randomBetween(20, 100),
      session_duration: randomBetween(20, 100),
      error_rate: randomBetween(20, 100),
    },
  };
}

export async function fetchUserRiskHistory(userId: string): Promise<{ date: string; score: number }[]> {
  await new Promise((r) => setTimeout(r, 150));
  return Array.from({ length: 30 }, (_, i) => ({
    date: format(subDays(new Date(), 29 - i), 'yyyy-MM-dd'),
    score: randomBetween(5, 90),
  }));
}

export async function fetchUserAlerts(userId: string): Promise<FraudAlert[]> {
  await new Promise((r) => setTimeout(r, 100));
  const allAlerts = await fetchFraudAlerts(10);
  return allAlerts.map((a) => ({ ...a, userId }));
}

export async function fetchUserDeviceHistory(userId: string): Promise<{ fingerprint: string; deviceType: string; firstSeen: string; lastSeen: string; riskScore: number }[]> {
  await new Promise((r) => setTimeout(r, 100));
  return Array.from({ length: randomInt(2, 6) }, (_, i) => ({
    fingerprint: `FP-${generateId().toUpperCase()}`,
    deviceType: deviceTypes[randomInt(0, deviceTypes.length - 1)],
    firstSeen: subDays(new Date(), randomInt(30, 365)).toISOString(),
    lastSeen: subHours(new Date(), randomInt(1, 48)).toISOString(),
    riskScore: randomBetween(5, 80),
  }));
}

export async function fetchUserTransactions(userId: string): Promise<{ id: string; amount: number; timestamp: string; riskScore: number; status: string }[]> {
  await new Promise((r) => setTimeout(r, 100));
  return Array.from({ length: randomInt(5, 15) }, (_, i) => ({
    id: `TXN-${generateId().toUpperCase()}`,
    amount: randomBetween(10, 5000),
    timestamp: subHours(new Date(), randomInt(1, 168)).toISOString(),
    riskScore: randomBetween(5, 90),
    status: (['APPROVED', 'FLAGGED', 'BLOCKED', 'PENDING'] as const)[randomInt(0, 3)],
  }));
}

export async function fetchModelInfo(): Promise<ModelInfo> {
  await new Promise((r) => setTimeout(r, 200));
  return {
    modelVersion: modelVersions[0],
    lastTrained: subHours(new Date(), randomInt(1, 48)).toISOString(),
    driftStatus: (['STABLE', 'WARNING', 'DRIFTED'] as const)[randomInt(0, 2)],
    accuracy: randomBetween(92, 99),
    falsePositiveRate: randomBetween(0.5, 5.0),
    avgAnomalyScore: randomBetween(15, 45),
    featureDriftScores: {
      typing_speed: randomBetween(0.01, 0.5),
      mouse_movement: randomBetween(0.01, 0.5),
      touch_pressure: randomBetween(0.01, 0.5),
      swipe_velocity: randomBetween(0.01, 0.5),
      navigation_pattern: randomBetween(0.01, 0.5),
    },
  };
}

export async function fetchUserModelHealth(): Promise<UserModelHealth[]> {
  await new Promise((r) => setTimeout(r, 200));
  return sampleUserIds.slice(0, 30).map((userId) => ({
    userId,
    sessionCount: randomInt(10, 500),
    lastTrained: subDays(new Date(), randomInt(0, 14)).toISOString(),
    driftStatus: (['STABLE', 'WARNING', 'DRIFTED'] as const)[randomInt(0, 2)],
    modelVersion: modelVersions[randomInt(0, modelVersions.length - 1)],
    threshold: randomBetween(0.6, 0.95),
    avgRiskScore: randomBetween(10, 60),
  }));
}

export async function fetchExplainability(sessionId: string): Promise<ExplainabilityResult> {
  await new Promise((r) => setTimeout(r, 200));
  const riskScore = randomBetween(15, 95);
  const contributions: FeatureContribution[] = [
    { feature: 'Typing Speed', contribution: randomBetween(-30, 40), direction: Math.random() > 0.3 ? 'increases' : 'decreases' },
    { feature: 'Mouse Movement', contribution: randomBetween(-20, 35), direction: Math.random() > 0.3 ? 'increases' : 'decreases' },
    { feature: 'Touch Pressure', contribution: randomBetween(-15, 25), direction: Math.random() > 0.3 ? 'increases' : 'decreases' },
    { feature: 'Swipe Velocity', contribution: randomBetween(-10, 30), direction: Math.random() > 0.3 ? 'increases' : 'decreases' },
    { feature: 'Navigation Pattern', contribution: randomBetween(-25, 40), direction: Math.random() > 0.3 ? 'increases' : 'decreases' },
    { feature: 'Session Duration', contribution: randomBetween(-20, 20), direction: Math.random() > 0.3 ? 'increases' : 'decreases' },
    { feature: 'Error Rate', contribution: randomBetween(-10, 45), direction: Math.random() > 0.3 ? 'increases' : 'decreases' },
    { feature: 'Device Fingerprint', contribution: randomBetween(-5, 50), direction: Math.random() > 0.5 ? 'increases' : 'decreases' },
  ];
  return {
    sessionId,
    userId: sampleUserIds[randomInt(0, sampleUserIds.length - 1)],
    timestamp: new Date().toISOString(),
    riskScore: {
      overall: riskScore,
      ml: randomBetween(10, 95),
      rules: randomBetween(10, 95),
      heuristic: randomBetween(10, 95),
    },
    riskBand: getRiskBand(riskScore),
    contributions,
    reasons: [
      `Typing speed is ${randomBetween(2, 5).toFixed(1)} standard deviations from user baseline`,
      `Mouse movement pattern matches known fraud cluster #${randomInt(3, 12)}`,
      `Session location differs from 80% of recent sessions`,
      `Device fingerprint associated with ${randomInt(1, 5)} previous fraud alerts`,
    ],
    modelVersion: modelVersions[randomInt(0, modelVersions.length - 1)],
    modelConfidence: randomBetween(75, 99),
    baselineComparison: randomBetween(20, 80),
  };
}

export async function fetchTypingProfiles(): Promise<TypingProfile[]> {
  await new Promise((r) => setTimeout(r, 200));
  return Array.from({ length: 40 }, (_, i) => {
    const userId = sampleUserIds[i];
    return {
      userId,
      wpm: randomBetween(25, 95),
      isAnomalous: Math.random() < 0.12,
    };
  });
}

export async function fetchMouseProfiles(): Promise<MouseProfile[]> {
  await new Promise((r) => setTimeout(r, 200));
  return Array.from({ length: 40 }, (_, i) => {
    const userId = sampleUserIds[i];
    return {
      userId,
      speed: randomBetween(50, 600),
      acceleration: randomBetween(200, 3000),
      isAnomalous: Math.random() < 0.12,
    };
  });
}

export async function fetchTouchProfiles(): Promise<TouchProfile[]> {
  await new Promise((r) => setTimeout(r, 200));
  return Array.from({ length: 40 }, (_, i) => {
    const userId = sampleUserIds[i];
    return {
      userId,
      pressure: randomBetween(0.05, 0.95),
      swipeVelocity: randomBetween(100, 1200),
      gestureCluster: randomInt(0, 5),
      isAnomalous: Math.random() < 0.12,
    };
  });
}

export async function fetchDeviceRisks(): Promise<DeviceRisk[]> {
  await new Promise((r) => setTimeout(r, 150));
  return [
    { deviceType: 'Desktop', riskScore: randomBetween(10, 30), sessionCount: randomInt(500, 2000) },
    { deviceType: 'Mobile', riskScore: randomBetween(20, 50), sessionCount: randomInt(300, 1500) },
    { deviceType: 'Tablet', riskScore: randomBetween(15, 40), sessionCount: randomInt(50, 300) },
    { deviceType: 'API', riskScore: randomBetween(30, 70), sessionCount: randomInt(100, 500) },
  ];
}

export async function fetchTimeHeatmap(): Promise<TimeHeatmapData[]> {
  await new Promise((r) => setTimeout(r, 150));
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const data: TimeHeatmapData[] = [];
  for (const day of days) {
    for (let hour = 0; hour < 24; hour++) {
      data.push({
        hour,
        day,
        riskLevel: randomBetween(5, 90),
        sessionCount: randomInt(5, 200),
      });
    }
  }
  return data;
}

export async function fetchAuditLogs(): Promise<AuditLog[]> {
  await new Promise((r) => setTimeout(r, 200));
  const actions = ['user.login', 'user.logout', 'alert.updated', 'user.blocked', 'settings.changed', 'report.exported', 'model.retrained', 'threshold.updated'];
  return Array.from({ length: 100 }, (_, i) => ({
    id: `LOG-${String(i + 1).padStart(5, '0')}`,
    timestamp: subHours(new Date(), randomInt(0, 168)).toISOString(),
    action: actions[randomInt(0, actions.length - 1)],
    actorId: sampleUserIds[randomInt(0, 3)],
    actorName: ['Sarah Chen', 'Marcus Jones', 'Elena Kovac', 'System'][randomInt(0, 3)],
    resourceType: (['User', 'Alert', 'Session', 'Model', 'Setting'] as const)[randomInt(0, 4)],
    resourceId: generateId(),
    details: { ip: `192.168.${randomInt(0, 255)}.${randomInt(1, 254)}`, userAgent: 'Mozilla/5.0' },
    ipAddress: `192.168.${randomInt(0, 255)}.${randomInt(1, 254)}`,
  }));
}

export async function fetchRiskThresholds(): Promise<RiskThreshold[]> {
  return [
    { band: 'LOW', min: 0, max: 29 },
    { band: 'MEDIUM', min: 30, max: 59 },
    { band: 'HIGH', min: 60, max: 79 },
    { band: 'CRITICAL', min: 80, max: 100 },
  ];
}

export async function fetchUserDetails(userId: string): Promise<UserDetails | null> {
  await new Promise((r) => setTimeout(r, 100));
  const userName = generateUserName(userId);
  return {
    id: userId,
    email: generateEmail(userName),
    name: userName,
    role: 'user',
    mfaEnabled: Math.random() > 0.3,
    lastLogin: subHours(new Date(), randomInt(0, 72)).toISOString(),
    ipRestricted: Math.random() > 0.5,
    avatar: undefined,
    accountCreated: subDays(new Date(), randomInt(30, 730)).toISOString(),
    totalSessions: randomInt(20, 500),
    avgSessionRisk: randomBetween(10, 50),
    status: Math.random() > 0.1 ? 'ACTIVE' : 'BLOCKED',
    phone: `+1-${randomInt(200, 999)}-${randomInt(100, 999)}-${randomInt(1000, 9999)}`,
  };
}

export async function fetchNotificationSettings(): Promise<NotificationSetting[]> {
  return [
    { id: '1', channel: 'Email', enabled: true, events: ['CRITICAL_ALERT', 'HIGH_ALERT', 'MODEL_DRIFT'] },
    { id: '2', channel: 'Slack', enabled: true, webhookUrl: 'https://hooks.slack.com/services/xxx', events: ['CRITICAL_ALERT', 'HIGH_ALERT'] },
    { id: '3', channel: 'PagerDuty', enabled: false, webhookUrl: '', events: ['CRITICAL_ALERT'] },
    { id: '4', channel: 'SMS', enabled: true, events: ['CRITICAL_ALERT'] },
  ];
}
