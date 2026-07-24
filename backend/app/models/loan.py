import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, Enum, ForeignKey, Numeric, JSON
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class LoanType(str, enum.Enum):
    PERSONAL = "PERSONAL"
    HOME = "HOME"
    CAR = "CAR"
    EDUCATION = "EDUCATION"
    BUSINESS = "BUSINESS"


class LoanStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    DEFAULTED = "DEFAULTED"


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"), nullable=False)
    loan_type: Mapped[LoanType] = mapped_column(Enum(LoanType), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    tenure_months: Mapped[int] = mapped_column(Integer, nullable=False)
    interest_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    emi_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    total_payable: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    amount_paid: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    status: Mapped[LoanStatus] = mapped_column(Enum(LoanStatus), default=LoanStatus.PENDING, nullable=False)
    disbursed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    next_emi_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    emi_schedule: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="loans", lazy="selectin")
    account = relationship("Account", back_populates="loans", lazy="selectin")

    def __repr__(self):
        return f"<Loan {self.id}: {self.loan_type} {self.amount}>"


class EmiSchedule(Base):
    __tablename__ = "emi_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    loan_id: Mapped[int] = mapped_column(Integer, ForeignKey("loans.id"), nullable=False, index=True)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    principal_component: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    interest_component: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    transaction_id: Mapped[int] = mapped_column(Integer, ForeignKey("transactions.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
