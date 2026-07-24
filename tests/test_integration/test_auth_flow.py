import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock, ANY
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from jose import jwt

from app.config import settings


class TestAuthFlow:
    def test_complete_registration_login_flow(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            reg_service = MagicMock()
            reg_service.return_value = MagicMock(id=1, email="new@example.com")
            with patch("app.services.auth_service.AuthService.register", reg_service):
                register_resp = test_client.post("/api/auth/register", json={
                    "email": "new@example.com",
                    "phone": "+911234567890",
                    "full_name": "New User",
                    "password": "StrongP@ss1",
                })
                assert register_resp.status_code == 201
                user_id = register_resp.json().get("user", {}).get("id", 1)

            login_service = MagicMock()
            login_service.return_value = {
                "mfa_required": False,
                "access_token": jwt.encode({"sub": user_id, "role": "CUSTOMER", "exp": time.time() + 3600, "type": "access"},
                                            settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM),
                "refresh_token": "rtoken",
                "expires_in": 1800,
            }
            with patch("app.services.auth_service.AuthService.login", login_service):
                login_resp = test_client.post("/api/auth/login", json={
                    "email": "new@example.com",
                    "password": "StrongP@ss1",
                })
                assert login_resp.status_code == 200
                token = login_resp.json().get("access_token")
                assert token is not None

                with patch("app.api.auth.get_db", return_value=mock_db):
                    with patch("app.api.auth.get_current_user") as get_user:
                        user_mock = MagicMock(id=user_id, email="new@example.com", role="CUSTOMER",
                                               full_name="New User", is_active=True)
                        get_user.return_value = user_mock
                        me_resp = test_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
                        assert me_resp.status_code == 200

    def test_login_with_mfa_validation(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.login") as mock_login:
                mock_login.return_value = {"mfa_required": True, "mfa_token": "mfa_temp_token",
                                           "access_token": None, "expires_in": None}
                resp = test_client.post("/api/auth/login", json={
                    "email": "mfa@example.com",
                    "password": "StrongP@ss1",
                })
                assert resp.status_code == 200
                data = resp.json()
                assert data.get("mfa_required")
                assert data.get("mfa_token")

    def test_mfa_setup_then_verify(self, test_client: TestClient, mock_db, auth_headers):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")
                setup_service = MagicMock()
                setup_service.return_value = {"secret": "JBSWY3DPEHPK3PXP",
                                              "qr_code_url": "otpauth://totp/test?secret=JBSWY3DPEHPK3PXP"}
                with patch("app.services.auth_service.AuthService.setup_mfa", setup_service):
                    setup_resp = test_client.post("/api/auth/mfa/setup", headers=auth_headers)
                    assert setup_resp.status_code == 200
                    assert setup_resp.json().get("secret")

                verify_service = MagicMock()
                verify_service.return_value = {"success": True, "message": "MFA enabled"}
                with patch("app.services.auth_service.AuthService.verify_mfa", verify_service):
                    verify_resp = test_client.post("/api/auth/mfa/verify", json={"code": "123456"},
                                                    headers=auth_headers)
                    assert verify_resp.status_code == 200

    def test_forgot_password_then_reset(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            forgot_service = MagicMock()
            forgot_service.return_value = {"message": "Reset email sent", "reset_token": "temp_reset"}
            with patch("app.services.auth_service.AuthService.forgot_password", forgot_service):
                forgot_resp = test_client.post("/api/auth/forgot-password", json={"email": "test@example.com"})
                assert forgot_resp.status_code == 200

                reset_service = MagicMock()
                reset_service.return_value = {"message": "Password reset successful"}
                with patch("app.services.auth_service.AuthService.reset_password", reset_service):
                    reset_resp = test_client.post("/api/auth/reset-password", json={
                        "token": "temp_reset",
                        "new_password": "NewStrongP@ss1",
                    })
                    assert reset_resp.status_code == 200

    def test_token_refresh_flow(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            refresh_service = MagicMock()
            refresh_service.return_value = {"access_token": "new_access", "refresh_token": "new_refresh",
                                             "expires_in": 1800}
            with patch("app.services.auth_service.AuthService.refresh_token", refresh_service):
                resp = test_client.post("/api/auth/refresh", json={"refresh_token": "valid_refresh"})
                assert resp.status_code == 200
                assert resp.json().get("access_token") == "new_access"

    def test_logout_flow(self, test_client: TestClient, mock_db, auth_headers):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")
                with patch("app.services.auth_service.AuthService.logout") as mock_logout:
                    mock_logout.return_value = {"message": "Logged out"}
                    resp = test_client.post("/api/auth/logout", json={"refresh_token": "rtoken"},
                                            headers=auth_headers)
                    assert resp.status_code == 200
                    mock_logout.assert_called_once()

    def test_profile_get_update_flow(self, test_client: TestClient, mock_db, auth_headers):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER", email="test@example.com",
                                                   full_name="Test User", phone="+911234567890",
                                                   is_active=True)
                profile_service = MagicMock()
                profile_service.return_value = {"id": 1, "email": "test@example.com",
                                                 "full_name": "Test User", "phone": "+911234567890"}
                with patch("app.services.auth_service.AuthService.get_profile", profile_service):
                    resp = test_client.get("/api/auth/me", headers=auth_headers)
                    assert resp.status_code == 200

                update_service = MagicMock()
                update_service.return_value = {"id": 1, "full_name": "Updated User"}
                with patch("app.services.auth_service.AuthService.update_profile", update_service):
                    resp = test_client.put("/api/auth/profile", json={"full_name": "Updated User"},
                                           headers=auth_headers)
                    assert resp.status_code == 200
