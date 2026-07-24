import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, Enum, ForeignKey, Text, Float
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.database import Base


class UserRole(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    ANALYST = "ANALYST"
    ADMIN = "ADMIN"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    SUSPENDED = "SUSPENDED"
    LOCKED = "LOCKED"


class MFAMethod(str, enum.Enum):
    TOTP = "TOTP"
    SMS = "SMS"
    EMAIL = "EMAIL"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)

    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mfa_method: Mapped[Optional[MFAMethod]] = mapped_column(Enum(MFAMethod), nullable=True)
    mfa_temp_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    device_fingerprints: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    trusted_devices: Mapped[Optional[dict]] = mapped_column(JSON, default=list)

    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reset_token_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    accounts = relationship("Account", back_populates="user", lazy="selectin")
    cards = relationship("Card", back_populates="user", lazy="selectin")
    loans = relationship("Loan", back_populates="user", lazy="selectin")
    beneficiaries = relationship("Beneficiary", back_populates="user", lazy="selectin")

    def __repr__(self):
        return f"<User {self.id}: {self.email}>"
