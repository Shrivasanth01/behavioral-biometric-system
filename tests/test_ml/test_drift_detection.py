import pytest
import numpy as np
from ml.drift_detection import DriftDetector
from ml.config import MLConfig


class TestDriftDetector:
    @pytest.fixture
    def detector(self):
        config = MLConfig()
        config.drift_threshold_psi = 0.25
        config.drift_threshold_feature = 0.30
        config.drift_threshold_accuracy = 0.15
        return DriftDetector(config)

    def test_psi_calculation_homogeneous(self, detector):
        reference = np.random.randn(1000, 10)
        current = np.random.randn(1000, 10)
        methods = ["psi", "kl_div", "ks_stat"]
        for method in methods:
            psi = detector._calculate_psi(reference, current, bins=10, method=method)
            assert isinstance(psi, float)
            assert 0 <= psi <= 1

    def test_psi_calculation_different(self, detector):
        reference = np.random.randn(1000, 10)
        current = np.random.randn(1000, 10) + 3.0
        psi = detector._calculate_psi(reference, current)
        assert psi > 0

    def test_feature_drift_detection(self, detector):
        reference = {"typingspeed": np.random.randn(500)}
        current = {"typingspeed": np.random.randn(500) + 2.0}
        drift_result = detector.detect_feature_drift(reference, current)
        assert "typingspeed" in drift_result
        assert drift_result["typingspeed"]["drifted"]

    def test_no_drift(self, detector):
        reference = {"typingspeed": np.random.randn(500)}
        current = {"typingspeed": np.random.randn(500) * 0.5}
        drift_result = detector.detect_feature_drift(reference, current)
        assert "typingspeed" in drift_result
        assert not drift_result["typingspeed"].get("drifted", False) or drift_result["typingspeed"].get("psi", 1) < detector.config.drift_threshold_psi

    def test_accuracy_degradation_not_drifted(self, detector):
        accuracy = 0.95
        baseline = 0.97
        result = detector.detect_accuracy_degradation(accuracy, baseline, metric="accuracy")
        assert result is not None
        assert not result["drifted"]

    def test_accuracy_degradation_drifted(self, detector):
        accuracy = 0.60
        baseline = 0.95
        result = detector.detect_accuracy_degradation(accuracy, baseline, metric="accuracy")
        assert result["drifted"]

    def test_alert_generation(self, detector):
        drift_results = {"feature_1": {"drifted": True, "psi": 0.45, "direction": "increase"},
                         "feature_2": {"drifted": False, "psi": 0.05, "direction": "stable"}}
        alerts = detector.generate_alerts(drift_results)
        assert len(alerts) >= 1

    def test_no_alert_on_stable(self, detector):
        drift_results = {"feature_1": {"drifted": False, "psi": 0.01}}
        alerts = detector.generate_alerts(drift_results)
        assert len(alerts) == 0

    def test_drift_triggers_retraining(self, detector):
        drift_results = {"feature_1": {"drifted": True, "psi": 0.45, "direction": "increase"},
                         "feature_2": {"drifted": True, "psi": 0.35, "direction": "decrease"}}
        should_retrain = detector.should_retrain(drift_results)
        assert should_retrain

    def test_no_retrain_without_drift(self, detector):
        drift_results = {"feature_1": {"drifted": False, "psi": 0.01}}
        should_retrain = detector.should_retrain(drift_results)
        assert not should_retrain

    def test_psi_upper_bound(self, detector):
        huge = np.random.randn(1000, 10) * 100
        tiny = np.random.randn(1000, 10) * 0.01
        psi = detector._calculate_psi(huge, tiny)
        assert psi <= 1.0

    def test_psi_same_distribution(self, detector):
        ref = np.random.randn(10000)
        cur = np.random.randn(10000)
        psi = detector._calculate_psi(ref.reshape(-1, 1), cur.reshape(-1, 1))
        assert psi < 0.1

    def test_multiple_features_drift(self, detector):
        n = 50
        reference = {f"feat_{i}": np.random.randn(1000) for i in range(n)}
        current = {f"feat_{i}": np.random.randn(1000) + (2.0 if i % 2 == 0 else 0.0) for i in range(n)}
        drift_result = detector.detect_feature_drift(reference, current)
        drifted_count = sum(1 for v in drift_result.values() if v["drifted"])
        expected_drifted = n // 2
        assert abs(drifted_count - expected_drifted) <= 10


class TestDriftDetectorEdgeCases:
    @pytest.fixture
    def detector(self):
        return DriftDetector(MLConfig())

    def test_empty_distributions(self, detector):
        with pytest.raises((ValueError, TypeError)):
            detector._calculate_psi(np.array([]), np.array([1, 2, 3]))

    def test_single_value_distributions(self, detector):
        ref = np.ones((100, 1))
        cur = np.ones((100, 1))
        psi = detector._calculate_psi(ref, cur)
        assert 0 <= psi <= 1

    def test_nan_in_distribution(self, detector):
        ref = np.random.randn(100, 5)
        cur = np.random.randn(100, 5)
        cur[0, 0] = float('nan')
        ref[1, 1] = float('nan')
        psi = detector._calculate_psi(ref, cur)
        assert 0 <= psi <= 1

    def test_inf_in_distribution(self, detector):
        ref = np.random.randn(100, 5)
        cur = np.random.randn(100, 5)
        cur[0, 0] = float('inf')
        ref[1, 1] = float('-inf')
        psi = detector._calculate_psi(ref, cur)
        assert 0 <= psi <= 1

    def test_mismatched_bins(self, detector):
        ref = np.random.randn(500, 3)
        cur = np.random.randn(500, 3)
        psi_bins_5 = detector._calculate_psi(ref, cur, bins=5)
        psi_bins_20 = detector._calculate_psi(ref, cur, bins=20)
        assert isinstance(psi_bins_5, float)
        assert isinstance(psi_bins_20, float)
