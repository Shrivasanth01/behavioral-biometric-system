import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, Enum, ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TransactionType(str, enum.Enum):
    TRANSFER = "TRANSFER"
    PAYMENT = "PAYMENT"
    RECHARGE = "RECHARGE"
    UPI = "UPI"
    WITHDRAWAL = "WITHDRAWAL"
    DEPOSIT = "DEPOSIT"


class TransactionStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"
    REVERSED = "REVERSED"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"), nullable=True, index=True)
    to_account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"), nullable=True, index=True)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    reference: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    utr_number: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True)

    ifsc_code: Mapped[str] = mapped_column(String(20), nullable=True)
    to_account_number: Mapped[str] = mapped_column(String(20), nullable=True)
    to_account_name: Mapped[str] = mapped_column(String(255), nullable=True)
    bank_name: Mapped[str] = mapped_column(String(255), nullable=True)
    upi_id: Mapped[str] = mapped_column(String(255), nullable=True)

    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_band: Mapped[str] = mapped_column(String(20), default="LOW")

    failure_reason: Mapped[str] = mapped_column(String(500), nullable=True)
    reversed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    reversal_reference: Mapped[str] = mapped_column(String(50), nullable=True)

    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    device_fingerprint: Mapped[str] = mapped_column(String(255), nullable=True)
    geo_location: Mapped[dict] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    def __repr__(self):
        return f"<Transaction {self.reference}: {self.amount}>"
