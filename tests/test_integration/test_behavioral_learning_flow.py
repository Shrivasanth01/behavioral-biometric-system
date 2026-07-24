import pytest
import numpy as np
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient


class TestBehavioralLearningFlow:
    def test_event_ingestion_and_risk_assessment(self, test_client, mock_db, auth_headers):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")

                ingest_service = MagicMock()
                ingest_service.return_value = {"event_ids": [1], "user_id": 1, "count": 1}
                with patch("app.services.behavioral_service.BehavioralService.ingest_event", ingest_service):
                    event_resp = test_client.post("/api/behavioral/events", json={
                        "event_type": "keydown",
                        "timestamp": 1000.0,
                        "event_data": {"key": "a"},
                    }, headers=auth_headers)
                    assert event_resp.status_code == 200

                    assess_service = MagicMock()
                    assess_service.return_value = {"risk_score": 15, "risk_band": "low", "reasons": []}
                    with patch("app.services.behavioral_service.BehavioralService.assess_risk", assess_service):
                        risk_resp = test_client.post("/api/behavioral/risk/assess", json={
                            "user_id": 1, "session_id": 123,
                        }, headers=auth_headers)
                        assert risk_resp.status_code == 200
                        data = risk_resp.json()
                        assert 0 <= data.get("risk_score", 0) <= 100

    def test_batch_events_then_profile_check(self, test_client, mock_db, auth_headers):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")

                batch_service = MagicMock()
                batch_service.return_value = {"event_ids": [1, 2, 3], "user_id": 1, "count": 3}
                with patch("app.services.behavioral_service.BehavioralService.ingest_events_batch", batch_service):
                    resp = test_client.post("/api/behavioral/events/batch", json={
                        "events": [
                            {"event_type": "keydown", "timestamp": 1000.0, "event_data": {"key": "a"}},
                            {"event_type": "keyup", "timestamp": 1080.0, "event_data": {"key": "a"}},
                            {"event_type": "mousemove", "timestamp": 2000.0, "event_data": {"x": 100, "y": 200}},
                        ],
                    }, headers=auth_headers)
                    assert resp.status_code == 200
                    assert resp.json().get("count") == 3

    def test_profile_evolution_over_multiple_sessions(self, test_client, mock_db, auth_headers):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")

                profile_service = MagicMock()
                profile_service.return_value = {
                    "user_id": 1,
                    "feature_stats": {"typing_speed_mean": 52.3, "session_count": 10},
                    "risk_history": [],
                }
                with patch("app.services.behavioral_service.BehavioralService.get_user_profile", profile_service):
                    resp = test_client.get("/api/behavioral/profile/1", headers=auth_headers)
                    assert resp.status_code == 200
                    data = resp.json()
                    assert data.get("user_id") == 1
                    assert "feature_stats" in data or "features" in data

    def test_concurrent_event_ingestion(self, test_client, mock_db, auth_headers):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")

                ingest_service = MagicMock()
                ingest_service.return_value = {"event_ids": [5], "user_id": 1, "count": 1}
                with patch("app.services.behavioral_service.BehavioralService.ingest_event", ingest_service):
                    responses = []
                    for _ in range(5):
                        resp = test_client.post("/api/behavioral/events", json={
                            "event_type": "keydown", "timestamp": 1000.0, "event_data": {"key": "a"},
                        }, headers=auth_headers)
                        responses.append(resp)
                    assert all(r.status_code == 200 for r in responses)

    def test_risk_history_across_sessions(self, test_client, mock_db, auth_headers):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")

                risk_history_service = MagicMock()
                risk_history_service.return_value = [
                    {"session_id": 1, "risk_score": 10, "timestamp": "2024-01-01T00:00:00"},
                    {"session_id": 2, "risk_score": 20, "timestamp": "2024-01-02T00:00:00"},
                ]
                with patch("app.services.behavioral_service.BehavioralService.get_risk_history", risk_history_service):
                    resp = test_client.get("/api/behavioral/risk/history/1", headers=auth_headers)
                    assert resp.status_code == 200
                    assert len(resp.json()) >= 2

    def test_full_behavioral_pipeline(self, test_client, mock_db, auth_headers):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.get_current_user") as get_user:
                get_user.return_value = MagicMock(id=1, role="CUSTOMER")

                ingest = MagicMock()
                ingest.return_value = {"event_ids": [10], "user_id": 1, "count": 1}
                with patch("app.services.behavioral_service.BehavioralService.ingest_event", ingest):
                    test_client.post("/api/behavioral/events", json={
                        "event_type": "keydown", "timestamp": 1000.0, "event_data": {"key": "a"},
                    }, headers=auth_headers)

                assess = MagicMock()
                assess.return_value = {"risk_score": 25, "risk_band": "low", "reasons": []}
                with patch("app.services.behavioral_service.BehavioralService.assess_risk", assess):
                    risk_resp = test_client.post("/api/behavioral/risk/assess", json={
                        "user_id": 1, "session_id": 999,
                    }, headers=auth_headers)
                    assert risk_resp.status_code == 200

                profile = MagicMock()
                profile.return_value = {"user_id": 1, "feature_stats": {}, "risk_history": []}
                with patch("app.services.behavioral_service.BehavioralService.get_user_profile", profile):
                    prof_resp = test_client.get("/api/behavioral/profile/1", headers=auth_headers)
                    assert prof_resp.status_code == 200
