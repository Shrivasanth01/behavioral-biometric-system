from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class BehavioralEventCreate(BaseModel):
    session_id: str = Field(..., max_length=255)
    user_id: Optional[int] = None
    device_type: Optional[str] = Field(None, max_length=100)
    device_fingerprint: Optional[str] = Field(None, max_length=255)
    event_type: str = Field(..., max_length=100)
    event_data: Optional[Any] = None
    client_timestamp: Optional[datetime] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None


class BehavioralEventResponse(BaseModel):
    id: int
    session_id: str
    user_id: Optional[int]
    device_type: Optional[str]
    device_fingerprint: Optional[str]
    event_type: str
    event_data: Optional[Any]
    client_timestamp: Optional[datetime]
    server_timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]

    class Config:
        from_attributes = True


class BehavioralEventBatch(BaseModel):
    events: list[BehavioralEventCreate]


class BehavioralProfileResponse(BaseModel):
    id: int
    user_id: int
    profile: Optional[Any]
    model_version: Optional[str]
    session_count: int
    last_trained_at: Optional[datetime]
    drift_status: str

    class Config:
        from_attributes = True


class BehavioralFeatureResponse(BaseModel):
    session_id: str
    user_id: int
    features: Optional[Any]
    model_version: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RiskHistoryResponse(BaseModel):
    date: datetime
    risk_score: float
    risk_band: str
    transaction_count: int
    alert_count: int


class SessionResponse(BaseModel):
    session_id: str
    device_type: Optional[str]
    ip_address: Optional[str]
    event_count: int
    first_event: datetime
    last_event: datetime
    risk_score: Optional[float]

    class Config:
        from_attributes = True


class IngestEventResponse(BaseModel):
    success: bool = True
    event_id: int
    message: str = "Event ingested"
