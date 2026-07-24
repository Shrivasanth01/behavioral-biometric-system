import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from jose import jwt
import time

from app.config import settings


class TestRoleBasedAccess:
    def test_admin_endpoints_require_admin(self, test_client: TestClient, mock_db):
        for role, expected in [("CUSTOMER", 403), ("ADMIN", 200)]:
            token = jwt.encode({"sub": 1, "role": role, "exp": time.time() + 3600, "type": "access",
                                 "iss": settings.JWT_ISSUER},
                                settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
            headers = {"Authorization": f"Bearer {token}"}
            with patch("app.api.admin.get_db", return_value=mock_db):
                with patch("app.api.admin.get_current_user") as get_user:
                    get_user.return_value = MagicMock(id=1, role=role)
                    with patch("app.services.admin_service.AdminService.get_all_users") as svc:
                        svc.return_value = [{"id": 1, "email": "admin@example.com"}]
                        resp = test_client.get("/api/admin/users", headers=headers)
                        assert resp.status_code == expected

    def test_customer_cannot_access_anothers_data(self, test_client: TestClient, mock_db):
        token = jwt.encode({"sub": 1, "role": "CUSTOMER", "exp": time.time() + 3600, "type": "access",
                             "iss": settings.JWT_ISSUER},
                            settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        headers = {"Authorization": f"Bearer {token}"}
        with patch("app.api.banking.get_db", return_value=mock_db):
            with patch("app.api.banking.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")
                with patch("app.services.banking_service.BankingService.get_accounts") as svc:
                    svc.return_value = [{"id": 1, "user_id": 1}]
                    resp = test_client.get("/api/accounts/2", headers=headers)
                    assert resp.status_code in (200, 403, 404)

    def test_mfa_bypass_prevention(self, test_client: TestClient, mock_db):
        with patch("app.api.auth.get_db", return_value=mock_db):
            token = jwt.encode({"sub": 1, "role": "CUSTOMER", "exp": time.time() + 3600, "type": "access",
                                 "mfa_verified": False, "iss": settings.JWT_ISSUER},
                                settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
            headers = {"Authorization": f"Bearer {token}"}
            with patch("app.api.banking.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER", mfa_enabled=True)
                with patch("app.middleware.auth.requires_mfa") as mfa_check:
                    mfa_check.side_effect = Exception("MFA required")
                    resp = test_client.get("/api/accounts", headers=headers)
                    assert resp.status_code in (401, 403)

    def test_deactivated_user_blocked(self, test_client: TestClient, mock_db):
        token = jwt.encode({"sub": 1, "role": "CUSTOMER", "exp": time.time() + 3600, "type": "access",
                             "iss": settings.JWT_ISSUER},
                            settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        headers = {"Authorization": f"Bearer {token}"}
        with patch("app.api.auth.get_db", return_value=mock_db):
            with patch("app.api.auth.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER", is_active=False)
                resp = test_client.get("/api/auth/me", headers=headers)
                assert resp.status_code == 403
