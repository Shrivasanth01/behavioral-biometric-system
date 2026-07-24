from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from app.models.account import AccountType, AccountStatus
from app.models.transaction import TransactionType, TransactionStatus
from app.models.card import CardType, CardStatus
from app.models.loan import LoanType, LoanStatus
from app.models.beneficiary import BeneficiaryType, BeneficiaryStatus


class AccountResponse(BaseModel):
    id: int
    user_id: int
    account_number: str
    account_type: AccountType
    balance: float
    currency: str
    status: AccountStatus
    interest_rate: float
    overdraft_limit: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedAccounts(BaseModel):
    items: list[AccountResponse]
    total: int


class TransactionResponse(BaseModel):
    id: int
    from_account_id: Optional[int]
    to_account_id: Optional[int]
    amount: float
    currency: str
    type: TransactionType
    status: TransactionStatus
    reference: str
    utr_number: Optional[str]
    description: Optional[str]
    category: Optional[str]
    ifsc_code: Optional[str]
    to_account_number: Optional[str]
    to_account_name: Optional[str]
    bank_name: Optional[str]
    upi_id: Optional[str]
    risk_score: float
    risk_band: str
    failure_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedTransactions(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    page_size: int


class TransferRequest(BaseModel):
    from_account_id: int
    to_account_number: str
    ifsc_code: Optional[str] = None
    amount: float = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = None
    schedule_date: Optional[str] = None


class ExternalTransferRequest(BaseModel):
    from_account_id: int
    to_account_number: str = Field(..., max_length=20)
    ifsc_code: str = Field(..., max_length=20)
    bank_name: str = Field(..., max_length=255)
    to_account_name: str = Field(..., max_length=255)
    amount: float = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)


class UpiTransferRequest(BaseModel):
    from_account_id: int
    upi_id: str = Field(..., max_length=255)
    amount: float = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)


class TransferResponse(BaseModel):
    success: bool = True
    message: str
    reference: str
    utr_number: Optional[str] = None
    status: TransactionStatus
    risk_score: Optional[float] = None
    risk_band: Optional[str] = None


class CardResponse(BaseModel):
    id: int
    user_id: int
    account_id: int
    card_number: str
    card_type: CardType
    card_holder_name: str
    expiry_month: int
    expiry_year: int
    status: CardStatus
    daily_limit: float
    monthly_limit: float
    used_daily: float
    used_monthly: float
    is_virtual: bool
    last_used_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedCards(BaseModel):
    items: list[CardResponse]
    total: int


class CardFreezeResponse(BaseModel):
    success: bool = True
    message: str
    status: CardStatus


class CardLimitUpdate(BaseModel):
    daily_limit: Optional[float] = Field(None, gt=0)
    monthly_limit: Optional[float] = Field(None, gt=0)


class LoanResponse(BaseModel):
    id: int
    user_id: int
    account_id: int
    loan_type: LoanType
    amount: float
    tenure_months: int
    interest_rate: float
    emi_amount: float
    total_payable: float
    amount_paid: float
    status: LoanStatus
    disbursed_at: Optional[datetime]
    next_emi_date: Optional[datetime]
    emi_schedule: Optional[Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedLoans(BaseModel):
    items: list[LoanResponse]
    total: int


class LoanApplyRequest(BaseModel):
    account_id: int
    loan_type: LoanType
    amount: float = Field(..., gt=0)
    tenure_months: int = Field(..., ge=1, le=360)
    interest_rate: Optional[float] = None


class LoanApplyResponse(BaseModel):
    success: bool = True
    message: str
    loan_id: int
    status: LoanStatus


class EMICalculateRequest(BaseModel):
    amount: float = Field(..., gt=0)
    annual_interest_rate: float = Field(..., gt=0)
    tenure_months: int = Field(..., ge=1, le=360)


class EMICalculateResponse(BaseModel):
    success: bool = True
    emi_amount: float
    total_interest: float
    total_payable: float
    monthly_rate: float


class EmiScheduleResponse(BaseModel):
    emi_schedule: list


class BeneficiaryResponse(BaseModel):
    id: int
    name: str
    account_number: Optional[str]
    ifsc_code: Optional[str]
    bank_name: Optional[str]
    beneficiary_type: BeneficiaryType
    upi_id: Optional[str]
    phone: Optional[str]
    status: BeneficiaryStatus
    transfer_limit: float
    total_transferred: float
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedBeneficiaries(BaseModel):
    items: list[BeneficiaryResponse]
    total: int


class BeneficiaryCreate(BaseModel):
    name: str = Field(..., max_length=255)
    account_number: Optional[str] = Field(None, max_length=20)
    ifsc_code: Optional[str] = Field(None, max_length=20)
    bank_name: Optional[str] = Field(None, max_length=255)
    beneficiary_type: BeneficiaryType = BeneficiaryType.EXTERNAL
    upi_id: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    transfer_limit: float = Field(default=100000.0, gt=0)


class BeneficiaryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    bank_name: Optional[str] = Field(None, max_length=255)
    transfer_limit: Optional[float] = Field(None, gt=0)
    status: Optional[BeneficiaryStatus] = None
