from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.schemas.banking import (
    AccountResponse, PaginatedAccounts,
    TransactionResponse, PaginatedTransactions,
    TransferRequest, TransferResponse,
    ExternalTransferRequest,
    UpiTransferRequest,
    CardResponse, PaginatedCards,
    CardFreezeResponse, CardLimitUpdate,
    LoanResponse, PaginatedLoans,
    LoanApplyRequest, LoanApplyResponse,
    EMICalculateRequest, EMICalculateResponse,
    EmiScheduleResponse,
    BeneficiaryResponse, PaginatedBeneficiaries,
    BeneficiaryCreate, BeneficiaryUpdate,
)
from app.services.banking_service import BankingService
from app.middleware.auth import get_current_user
from app.middleware.audit import audit_logger
from app.models.user import User
from app.utils import get_client_ip

router = APIRouter(prefix="/api", tags=["Banking"])


@router.get("/accounts", response_model=PaginatedAccounts)
async def list_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    accounts = await service.get_accounts(current_user.id)
    return PaginatedAccounts(items=accounts, total=len(accounts))


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    return await service.get_account(account_id, current_user.id)


@router.get("/accounts/{account_id}/transactions", response_model=PaginatedTransactions)
async def get_account_transactions(
    account_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type_filter: Optional[str] = Query(None, alias="type"),
    status_filter: Optional[str] = Query(None, alias="status"),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    txs, total = await service.get_transactions(
        current_user.id, account_id, page, page_size,
        type_filter, status_filter, from_date, to_date,
    )
    return PaginatedTransactions(items=txs, total=total, page=page, page_size=page_size)


@router.post("/transactions/transfer", response_model=TransferResponse)
async def internal_transfer(
    request: Request,
    req: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    ip = get_client_ip(request)
    result = await service.create_internal_transfer(
        user_id=current_user.id,
        from_account_id=req.from_account_id,
        to_account_number=req.to_account_number,
        amount=req.amount,
        description=req.description,
        category=req.category,
        ip_address=ip,
    )
    await audit_logger(request, "internal_transfer", "transaction", result["reference"],
                       {"amount": req.amount}, db, current_user)
    return TransferResponse(
        message="Transfer successful",
        reference=result["reference"],
        utr_number=result.get("utr_number"),
        status=result["status"],
    )


@router.post("/transactions/external", response_model=TransferResponse)
async def external_transfer(
    request: Request,
    req: ExternalTransferRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    ip = get_client_ip(request)
    result = await service.create_external_transfer(
        user_id=current_user.id,
        from_account_id=req.from_account_id,
        to_account_number=req.to_account_number,
        ifsc_code=req.ifsc_code,
        bank_name=req.bank_name,
        to_account_name=req.to_account_name,
        amount=req.amount,
        description=req.description,
        ip_address=ip,
    )
    await audit_logger(request, "external_transfer", "transaction", result["reference"],
                       {"amount": req.amount, "bank": req.bank_name}, db, current_user)
    return TransferResponse(
        message="External transfer successful",
        reference=result["reference"],
        utr_number=result.get("utr_number"),
        status=result["status"],
    )


@router.post("/transactions/upi", response_model=TransferResponse)
async def upi_transfer(
    request: Request,
    req: UpiTransferRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    ip = get_client_ip(request)
    result = await service.create_upi_transfer(
        user_id=current_user.id,
        from_account_id=req.from_account_id,
        upi_id=req.upi_id,
        amount=req.amount,
        description=req.description,
        ip_address=ip,
    )
    await audit_logger(request, "upi_transfer", "transaction", result["reference"],
                       {"amount": req.amount, "upi": req.upi_id}, db, current_user)
    return TransferResponse(
        message="UPI transfer successful",
        reference=result["reference"],
        utr_number=result.get("utr_number"),
        status=result["status"],
    )


@router.get("/beneficiaries", response_model=PaginatedBeneficiaries)
async def list_beneficiaries(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    beneficiaries = await service.get_beneficiaries(current_user.id)
    return PaginatedBeneficiaries(items=beneficiaries, total=len(beneficiaries))


@router.post("/beneficiaries", response_model=BeneficiaryResponse)
async def create_beneficiary(
    request: Request,
    req: BeneficiaryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    beneficiary = await service.create_beneficiary(current_user.id, req.model_dump())
    await audit_logger(request, "beneficiary_created", "beneficiary", str(beneficiary.id),
                       {"name": req.name}, db, current_user)
    return beneficiary


@router.put("/beneficiaries/{beneficiary_id}", response_model=BeneficiaryResponse)
async def update_beneficiary(
    request: Request,
    beneficiary_id: int,
    req: BeneficiaryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    beneficiary = await service.update_beneficiary(
        beneficiary_id, current_user.id, req.model_dump(exclude_unset=True)
    )
    await audit_logger(request, "beneficiary_updated", "beneficiary", str(beneficiary_id),
                       None, db, current_user)
    return beneficiary


@router.delete("/beneficiaries/{beneficiary_id}")
async def delete_beneficiary(
    request: Request,
    beneficiary_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    await service.delete_beneficiary(beneficiary_id, current_user.id)
    await audit_logger(request, "beneficiary_deleted", "beneficiary", str(beneficiary_id),
                       None, db, current_user)
    return {"success": True, "message": "Beneficiary deleted"}


@router.get("/cards", response_model=PaginatedCards)
async def list_cards(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    cards = await service.get_cards(current_user.id)
    return PaginatedCards(items=cards, total=len(cards))


@router.post("/cards/{card_id}/freeze", response_model=CardFreezeResponse)
async def freeze_card(
    request: Request,
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    card = await service.freeze_card(card_id, current_user.id)
    await audit_logger(request, "card_frozen", "card", str(card_id), None, db, current_user)
    return CardFreezeResponse(message="Card frozen successfully", status=card.status)


@router.post("/cards/{card_id}/unfreeze", response_model=CardFreezeResponse)
async def unfreeze_card(
    request: Request,
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    card = await service.unfreeze_card(card_id, current_user.id)
    await audit_logger(request, "card_unfrozen", "card", str(card_id), None, db, current_user)
    return CardFreezeResponse(message="Card unfrozen successfully", status=card.status)


@router.put("/cards/{card_id}/limits", response_model=CardFreezeResponse)
async def update_card_limits(
    request: Request,
    card_id: int,
    req: CardLimitUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    card = await service.update_card_limits(
        card_id, current_user.id, req.daily_limit, req.monthly_limit
    )
    await audit_logger(request, "card_limits_updated", "card", str(card_id),
                       {"daily": req.daily_limit, "monthly": req.monthly_limit}, db, current_user)
    return CardFreezeResponse(message="Card limits updated", status=card.status)


@router.get("/loans", response_model=PaginatedLoans)
async def list_loans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    loans = await service.get_loans(current_user.id)
    return PaginatedLoans(items=loans, total=len(loans))


@router.post("/loans/apply", response_model=LoanApplyResponse)
async def apply_loan(
    request: Request,
    req: LoanApplyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    loan = await service.apply_loan(
        user_id=current_user.id,
        account_id=req.account_id,
        loan_type=req.loan_type,
        amount=req.amount,
        tenure_months=req.tenure_months,
        interest_rate=req.interest_rate,
    )
    await audit_logger(request, "loan_applied", "loan", str(loan.id),
                       {"type": req.loan_type.value, "amount": req.amount}, db, current_user)
    return LoanApplyResponse(
        message="Loan application submitted successfully",
        loan_id=loan.id,
        status=loan.status,
    )


@router.get("/loans/{loan_id}/emi-schedule", response_model=EmiScheduleResponse)
async def get_emi_schedule(
    loan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    loan = await service.get_loan(loan_id, current_user.id)
    return EmiScheduleResponse(emi_schedule=loan.emi_schedule or [])


@router.post("/loans/calculate-emi", response_model=EMICalculateResponse)
async def calculate_emi_endpoint(
    req: EMICalculateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    result = await service.calculate_emi(req.amount, req.annual_interest_rate, req.tenure_months)
    return EMICalculateResponse(
        emi_amount=result["emi_amount"],
        total_interest=result["total_interest"],
        total_payable=result["total_payable"],
        monthly_rate=result["monthly_rate"],
    )
