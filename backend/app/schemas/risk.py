from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import datetime
from app.models.behavioral import SeverityLevel, AlertStatus


class RiskAssessmentRequest(BaseModel):
    user_id: int
    session_id: Optional[str] = None
    transaction_id: Optional[int] = None
    transaction_amount: Optional[float] = None
    transaction_type: Optional[str] = None
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None


class RiskAssessmentResponse(BaseModel):
    success: bool = True
    session_id: Optional[str]
    risk_score: float
    risk_band: str
    should_block: bool
    requires_mfa: bool
    requires_approval: bool
    reasons: list[str]
    ml_score: float
    rules_score: float
    heuristic_score: float


class RiskScoreResponse(BaseModel):
    id: int
    session_id: Optional[str]
    transaction_id: Optional[int]
    user_id: int
    ml_score: float
    rules_score: float
    heuristic_score: float
    final_score: float
    risk_band: str
    features_contribution: Optional[Any]
    created_at: datetime

    class Config:
        from_attributes = True


class ExplainabilityResponse(BaseModel):
    id: int
    risk_score_id: int
    reasons: list[str]
    feature_contributions: dict
    created_at: datetime

    class Config:
        from_attributes = True


class FraudAlertResponse(BaseModel):
    id: int
    user_id: Optional[int]
    session_id: Optional[str]
    transaction_id: Optional[int]
    alert_type: str
    severity: SeverityLevel
    risk_score: float
    status: AlertStatus
    details: Optional[Any]
    assigned_to: Optional[int]
    resolved_by: Optional[int]
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedFraudAlerts(BaseModel):
    items: list[FraudAlertResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class FraudAlertStatusUpdate(BaseModel):
    status: AlertStatus
    assigned_to: Optional[int] = None
    resolution_notes: Optional[str] = None


class DashboardSummaryResponse(BaseModel):
    total_users: int
    active_users: int
    total_transactions: int
    blocked_transactions: int
    open_alerts: int
    critical_alerts: int
    high_risk_sessions: int
    avg_risk_score: float
    total_fraud_saved: float
    model_accuracy: float


class RiskTrendPoint(BaseModel):
    date: str
    avg_risk_score: float
    transaction_count: int
    alert_count: int
    blocked_count: int


class RiskTrendsResponse(BaseModel):
    trends: list[RiskTrendPoint]


class RiskDistributionResponse(BaseModel):
    low: int
    medium: int
    high: int
    critical: int
    total: int
