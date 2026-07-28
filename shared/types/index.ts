export enum RiskBand {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

export enum SeverityLevel {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

export enum AlertStatus {
  OPEN = "OPEN",
  INVESTIGATING = "INVESTIGATING",
  RESOLVED = "RESOLVED",
  DISMISSED = "DISMISSED",
}

export enum UserRole {
  CUSTOMER = "customer",
  SECURITY_ANALYST = "security_analyst",
  ADMIN = "admin",
  ML_ADMIN = "ml_admin",
}

export interface RiskAssessmentResponse {
  session_id: string;
  risk_score: number;
  risk_band: RiskBand;
  should_block: boolean;
  requires_mfa: boolean;
  requires_approval: boolean;
  reasons: string[];
  ml_score: number;
  rules_score: number;
  heuristic_score: number;
}

export interface BehavioralEventPayload {
  session_id: string;
  user_id?: number;
  device_type?: string;
  device_fingerprint?: string;
  event_type: "keydown" | "keyup" | "mousemove" | "mouseclick" | "scroll" | "pageview" | "touchstart" | "touchmove" | "touchend";
  event_data?: Record<string, any>;
  client_timestamp?: string;
}
