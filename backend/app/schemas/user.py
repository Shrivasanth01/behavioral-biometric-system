from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any
from datetime import datetime
from app.models.user import UserRole, UserStatus, MFAMethod


class UserBase(BaseModel):
    email: str = Field(..., max_length=255)
    phone: str = Field(..., max_length=20)
    full_name: str = Field(..., max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    full_name: Optional[str] = Field(None, max_length=255)


class UserResponse(UserBase):
    id: int
    role: UserRole
    mfa_enabled: bool
    status: UserStatus
    mfa_method: Optional[MFAMethod]
    failed_login_attempts: int
    last_login_at: Optional[datetime]
    last_login_ip: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: int
    email: str
    phone: str
    full_name: str
    role: UserRole
    mfa_enabled: bool
    mfa_method: Optional[MFAMethod]
    status: UserStatus
    last_login_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class UserStatusUpdate(BaseModel):
    status: UserStatus
    reason: Optional[str] = None


class UserSessionsResponse(BaseModel):
    session_id: str
    device_type: Optional[str]
    ip_address: Optional[str]
    event_count: int
    first_event: datetime
    last_event: datetime
    risk_score: Optional[float]


class UserDetailsResponse(UserResponse):
    total_accounts: int = 0
    total_cards: int = 0
    total_loans: int = 0
    total_transactions: int = 0
    total_balance: float = 0.0
    device_count: int = 0
    trusted_device_count: int = 0


class PaginatedUsers(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
