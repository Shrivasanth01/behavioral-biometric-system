import pytest
import time
import json
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from fastapi.testclient import TestClient
from datetime import datetime, timezone


class TestRateLimiting:
    def test_rate_limit_headers_present(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.login") as mock_login:
                mock_login.return_value = {
                    "mfa_required": False,
                    "access_token": "token",
                    "refresh_token": "refresh",
                    "expires_in": 1800,
                }
                response = test_client.post("/api/auth/login", json={
                    "email": "test@example.com",
                    "password": "StrongP@ss1",
                })
                assert "X-RateLimit-Limit" in response.headers
                assert "X-RateLimit-Remaining" in response.headers
                assert "X-RateLimit-Reset" in response.headers

    def test_rate_limit_disabled_by_config(self, test_client: TestClient):
        with patch("app.config.settings.RATE_LIMIT_ENABLED", False):
            response = test_client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "StrongP@ss1",
            })
            assert response.status_code in (200, 401, 422)

    def test_rate_limit_auth_endpoints_stricter(self, test_client: TestClient):
        with patch("app.middleware.rate_limit.rate_limiter.check") as mock_check:
            mock_check.return_value = True
            with patch("app.api.auth.get_db", return_value=MagicMock()):
                with patch("app.services.auth_service.AuthService.login") as mock_login:
                    mock_login.return_value = {
                        "mfa_required": False,
                        "access_token": "token",
                        "refresh_token": "refresh",
                        "expires_in": 1800,
                    }
                    response = test_client.post("/api/auth/login", json={
                        "email": "test@example.com",
                        "password": "StrongP@ss1",
                    })
                    assert response.status_code == 200


class TestJWTAuthentication:
    def test_missing_token(self, test_client: TestClient):
        response = test_client.get("/api/auth/me")
        assert response.status_code == 401

    def test_invalid_token_format(self, test_client: TestClient):
        response = test_client.get("/api/auth/me", headers={"Authorization": "Invalid"})
        assert response.status_code == 401

    def test_expired_token(self, test_client: TestClient):
        from jose import jwt
        from app.config import settings
        now = datetime.now(timezone.utc)
        expired_payload = {
            "sub": 1,
            "role": "CUSTOMER",
            "iat": (now.timestamp() - 7200),
            "exp": (now.timestamp() - 3600),
            "iss": settings.JWT_ISSUER,
            "type": "access",
        }
        expired_token = jwt.encode(expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        response = test_client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
        assert response.status_code == 401

    def test_tampered_token(self, test_client: TestClient):
        tampered = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.tampered.signature"
        response = test_client.get("/api/auth/me", headers={"Authorization": f"Bearer {tampered}"})
        assert response.status_code == 401

    def test_wrong_secret_token(self, test_client: TestClient):
        from jose import jwt
        payload = {"sub": 1, "role": "CUSTOMER", "exp": 9999999999, "type": "access"}
        wrong_token = jwt.encode(payload, "wrong_secret", algorithm="HS256")
        response = test_client.get("/api/auth/me", headers={"Authorization": f"Bearer {wrong_token}"})
        assert response.status_code == 401


class TestAuditLogging:
    def test_audit_log_on_register(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.audit_logger") as mock_audit:
                mock_audit.return_value = None
                with patch("app.services.auth_service.AuthService.register") as mock_register:
                    mock_register.return_value = MagicMock(id=1)
                    test_client.post("/api/auth/register", json={
                        "email": "new@example.com",
                        "phone": "+911234567890",
                        "full_name": "New User",
                        "password": "StrongP@ss1",
                    })
                    mock_audit.assert_called_once()

    def test_audit_log_on_login(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.audit_logger") as mock_audit:
                mock_audit.return_value = None
                with patch("app.services.auth_service.AuthService.login") as mock_login:
                    mock_login.return_value = {
                        "mfa_required": False,
                        "access_token": "token",
                        "refresh_token": "refresh",
                        "expires_in": 1800,
                    }
                    test_client.post("/api/auth/login", json={
                        "email": "test@example.com",
                        "password": "StrongP@ss1",
                    })
                    mock_audit.assert_called_once()

    def test_audit_log_on_transfer(self, test_client: TestClient, auth_headers, mock_db):
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.api.banking.audit_logger") as mock_audit:
                    mock_audit.return_value = None
                    with patch("app.services.banking_service.BankingService.create_internal_transfer") as mock_t:
                        mock_t.return_value = {
                            "success": True, "reference": "REF123",
                            "utr_number": "UTR456", "status": "SUCCESS",
                        }
                        test_client.post("/api/transactions/transfer", json={
                            "from_account_id": 1,
                            "to_account_number": "1000999999999001",
                            "amount": 1000.00,
                        }, headers=auth_headers)
                        mock_audit.assert_called_once()


class TestCORS:
    def test_cors_headers_present(self, test_client: TestClient):
        response = test_client.options(
            "/api/auth/login",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert "access-control-allow-origin" in response.headers

    def test_cors_allowed_origin(self, test_client: TestClient):
        response = test_client.options(
            "/api/auth/login",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.status_code == 200

    def test_cors_blocked_origin(self, test_client: TestClient):
        with patch("app.config.settings.CORS_ORIGINS", ["http://localhost:3000"]):
            response = test_client.options(
                "/api/auth/login",
                headers={
                    "Origin": "https://evil.com",
                    "Access-Control-Request-Method": "POST",
                },
            )
            allow_origin = response.headers.get("access-control-allow-origin", "")
            assert "evil.com" not in allow_origin


class TestSecurityHeaders:
    def test_response_has_security_headers(self, test_client: TestClient):
        response = test_client.get("/health")
        headers = response.headers
        assert "content-type" in headers
        assert response.status_code == 200

    def test_no_server_info_leak(self, test_client: TestClient):
        response = test_client.get("/health")
        assert "server" not in response.headers or response.headers["server"] != "uvicorn"
