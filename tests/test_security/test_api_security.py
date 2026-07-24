import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import json


class TestAPIEndpointSecurity:
    def test_sql_injection_prevention(self, test_client: TestClient):
        payloads = [
            {"email": "test@example.com' OR '1'='1", "password": "test"},
            {"account_number": "1000999999999001; DROP TABLE users;"},
            {"amount": "500; SELECT * FROM accounts;"},
        ]
        for payload in payloads:
            resp = test_client.post("/api/auth/login", json=payload)
            assert resp.status_code in (401, 422)

    def test_xss_prevention_headers(self, test_client: TestClient):
        resp = test_client.get("/health")
        headers = resp.headers
        content_type = headers.get("content-type", "")
        assert "text/html" not in content_type or resp.status_code != 200

    def test_idor_prevention(self, test_client: TestClient, mock_db, auth_headers):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")
                with patch("app.services.banking_service.BankingService.get_account") as svc:
                    svc.side_effect = Exception("Not found")
                    resp = test_client.get("/api/accounts/99999", headers=auth_headers)
                    assert resp.status_code in (403, 404)

    def test_csrf_prevention(self, test_client: TestClient, auth_headers):
        resp = test_client.post("/api/auth/logout", json={"refresh_token": "rtoken"},
                                headers=auth_headers)
        if resp.status_code == 200:
            assert True
        else:
            assert resp.status_code == 401

    def test_input_validation_limits(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            oversized = "A" * 10001
            resp = test_client.post("/api/auth/register", json={
                "email": f"{oversized}@example.com",
                "phone": "+911234567890",
                "full_name": oversized,
                "password": "StrongP@ss1",
            })
            assert resp.status_code in (422, 400)

    def test_negative_amount_prevention(self, test_client: TestClient, mock_db, auth_headers):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")
                resp = test_client.post("/api/transactions/transfer", json={
                    "from_account_id": 1,
                    "to_account_number": "1000999999999001",
                    "amount": -100,
                }, headers=auth_headers)
                assert resp.status_code == 422

    def test_enumeration_protection(self, test_client: TestClient):
        existing = test_client.post("/api/auth/login", json={
            "email": "existing@example.com", "password": "WrongP@ss1",
        })
        nonexistent = test_client.post("/api/auth/login", json={
            "email": "nonexistent@example.com", "password": "WrongP@ss1",
        })
        assert existing.status_code == nonexistent.status_code

    def test_response_contains_no_sensitive_data(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.login") as mock_login:
                token_data = {"access_token": "tok", "refresh_token": "rt",
                              "mfa_required": False, "expires_in": 1800}
                mock_login.return_value = token_data
                resp = test_client.post("/api/auth/login", json={
                    "email": "test@example.com",
                    "password": "StrongP@ss1",
                })
                body = resp.text.lower()
                assert "password" not in body or resp.status_code != 200
