from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional

from app.database import get_db
from app.schemas.user import (
    UserResponse, UserDetailsResponse, UserStatusUpdate,
    PaginatedUsers, UserSessionsResponse,
)
from app.schemas.risk import DashboardSummaryResponse
from app.services.risk_service import RiskService
from app.services.behavioral_service import BehavioralService
from app.middleware.auth import require_admin, get_current_user
from app.middleware.audit import audit_logger
from app.models.user import User, UserRole, UserStatus
from app.models.behavioral import MlModel, AuditLog, BehavioralEvent, RiskScore
from app.models.account import Account
from app.models.transaction import Transaction
from app.exceptions import NotFoundException

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users", response_model=PaginatedUsers)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = select(User)

    if role:
        query = query.where(User.role == role)
    if status:
        query = query.where(User.status == status)
    if search:
        query = query.where(
            User.email.ilike(f"%{search}%") |
            User.full_name.ilike(f"%{search}%") |
            User.phone.ilike(f"%{search}%")
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(desc(User.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    users = result.scalars().all()

    total_pages = max(1, (total + page_size - 1) // page_size)
    return PaginatedUsers(
        items=users, total=total, page=page,
        page_size=page_size, total_pages=total_pages,
    )


@router.get("/users/{user_id}", response_model=UserDetailsResponse)
async def get_user_details(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException("User not found")

    accounts = await db.execute(
        select(func.count(Account.id)).where(Account.user_id == user_id)
    )
    total_accounts = accounts.scalar() or 0

    cards = await db.execute(
        select(func.count(Account.id)).select_from(
            select(Account).where(Account.user_id == user_id).subquery()
        )
    )

    balance = await db.execute(
        select(func.coalesce(func.sum(Account.balance), 0)).where(Account.user_id == user_id)
    )
    total_balance = float(balance.scalar() or 0.0)

    devices = len(user.device_fingerprints) if user.device_fingerprints else 0
    trusted = len(user.trusted_devices) if user.trusted_devices else 0

    txn_query = select(func.count(Transaction.id)).where(
        Transaction.from_account_id.in_(
            select(Account.id).where(Account.user_id == user_id)
        )
    )
    txn_result = await db.execute(txn_query)
    total_txns = txn_result.scalar() or 0

    return UserDetailsResponse(
        id=user.id,
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        role=user.role,
        mfa_enabled=user.mfa_enabled,
        mfa_method=user.mfa_method,
        status=user.status,
        failed_login_attempts=user.failed_login_attempts,
        last_login_at=user.last_login_at,
        last_login_ip=user.last_login_ip,
        created_at=user.created_at,
        updated_at=user.updated_at,
        total_accounts=total_accounts or 0,
        total_cards=cards.scalar() or 0,
        total_loans=0,
        total_transactions=total_txns,
        total_balance=total_balance,
        device_count=devices,
        trusted_device_count=trusted,
    )


@router.put("/users/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    request: Request,
    user_id: int,
    req: UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException("User not found")

    user.status = req.status
    if req.status == UserStatus.ACTIVE:
        user.failed_login_attempts = 0
        user.locked_until = None
    user.updated_at = _now()

    await db.flush()
    await db.refresh(user)

    await audit_logger(request, "user_status_changed", "user", str(user_id),
                       {"status": req.status.value, "reason": req.reason}, db, current_user)
    return user


@router.get("/users/{user_id}/sessions", response_model=list[UserSessionsResponse])
async def get_user_sessions(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = BehavioralService(db)
    sessions = await service.get_user_sessions(user_id, 50)
    return sessions


@router.get("/models")
async def list_models(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(
        select(MlModel).order_by(desc(MlModel.trained_at))
    )
    models = result.scalars().all()
    return {
        "success": True,
        "items": [
            {
                "id": m.id,
                "user_id": m.user_id,
                "model_type": m.model_type,
                "model_version": m.model_version,
                "is_active": m.is_active,
                "metrics": m.metrics,
                "session_count": m.session_count,
                "training_duration": m.training_duration,
                "trained_at": m.trained_at.isoformat() if m.trained_at else None,
            }
            for m in models
        ],
        "total": len(models),
    }


@router.get("/models/{model_id}")
async def get_model_details(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(MlModel).where(MlModel.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise NotFoundException("Model not found")
    return {
        "success": True,
        "id": model.id,
        "user_id": model.user_id,
        "model_type": model.model_type,
        "model_version": model.model_version,
        "metrics": model.metrics,
        "is_active": model.is_active,
        "session_count": model.session_count,
        "training_duration": model.training_duration,
        "trained_at": model.trained_at.isoformat() if model.trained_at else None,
    }


@router.post("/models/retrain")
async def retrain_models(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    from app.tasks import retrain_global_model, retrain_user_model
    retrain_global_model.delay()

    result = await db.execute(
        select(User.id).where(User.role == UserRole.CUSTOMER, User.status == UserStatus.ACTIVE)
    )
    user_ids = [row[0] for row in result.fetchall()]
    for uid in user_ids[:10]:
        retrain_user_model.delay(uid)

    await audit_logger(request, "models_retrain_triggered", "model", None,
                       {"global": True, "users": len(user_ids[:10])}, db, current_user)
    return {
        "success": True,
        "message": f"Retraining triggered for global model and {min(10, len(user_ids))} users",
    }


@router.get("/analytics/overview", response_model=DashboardSummaryResponse)
async def analytics_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = RiskService(db)
    summary = await service.get_dashboard_summary()
    return DashboardSummaryResponse(**summary)


@router.get("/audit-logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = select(AuditLog)

    if action:
        query = query.where(AuditLog.action == action)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(desc(AuditLog.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "success": True,
        "items": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


def _now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)
