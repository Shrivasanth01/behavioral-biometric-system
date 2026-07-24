import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from datetime import datetime, timezone

from app.models.behavioral import SeverityLevel, AlertStatus


class TestRiskAssessment:
    def test_assess_risk(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.assess_risk") as mock_assess:
                    mock_assess.return_value = {
                        "session_id": "session-abc",
                        "risk_score": 0.25,
                        "risk_band": "LOW",
                        "should_block": False,
                        "requires_mfa": False,
                        "requires_approval": False,
                        "reasons": ["Transaction within normal parameters"],
                        "ml_score": 0.15,
                        "rules_score": 0.05,
                        "heuristic_score": 0.05,
                    }
                    response = test_client.post("/api/risk/assess", json={
                        "user_id": 2,
                        "session_id": "session-abc",
                        "transaction_amount": 5000.0,
                        "transaction_type": "TRANSFER",
                    }, headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["risk_band"] == "LOW"
                    assert data["should_block"] is False

    def test_assess_risk_high(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.assess_risk") as mock_assess:
                    mock_assess.return_value = {
                        "session_id": "session-high",
                        "risk_score": 0.85,
                        "risk_band": "CRITICAL",
                        "should_block": True,
                        "requires_mfa": True,
                        "requires_approval": True,
                        "reasons": [
                            "ML model detected anomalous behavioral pattern",
                            "Transaction exceeds standard risk thresholds",
                            "Overall risk score (0.85) exceeds high-risk threshold",
                        ],
                        "ml_score": 0.90,
                        "rules_score": 0.75,
                        "heuristic_score": 0.80,
                    }
                    response = test_client.post("/api/risk/assess", json={
                        "user_id": 2,
                        "session_id": "session-high",
                        "transaction_amount": 500000.0,
                        "transaction_type": "UPI",
                    }, headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["risk_band"] == "CRITICAL"
                    assert data["should_block"] is True
                    assert data["requires_mfa"] is True

    def test_assess_risk_missing_user_id(self, test_client, auth_headers):
        response = test_client.post("/api/risk/assess", json={
            "session_id": "session-abc",
        }, headers=auth_headers)
        assert response.status_code == 422


class TestRiskScore:
    def test_get_risk_score(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.get_risk_score") as mock_get:
                    mock_get.return_value = MagicMock(
                        id=1, session_id="session-abc", transaction_id=None,
                        user_id=2, ml_score=0.15, rules_score=0.05,
                        heuristic_score=0.05, final_score=0.25,
                        risk_band="LOW", features_contribution={},
                        created_at=datetime.now(timezone.utc),
                    )
                    response = test_client.get("/api/risk/score/session-abc", headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["risk_band"] == "LOW"

    def test_get_risk_score_not_found(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.get_risk_score") as mock_get:
                    mock_get.side_effect = Exception("No risk score found for this session")
                    response = test_client.get("/api/risk/score/nonexistent", headers=auth_headers)
                    assert response.status_code == 500


class TestRiskExplainability:
    def test_explain_risk(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.get_explainability") as mock_get:
                    mock_get.return_value = MagicMock(
                        id=1, risk_score_id=1,
                        reasons=["Transaction within normal parameters"],
                        feature_contributions={"ml_score": 0.15},
                        created_at=datetime.now(timezone.utc),
                    )
                    response = test_client.get("/api/risk/explain/session-abc", headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data["reasons"]) > 0

    def test_explain_risk_not_found(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.get_explainability") as mock_get:
                    mock_get.side_effect = Exception("No explainability data found")
                    response = test_client.get("/api/risk/explain/nonexistent", headers=auth_headers)
                    assert response.status_code == 500


class TestFraudAlerts:
    def test_list_alerts(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.get_alerts") as mock_get:
                    mock_get.return_value = ([], 0)
                    response = test_client.get("/api/risk/alerts", headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["total"] == 0
                    assert data["total_pages"] == 1

    def test_list_alerts_with_filters(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.get_alerts") as mock_get:
                    mock_get.return_value = ([], 0)
                    response = test_client.get(
                        "/api/risk/alerts?status=OPEN&severity=HIGH&page=1&page_size=10",
                        headers=auth_headers,
                    )
                    assert response.status_code == 200

    def test_get_alert(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.get_alert") as mock_get:
                    mock_get.return_value = MagicMock(
                        id=1, user_id=2, session_id="session-abc",
                        transaction_id=None, alert_type="high_risk_session",
                        severity=SeverityLevel.HIGH, risk_score=0.85,
                        status=AlertStatus.OPEN, details={"reasons": ["test"]},
                        assigned_to=None, resolved_by=None, resolved_at=None,
                        created_at=datetime.now(timezone.utc),
                    )
                    response = test_client.get("/api/risk/alerts/1", headers=auth_headers)
                    assert response.status_code == 200

    def test_get_alert_not_found(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.get_alert") as mock_get:
                    mock_get.side_effect = Exception("Alert not found")
                    response = test_client.get("/api/risk/alerts/999", headers=auth_headers)
                    assert response.status_code == 500

    def test_update_alert_status(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.update_alert_status") as mock_update:
                    mock_update.return_value = MagicMock(
                        id=1, user_id=2, session_id="session-abc",
                        transaction_id=None, alert_type="high_risk_session",
                        severity=SeverityLevel.HIGH, risk_score=0.85,
                        status=AlertStatus.INVESTIGATING, details={},
                        assigned_to=3, resolved_by=None, resolved_at=None,
                        created_at=datetime.now(timezone.utc),
                    )
                    response = test_client.put("/api/risk/alerts/1/status", json={
                        "status": "INVESTIGATING",
                        "assigned_to": 3,
                    }, headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == AlertStatus.INVESTIGATING.value

    def test_update_alert_status_resolved(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.update_alert_status") as mock_update:
                    mock_update.return_value = MagicMock(
                        id=1, user_id=2, session_id="session-abc",
                        transaction_id=None, alert_type="high_risk_session",
                        severity=SeverityLevel.HIGH, risk_score=0.85,
                        status=AlertStatus.RESOLVED, details={},
                        assigned_to=None, resolved_by=2, resolved_at=datetime.now(timezone.utc),
                        created_at=datetime.now(timezone.utc),
                    )
                    response = test_client.put("/api/risk/alerts/1/status", json={
                        "status": "RESOLVED",
                    }, headers=auth_headers)
                    assert response.status_code == 200


class TestRiskDashboard:
    def test_dashboard_summary(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.get_dashboard_summary") as mock_get:
                    mock_get.return_value = {
                        "total_users": 100,
                        "active_users": 85,
                        "total_transactions": 5000,
                        "blocked_transactions": 25,
                        "open_alerts": 15,
                        "critical_alerts": 3,
                        "high_risk_sessions": 10,
                        "avg_risk_score": 0.35,
                        "total_fraud_saved": 250000.0,
                        "model_accuracy": 0.94,
                    }
                    response = test_client.get("/api/risk/dashboard/summary", headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["total_users"] == 100
                    assert data["open_alerts"] == 15

    def test_dashboard_trends(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.get_risk_trends") as mock_get:
                    mock_get.return_value = [
                        {"date": "2024-01-01", "avg_risk_score": 0.3, "transaction_count": 100,
                         "alert_count": 2, "blocked_count": 1},
                        {"date": "2024-01-02", "avg_risk_score": 0.35, "transaction_count": 120,
                         "alert_count": 3, "blocked_count": 2},
                    ]
                    response = test_client.get("/api/risk/dashboard/trends?days=7", headers=auth_headers)
                    assert response.status_code == 200
                    assert len(response.json()["trends"]) == 2

    def test_dashboard_distribution(self, test_client, auth_headers, mock_db):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.risk_service.RiskService.get_risk_distribution") as mock_get:
                    mock_get.return_value = {"LOW": 800, "MEDIUM": 150, "HIGH": 40, "CRITICAL": 10, "total": 1000}
                    response = test_client.get("/api/risk/dashboard/distribution", headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["LOW"] == 800
                    assert data["total"] == 1000
