import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.models.account import AccountType, AccountStatus
from app.models.transaction import TransactionType, TransactionStatus
from app.models.card import CardType, CardStatus
from app.models.loan import LoanType, LoanStatus
from app.models.beneficiary import BeneficiaryType, BeneficiaryStatus
from app.exceptions import (
    NotFoundException, BadRequestException, ForbiddenException,
    InsufficientBalanceException, DailyLimitExceededException,
    AccountFrozenException,
)


class TestBankingAccounts:
    def test_list_accounts(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.get_accounts") as mock_get:
                    mock_get.return_value = [
                        MagicMock(id=1, user_id=2, account_number="1000123456789001",
                                  account_type=AccountType.SAVINGS, balance=Decimal("50000.00"),
                                  currency="INR", status=AccountStatus.ACTIVE,
                                  interest_rate=Decimal("3.50"), overdraft_limit=Decimal("0.00"),
                                  created_at=datetime.now(timezone.utc),
                                  updated_at=datetime.now(timezone.utc)),
                    ]
                    response = test_client.get("/api/accounts", headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["total"] == 1
                    assert len(data["items"]) == 1

    def test_get_account_details(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.get_account") as mock_get:
                    mock_get.return_value = MagicMock(
                        id=1, user_id=2, account_number="1000123456789001",
                        account_type=AccountType.SAVINGS, balance=Decimal("50000.00"),
                        currency="INR", status=AccountStatus.ACTIVE,
                        interest_rate=Decimal("3.50"), overdraft_limit=Decimal("0.00"),
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc),
                    )
                    response = test_client.get("/api/accounts/1", headers=auth_headers)
                    assert response.status_code == 200

    def test_get_account_not_found(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.get_account") as mock_get:
                    mock_get.side_effect = NotFoundException("Account not found")
                    response = test_client.get("/api/accounts/999", headers=auth_headers)
                    assert response.status_code == 404

    def test_get_account_other_user(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=3)
                with patch("app.services.banking_service.BankingService.get_account") as mock_get:
                    mock_get.side_effect = NotFoundException("Account not found")
                    response = test_client.get("/api/accounts/1", headers=auth_headers)
                    assert response.status_code == 404


class TestBankingTransactions:
    def test_get_transactions(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.get_transactions") as mock_get:
                    mock_get.return_value = ([], 0)
                    response = test_client.get("/api/accounts/1/transactions", headers=auth_headers)
                    assert response.status_code == 200

    def test_get_transactions_with_filters(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.get_transactions") as mock_get:
                    mock_get.return_value = ([], 0)
                    response = test_client.get(
                        "/api/accounts/1/transactions?type=TRANSFER&status=SUCCESS&from_date=2024-01-01&to_date=2024-12-31",
                        headers=auth_headers,
                    )
                    assert response.status_code == 200
                    mock_get.assert_called_once()


class TestBankingTransfers:
    def test_internal_transfer_success(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.create_internal_transfer") as mock_transfer:
                    mock_transfer.return_value = {
                        "success": True,
                        "reference": "TXN240101120000ABCD",
                        "utr_number": "UTR20240101120000XYZ",
                        "status": TransactionStatus.SUCCESS,
                    }
                    response = test_client.post("/api/transactions/transfer", json={
                        "from_account_id": 1,
                        "to_account_number": "1000999999999001",
                        "amount": 1000.00,
                        "description": "Test transfer",
                        "category": "general",
                    }, headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["reference"] == "TXN240101120000ABCD"
                    assert data["status"] == TransactionStatus.SUCCESS.value

    def test_internal_transfer_insufficient_funds(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.create_internal_transfer") as mock_transfer:
                    mock_transfer.side_effect = InsufficientBalanceException("Insufficient balance in source account")
                    response = test_client.post("/api/transactions/transfer", json={
                        "from_account_id": 1,
                        "to_account_number": "1000999999999001",
                        "amount": 999999.00,
                        "description": "Overdraft test",
                    }, headers=auth_headers)
                    assert response.status_code == 400

    def test_internal_transfer_invalid_account(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.create_internal_transfer") as mock_transfer:
                    mock_transfer.side_effect = NotFoundException("Account not found")
                    response = test_client.post("/api/transactions/transfer", json={
                        "from_account_id": 999,
                        "to_account_number": "1000999999999001",
                        "amount": 100.00,
                    }, headers=auth_headers)
                    assert response.status_code == 404

    def test_internal_transfer_same_account(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.create_internal_transfer") as mock_transfer:
                    mock_transfer.side_effect = BadRequestException("Cannot transfer to same account")
                    response = test_client.post("/api/transactions/transfer", json={
                        "from_account_id": 1,
                        "to_account_number": "1000123456789001",
                        "amount": 100.00,
                    }, headers=auth_headers)
                    assert response.status_code == 400

    def test_external_transfer_success(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.create_external_transfer") as mock_transfer:
                    mock_transfer.return_value = {
                        "success": True,
                        "reference": "TXN240101120000EFGH",
                        "utr_number": "UTR20240101120000ABC",
                        "status": TransactionStatus.SUCCESS,
                    }
                    response = test_client.post("/api/transactions/external", json={
                        "from_account_id": 1,
                        "to_account_number": "2000999999999001",
                        "ifsc_code": "HDFC0001234",
                        "bank_name": "HDFC Bank",
                        "to_account_name": "External User",
                        "amount": 5000.00,
                        "description": "External transfer",
                    }, headers=auth_headers)
                    assert response.status_code == 200

    def test_external_transfer_invalid_ifsc(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.create_external_transfer") as mock_transfer:
                    mock_transfer.side_effect = BadRequestException("Invalid IFSC code format")
                    response = test_client.post("/api/transactions/external", json={
                        "from_account_id": 1,
                        "to_account_number": "2000999999999001",
                        "ifsc_code": "INVALID",
                        "bank_name": "Test Bank",
                        "to_account_name": "Test",
                        "amount": 5000.00,
                    }, headers=auth_headers)
                    assert response.status_code == 400

    def test_upi_transfer_success(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.create_upi_transfer") as mock_transfer:
                    mock_transfer.return_value = {
                        "success": True,
                        "reference": "TXN240101120000IJKL",
                        "utr_number": "UTR20240101120000XYZ",
                        "status": TransactionStatus.SUCCESS,
                    }
                    response = test_client.post("/api/transactions/upi", json={
                        "from_account_id": 1,
                        "upi_id": "user@paytm",
                        "amount": 500.00,
                        "description": "UPI payment",
                    }, headers=auth_headers)
                    assert response.status_code == 200

    def test_upi_transfer_invalid_upi(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.create_upi_transfer") as mock_transfer:
                    mock_transfer.side_effect = BadRequestException("Invalid UPI ID format")
                    response = test_client.post("/api/transactions/upi", json={
                        "from_account_id": 1,
                        "upi_id": "invalid-upi",
                        "amount": 500.00,
                    }, headers=auth_headers)
                    assert response.status_code == 400

    def test_transfer_exceeds_daily_limit(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.create_external_transfer") as mock_transfer:
                    mock_transfer.side_effect = DailyLimitExceededException("Daily transaction limit exceeded")
                    response = test_client.post("/api/transactions/external", json={
                        "from_account_id": 1,
                        "to_account_number": "2000999999999001",
                        "ifsc_code": "HDFC0001234",
                        "bank_name": "HDFC Bank",
                        "to_account_name": "Test",
                        "amount": 10000000.00,
                    }, headers=auth_headers)
                    assert response.status_code == 400


class TestBankingBeneficiaries:
    def test_list_beneficiaries(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.get_beneficiaries") as mock_get:
                    mock_get.return_value = []
                    response = test_client.get("/api/beneficiaries", headers=auth_headers)
                    assert response.status_code == 200

    def test_create_beneficiary(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.create_beneficiary") as mock_create:
                    mock_create.return_value = MagicMock(
                        id=1, name="John Doe", account_number="2000999999999001",
                        ifsc_code="HDFC0001234", bank_name="HDFC Bank",
                        beneficiary_type=BeneficiaryType.EXTERNAL, upi_id=None,
                        phone=None, status=BeneficiaryStatus.ACTIVE,
                        transfer_limit=100000.0, total_transferred=0.0,
                        created_at=datetime.now(timezone.utc),
                    )
                    response = test_client.post("/api/beneficiaries", json={
                        "name": "John Doe",
                        "account_number": "2000999999999001",
                        "ifsc_code": "HDFC0001234",
                        "bank_name": "HDFC Bank",
                        "beneficiary_type": "EXTERNAL",
                        "transfer_limit": 100000.0,
                    }, headers=auth_headers)
                    assert response.status_code == 200

    def test_update_beneficiary(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.update_beneficiary") as mock_update:
                    mock_update.return_value = MagicMock(
                        id=1, name="John Updated", account_number="2000999999999001",
                        ifsc_code="HDFC0001234", bank_name="HDFC Bank",
                        beneficiary_type=BeneficiaryType.EXTERNAL, upi_id=None,
                        phone=None, status=BeneficiaryStatus.ACTIVE,
                        transfer_limit=200000.0, total_transferred=0.0,
                        created_at=datetime.now(timezone.utc),
                    )
                    response = test_client.put("/api/beneficiaries/1", json={
                        "name": "John Updated",
                        "transfer_limit": 200000.0,
                    }, headers=auth_headers)
                    assert response.status_code == 200

    def test_delete_beneficiary(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.delete_beneficiary") as mock_delete:
                    mock_delete.return_value = None
                    response = test_client.delete("/api/beneficiaries/1", headers=auth_headers)
                    assert response.status_code == 200

    def test_delete_beneficiary_not_found(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.delete_beneficiary") as mock_delete:
                    mock_delete.side_effect = NotFoundException("Beneficiary not found")
                    response = test_client.delete("/api/beneficiaries/999", headers=auth_headers)
                    assert response.status_code == 404


class TestBankingCards:
    def test_list_cards(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.get_cards") as mock_get:
                    mock_get.return_value = []
                    response = test_client.get("/api/cards", headers=auth_headers)
                    assert response.status_code == 200

    def test_freeze_card(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.freeze_card") as mock_freeze:
                    mock_freeze.return_value = MagicMock(status=CardStatus.FROZEN)
                    response = test_client.post("/api/cards/1/freeze", headers=auth_headers)
                    assert response.status_code == 200
                    assert response.json()["status"] == CardStatus.FROZEN.value

    def test_unfreeze_card(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.unfreeze_card") as mock_unfreeze:
                    mock_unfreeze.return_value = MagicMock(status=CardStatus.ACTIVE)
                    response = test_client.post("/api/cards/1/unfreeze", headers=auth_headers)
                    assert response.status_code == 200
                    assert response.json()["status"] == CardStatus.ACTIVE.value

    def test_freeze_already_frozen_card(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.freeze_card") as mock_freeze:
                    mock_freeze.side_effect = BadRequestException("Card is already frozen")
                    response = test_client.post("/api/cards/1/freeze", headers=auth_headers)
                    assert response.status_code == 400

    def test_update_card_limits(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.update_card_limits") as mock_update:
                    mock_update.return_value = MagicMock(status=CardStatus.ACTIVE)
                    response = test_client.put("/api/cards/1/limits", json={
                        "daily_limit": 75000.0,
                        "monthly_limit": 300000.0,
                    }, headers=auth_headers)
                    assert response.status_code == 200

    def test_update_card_limits_negative(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.update_card_limits") as mock_update:
                    mock_update.side_effect = BadRequestException("Daily limit must be positive")
                    response = test_client.put("/api/cards/1/limits", json={
                        "daily_limit": -100,
                    }, headers=auth_headers)
                    assert response.status_code == 400


class TestBankingLoans:
    def test_list_loans(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.get_loans") as mock_get:
                    mock_get.return_value = []
                    response = test_client.get("/api/loans", headers=auth_headers)
                    assert response.status_code == 200

    def test_apply_loan(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.apply_loan") as mock_apply:
                    mock_apply.return_value = MagicMock(
                        id=1, status=LoanStatus.ACTIVE,
                    )
                    response = test_client.post("/api/loans/apply", json={
                        "account_id": 1,
                        "loan_type": "PERSONAL",
                        "amount": 500000.0,
                        "tenure_months": 60,
                        "interest_rate": 10.5,
                    }, headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["loan_id"] == 1
                    assert data["status"] == LoanStatus.ACTIVE.value

    def test_apply_loan_invalid_account(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.apply_loan") as mock_apply:
                    mock_apply.side_effect = NotFoundException("Account not found")
                    response = test_client.post("/api/loans/apply", json={
                        "account_id": 999,
                        "loan_type": "PERSONAL",
                        "amount": 500000.0,
                        "tenure_months": 60,
                    }, headers=auth_headers)
                    assert response.status_code == 404

    def test_apply_loan_frozen_account(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.apply_loan") as mock_apply:
                    mock_apply.side_effect = AccountFrozenException("Source account is frozen")
                    response = test_client.post("/api/loans/apply", json={
                        "account_id": 1,
                        "loan_type": "PERSONAL",
                        "amount": 500000.0,
                        "tenure_months": 60,
                    }, headers=auth_headers)
                    assert response.status_code == 423

    def test_calculate_emi(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.calculate_emi") as mock_calc:
                    mock_calc.return_value = {
                        "emi_amount": 10749.04,
                        "total_interest": 144942.40,
                        "total_payable": 644942.40,
                        "monthly_rate": 0.00875,
                    }
                    response = test_client.post("/api/loans/calculate-emi", json={
                        "amount": 500000.0,
                        "annual_interest_rate": 10.5,
                        "tenure_months": 60,
                    }, headers=auth_headers)
                    assert response.status_code == 200

    def test_get_emi_schedule(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.get_loan") as mock_get:
                    mock_get.return_value = MagicMock(emi_schedule=[
                        {"installment": 1, "due_date": "2024-02-01", "amount": 10749.04},
                    ])
                    response = test_client.get("/api/loans/1/emi-schedule", headers=auth_headers)
                    assert response.status_code == 200

    def test_emi_schedule_loan_not_found(self, test_client, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.banking_service.BankingService.get_loan") as mock_get:
                    mock_get.side_effect = NotFoundException("Loan not found")
                    response = test_client.get("/api/loans/999/emi-schedule", headers=auth_headers)
                    assert response.status_code == 404
