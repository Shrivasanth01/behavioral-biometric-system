from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.schemas.risk import (
    RiskAssessmentRequest, RiskAssessmentResponse,
    RiskScoreResponse,
    ExplainabilityResponse,
    FraudAlertResponse, PaginatedFraudAlerts,
    FraudAlertStatusUpdate,
    DashboardSummaryResponse,
    RiskTrendsResponse, RiskTrendPoint,
    RiskDistributionResponse,
)
from app.services.risk_service import RiskService
from app.middleware.auth import get_current_user, require_analyst
from app.middleware.audit import audit_logger
from app.models.user import User
from app.models.behavioral import AlertStatus, SeverityLevel

router = APIRouter(prefix="/api/risk", tags=["Risk Engine"])


@router.post("/assess", response_model=RiskAssessmentResponse)
async def assess_risk(
    request: Request,
    req: RiskAssessmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RiskService(db)
    result = await service.assess_risk(
        user_id=req.user_id,
        session_id=req.session_id,
        transaction_id=req.transaction_id,
        transaction_amount=req.transaction_amount,
        transaction_type=req.transaction_type,
        device_fingerprint=req.device_fingerprint,
        ip_address=req.ip_address,
        user_agent=req.user_agent,
    )
    await audit_logger(request, "risk_assessment", "risk", req.session_id,
                       {"risk_score": result["risk_score"], "risk_band": result["risk_band"]},
                       db, current_user)
    return RiskAssessmentResponse(**result)


@router.get("/score/{session_id}", response_model=RiskScoreResponse)
async def get_risk_score(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RiskService(db)
    score = await service.get_risk_score(session_id)
    return score


@router.get("/explain/{session_id}", response_model=ExplainabilityResponse)
async def explain_risk(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RiskService(db)
    explanation = await service.get_explainability(session_id)
    return explanation


@router.get("/alerts", response_model=PaginatedFraudAlerts)
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[AlertStatus] = None,
    severity: Optional[SeverityLevel] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RiskService(db)
    alerts, total = await service.get_alerts(
        status=status, severity=severity, page=page, page_size=page_size
    )
    total_pages = max(1, (total + page_size - 1) // page_size)
    return PaginatedFraudAlerts(
        items=alerts, total=total, page=page,
        page_size=page_size, total_pages=total_pages,
    )


@router.get("/alerts/{alert_id}", response_model=FraudAlertResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RiskService(db)
    return await service.get_alert(alert_id)


@router.put("/alerts/{alert_id}/status", response_model=FraudAlertResponse)
async def update_alert_status(
    request: Request,
    alert_id: int,
    req: FraudAlertStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RiskService(db)
    alert = await service.update_alert_status(
        alert_id=alert_id,
        status=req.status,
        assigned_to=req.assigned_to,
        resolved_by=current_user.id if req.status in (AlertStatus.RESOLVED, AlertStatus.DISMISSED) else None,
    )
    await audit_logger(request, "alert_status_updated", "alert", str(alert_id),
                       {"status": req.status.value}, db, current_user)
    return alert


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
async def dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RiskService(db)
    summary = await service.get_dashboard_summary()
    return DashboardSummaryResponse(**summary)


@router.get("/dashboard/trends", response_model=RiskTrendsResponse)
async def dashboard_trends(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RiskService(db)
    trends = await service.get_risk_trends(days)
    return RiskTrendsResponse(trends=[RiskTrendPoint(**t) for t in trends])


@router.get("/dashboard/distribution", response_model=RiskDistributionResponse)
async def dashboard_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RiskService(db)
    distribution = await service.get_risk_distribution()
    return RiskDistributionResponse(**distribution)
