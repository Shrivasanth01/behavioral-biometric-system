import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CardType(str, enum.Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class CardStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    EXPIRED = "EXPIRED"
    CLOSED = "CLOSED"


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"), nullable=False)
    card_number: Mapped[str] = mapped_column(String(255), nullable=False)
    card_type: Mapped[CardType] = mapped_column(Enum(CardType), default=CardType.DEBIT, nullable=False)
    card_holder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    expiry_month: Mapped[int] = mapped_column(Integer, nullable=False)
    expiry_year: Mapped[int] = mapped_column(Integer, nullable=False)
    cvv: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[CardStatus] = mapped_column(Enum(CardStatus), default=CardStatus.ACTIVE, nullable=False)
    daily_limit: Mapped[float] = mapped_column(Numeric(18, 2), default=50000.0, nullable=False)
    monthly_limit: Mapped[float] = mapped_column(Numeric(18, 2), default=200000.0, nullable=False)
    used_daily: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    used_monthly: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0, nullable=False)
    pin_attempts: Mapped[int] = mapped_column(Integer, default=0)
    is_virtual: Mapped[bool] = mapped_column(Boolean, default=False)
    last_used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="cards", lazy="selectin")
    account = relationship("Account", back_populates="cards", lazy="selectin")

    def __repr__(self):
        masked = self.card_number[:4] + "XXXXXXXX" + self.card_number[-4:] if len(self.card_number) >= 16 else self.card_number
        return f"<Card {masked}: {self.card_type}>"
