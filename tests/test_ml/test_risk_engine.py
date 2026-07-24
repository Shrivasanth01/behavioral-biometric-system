import pytest
import numpy as np
from ml.risk_engine import HybridRiskEngine
from ml.config import MLConfig


class TestHybridRiskEngine:
    @pytest.fixture
    def engine(self):
        return HybridRiskEngine()

    def test_ml_scoring(self, engine):
        features = {"typing_speed_mean": 50, "key_hold_mean": 100, "cursor_velocity_mean": 200}
        features.update({k: 0.0 for k in [
            "typing_speed_std", "key_hold_std", "backspace_rate", "key_press_freq_entropy",
            "special_key_ratio", "trigram_latency_mean", "error_correction_rate",
            "cursor_velocity_std", "cursor_accel_mean", "path_length", "direction_entropy",
            "click_frequency", "double_click_rate", "idle_time_ratio",
        ]})
        score = engine._ml_scoring(features)
        assert 0 <= score <= 100

    def test_rules_scoring(self, engine):
        score = engine._rules_scoring(night_hours=True, new_device=True, vpn_active=True)
        assert 0 <= score <= 100
        assert score > 0

    def test_rules_scoring_normal(self, engine):
        score = engine._rules_scoring(night_hours=False, new_device=False, vpn_active=False)
        assert score == 0

    def test_heuristic_scoring(self, engine):
        score = engine._heuristic_scoring(amount=50000, transaction_count_24h=15)
        assert 0 <= score <= 100
        assert score > 0

    def test_heuristic_scoring_low(self, engine):
        score = engine._heuristic_scoring(amount=100, transaction_count_24h=1)
        assert score < 30

    def test_evaluate_minimal(self, engine):
        features = {"typing_speed_mean": 50, "key_hold_mean": 100, "cursor_velocity_mean": 200}
        features.update({k: 0.0 for k in [
            "typing_speed_std", "key_hold_std", "backspace_rate", "key_press_freq_entropy",
            "special_key_ratio", "trigram_latency_mean", "error_correction_rate",
            "cursor_velocity_std", "cursor_accel_mean", "path_length", "direction_entropy",
            "click_frequency", "double_click_rate", "idle_time_ratio",
        ]})
        result = engine.evaluate(features, night_hours=False, new_device=False, vpn_active=False, amount=100, transaction_count_24h=1)
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100

    def test_evaluate_full(self, engine):
        features = {"typing_speed_mean": 50, "key_hold_mean": 100, "typing_speed_std": 10,
                    "key_hold_std": 20, "cursor_velocity_mean": 200, "cursor_velocity_std": 30,
                    "cursor_accel_mean": 5, "path_length": 500, "direction_entropy": 3.5,
                    "click_frequency": 2, "double_click_rate": 0.1, "idle_time_ratio": 0.2,
                    "backspace_rate": 0.05, "key_press_freq_entropy": 4.0,
                    "special_key_ratio": 0.1, "trigram_latency_mean": 200,
                    "error_correction_rate": 0.03, "session_duration": 300, "total_interactions": 50,
                    "interaction_density": 0.1, "time_of_day": 0.5, "day_of_week": 0.3,
                    "navigation_depth": 5,
                }
        result = engine.evaluate(features, night_hours=True, new_device=True, vpn_active=True,
                                  amount=50000, transaction_count_24h=20)
        assert 0 <= result["overall_score"] <= 100
        assert "ml_score" in result
        assert "rules_score" in result
        assert "heuristic_score" in result

    def test_score_components_weighted(self, engine):
        features = {"typing_speed_mean": 50, "key_hold_mean": 100, "cursor_velocity_mean": 200}
        features.update({k: 0.0 for k in [
            "typing_speed_std", "key_hold_std", "backspace_rate", "key_press_freq_entropy",
            "special_key_ratio", "trigram_latency_mean", "error_correction_rate",
            "cursor_velocity_std", "cursor_accel_mean", "path_length", "direction_entropy",
            "click_frequency", "double_click_rate", "idle_time_ratio",
        ]})
        result = engine.evaluate(features, night_hours=False, new_device=False, vpn_active=False, amount=100, transaction_count_24h=1)
        ml = result["ml_score"]
        rules = result["rules_score"]
        heur = result["heuristic_score"]
        expected = ml * 0.5 + rules * 0.2 + heur * 0.3
        assert result["overall_score"] == pytest.approx(expected, abs=1)

    def test_score_upper_bound(self, engine):
        features = {k: 999999 for k in [
            "typing_speed_mean", "key_hold_mean", "cursor_velocity_mean",
            "typing_speed_std", "key_hold_std", "backspace_rate", "key_press_freq_entropy",
            "special_key_ratio", "trigram_latency_mean", "error_correction_rate",
            "cursor_velocity_std", "cursor_accel_mean", "path_length", "direction_entropy",
            "click_frequency", "double_click_rate", "idle_time_ratio",
            "session_duration", "total_interactions", "interaction_density",
            "time_of_day", "day_of_week", "navigation_depth",
        ]}
        result = engine.evaluate(features, night_hours=True, new_device=True, vpn_active=True,
                                  amount=1e7, transaction_count_24h=1000)
        assert result["overall_score"] <= 100

    def test_score_lower_bound(self, engine):
        features = {k: 0 for k in [
            "typing_speed_mean", "key_hold_mean", "cursor_velocity_mean",
            "typing_speed_std", "key_hold_std", "backspace_rate", "key_press_freq_entropy",
            "special_key_ratio", "trigram_latency_mean", "error_correction_rate",
            "cursor_velocity_std", "cursor_accel_mean", "path_length", "direction_entropy",
            "click_frequency", "double_click_rate", "idle_time_ratio",
            "session_duration", "total_interactions", "interaction_density",
            "time_of_day", "day_of_week", "navigation_depth",
        ]}
        result = engine.evaluate(features, night_hours=False, new_device=False, vpn_active=False,
                                  amount=1, transaction_count_24h=1)
        assert result["overall_score"] >= 0

    def test_risk_band_mapping(self, engine):
        low = engine._map_risk_band(15)
        medium = engine._map_risk_band(40)
        high = engine._map_risk_band(65)
        critical = engine._map_risk_band(85)
        assert low == "low"
        assert medium == "medium"
        assert high == "high"
        assert critical == "critical"

    def test_ml_score_ge_zero(self, engine):
        features = {"typing_speed_mean": 50, "key_hold_mean": 100, "cursor_velocity_mean": 200}
        features.update({k: 0.0 for k in [
            "typing_speed_std", "key_hold_std", "backspace_rate", "key_press_freq_entropy",
            "special_key_ratio", "trigram_latency_mean", "error_correction_rate",
            "cursor_velocity_std", "cursor_accel_mean", "path_length", "direction_entropy",
            "click_frequency", "double_click_rate", "idle_time_ratio",
        ]})
        score = engine._ml_scoring(features)
        assert score >= 0

    def test_empty_features_all_zeros(self, engine):
        features = {k: 0.0 for k in [
            "typing_speed_mean", "key_hold_mean", "cursor_velocity_mean",
            "typing_speed_std", "key_hold_std", "backspace_rate", "key_press_freq_entropy",
            "special_key_ratio", "trigram_latency_mean", "error_correction_rate",
            "cursor_velocity_std", "cursor_accel_mean", "path_length", "direction_entropy",
            "click_frequency", "double_click_rate", "idle_time_ratio",
        ]}
        result = engine.evaluate(features, night_hours=False, new_device=False, vpn_active=False,
                                  amount=0, transaction_count_24h=0)
        assert result["overall_score"] == 0
