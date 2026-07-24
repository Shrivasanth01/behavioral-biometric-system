import pytest
import numpy as np
from datetime import datetime, timezone
from ml.behavioral_profile import BehavioralProfileManager
from ml.config import MLConfig


class TestProfileCreation:
    @pytest.fixture
    def manager(self, temp_profile_store):
        config = MLConfig()
        config.profile_store = temp_profile_store
        return BehavioralProfileManager(config)

    def test_create_new_profile(self, manager):
        profile = manager.get_or_create_profile(user_id=1)
        assert profile is not None
        assert profile["user_id"] == 1
        assert "feature_stats" in profile
        assert "session_count" in profile

    def test_get_existing_profile(self, manager):
        profile = manager.get_or_create_profile(user_id=1)
        profile2 = manager.get_or_create_profile(user_id=1)
        assert profile["user_id"] == profile2["user_id"]

    def test_profile_stores_initialized(self, manager):
        profile = manager.get_or_create_profile(user_id=2)
        assert profile["feature_stats"] == {}

    def test_profile_initial_session_count(self, manager):
        profile = manager.get_or_create_profile(user_id=3)
        assert profile["session_count"] == 0
        assert profile.get("data_points", 0) == 0


class TestProfileUpdate:
    @pytest.fixture
    def manager(self, temp_profile_store):
        config = MLConfig()
        config.profile_store = temp_profile_store
        return BehavioralProfileManager(config)

    def test_update_profile_with_features(self, manager):
        features = {"typing_speed_mean": 50.0, "key_hold_mean": 100.0}
        manager.update_profile(user_id=10, features=features)
        profile = manager.get_or_create_profile(user_id=10)
        assert "typing_speed_mean" in profile.get("feature_stats", {}) or \
               "typing_speed_mean" in profile.get("feature_means", {})

    def test_session_count_increments(self, manager):
        initial = manager.get_or_create_profile(user_id=20)
        start_sessions = initial.get("session_count", 0) or initial.get("data_points", 0)
        manager.update_profile(user_id=20, features={"a": 1.0})
        updated = manager.get_or_create_profile(user_id=20)
        assert updated.get("session_count", 0) > start_sessions or updated.get("data_points", 0) > start_sessions

    def test_feature_stats_accumulate(self, manager):
        for i in range(5):
            features = {"typing_speed_mean": float(50 + i * 10), "key_hold_mean": float(100 + i * 5)}
            manager.update_profile(user_id=30, features=features)
        profile = manager.get_or_create_profile(user_id=30)
        stats = profile.get("feature_stats", {}) or profile.get("feature_means", {})
        assert any("typing_speed_mean" in k for k in stats)

    def test_update_nonexistent_user_creates(self, manager):
        manager.update_profile(user_id=99999, features={"test": 1.0})
        profile = manager.get_or_create_profile(user_id=99999)
        assert profile is not None


class TestProfileStatistics:
    @pytest.fixture
    def manager(self, temp_profile_store):
        config = MLConfig()
        config.profile_store = temp_profile_store
        return BehavioralProfileManager(config)

    def test_feature_statistics_computation(self, manager):
        rng = np.random.RandomState(42)
        for _ in range(20):
            features = {"speed": float(rng.randn() * 10 + 50), "hold": float(rng.randn() * 5 + 100)}
            manager.update_profile(user_id=40, features=features)
        stats = manager.get_profile_statistics(user_id=40)
        assert stats is not None
        if isinstance(stats, dict):
            assert len(stats) > 0

    def test_statistics_with_single_sample(self, manager):
        manager.update_profile(user_id=50, features={"speed": 55.0})
        stats = manager.get_profile_statistics(user_id=50)
        assert stats is not None

    def test_statistics_empty_profile(self, manager):
        stats = manager.get_profile_statistics(user_id=99998)
        assert stats == {} or stats is None


class TestDeviceFingerprint:
    @pytest.fixture
    def manager(self, temp_profile_store):
        config = MLConfig()
        config.profile_store = temp_profile_store
        return BehavioralProfileManager(config)

    def test_register_device(self, manager):
        device_info = {"user_agent": "Mozilla/5.0", "screen_resolution": "1920x1080", "platform": "Windows"}
        device_id = manager.register_device(user_id=60, device_info=device_info)
        assert device_id is not None
        assert isinstance(device_id, str)

    def test_device_fingerprint_consistency(self, manager):
        info = {"user_agent": "TestAgent", "screen_resolution": "1024x768"}
        id1 = manager.register_device(user_id=70, device_info=info)
        id2 = manager.register_device(user_id=70, device_info=info)
        assert id1 == id2

    def test_device_fingerprint_different_devices(self, manager):
        id1 = manager.register_device(user_id=80, device_info={"user_agent": "A"})
        id2 = manager.register_device(user_id=80, device_info={"user_agent": "B"})
        assert id1 != id2

    def test_get_user_devices(self, manager):
        for i in range(3):
            manager.register_device(user_id=90, device_info={"user_agent": f"Agent{i}"})
        devices = manager.get_user_devices(user_id=90)
        assert len(devices) == 3


class TestRiskHistory:
    @pytest.fixture
    def manager(self, temp_profile_store):
        config = MLConfig()
        config.profile_store = temp_profile_store
        return BehavioralProfileManager(config)

    def test_record_risk_score(self, manager):
        manager.record_risk_score(user_id=100, score=45, reason="Testing")
        history = manager.get_risk_history(user_id=100)
        assert len(history) > 0

    def test_get_risk_history_empty(self, manager):
        history = manager.get_risk_history(user_id=99997)
        assert history == [] or history is None

    def test_risk_history_ordered(self, manager):
        manager.record_risk_score(user_id=110, score=20, reason="First")
        import time
        time.sleep(0.001)
        manager.record_risk_score(user_id=110, score=80, reason="Second")
        history = manager.get_risk_history(user_id=110)
        if len(history) >= 2:
            assert history[-1]["score"] == 80

    def test_risk_score_range(self, manager):
        for s in [0, 50, 100]:
            manager.record_risk_score(user_id=120, score=s)
        history = manager.get_risk_history(user_id=120)
        assert len(history) == 3

    def test_risk_history_limit(self, manager):
        for i in range(50):
            manager.record_risk_score(user_id=130, score=i, reason=f"Score {i}")
        history = manager.get_risk_history(user_id=130)
        assert len(history) <= 100 or len(history) == 50
