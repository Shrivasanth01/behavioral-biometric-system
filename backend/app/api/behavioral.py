from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.schemas.behavioral import (
    BehavioralEventCreate, BehavioralEventResponse,
    BehavioralEventBatch,
    BehavioralProfileResponse,
    RiskHistoryResponse,
    SessionResponse,
    IngestEventResponse,
)
from app.services.behavioral_service import BehavioralService
from app.middleware.auth import get_current_user, optional_current_user
from app.models.user import User
from app.utils import get_client_ip, get_user_agent

router = APIRouter(prefix="/events", tags=["Behavioral"])


@router.post("", response_model=IngestEventResponse)
async def ingest_event(
    request: Request,
    event: BehavioralEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user),
):
    service = BehavioralService(db)
    event_data = event.model_dump()
    if current_user and not event_data.get("user_id"):
        event_data["user_id"] = current_user.id
    if not event_data.get("ip_address"):
        event_data["ip_address"] = get_client_ip(request)
    if not event_data.get("user_agent"):
        event_data["user_agent"] = get_user_agent(request)

    created = await service.ingest_event(event_data)
    return IngestEventResponse(event_id=created.id)


@router.post("/batch")
async def ingest_event_batch(
    request: Request,
    batch: BehavioralEventBatch,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user),
):
    service = BehavioralService(db)
    ip = get_client_ip(request)
    ua = get_user_agent(request)
    event_ids = []
    for event in batch.events:
        event_data = event.model_dump()
        if current_user and not event_data.get("user_id"):
            event_data["user_id"] = current_user.id
        if not event_data.get("ip_address"):
            event_data["ip_address"] = ip
        if not event_data.get("user_agent"):
            event_data["user_agent"] = ua
        created = await service.ingest_event(event_data)
        event_ids.append(created.id)
    return {"success": True, "event_ids": event_ids, "count": len(event_ids)}


@router.get("/session/{session_id}", response_model=list[BehavioralEventResponse])
async def get_session_events(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = BehavioralService(db)
    events = await service.get_session_events(session_id)
    return events


@router.get("/profile/{user_id}", response_model=BehavioralProfileResponse)
async def get_behavioral_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BehavioralService(db)
    profile = await service.get_user_profile(user_id)
    return profile


@router.get("/profile/{user_id}/risk-history", response_model=list[RiskHistoryResponse])
async def get_risk_history(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BehavioralService(db)
    history = await service.get_risk_history(user_id, days)
    return history


@router.get("/profile/{user_id}/sessions", response_model=list[SessionResponse])
async def get_user_sessions(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BehavioralService(db)
    sessions = await service.get_user_sessions(user_id, limit)
    return sessions
