import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class BeneficiaryType(str, enum.Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
    UPI = "UPI"


class BeneficiaryStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_number: Mapped[str] = mapped_column(String(20), nullable=True)
    ifsc_code: Mapped[str] = mapped_column(String(20), nullable=True)
    bank_name: Mapped[str] = mapped_column(String(255), nullable=True)
    beneficiary_type: Mapped[BeneficiaryType] = mapped_column(Enum(BeneficiaryType), default=BeneficiaryType.EXTERNAL, nullable=False)
    upi_id: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    status: Mapped[BeneficiaryStatus] = mapped_column(Enum(BeneficiaryStatus), default=BeneficiaryStatus.ACTIVE, nullable=False)
    transfer_limit: Mapped[float] = mapped_column(Numeric(18, 2), default=100000.0)
    total_transferred: Mapped[float] = mapped_column(Numeric(18, 2), default=0.0)
    transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="beneficiaries", lazy="selectin")

    def __repr__(self):
        return f"<Beneficiary {self.name}: {self.beneficiary_type}>"
