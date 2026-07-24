export interface User {
  id: string;
  email: string;
  name: string;
  role: 'analyst' | 'admin';
  avatar?: string;
  lastLogin: string;
  mfaEnabled: boolean;
  ipRestricted: boolean;
}

export interface RiskScore {
  overall: number;
  ml: number;
  rules: number;
  heuristic: number;
}

export interface FeatureContribution {
  feature: string;
  contribution: number;
  direction: 'increases' | 'decreases';
}

export interface ExplainabilityResult {
  sessionId: string;
  userId: string;
  timestamp: string;
  riskScore: RiskScore;
  riskBand: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  contributions: FeatureContribution[];
  reasons: string[];
  modelVersion: string;
  modelConfidence: number;
  baselineComparison: number;
}

export interface FraudAlert {
  id: string;
  userId: string;
  userName: string;
  userEmail: string;
  type: 'behavioral_anomaly' | 'location_anomaly' | 'device_anomaly' | 'transaction_anomaly' | 'velocity_anomaly';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  riskScore: number;
  timestamp: string;
  status: 'OPEN' | 'INVESTIGATING' | 'RESOLVED' | 'DISMISSED';
  assignedTo: string | null;
  description: string;
  sessionId: string;
  transactionId?: string;
  riskBreakdown: RiskScore;
  reasons: string[];
  modelVersion: string;
}

export interface Session {
  id: string;
  userId: string;
  startTime: string;
  endTime?: string;
  riskScore: number;
  riskBand: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  deviceType: string;
  deviceFingerprint: string;
  ipAddress: string;
  location: string;
  actions: number;
  isActive: boolean;
}

export interface UserBehavioralProfile {
  userId: string;
  typingSpeed: number;
  typingSpeedVariance: number;
  mouseSpeed: number;
  mouseAcceleration: number;
  touchPressure: number;
  swipeVelocity: number;
  gesturePatternCluster: number;
  features: Record<string, number>;
}

export interface ModelInfo {
  modelVersion: string;
  lastTrained: string;
  driftStatus: 'STABLE' | 'WARNING' | 'DRIFTED';
  accuracy: number;
  falsePositiveRate: number;
  avgAnomalyScore: number;
  featureDriftScores: Record<string, number>;
}

export interface UserModelHealth {
  userId: string;
  sessionCount: number;
  lastTrained: string;
  driftStatus: 'STABLE' | 'WARNING' | 'DRIFTED';
  modelVersion: string;
  threshold: number;
  avgRiskScore: number;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  action: string;
  actorId: string;
  actorName: string;
  resourceType: string;
  resourceId: string;
  details: Record<string, unknown>;
  ipAddress: string;
}

export interface KPI {
  activeUsers: number;
  activeSessions: number;
  transactionsToday: number;
  fraudAlerts: number;
  avgRiskScore: number;
  blockedSessions: number;
}

export type BehavioralProfile = UserBehavioralProfile;

export interface UserDetails {
  id: string;
  email: string;
  name: string;
  role: string;
  avatar?: string;
  lastLogin: string;
  mfaEnabled: boolean;
  ipRestricted: boolean;
  accountCreated: string;
  totalSessions: number;
  avgSessionRisk: number;
  status: string;
  phone: string;
}

export interface DailyTrend {
  date: string;
  avgRisk: number;
  alerts: number;
  transactions: number;
  blocked: number;
}

export interface RiskDistribution {
  low: number;
  medium: number;
  high: number;
  critical: number;
}

export interface TypingProfile {
  userId: string;
  wpm: number;
  isAnomalous: boolean;
}

export interface MouseProfile {
  userId: string;
  speed: number;
  acceleration: number;
  isAnomalous: boolean;
}

export interface TouchProfile {
  userId: string;
  pressure: number;
  swipeVelocity: number;
  gestureCluster: number;
  isAnomalous: boolean;
}

export interface DeviceRisk {
  deviceType: string;
  riskScore: number;
  sessionCount: number;
}

export interface TimeHeatmapData {
  hour: number;
  day: string;
  riskLevel: number;
  sessionCount: number;
}

export interface NotificationSetting {
  id: string;
  channel: string;
  enabled: boolean;
  webhookUrl?: string;
  events: string[];
}

export interface RiskThreshold {
  band: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  min: number;
  max: number;
}
