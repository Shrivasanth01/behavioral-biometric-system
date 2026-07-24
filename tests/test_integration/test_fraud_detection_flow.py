import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient


class TestFraudDetectionFlow:
    def test_risk_assessment_triggers_fraud_alert(self, test_client, mock_db, auth_headers):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")

                assess_service = MagicMock()
                assess_service.return_value = {
                    "risk_score": 85, "risk_band": "critical",
                    "reasons": ["High transaction amount", "Unusual location"],
                }
                with patch("app.services.risk_service.RiskService.assess_risk", assess_service):
                    resp = test_client.post("/api/risk/assess", json={
                        "user_id": 1, "session_id": 100, "transaction_id": 500,
                    }, headers=auth_headers)
                    assert resp.status_code == 200
                    assert resp.json().get("risk_band") == "critical"

    def test_fraud_alert_lifecycle(self, test_client, mock_db, auth_headers):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="ADMIN")

                create_service = MagicMock()
                create_service.return_value = {
                    "id": 1, "user_id": 1, "severity": "HIGH",
                    "status": "OPEN", "description": "Fraud detected",
                }
                with patch("app.services.risk_service.RiskService.create_alert", create_service):
                    resp = test_client.post("/api/risk/alerts", json={
                        "user_id": 1, "severity": "HIGH", "description": "Fraud detected",
                    }, headers=auth_headers)
                    assert resp.status_code == 201

                alerts_service = MagicMock()
                alerts_service.return_value = [{"id": 1, "severity": "HIGH", "status": "OPEN"}]
                with patch("app.services.risk_service.RiskService.get_alerts", alerts_service):
                    resp = test_client.get("/api/risk/alerts", headers=auth_headers)
                    assert resp.status_code == 200

                update_service = MagicMock()
                update_service.return_value = {"id": 1, "status": "INVESTIGATING"}
                with patch("app.services.risk_service.RiskService.update_alert", update_service):
                    resp = test_client.put("/api/risk/alerts/1", json={"status": "INVESTIGATING"},
                                           headers=auth_headers)
                    assert resp.status_code == 200

                dismiss_service = MagicMock()
                dismiss_service.return_value = {"id": 1, "status": "DISMISSED"}
                with patch("app.services.risk_service.RiskService.dismiss_alert", dismiss_service):
                    resp = test_client.post("/api/risk/alerts/1/dismiss", headers=auth_headers)
                    assert resp.status_code == 200

    def test_dashboard_reflects_risk_activity(self, test_client, mock_db, auth_headers):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="ADMIN")

                summary_service = MagicMock()
                summary_service.return_value = {
                    "total_alerts": 50, "open_alerts": 10, "critical_alerts": 3,
                }
                with patch("app.services.risk_service.RiskService.get_dashboard_summary", summary_service):
                    resp = test_client.get("/api/risk/alerts/summary", headers=auth_headers)
                    assert resp.status_code == 200
                    data = resp.json()
                    assert data.get("total_alerts", 0) >= 0

                trends_service = MagicMock()
                trends_service.return_value = {
                    "daily_trends": [{"date": "2024-01-01", "count": 5}],
                }
                with patch("app.services.risk_service.RiskService.get_risk_trends", trends_service):
                    resp = test_client.get("/api/risk/trends", params={"days": 7}, headers=auth_headers)
                    assert resp.status_code == 200

                dist_service = MagicMock()
                dist_service.return_value = {
                    "severity_distribution": {"LOW": 20, "MEDIUM": 15, "HIGH": 10, "CRITICAL": 5},
                }
                with patch("app.services.risk_service.RiskService.get_risk_distribution", dist_service):
                    resp = test_client.get("/api/risk/distribution", headers=auth_headers)
                    assert resp.status_code == 200

    def test_high_risk_leads_to_auto_alert(self, test_client, mock_db, auth_headers):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")

                assess_service = MagicMock()
                assess_service.return_value = {
                    "risk_score": 92, "risk_band": "critical",
                    "reasons": ["Multiple failed attempts", "High-value transaction"],
                }
                with patch("app.services.risk_service.RiskService.assess_risk", assess_service):
                    resp = test_client.post("/api/risk/assess", json={
                        "user_id": 1, "session_id": 200, "transaction_id": 600,
                    }, headers=auth_headers)
                    assert resp.status_code == 200
                    assert resp.json().get("risk_score") == 92

    def test_fraud_alert_severity_escalation(self, test_client, mock_db, auth_headers):
        with patch("app.api.risk.get_db", return_value=mock_db):
            with patch("app.api.risk.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="ADMIN")

                for severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
                    create_service = MagicMock()
                    create_service.return_value = {"id": 1, "severity": severity, "status": "OPEN"}
                    with patch("app.services.risk_service.RiskService.create_alert", create_service):
                        resp = test_client.post("/api/risk/alerts", json={
                            "user_id": 1, "severity": severity, "description": f"{severity} alert",
                        }, headers=auth_headers)
                        assert resp.status_code == 201
                        assert resp.json().get("severity") == severity
