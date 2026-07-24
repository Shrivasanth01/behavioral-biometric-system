import pytest
from unittest.mock import AsyncMock, patch, MagicMock, ANY
from fastapi.testclient import TestClient


class TestTransactionFlow:
    def test_account_creation_and_transaction(self, test_client: TestClient, mock_db, auth_headers):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")

                acct_service = MagicMock()
                acct_service.return_value = {
                    "id": 100, "account_number": "1000999999999100", "account_type": "SAVINGS",
                    "balance": 5000.0, "status": "ACTIVE", "user_id": 1,
                }
                with patch("app.services.banking_service.BankingService.create_account", acct_service):
                    resp = test_client.post("/api/accounts", json={
                        "account_type": "SAVINGS", "initial_deposit": 5000.0,
                    }, headers=auth_headers)
                    assert resp.status_code == 201
                    acct_num = resp.json().get("account_number", "1000999999999100")

                list_service = MagicMock()
                list_service.return_value = [{"id": 100, "account_number": acct_num, "balance": 5000.0}]
                with patch("app.services.banking_service.BankingService.get_accounts", list_service):
                    list_resp = test_client.get("/api/accounts", headers=auth_headers)
                    assert list_resp.status_code == 200
                    assert len(list_resp.json()) >= 1

                tx_service = MagicMock()
                tx_service.return_value = {
                    "success": True, "reference": "REF123",
                    "utr_number": "UTR456", "status": "SUCCESS",
                }
                with patch("app.services.banking_service.BankingService.create_internal_transfer", tx_service):
                    tx_resp = test_client.post("/api/transactions/transfer", json={
                        "from_account_id": 100,
                        "to_account_number": "1000999999999001",
                        "amount": 1000.0,
                    }, headers=auth_headers)
                    assert tx_resp.status_code == 200
                    assert tx_resp.json().get("success")

    def test_external_and_upi_transfer(self, test_client: TestClient, mock_db, auth_headers):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")

                for url, service_name, service_data in [
                    ("/api/transactions/external-transfer", "create_external_transfer",
                     {"success": True, "reference": "EXT123", "status": "PENDING"}),
                    ("/api/upi/transfer", "create_upi_payment",
                     {"success": True, "reference": "UPI123", "status": "SUCCESS"}),
                ]:
                    with patch(f"app.services.banking_service.BankingService.{service_name}") as mock_svc:
                        mock_svc.return_value = service_data
                        resp = test_client.post(url, json={"from_account_id": 1, "amount": 500.0},
                                                headers=auth_headers)
                        assert resp.status_code == 200
                        assert resp.json().get("success")

    def test_beneficiary_lifecycle(self, test_client: TestClient, mock_db, auth_headers):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")

                with patch("app.services.banking_service.BankingService.add_beneficiary") as add_svc:
                    add_svc.return_value = {"id": 50, "account_number": "1000999999999002",
                                            "nickname": "Friend", "status": "ACTIVE"}
                    resp = test_client.post("/api/beneficiaries", json={
                        "account_number": "1000999999999002", "ifsc_code": "SBIN0001234",
                        "nickname": "Friend",
                    }, headers=auth_headers)
                    assert resp.status_code == 201

                with patch("app.services.banking_service.BankingService.get_beneficiaries") as list_svc:
                    list_svc.return_value = [{"id": 50, "nickname": "Friend"}]
                    list_resp = test_client.get("/api/beneficiaries", headers=auth_headers)
                    assert list_resp.status_code == 200

                with patch("app.services.banking_service.BankingService.delete_beneficiary") as del_svc:
                    del_svc.return_value = {"success": True}
                    del_resp = test_client.delete("/api/beneficiaries/50", headers=auth_headers)
                    assert del_resp.status_code == 200

    def test_card_lifecycle(self, test_client: TestClient, mock_db, auth_headers):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")

                freeze_service = MagicMock()
                freeze_service.return_value = {"success": True, "status": "FROZEN"}
                with patch("app.services.banking_service.BankingService.freeze_card", freeze_service):
                    resp = test_client.post("/api/cards/1/freeze", headers=auth_headers)
                    assert resp.status_code == 200

                unfreeze_service = MagicMock()
                unfreeze_service.return_value = {"success": True, "status": "ACTIVE"}
                with patch("app.services.banking_service.BankingService.unfreeze_card", unfreeze_service):
                    resp = test_client.post("/api/cards/1/unfreeze", headers=auth_headers)
                    assert resp.status_code == 200

                limit_service = MagicMock()
                limit_service.return_value = {"success": True, "daily_limit": 50000}
                with patch("app.services.banking_service.BankingService.update_card_limit", limit_service):
                    resp = test_client.put("/api/cards/1/limits", json={"daily_limit": 50000, "transaction_limit": 15000},
                                           headers=auth_headers)
                    assert resp.status_code == 200

    def test_loan_application_and_emi(self, test_client: TestClient, mock_db, auth_headers):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")

                apply_service = MagicMock()
                apply_service.return_value = {
                    "id": 200, "loan_type": "PERSONAL", "amount": 500000,
                    "tenure_months": 60, "interest_rate": 10.5, "status": "PENDING",
                    "emi": 10748.44,
                }
                with patch("app.services.banking_service.BankingService.apply_loan", apply_service):
                    resp = test_client.post("/api/loans/apply", json={
                        "loan_type": "PERSONAL", "amount": 500000, "tenure_months": 60,
                    }, headers=auth_headers)
                    assert resp.status_code == 201
                    assert resp.json().get("emi") > 0
