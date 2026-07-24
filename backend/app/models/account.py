import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AccountType(str, enum.Enum):
    SAVINGS = "SAVINGS"
    CURRENT = "CURRENT"


class AccountStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    account_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType), default=AccountType.SAVINGS, nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    status: Mapped[AccountStatus] = mapped_column(Enum(AccountStatus), default=AccountStatus.ACTIVE, nullable=False)
    interest_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=3.5, nullable=False)
    overdraft_limit: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)

    daily_turnover: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    monthly_turnover: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    last_transaction_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="accounts", lazy="selectin")
    cards = relationship("Card", back_populates="account", lazy="selectin")
    loans = relationship("Loan", back_populates="account", lazy="selectin")

    def __repr__(self):
        return f"<Account {self.account_number}: {self.balance}>"
