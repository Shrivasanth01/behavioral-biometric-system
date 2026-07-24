from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone, timedelta
from typing import Optional
import random

from app.models.user import User, UserStatus
from app.models.account import Account, AccountType, AccountStatus
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.card import Card, CardType, CardStatus
from app.models.loan import Loan, LoanType, LoanStatus, EmiSchedule
from app.models.beneficiary import Beneficiary, BeneficiaryType, BeneficiaryStatus
from app.config import settings
from app.exceptions import (
    NotFoundException,
    BadRequestException,
    ForbiddenException,
    InsufficientBalanceException,
    DailyLimitExceededException,
    TransactionBlockedException,
    AccountFrozenException,
)
from app.utils import (
    generate_reference_number,
    generate_utr_number,
    generate_account_number,
    calculate_emi,
    validate_ifsc,
    validate_upi_id,
)


class BankingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_accounts(self, user_id: int) -> list[Account]:
        result = await self.db.execute(
            select(Account).where(Account.user_id == user_id).order_by(Account.created_at.desc())
        )
        return result.scalars().all()

    async def get_account(self, account_id: int, user_id: int) -> Account:
        result = await self.db.execute(
            select(Account).where(
                Account.id == account_id,
                Account.user_id == user_id,
            )
        )
        account = result.scalar_one_or_none()
        if not account:
            raise NotFoundException("Account not found")
        return account

    async def get_account_by_number(self, account_number: str) -> Account:
        result = await self.db.execute(
            select(Account).where(Account.account_number == account_number)
        )
        account = result.scalar_one_or_none()
        if not account:
            raise NotFoundException("Account not found")
        return account

    async def check_account_active(self, account: Account):
        if account.status == AccountStatus.FROZEN:
            raise AccountFrozenException("Source account is frozen")
        if account.status == AccountStatus.CLOSED:
            raise BadRequestException("Source account is closed")

    async def get_transactions(
        self,
        user_id: int,
        account_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> tuple[list[Transaction], int]:
        user_accounts = await self.db.execute(
            select(Account.id).where(Account.user_id == user_id)
        )
        account_ids = [row[0] for row in user_accounts.fetchall()]

        if not account_ids:
            return [], 0

        query = select(Transaction).where(
            or_(
                Transaction.from_account_id.in_(account_ids),
                Transaction.to_account_id.in_(account_ids),
            )
        )

        if account_id:
            query = query.where(
                or_(
                    Transaction.from_account_id == account_id,
                    Transaction.to_account_id == account_id,
                )
            )
        if type_filter:
            query = query.where(Transaction.type == type_filter)
        if status_filter:
            query = query.where(Transaction.status == status_filter)
        if from_date:
            query = query.where(Transaction.created_at >= from_date)
        if to_date:
            query = query.where(Transaction.created_at <= to_date)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(desc(Transaction.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def create_internal_transfer(
        self,
        user_id: int,
        from_account_id: int,
        to_account_number: str,
        amount: float,
        description: Optional[str] = None,
        category: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
    ) -> dict:
        source = await self.get_account(from_account_id, user_id)
        await self.check_account_active(source)

        target = await self.get_account_by_number(to_account_number)

        if source.id == target.id:
            raise BadRequestException("Cannot transfer to same account")

        if float(source.balance) < amount:
            raise InsufficientBalanceException("Insufficient balance in source account")

        reference = generate_reference_number()
        utr = generate_utr_number()

        transaction = Transaction(
            from_account_id=source.id,
            to_account_id=target.id,
            amount=amount,
            currency=source.currency,
            type=TransactionType.TRANSFER,
            status=TransactionStatus.SUCCESS,
            reference=reference,
            utr_number=utr,
            description=description or f"Transfer to {target.account_number}",
            category=category,
            risk_score=0.0,
            risk_band="LOW",
            ip_address=ip_address,
            device_fingerprint=device_fingerprint,
        )
        self.db.add(transaction)

        source.balance = float(source.balance) - amount
        target.balance = float(target.balance) + amount
        source.last_transaction_at = datetime.now(timezone.utc)
        target.last_transaction_at = datetime.now(timezone.utc)
        source.daily_turnover = float(source.daily_turnover) + amount
        source.monthly_turnover = float(source.monthly_turnover) + amount

        await self.db.flush()

        return {
            "success": True,
            "reference": reference,
            "utr_number": utr,
            "status": TransactionStatus.SUCCESS,
        }

    async def create_external_transfer(
        self,
        user_id: int,
        from_account_id: int,
        to_account_number: str,
        ifsc_code: str,
        bank_name: str,
        to_account_name: str,
        amount: float,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
    ) -> dict:
        source = await self.get_account(from_account_id, user_id)
        await self.check_account_active(source)

        if not validate_ifsc(ifsc_code):
            raise BadRequestException("Invalid IFSC code format")

        if float(source.balance) < amount:
            raise InsufficientBalanceException("Insufficient balance")

        if float(source.daily_turnover) + amount > float(source.overdraft_limit or 0) * 2:
            raise DailyLimitExceededException("Daily transaction limit exceeded")

        reference = generate_reference_number()
        utr = generate_utr_number()

        transaction = Transaction(
            from_account_id=source.id,
            to_account_id=None,
            amount=amount,
            currency=source.currency,
            type=TransactionType.TRANSFER,
            status=TransactionStatus.SUCCESS,
            reference=reference,
            utr_number=utr,
            description=description or f"External transfer to {to_account_name}",
            ifsc_code=ifsc_code,
            to_account_number=to_account_number,
            to_account_name=to_account_name,
            bank_name=bank_name,
            risk_score=0.0,
            risk_band="LOW",
            ip_address=ip_address,
            device_fingerprint=device_fingerprint,
        )
        self.db.add(transaction)

        source.balance = float(source.balance) - amount
        source.last_transaction_at = datetime.now(timezone.utc)
        source.daily_turnover = float(source.daily_turnover) + amount
        source.monthly_turnover = float(source.monthly_turnover) + amount

        await self.db.flush()

        return {
            "success": True,
            "reference": reference,
            "utr_number": utr,
            "status": TransactionStatus.SUCCESS,
        }

    async def create_upi_transfer(
        self,
        user_id: int,
        from_account_id: int,
        upi_id: str,
        amount: float,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
    ) -> dict:
        source = await self.get_account(from_account_id, user_id)
        await self.check_account_active(source)

        if not validate_upi_id(upi_id):
            raise BadRequestException("Invalid UPI ID format")

        if float(source.balance) < amount:
            raise InsufficientBalanceException("Insufficient balance")

        reference = generate_reference_number()
        utr = generate_utr_number()

        transaction = Transaction(
            from_account_id=source.id,
            to_account_id=None,
            amount=amount,
            currency=source.currency,
            type=TransactionType.UPI,
            status=TransactionStatus.SUCCESS,
            reference=reference,
            utr_number=utr,
            description=description or f"UPI transfer to {upi_id}",
            upi_id=upi_id,
            risk_score=0.0,
            risk_band="LOW",
            ip_address=ip_address,
            device_fingerprint=device_fingerprint,
        )
        self.db.add(transaction)

        source.balance = float(source.balance) - amount
        source.last_transaction_at = datetime.now(timezone.utc)
        source.daily_turnover = float(source.daily_turnover) + amount
        source.monthly_turnover = float(source.monthly_turnover) + amount

        await self.db.flush()

        return {
            "success": True,
            "reference": reference,
            "utr_number": utr,
            "status": TransactionStatus.SUCCESS,
        }

    async def get_cards(self, user_id: int) -> list[Card]:
        result = await self.db.execute(
            select(Card).where(Card.user_id == user_id).order_by(Card.created_at.desc())
        )
        return result.scalars().all()

    async def get_card(self, card_id: int, user_id: int) -> Card:
        result = await self.db.execute(
            select(Card).where(Card.id == card_id, Card.user_id == user_id)
        )
        card = result.scalar_one_or_none()
        if not card:
            raise NotFoundException("Card not found")
        return card

    async def freeze_card(self, card_id: int, user_id: int) -> Card:
        card = await self.get_card(card_id, user_id)
        if card.status != CardStatus.ACTIVE:
            raise BadRequestException(f"Card is already {card.status.value.lower()}")
        card.status = CardStatus.FROZEN
        card.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(card)
        return card

    async def unfreeze_card(self, card_id: int, user_id: int) -> Card:
        card = await self.get_card(card_id, user_id)
        if card.status != CardStatus.FROZEN:
            raise BadRequestException(f"Card is not frozen (current: {card.status.value.lower()})")
        card.status = CardStatus.ACTIVE
        card.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(card)
        return card

    async def update_card_limits(self, card_id: int, user_id: int, daily_limit: Optional[float], monthly_limit: Optional[float]) -> Card:
        card = await self.get_card(card_id, user_id)
        if daily_limit is not None:
            if daily_limit <= 0:
                raise BadRequestException("Daily limit must be positive")
            card.daily_limit = daily_limit
        if monthly_limit is not None:
            if monthly_limit <= 0:
                raise BadRequestException("Monthly limit must be positive")
            card.monthly_limit = monthly_limit
        card.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(card)
        return card

    async def get_loans(self, user_id: int) -> list[Loan]:
        result = await self.db.execute(
            select(Loan).where(Loan.user_id == user_id).order_by(Loan.created_at.desc())
        )
        return result.scalars().all()

    async def get_loan(self, loan_id: int, user_id: int) -> Loan:
        result = await self.db.execute(
            select(Loan).where(Loan.id == loan_id, Loan.user_id == user_id)
        )
        loan = result.scalar_one_or_none()
        if not loan:
            raise NotFoundException("Loan not found")
        return loan

    async def apply_loan(
        self,
        user_id: int,
        account_id: int,
        loan_type: LoanType,
        amount: float,
        tenure_months: int,
        interest_rate: Optional[float] = None,
    ) -> Loan:
        account = await self.get_account(account_id, user_id)
        await self.check_account_active(account)

        rate_map = {
            LoanType.PERSONAL: 10.5,
            LoanType.HOME: 8.5,
            LoanType.CAR: 9.0,
            LoanType.EDUCATION: 7.5,
            LoanType.BUSINESS: 12.0,
        }
        rate = interest_rate or rate_map.get(loan_type, 10.0)
        emi = calculate_emi(amount, rate, tenure_months)
        total_payable = round(emi * tenure_months, 2)

        loan = Loan(
            user_id=user_id,
            account_id=account.id,
            loan_type=loan_type,
            amount=amount,
            tenure_months=tenure_months,
            interest_rate=rate,
            emi_amount=emi,
            total_payable=total_payable,
            amount_paid=0.0,
            status=LoanStatus.ACTIVE,
            disbursed_at=datetime.now(timezone.utc),
            next_emi_date=datetime.now(timezone.utc) + timedelta(days=30),
        )

        schedule = []
        remaining = amount
        monthly_rate = rate / (12 * 100)
        for i in range(tenure_months):
            interest_component = remaining * monthly_rate
            principal_component = emi - interest_component
            if principal_component < 0:
                principal_component = 0
            remaining -= principal_component
            due_date = datetime.now(timezone.utc) + timedelta(days=30 * (i + 1))
            schedule.append({
                "installment": i + 1,
                "due_date": due_date.isoformat(),
                "amount": round(emi, 2),
                "principal_component": round(principal_component, 2),
                "interest_component": round(interest_component, 2),
                "balance_after": round(max(remaining, 0), 2),
                "status": "PENDING",
            })
        loan.emi_schedule = schedule
        account.balance = float(account.balance) + amount

        self.db.add(loan)
        await self.db.flush()
        await self.db.refresh(loan)
        return loan

    async def calculate_emi(self, amount: float, annual_rate: float, tenure_months: int) -> dict:
        if amount <= 0:
            raise BadRequestException("Amount must be positive")
        if annual_rate <= 0:
            raise BadRequestException("Interest rate must be positive")
        if tenure_months <= 0:
            raise BadRequestException("Tenure must be positive")

        emi = calculate_emi(amount, annual_rate, tenure_months)
        total_payable = round(emi * tenure_months, 2)
        total_interest = round(total_payable - amount, 2)

        return {
            "emi_amount": emi,
            "total_interest": total_interest,
            "total_payable": total_payable,
            "monthly_rate": round(annual_rate / (12 * 100), 6),
        }

    async def get_beneficiaries(self, user_id: int) -> list[Beneficiary]:
        result = await self.db.execute(
            select(Beneficiary).where(
                Beneficiary.user_id == user_id,
                Beneficiary.status == BeneficiaryStatus.ACTIVE,
            ).order_by(Beneficiary.created_at.desc())
        )
        return result.scalars().all()

    async def get_beneficiary(self, beneficiary_id: int, user_id: int) -> Beneficiary:
        result = await self.db.execute(
            select(Beneficiary).where(
                Beneficiary.id == beneficiary_id,
                Beneficiary.user_id == user_id,
            )
        )
        beneficiary = result.scalar_one_or_none()
        if not beneficiary:
            raise NotFoundException("Beneficiary not found")
        return beneficiary

    async def create_beneficiary(self, user_id: int, data: dict) -> Beneficiary:
        beneficiary = Beneficiary(
            user_id=user_id,
            name=data["name"],
            account_number=data.get("account_number"),
            ifsc_code=data.get("ifsc_code"),
            bank_name=data.get("bank_name"),
            beneficiary_type=BeneficiaryType(data.get("beneficiary_type", "EXTERNAL")),
            upi_id=data.get("upi_id"),
            phone=data.get("phone"),
            transfer_limit=data.get("transfer_limit", 100000.0),
            total_transferred=0.0,
            transaction_count=0,
        )
        self.db.add(beneficiary)
        await self.db.flush()
        await self.db.refresh(beneficiary)
        return beneficiary

    async def update_beneficiary(self, beneficiary_id: int, user_id: int, data: dict) -> Beneficiary:
        beneficiary = await self.get_beneficiary(beneficiary_id, user_id)
        for key, value in data.items():
            if value is not None and hasattr(beneficiary, key):
                setattr(beneficiary, key, value)
        await self.db.flush()
        await self.db.refresh(beneficiary)
        return beneficiary

    async def delete_beneficiary(self, beneficiary_id: int, user_id: int):
        beneficiary = await self.get_beneficiary(beneficiary_id, user_id)
        await self.db.delete(beneficiary)
        await self.db.flush()
