from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timezone

from app.database import get_db
from app.middleware.auth import get_current_user, require_admin, require_analyst
from app.models.user import User
from app.models.behavioral import AuditLog, MlModel, RiskScore, FraudAlert
from sqlalchemy import select, desc, func

# Initialize Domain Routers for the remaining enterprise microservices
mlops_router = APIRouter(prefix="/api/v1/mlops", tags=["MLOps Service"])
audit_router = APIRouter(prefix="/api/v1/audit", tags=["Audit Service"])
notifications_router = APIRouter(prefix="/api/v1/notifications", tags=["Notification Service"])
dashboards_router = APIRouter(prefix="/api/v1/dashboards", tags=["Dashboard APIs"])


# ============================================================================
# 1. MLOPS SERVICE ENDPOINTS
# ============================================================================
@mlops_router.post("/training/user/{user_id}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_user_model_training(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.tasks import retrain_user_model
    job = retrain_user_model.delay(user_id)
    return {"job_id": str(job.id), "user_id": user_id, "status": "QUEUED", "triggered_by": current_user.email}


@mlops_router.post("/training/global-model", status_code=status.HTTP_202_ACCEPTED)
async def trigger_global_model_training(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.tasks import retrain_global_model
    job = retrain_global_model.delay()
    return {"job_id": str(job.id), "status": "TRAINING_GLOBAL", "triggered_by": current_user.email}


@mlops_router.get("/models")
async def list_active_models(
    model_type: Optional[str] = None,
    is_active: bool = True,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    query = select(MlModel).where(MlModel.is_active == is_active).order_by(desc(MlModel.trained_at))
    if model_type:
        query = query.where(MlModel.model_type == model_type)
    result = await db.execute(query.limit(50))
    models = result.scalars().all()
    return [
        {
            "id": m.id,
            "user_id": m.user_id,
            "model_type": m.model_type,
            "model_version": m.model_version,
            "metrics": m.metrics,
            "session_count": m.session_count,
            "trained_at": m.trained_at.isoformat() if m.trained_at else None,
        }
        for m in models
    ]


# ============================================================================
# 2. AUDIT SERVICE ENDPOINTS
# ============================================================================
@audit_router.get("/logs")
async def get_audit_logs(
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    query = select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit).offset(offset)
    if action:
        query = query.where(AuditLog.action == action)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
        
    result = await db.execute(query)
    logs = result.scalars().all()
    
    total_query = select(func.count(AuditLog.id))
    total_res = await db.execute(total_query)
    total_count = total_res.scalar_one() or 0
    
    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": str(log.ip_address) if log.ip_address else None,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
    }


# ============================================================================
# 3. NOTIFICATIONS SERVICE ENDPOINTS
# ============================================================================
@notifications_router.get("/user")
async def list_user_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Fetch latest fraud alerts or system security alerts for this customer
    query = (
        select(FraudAlert)
        .where(FraudAlert.user_id == current_user.id)
        .order_by(desc(FraudAlert.created_at))
        .limit(20)
    )
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return [
        {
            "id": alert.id,
            "title": f"Security Notice: {alert.alert_type}",
            "body": f"We detected unusual activity with risk level: {alert.severity}. Please review your recent sessions.",
            "severity": alert.severity,
            "status": alert.status,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "read": alert.status != "OPEN",
        }
        for alert in alerts
    ]


# ============================================================================
# 4. DASHBOARD AGGREGATORS (BFF Layer)
# ============================================================================
@dashboards_router.get("/customer/summary")
async def get_customer_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.services.banking_service import BankingService
    banking_svc = BankingService(db)
    accounts_data = await banking_svc.get_user_accounts(current_user.id)
    
    # Check latest risk score
    risk_query = (
        select(RiskScore.risk_band, RiskScore.final_score)
        .where(RiskScore.user_id == current_user.id)
        .order_by(desc(RiskScore.created_at))
        .limit(1)
    )
    risk_res = await db.execute(risk_query)
    latest_risk = risk_res.first()
    
    total_balance = sum(float(a.get("balance", 0.0)) for a in accounts_data) if isinstance(accounts_data, list) else 0.0
    
    return {
        "user_id": current_user.id,
        "full_name": current_user.full_name,
        "total_balance": round(total_balance, 2),
        "accounts_count": len(accounts_data) if isinstance(accounts_data, list) else 0,
        "security_status": {
            "mfa_enabled": current_user.mfa_enabled,
            "current_risk_band": latest_risk.risk_band if latest_risk else "TRUSTED",
            "last_login": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
        },
    }
