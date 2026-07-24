from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.behavioral import AuditLog
from app.middleware.auth import get_current_user, optional_current_user
from app.models.user import User
from app.utils import get_client_ip, get_user_agent
from datetime import datetime, timezone
from typing import Optional


async def log_audit(
    db: AsyncSession,
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    user_id: Optional[int] = None,
):
    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        details=details or {},
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.now(timezone.utc),
    )
    db.add(audit_entry)
    await db.flush()


async def audit_logger(
    request: Request,
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    db: Optional[AsyncSession] = None,
    user: Optional[User] = None,
):
    if db is None:
        return
    ip = get_client_ip(request)
    ua = get_user_agent(request)
    await log_audit(
        db=db,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip,
        user_agent=ua,
        user_id=user.id if user else None,
    )
