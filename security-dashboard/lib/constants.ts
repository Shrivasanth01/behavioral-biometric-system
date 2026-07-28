export const RISK_THRESHOLDS = {
  CRITICAL: 80,
  HIGH: 60,
  MEDIUM: 30,
  LOW: 0,
};

export const RISK_BANDS = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'] as const;

export const SEVERITY_COLORS = {
  LOW: 'text-alert-low bg-alert-low/10 border-alert-low/30',
  MEDIUM: 'text-alert-medium bg-alert-medium/10 border-alert-medium/30',
  HIGH: 'text-alert-high bg-alert-high/10 border-alert-high/30',
  CRITICAL: 'text-alert-critical bg-alert-critical/10 border-alert-critical/30',
};

export const SEVERITY_BG = {
  LOW: 'bg-alert-low',
  MEDIUM: 'bg-alert-medium',
  HIGH: 'bg-alert-high',
  CRITICAL: 'bg-alert-critical',
};

export const ALERT_TYPES = {
  behavioral_anomaly: 'Behavioral Anomaly',
  location_anomaly: 'Location Anomaly',
  device_anomaly: 'Device Anomaly',
  transaction_anomaly: 'Transaction Anomaly',
  velocity_anomaly: 'Velocity Anomaly',
} as const;

export const ALERT_ICONS = {
  behavioral_anomaly: 'Activity',
  location_anomaly: 'MapPin',
  device_anomaly: 'Monitor',
  transaction_anomaly: 'CreditCard',
  velocity_anomaly: 'Gauge',
} as const;

export const NAV_ITEMS = [
  { href: '/dashboard', label: 'Executive Overview', icon: 'LayoutDashboard' },
  { href: '/console/alerts', label: 'SecOps Live Alerts', icon: 'Bell' },
  { href: '/console/investigate/SEC-ALT-884', label: 'Forensic Workbench', icon: 'Search' },
  { href: '/dashboard/behavioral', label: 'Behavioral Analytics', icon: 'Activity' },
  { href: '/dashboard/investigate', label: 'User Search & Lookup', icon: 'Search' },
  { href: '/dashboard/ml-monitoring', label: 'ML Monitoring', icon: 'BrainCircuit' },
  { href: '/dashboard/alerts', label: 'Fraud Alerts (Legacy)', icon: 'Bell' },
  { href: '/dashboard/explain', label: 'Explainability', icon: 'Eye' },
  { href: '/dashboard/risk-trends', label: 'Risk Trends', icon: 'TrendingUp' },
  { href: '/dashboard/audit-logs', label: 'Audit Logs', icon: 'FileText' },
  { href: '/dashboard/settings', label: 'Admin Settings', icon: 'Settings' },
];

export const MOCK_USERS: { id: string; email: string; name: string; role: 'analyst' | 'admin' }[] = [
  { id: 'USR-001', email: 'sarah.chen@bank.com', name: 'Sarah Chen', role: 'admin' },
  { id: 'USR-002', email: 'marcus.jones@bank.com', name: 'Marcus Jones', role: 'analyst' },
  { id: 'USR-003', email: 'elena.kovac@bank.com', name: 'Elena Kovac', role: 'analyst' },
];

export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || 'Sentinel Fraud Platform';
