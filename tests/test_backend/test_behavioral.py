import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from datetime import datetime, timezone


class TestBehavioralEventIngestion:
    def test_ingest_event_success(self, test_client, auth_headers, mock_db):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.optional_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.behavioral_service.BehavioralService.ingest_event") as mock_ingest:
                    mock_ingest.return_value = MagicMock(id=1)
                    response = test_client.post("/api/events", json={
                        "session_id": "session-abc-123",
                        "event_type": "keydown",
                        "event_data": {"key": "a", "timestamp": 1000},
                        "client_timestamp": "2024-01-01T00:00:00Z",
                    }, headers=auth_headers)
                    assert response.status_code == 200
                    assert response.json()["event_id"] == 1

    def test_ingest_event_without_auth(self, test_client, mock_db):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.optional_current_user") as mock_user:
                mock_user.return_value = None
                with patch("app.services.behavioral_service.BehavioralService.ingest_event") as mock_ingest:
                    mock_ingest.return_value = MagicMock(id=2)
                    response = test_client.post("/api/events", json={
                        "session_id": "session-anon-456",
                        "event_type": "mousemove",
                        "event_data": {"x": 100, "y": 200, "timestamp": 2000},
                        "user_id": 5,
                    })
                    assert response.status_code == 200
                    assert response.json()["event_id"] == 2

    def test_ingest_event_missing_session_id(self, test_client, auth_headers):
        response = test_client.post("/api/events", json={
            "event_type": "keydown",
        }, headers=auth_headers)
        assert response.status_code == 422

    def test_ingest_event_missing_event_type(self, test_client, auth_headers):
        response = test_client.post("/api/events", json={
            "session_id": "session-abc-123",
        }, headers=auth_headers)
        assert response.status_code == 422

    def test_ingest_event_batch(self, test_client, auth_headers, mock_db):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.optional_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.behavioral_service.BehavioralService.ingest_event") as mock_ingest:
                    mock_ingest.side_effect = [MagicMock(id=i) for i in range(1, 4)]
                    response = test_client.post("/api/events/batch", json={
                        "events": [
                            {"session_id": "s1", "event_type": "keydown", "event_data": {"key": "a"}},
                            {"session_id": "s1", "event_type": "keyup", "event_data": {"key": "a"}},
                            {"session_id": "s1", "event_type": "mousemove", "event_data": {"x": 100, "y": 200}},
                        ],
                    }, headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is True
                    assert data["count"] == 3
                    assert len(data["event_ids"]) == 3

    def test_ingest_event_batch_empty(self, test_client, auth_headers):
        response = test_client.post("/api/events/batch", json={
            "events": [],
        }, headers=auth_headers)
        assert response.status_code == 200

    def test_ingest_event_with_device_fingerprint(self, test_client, auth_headers, mock_db):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.optional_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.behavioral_service.BehavioralService.ingest_event") as mock_ingest:
                    mock_ingest.return_value = MagicMock(id=10)
                    response = test_client.post("/api/events", json={
                        "session_id": "session-dev-789",
                        "event_type": "click",
                        "device_type": "mouse",
                        "device_fingerprint": "fp_device_001",
                        "event_data": {"button": 0},
                    }, headers=auth_headers)
                    assert response.status_code == 200


class TestBehavioralSession:
    def test_get_session_events(self, test_client, mock_db):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.services.behavioral_service.BehavioralService.get_session_events") as mock_get:
                mock_get.return_value = [
                    MagicMock(
                        id=1, session_id="session-abc", user_id=2,
                        device_type="keyboard", device_fingerprint=None,
                        event_type="keydown", event_data={"key": "a"},
                        client_timestamp=datetime.now(timezone.utc),
                        server_timestamp=datetime.now(timezone.utc),
                        ip_address="127.0.0.1", user_agent="pytest",
                    ),
                ]
                response = test_client.get("/api/events/session/session-abc")
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["event_type"] == "keydown"

    def test_get_session_events_empty(self, test_client, mock_db):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.services.behavioral_service.BehavioralService.get_session_events") as mock_get:
                mock_get.return_value = []
                response = test_client.get("/api/events/session/nonexistent")
                assert response.status_code == 200
                assert response.json() == []


class TestBehavioralProfile:
    def test_get_profile(self, test_client, auth_headers, mock_db):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.behavioral_service.BehavioralService.get_user_profile") as mock_get:
                    mock_get.return_value = MagicMock(
                        id=1, user_id=2,
                        profile={"typing_speed_avg": 5.0, "session_count": 10},
                        model_version="1.0.0", session_count=10,
                        last_trained_at=datetime.now(timezone.utc),
                        drift_status="normal",
                    )
                    response = test_client.get("/api/events/profile/2", headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["user_id"] == 2
                    assert data["session_count"] == 10

    def test_get_profile_other_user(self, test_client, auth_headers, mock_db):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.behavioral_service.BehavioralService.get_user_profile") as mock_get:
                    mock_get.return_value = MagicMock(
                        id=1, user_id=3, profile={}, model_version="1.0.0",
                        session_count=5, last_trained_at=None, drift_status="normal",
                    )
                    response = test_client.get("/api/events/profile/3", headers=auth_headers)
                    assert response.status_code == 200

    def test_get_risk_history(self, test_client, auth_headers, mock_db):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.behavioral_service.BehavioralService.get_risk_history") as mock_get:
                    mock_get.return_value = [
                        {"date": "2024-01-01", "risk_score": 25.0, "risk_band": "LOW",
                         "transaction_count": 5, "alert_count": 0},
                        {"date": "2024-01-02", "risk_score": 45.0, "risk_band": "MEDIUM",
                         "transaction_count": 3, "alert_count": 1},
                    ]
                    response = test_client.get("/api/events/profile/2/risk-history", headers=auth_headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data) == 2

    def test_get_risk_history_with_days_param(self, test_client, auth_headers, mock_db):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.behavioral_service.BehavioralService.get_risk_history") as mock_get:
                    mock_get.return_value = []
                    response = test_client.get("/api/events/profile/2/risk-history?days=7", headers=auth_headers)
                    assert response.status_code == 200

    def test_get_user_sessions(self, test_client, auth_headers, mock_db):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.get_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.behavioral_service.BehavioralService.get_user_sessions") as mock_get:
                    mock_get.return_value = [
                        {"session_id": "s1", "device_type": "desktop", "ip_address": "127.0.0.1",
                         "event_count": 15, "first_event": datetime.now(timezone.utc),
                         "last_event": datetime.now(timezone.utc), "risk_score": 20.0},
                    ]
                    response = test_client.get("/api/events/profile/2/sessions", headers=auth_headers)
                    assert response.status_code == 200


class TestBehavioralConcurrency:
    def test_concurrent_event_submission(self, test_client, auth_headers, mock_db):
        with patch("app.api.behavioral.get_db", return_value=mock_db):
            with patch("app.api.behavioral.optional_current_user") as mock_user:
                mock_user.return_value = MagicMock(id=2)
                with patch("app.services.behavioral_service.BehavioralService.ingest_event") as mock_ingest:
                    mock_ingest.side_effect = [MagicMock(id=i) for i in range(1, 6)]
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                        futures = []
                        for i in range(5):
                            futures.append(executor.submit(
                                test_client.post, "/api/events",
                                json={"session_id": f"concurrent-{i}", "event_type": "keydown"},
                                headers=auth_headers,
                            ))
                        results = [f.result() for f in futures]
                    assert all(r.status_code == 200 for r in results)
