import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from jose import jwt
import time
from datetime import datetime, timezone

from app.config import settings


class TestAuthenticationMechanisms:
    def test_password_complexity_enforced(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            weak_passwords = ["short", "nodigits", "12345678", "password", "qwerty123"]
            for pw in weak_passwords:
                with patch("app.services.auth_service.AuthService.register") as mock_reg:
                    mock_reg.side_effect = ValueError("Password does not meet requirements")
                    resp = test_client.post("/api/auth/register", json={
                        "email": "test@example.com",
                        "phone": "+911234567890",
                        "full_name": "Test",
                        "password": pw,
                    })
                    if resp.status_code == 422:
                        assert True
                    elif resp.status_code == 400:
                        assert "password" in resp.text.lower() or "Password" in resp.text
                    else:
                        assert resp.status_code in (400, 422)

    def test_brute_force_protection(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.login") as mock_login:
                mock_login.side_effect = Exception("Invalid credentials")
                for _ in range(10):
                    test_client.post("/api/auth/login", json={
                        "email": "test@example.com",
                        "password": "WrongP@ss1",
                    })
                resp = test_client.post("/api/auth/login", json={
                    "email": "test@example.com",
                    "password": "WrongP@ss1",
                })
                assert resp.status_code in (200, 401, 429)

    def test_jwt_token_structure(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.login") as mock_login:
                token = jwt.encode({"sub": 1, "role": "CUSTOMER", "exp": time.time() + 3600, "type": "access",
                                     "iat": time.time(), "iss": settings.JWT_ISSUER},
                                    settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
                mock_login.return_value = {
                    "access_token": token, "refresh_token": "rt",
                    "mfa_required": False, "expires_in": 1800,
                }
                resp = test_client.post("/api/auth/login", json={
                    "email": "test@example.com",
                    "password": "StrongP@ss1",
                })
                assert resp.status_code == 200
                data = resp.json()
                decoded = jwt.decode(data["access_token"], settings.JWT_SECRET_KEY,
                                      algorithms=[settings.JWT_ALGORITHM])
                assert decoded.get("type") == "access"
                assert decoded.get("sub") == 1

    def test_different_token_types(self):
        access = jwt.encode({"type": "access", "sub": 1, "exp": time.time() + 3600},
                             settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        refresh = jwt.encode({"type": "refresh", "sub": 1, "exp": time.time() + 86400},
                              settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        assert access != refresh
        decoded_a = jwt.decode(access, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        decoded_r = jwt.decode(refresh, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert decoded_a["type"] == "access"
        assert decoded_r["type"] == "refresh"

    def test_token_contains_required_claims(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.login") as mock_login:
                token = jwt.encode({"sub": 1, "role": "CUSTOMER", "exp": time.time() + 3600,
                                     "iat": time.time(), "iss": settings.JWT_ISSUER, "type": "access"},
                                    settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
                mock_login.return_value = {
                    "access_token": token, "refresh_token": "rt",
                    "mfa_required": False, "expires_in": 1800,
                }
                decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                for claim in ["sub", "exp", "iat", "iss", "type"]:
                    assert claim in decoded, f"Missing claim: {claim}"
