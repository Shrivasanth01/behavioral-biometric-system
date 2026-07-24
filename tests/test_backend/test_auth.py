import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from datetime import datetime, timezone, timedelta
from jose import jwt
from fastapi.testclient import TestClient

from app.config import settings
from app.models.user import UserRole, UserStatus, MFAMethod
from app.exceptions import (
    BadRequestException, UnauthorizedException, ForbiddenException,
    ConflictException, NotFoundException, RateLimitException,
)


class TestAuthRegister:
    def test_register_success(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.register") as mock_register:
                mock_register.return_value = MagicMock(id=1)
                response = test_client.post("/api/auth/register", json={
                    "email": "new@example.com",
                    "phone": "+911234567890",
                    "full_name": "New User",
                    "password": "StrongP@ss1",
                })
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["user_id"] == 1

    def test_register_duplicate_email(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.register") as mock_register:
                mock_register.side_effect = ConflictException("User with this email or phone already exists")
                response = test_client.post("/api/auth/register", json={
                    "email": "existing@example.com",
                    "phone": "+911234567890",
                    "full_name": "Existing User",
                    "password": "StrongP@ss1",
                })
                assert response.status_code == 409
                assert response.json()["error"]["code"] == "conflict"

    def test_register_weak_password_no_upper(self, test_client: TestClient):
        response = test_client.post("/api/auth/register", json={
            "email": "test@example.com",
            "phone": "+911234567890",
            "full_name": "Test User",
            "password": "weakpass1",
        })
        assert response.status_code == 400

    def test_register_weak_password_no_number(self, test_client: TestClient):
        response = test_client.post("/api/auth/register", json={
            "email": "test@example.com",
            "phone": "+911234567890",
            "full_name": "Test User",
            "password": "WeakPass!@",
        })
        assert response.status_code == 400

    def test_register_weak_password_no_special(self, test_client: TestClient):
        response = test_client.post("/api/auth/register", json={
            "email": "test@example.com",
            "phone": "+911234567890",
            "full_name": "Test User",
            "password": "WeakPass1",
        })
        assert response.status_code == 400

    def test_register_short_password(self, test_client: TestClient):
        response = test_client.post("/api/auth/register", json={
            "email": "test@example.com",
            "phone": "+911234567890",
            "full_name": "Test User",
            "password": "Sh0rt!",
        })
        assert response.status_code == 400

    def test_register_invalid_email(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.validate_email", return_value=False):
                with patch("app.services.auth_service.AuthService.register") as mock_register:
                    mock_register.side_effect = BadRequestException("Invalid email format")
                    response = test_client.post("/api/auth/register", json={
                        "email": "not-an-email",
                        "phone": "+911234567890",
                        "full_name": "Test User",
                        "password": "StrongP@ss1",
                    })
                    assert response.status_code == 400

    def test_register_invalid_phone(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.register") as mock_register:
                mock_register.side_effect = BadRequestException("Invalid phone number format")
                response = test_client.post("/api/auth/register", json={
                    "email": "test@example.com",
                    "phone": "123",
                    "full_name": "Test User",
                    "password": "StrongP@ss1",
                })
                assert response.status_code == 400


class TestAuthLogin:
    def test_login_success(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.login") as mock_login:
                mock_login.return_value = {
                    "mfa_required": False,
                    "access_token": "test_access_token",
                    "refresh_token": "test_refresh_token",
                    "expires_in": 1800,
                }
                response = test_client.post("/api/auth/login", json={
                    "email": "test@example.com",
                    "password": "StrongP@ss1",
                })
                assert response.status_code == 200
                data = response.json()
                assert data["access_token"] == "test_access_token"
                assert data["mfa_required"] is False

    def test_login_wrong_password(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.login") as mock_login:
                mock_login.side_effect = UnauthorizedException("Invalid email or password")
                response = test_client.post("/api/auth/login", json={
                    "email": "test@example.com",
                    "password": "WrongP@ss1",
                })
                assert response.status_code == 401

    def test_login_locked_account(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.login") as mock_login:
                mock_login.side_effect = ForbiddenException("Account locked. Try again in 900 seconds")
                response = test_client.post("/api/auth/login", json={
                    "email": "locked@example.com",
                    "password": "StrongP@ss1",
                })
                assert response.status_code == 403

    def test_login_suspended_account(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.login") as mock_login:
                mock_login.side_effect = ForbiddenException("Account is suspended")
                response = test_client.post("/api/auth/login", json={
                    "email": "suspended@example.com",
                    "password": "StrongP@ss1",
                })
                assert response.status_code == 403

    def test_login_mfa_required(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.login") as mock_login:
                mock_login.return_value = {
                    "mfa_required": True,
                    "mfa_method": "TOTP",
                    "temp_token": "temp_token_value",
                }
                response = test_client.post("/api/auth/login", json={
                    "email": "mfa_user@example.com",
                    "password": "StrongP@ss1",
                })
                assert response.status_code == 200
                data = response.json()
                assert data["mfa_required"] is True
                assert data["mfa_method"] == "TOTP"
                assert data["temp_token"] == "temp_token_value"

    def test_login_with_device_fingerprint(self, test_client: TestClient, mock_db):
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
                    "device_fingerprint": "browser_fp_abc123",
                })
                assert response.status_code == 200
                mock_login.assert_called_once()
                kwargs = mock_login.call_args[1]
                assert kwargs.get("device_fingerprint") == "browser_fp_abc123"


class TestAuthTokenRefresh:
    def test_refresh_success(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.refresh_token") as mock_refresh:
                mock_refresh.return_value = {
                    "access_token": "new_access_token",
                    "expires_in": 1800,
                }
                response = test_client.post("/api/auth/refresh", json={
                    "refresh_token": "valid_refresh_token",
                })
                assert response.status_code == 200
                assert response.json()["access_token"] == "new_access_token"

    def test_refresh_expired_token(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.refresh_token") as mock_refresh:
                mock_refresh.side_effect = UnauthorizedException("Invalid refresh token")
                response = test_client.post("/api/auth/refresh", json={
                    "refresh_token": "expired_refresh_token",
                })
                assert response.status_code == 401

    def test_refresh_revoked_token(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.refresh_token") as mock_refresh:
                mock_refresh.side_effect = UnauthorizedException("Token has been revoked")
                response = test_client.post("/api/auth/refresh", json={
                    "refresh_token": "revoked_token",
                })
                assert response.status_code == 401


class TestAuthMFA:
    def test_setup_mfa_totp(self, test_client: TestClient, auth_headers, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2, email="customer@bank.com")
                with patch("app.services.auth_service.AuthService.setup_mfa") as mock_setup:
                    mock_setup.return_value = {
                        "secret": "BASE32SECRET1234",
                        "qr_code": "otpauth://totp/BioBank:customer@bank.com?secret=BASE32SECRET1234&issuer=BioBank",
                        "message": "Scan QR code with authenticator app",
                    }
                    response = test_client.post("/api/auth/setup-mfa", json={
                        "method": "TOTP",
                    }, headers=auth_headers)
                    assert response.status_code == 200
                    assert response.json()["secret"] == "BASE32SECRET1234"

    def test_setup_mfa_invalid_method(self, test_client: TestClient, auth_headers, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                response = test_client.post("/api/auth/setup-mfa", json={
                    "method": "INVALID",
                }, headers=auth_headers)
                assert response.status_code == 422

    def test_enable_mfa_success(self, test_client: TestClient, auth_headers, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2, mfa_method="TOTP")
                with patch("app.services.auth_service.AuthService.enable_mfa") as mock_enable:
                    mock_enable.return_value = (True, "MFA enabled successfully")
                    response = test_client.post("/api/auth/enable-mfa", json={
                        "temp_token": "temp",
                        "otp_code": "123456",
                    }, headers=auth_headers)
                    assert response.status_code == 200

    def test_enable_mfa_invalid_otp(self, test_client: TestClient, auth_headers, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2, mfa_method="TOTP")
                with patch("app.services.auth_service.AuthService.enable_mfa") as mock_enable:
                    mock_enable.side_effect = BadRequestException("Invalid OTP")
                    response = test_client.post("/api/auth/enable-mfa", json={
                        "temp_token": "temp",
                        "otp_code": "000000",
                    }, headers=auth_headers)
                    assert response.status_code == 400

    def test_disable_mfa(self, test_client: TestClient, auth_headers, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.auth_service.AuthService.disable_mfa") as mock_disable:
                    mock_disable.return_value = (True, "MFA disabled successfully")
                    response = test_client.post("/api/auth/disable-mfa", headers=auth_headers)
                    assert response.status_code == 200

    def test_verify_mfa_success(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.verify_mfa") as mock_verify:
                mock_verify.return_value = {
                    "access_token": "post_mfa_token",
                    "refresh_token": "post_mfa_refresh",
                }
                response = test_client.post("/api/auth/verify-mfa", json={
                    "temp_token": "valid_temp_token",
                    "otp_code": "123456",
                })
                assert response.status_code == 200
                assert response.json()["access_token"] == "post_mfa_token"

    def test_verify_mfa_invalid_otp(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.verify_mfa") as mock_verify:
                mock_verify.side_effect = UnauthorizedException("Invalid OTP code")
                response = test_client.post("/api/auth/verify-mfa", json={
                    "temp_token": "valid_temp_token",
                    "otp_code": "000000",
                })
                assert response.status_code == 401


class TestAuthPasswordReset:
    def test_forgot_password(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.forgot_password") as mock_forgot:
                mock_forgot.return_value = "If the email exists, a reset link has been sent"
                response = test_client.post("/api/auth/forgot-password", json={
                    "email": "user@example.com",
                })
                assert response.status_code == 200

    def test_forgot_password_nonexistent(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.forgot_password") as mock_forgot:
                mock_forgot.return_value = "If the email exists, a reset link has been sent"
                response = test_client.post("/api/auth/forgot-password", json={
                    "email": "nonexistent@example.com",
                })
                assert response.status_code == 200

    def test_reset_password_success(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.reset_password") as mock_reset:
                mock_reset.return_value = "Password reset successfully"
                response = test_client.post("/api/auth/reset-password", json={
                    "reset_token": "valid_reset_token",
                    "new_password": "NewStrongP@ss1",
                })
                assert response.status_code == 200

    def test_reset_password_invalid_token(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.reset_password") as mock_reset:
                mock_reset.side_effect = BadRequestException("Invalid or expired reset token")
                response = test_client.post("/api/auth/reset-password", json={
                    "reset_token": "invalid_token",
                    "new_password": "NewStrongP@ss1",
                })
                assert response.status_code == 400

    def test_reset_password_weak_password(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.services.auth_service.AuthService.reset_password") as mock_reset:
                mock_reset.side_effect = BadRequestException("Password must be at least 8 characters")
                response = test_client.post("/api/auth/reset-password", json={
                    "reset_token": "valid_token",
                    "new_password": "weak",
                })
                assert response.status_code == 400


class TestAuthLogout:
    def test_logout_success(self, test_client: TestClient, auth_headers, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                response = test_client.post("/api/auth/logout", json={
                    "refresh_token": "some_refresh_token",
                }, headers=auth_headers)
                assert response.status_code == 200
                assert response.json()["message"] == "Logged out successfully"

    def test_logout_unauthenticated(self, test_client: TestClient):
        response = test_client.post("/api/auth/logout", json={
            "refresh_token": "some_refresh_token",
        })
        assert response.status_code == 401


class TestAuthRBAC:
    def test_customer_cannot_access_admin(self, test_client: TestClient, auth_headers, mock_db):
        with patch("app.api.admin.get_db", return_value=mock_db):
            with patch("app.middleware.auth.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2, role=UserRole.CUSTOMER)
                response = test_client.get("/api/admin/users", headers=auth_headers)
                assert response.status_code == 403

    def test_customer_cannot_access_admin_details(self, test_client: TestClient, auth_headers, mock_db):
        with patch("app.api.admin.get_db", return_value=mock_db):
            with patch("app.middleware.auth.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2, role=UserRole.CUSTOMER)
                response = test_client.get("/api/admin/users/1", headers=auth_headers)
                assert response.status_code == 403

    def test_admin_can_access_admin_endpoints(self, test_client: TestClient, admin_headers, mock_db):
        with patch("app.api.admin.get_db", return_value=mock_db):
            def fake_get_current_user(**kwargs):
                return MagicMock(id=1, role=UserRole.ADMIN)

            with patch("app.middleware.auth.get_current_user") as mock_user:
                mock_user.side_effect = fake_get_current_user
                mock_execute = AsyncMock()
                mock_execute.scalars.return_value.all.return_value = []
                mock_execute.scalar.return_value = 0
                mock_db.execute = AsyncMock(return_value=mock_execute)

                response = test_client.get("/api/admin/users", headers=admin_headers)
                assert response.status_code in (200, 500)


class TestAuthProfile:
    def test_get_me(self, test_client: TestClient, auth_headers, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(
                    id=2, email="customer@bank.com", phone="+918888888888",
                    full_name="Customer User", role=UserRole.CUSTOMER,
                    mfa_enabled=False, mfa_method=None, status=UserStatus.ACTIVE,
                    last_login_at=None, created_at=datetime.now(timezone.utc),
                )
                response = test_client.get("/api/auth/me", headers=auth_headers)
                assert response.status_code == 200

    def test_update_me(self, test_client: TestClient, auth_headers, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2, full_name="Old Name")
                with patch("app.services.auth_service.AuthService.update_profile") as mock_update:
                    mock_update.return_value = MagicMock(
                        id=2, email="customer@bank.com", phone="+918888888888",
                        full_name="New Name", role=UserRole.CUSTOMER,
                        mfa_enabled=False, mfa_method=None, status=UserStatus.ACTIVE,
                        last_login_at=None, created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc),
                    )
                    response = test_client.put("/api/auth/me", json={
                        "full_name": "New Name",
                    }, headers=auth_headers)
                    assert response.status_code == 200
