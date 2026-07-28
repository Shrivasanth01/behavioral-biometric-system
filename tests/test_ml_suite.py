import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import json
import tempfile
import unittest
from datetime import datetime
from ml.config import MLConfig, FeatureConfig
from ml.feature_engineering import FeatureEngine
from ml.utils import (
    normalize_feature, compute_entropy, compute_psi,
    device_fingerprint, robust_normalize, safe_divide,
    validate_events, compute_cosine_similarity,
)
from ml.models.user_model import UserModel
from ml.models.global_model import GlobalModel
from ml.training_pipeline import TrainingPipeline
from ml.inference_pipeline import InferencePipeline
from ml.drift_detection import DriftDetector
from ml.risk_engine import HybridRiskEngine
from ml.explainability import Explainer
from ml.behavioral_profile import BehavioralProfile, BehavioralProfileManager
from ml.model_registry import ModelRegistry
from ml.evaluation import Evaluator


class TestUtils(unittest.TestCase):
    def test_normalize_feature(self):
        self.assertAlmostEqual(normalize_feature(10, 5, 2), 2.5)
        self.assertAlmostEqual(normalize_feature(5, 5, 0), 0.0)
        self.assertAlmostEqual(normalize_feature(0, 0, 0), 0.0)

    def test_compute_entropy(self):
        self.assertAlmostEqual(compute_entropy(np.array([1, 1, 1, 1])), np.log(4), places=5)
        self.assertEqual(compute_entropy(np.array([0, 0])), 0.0)
        self.assertEqual(compute_entropy(np.array([])), 0.0)

    def test_compute_psi(self):
        ref = np.random.randn(100)
        actual = np.random.randn(100)
        psi = compute_psi(ref, actual)
        self.assertGreaterEqual(psi, 0)
        self.assertAlmostEqual(compute_psi(ref, ref), 0.0, places=2)

    def test_device_fingerprint(self):
        fp1 = device_fingerprint({"browser": "chrome", "os": "windows"})
        fp2 = device_fingerprint({"browser": "chrome", "os": "windows"})
        fp3 = device_fingerprint({"browser": "firefox", "os": "windows"})
        self.assertEqual(fp1, fp2)
        self.assertNotEqual(fp1, fp3)
        self.assertEqual(len(fp1), 64)

    def test_robust_normalize(self):
        arr = np.array([1, 2, 3, 4, 100])
        normalized = robust_normalize(arr, method="robust")
        self.assertEqual(len(normalized), 5)
        self.assertTrue(np.all(np.isfinite(normalized)))
        empty = robust_normalize(np.array([]))
        self.assertEqual(len(empty), 0)

    def test_safe_divide(self):
        self.assertAlmostEqual(safe_divide(10, 2), 5.0)
        self.assertAlmostEqual(safe_divide(10, 0), 0.0)
        self.assertAlmostEqual(safe_divide(10, 0, default=-1), -1.0)

    def test_validate_events(self):
        self.assertTrue(validate_events([{"type": "keydown", "timestamp": 100}]))
        self.assertFalse(validate_events([]))
        self.assertFalse(validate_events([{"type": "keydown"}]))
        self.assertFalse(validate_events("not_a_list"))

    def test_compute_cosine_similarity(self):
        self.assertAlmostEqual(compute_cosine_similarity(np.array([1, 0]), np.array([1, 0])), 1.0)
        self.assertAlmostEqual(compute_cosine_similarity(np.array([1, 0]), np.array([0, 1])), 0.0)
        self.assertAlmostEqual(compute_cosine_similarity(np.array([1, 0]), np.array([-1, 0])), -1.0)
        self.assertEqual(compute_cosine_similarity(np.array([0, 0]), np.array([1, 0])), 0.0)


class TestFeatureEngineering(unittest.TestCase):
    def setUp(self):
        self.engine = FeatureEngine()

    def _make_keystroke_events(self, n=20):
        events = []
        t = 1000.0
        for i in range(n):
            events.append({"type": "keydown", "timestamp": t, "key": chr(97 + (i % 26))})
            t += 50 + np.random.randint(-10, 10)
            events.append({"type": "keyup", "timestamp": t + 80, "key": chr(97 + (i % 26))})
            t += 100
        events.append({"type": "keydown", "timestamp": t, "key": "Backspace"})
        return events

    def _make_mouse_events(self, n=30):
        events = []
        t = 2000.0
        x, y = 100.0, 100.0
        for i in range(n):
            events.append({"type": "mousemove", "timestamp": t, "x": x, "y": y})
            x += np.random.randint(-20, 20)
            y += np.random.randint(-20, 20)
            t += 16.0 + np.random.random() * 10
        events.append({"type": "mousedown", "timestamp": t, "button": 0})
        events.append({"type": "mouseup", "timestamp": t + 50, "button": 0})
        return events

    def test_extract_empty_events(self):
        features = self.engine.extract_all([])
        for k in self.engine.feature_config.all_features:
            self.assertIn(k, features)
            self.assertEqual(features[k], 0.0)

    def test_extract_keystroke_features(self):
        events = self._make_keystroke_events()
        features = self.engine.extract_all(events)
        self.assertGreater(features["typing_speed_mean"], 0)
        self.assertGreaterEqual(features["typing_speed_std"], 0)
        self.assertGreater(features["key_press_freq_entropy"], 0)
        self.assertGreater(features["backspace_rate"], 0)

    def test_extract_mouse_features(self):
        events = self._make_mouse_events()
        features = self.engine.extract_all(events)
        self.assertGreaterEqual(features["cursor_velocity_mean"], 0)
        self.assertGreaterEqual(features["path_length"], 0)
        self.assertGreater(features["click_frequency"], 0)

    def test_extract_session_features(self):
        events = self._make_keystroke_events() + self._make_mouse_events()
        features = self.engine.extract_all(events)
        self.assertGreater(features["session_duration"], 0)
        self.assertGreater(features["total_interactions"], 0)
        self.assertGreater(features["interaction_density"], 0)
        self.assertGreaterEqual(features["time_of_day"], 0)
        self.assertGreaterEqual(features["day_of_week"], 0)

    def test_extract_mobile_features(self):
        events = []
        t = 1000.0
        for i in range(10):
            events.append({"type": "touchstart", "timestamp": t, "x": 100 + i * 10, "y": 200, "touch_id": 0, "pressure": 0.5})
            events.append({"type": "touchmove", "timestamp": t + 50, "x": 100 + i * 10 + 20, "y": 200 + 10, "touch_id": 0, "pressure": 0.6})
            events.append({"type": "touchend", "timestamp": t + 100, "touch_id": 0})
            t += 200
        features = self.engine.extract_all(events, include_mobile=True)
        self.assertGreaterEqual(features["swipe_velocity_mean"], 0)
        self.assertGreater(features["touch_pressure_mean"], 0)

    def test_extract_batch(self):
        batches = [self._make_keystroke_events(), self._make_mouse_events()]
        df = self.engine.extract_batch(batches)
        self.assertEqual(len(df), 2)
        self.assertGreater(len(df.columns), 20)


class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.config = MLConfig()
        self.config.model_storage_path = tempfile.mkdtemp()
        self.model = UserModel("test_user", self.config)

    def _make_features(self, n=50):
        rng = np.random.RandomState(42)
        return rng.randn(n, 36)

    def test_train_and_predict(self):
        features = self._make_features()
        result = self.model.train(features)
        self.assertIn("version", result)
        self.assertIn("threshold", result)
        self.assertGreater(result["n_samples"], 0)

        test_vec = np.random.randn(36)
        score, contributions = self.model.predict(test_vec)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertIsInstance(contributions, dict)

    def test_save_and_load(self):
        features = self._make_features()
        self.model.train(features)
        path = self.model.save()
        self.assertTrue(os.path.exists(path))

        loaded = UserModel("test_user", self.config)
        success = loaded.load()
        self.assertTrue(success)
        self.assertEqual(loaded.version, self.model.version)
        self.assertIsNotNone(loaded.model)

    def test_predict_untrained_raises(self):
        with self.assertRaises(RuntimeError):
            self.model.predict(np.random.randn(36))

    def test_train_insufficient_samples(self):
        with self.assertRaises(ValueError):
            self.model.train(np.random.randn(2, 36))

    def test_score_batch(self):
        features = self._make_features(100)
        self.model.train(features[:50])
        scores = self.model.score_batch(features[50:])
        self.assertEqual(len(scores), 50)
        self.assertTrue(np.all(scores >= 0))
        self.assertTrue(np.all(scores <= 100))


class TestGlobalModel(unittest.TestCase):
    def setUp(self):
        self.config = MLConfig()
        self.config.model_storage_path = tempfile.mkdtemp()
        self.model = GlobalModel(self.config)

    def test_train_and_predict(self):
        rng = np.random.RandomState(42)
        features = rng.randn(100, 36)
        result = self.model.train(features)
        self.assertIn("version", result)
        self.assertGreater(result["n_estimators"], 0)

        score, raw = self.model.predict(np.random.randn(36))
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_save_and_load(self):
        features = np.random.RandomState(42).randn(100, 36)
        self.model.train(features)
        self.model.save()

        loaded = GlobalModel(self.config)
        success = loaded.load()
        self.assertTrue(success)
        self.assertGreater(len(loaded.ensemble), 0)

    def test_score_batch(self):
        features = np.random.RandomState(42).randn(50, 36)
        self.model.train(features[:30])
        scores = self.model.score_batch(features[30:])
        self.assertEqual(len(scores), 20)


class TestTrainingPipeline(unittest.TestCase):
    def setUp(self):
        self.config = MLConfig()
        self.config.model_storage_path = tempfile.mkdtemp()
        self.config.profile_storage_path = tempfile.mkdtemp()
        self.config.registry_path = tempfile.mkdtemp()
        self.pipeline = TrainingPipeline(self.config)

    def _make_session_events(self):
        events = []
        t = 1000.0
        for i in range(10):
            events.append({"type": "keydown", "timestamp": t, "key": "a"})
            t += 50
            events.append({"type": "keyup", "timestamp": t + 80, "key": "a"})
            t += 50
            events.append({"type": "mousemove", "timestamp": t, "x": float(i * 10), "y": float(i * 5)})
            t += 16
        return events

    def test_cold_start_global(self):
        batches = [self._make_session_events() for _ in range(10)]
        self.pipeline.ensure_global_model(batches)
        score = self.pipeline.get_fallback_score(self._make_session_events())
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_train_for_user(self):
        batches = [self._make_session_events() for _ in range(8)]
        result = self.pipeline.train_for_user("test_user", batches)
        self.assertEqual(result["trained"], True)
        self.assertIsNotNone(result["version"])

    def test_train_for_user_high_risk_skipped(self):
        batches = [self._make_session_events() for _ in range(6)]
        risk_scores = [80.0] * 6
        result = self.pipeline.train_for_user("test_user", batches, risk_scores)
        self.assertEqual(result["trained"], False)

    def test_retrain_if_needed(self):
        batches = [self._make_session_events() for _ in range(5)]
        result = self.pipeline.retrain_if_needed("test_user", batches)
        self.assertIn("trained", result)


class TestInferencePipeline(unittest.TestCase):
    def setUp(self):
        self.config = MLConfig()
        self.config.model_storage_path = tempfile.mkdtemp()
        self.config.profile_storage_path = tempfile.mkdtemp()
        self.pipeline = InferencePipeline(self.config)

    def _ensure_global_model(self):
        tp = TrainingPipeline(self.config)
        sessions = [[
            {"type": "keydown", "timestamp": float(1000 + j * 100), "key": "a"},
            {"type": "keyup", "timestamp": float(1080 + j * 100), "key": "a"},
            {"type": "mousemove", "timestamp": float(1100 + j * 100), "x": float(j * 10), "y": float(j * 5)},
        ] for j in range(10)]
        tp.ensure_global_model(sessions)

    def test_score_cold_start(self):
        self._ensure_global_model()
        events = [
            {"type": "keydown", "timestamp": 1000, "key": "a"},
            {"type": "keyup", "timestamp": 1080, "key": "a"},
            {"type": "mousemove", "timestamp": 1100, "x": 100, "y": 100},
        ]
        result = self.pipeline.score("new_user", events)
        self.assertIn("ml_score", result)
        self.assertIn("feature_contributions", result)
        self.assertIn("model_source", result)
        self.assertGreaterEqual(result["ml_score"], 0)
        self.assertLessEqual(result["ml_score"], 100)

    def test_score_with_trained_model(self):
        self._ensure_global_model()
        tp = TrainingPipeline(self.config)
        sessions = [
            [{"type": "keydown", "timestamp": float(1000 + i * 200), "key": "a"},
             {"type": "keyup", "timestamp": float(1080 + i * 200), "key": "a"},
             {"type": "mousemove", "timestamp": float(1100 + i * 200), "x": float(i * 10), "y": float(i * 5)}]
            for i in range(6)
        ]
        tp.train_for_user("existing_user", sessions)
        events = sessions[0]
        result = self.pipeline.score("existing_user", events)
        self.assertIn("model_source", result)

    def test_invalidate_cache(self):
        self.pipeline.invalidate_cache()
        self.pipeline.invalidate_cache("some_user")

    def test_score_batch(self):
        batches = [
            [{"type": "keydown", "timestamp": 1000, "key": "a"}],
            [{"type": "mousemove", "timestamp": 2000, "x": 100, "y": 100}],
        ]
        results = self.pipeline.score_batch("user", batches)
        self.assertEqual(len(results), 2)


class TestDriftDetection(unittest.TestCase):
    def setUp(self):
        self.detector = DriftDetector()

    def test_set_reference_and_check(self):
        ref = np.random.randn(100)
        self.detector.set_reference("test_feat", ref)
        for v in np.random.randn(50) + 0.1:
            self.detector.add_sample("test_feat", v)
        psi, drifted = self.detector.check_feature_drift("test_feat")
        self.assertGreaterEqual(psi, 0)
        self.assertIsInstance(drifted, bool)

    def test_check_all_features(self):
        for name in ["f1", "f2", "f3"]:
            self.detector.set_reference(name, np.random.randn(100))
            for v in np.random.randn(50):
                self.detector.add_sample(name, v)
        report = self.detector.check_all_features()
        self.assertIn(report.severity, ["STABLE", "WARNING", "CRITICAL"])
        self.assertIsInstance(report.drifted_features, list)
        self.assertGreaterEqual(report.psi_value, 0)

    def test_accuracy_degradation(self):
        result = self.detector.check_accuracy_degradation(0.85, 0.90)
        self.assertIsInstance(result, bool)

    def test_user_drift_status(self):
        self.detector.set_reference("typing_speed", np.random.randn(100))
        for v in np.random.randn(30):
            self.detector.add_sample("typing_speed", v)
        current = {"typing_speed": 5.0, "mouse_speed": 100.0}
        baseline = {
            "typing_speed": {"mean": 0.0, "std": 1.0},
            "mouse_speed": {"mean": 50.0, "std": 10.0},
        }
        report = self.detector.get_user_drift_status("u1", current, baseline)
        self.assertIn(report.severity, ["STABLE", "WARNING", "DRIFTED"])

    def test_drift_trend(self):
        name = "trend_feat"
        self.detector.set_reference(name, np.random.randn(100))
        for v in np.random.randn(50):
            self.detector.add_sample(name, v)
        self.detector.check_feature_drift(name)
        trend = self.detector.get_drift_trend(name)
        self.assertIn("trend", trend)
        self.assertIn("current_psi", trend)

    def test_clear(self):
        self.detector.set_reference("f1", np.array([1, 2, 3]))
        self.detector.clear()
        self.assertEqual(len(self.detector.reference_distributions), 0)


class TestRiskEngine(unittest.TestCase):
    def setUp(self):
        self.engine = HybridRiskEngine()

    def test_low_risk(self):
        result = self.engine.evaluate(
            ml_score=10.0,
            features={
                "typing_speed_mean": 5.0,
                "cursor_velocity_mean": 100.0,
                "session_duration": 300.0,
                "total_interactions": 50,
                "backspace_rate": 0.05,
                "direction_entropy": 1.5,
                "key_press_freq_entropy": 2.0,
                "navigation_entropy": 1.0,
                "time_of_day": 0.5,
            },
            session_count=10,
        )
        self.assertEqual(result["risk_band"], "LOW")
        self.assertLessEqual(result["risk_score"], 30)

    def test_high_risk(self):
        result = self.engine.evaluate(
            ml_score=90.0,
            features={
                "typing_speed_mean": 100.0,
                "cursor_velocity_mean": 5000.0,
                "session_duration": 5.0,
                "total_interactions": 2,
                "backspace_rate": 0.0,
                "direction_entropy": 0.1,
                "key_press_freq_entropy": 0.1,
                "navigation_entropy": 0.0,
                "time_of_day": 0.05,
            },
            user_baseline={
                "typing_speed_mean": {"mean": 5.0, "std": 1.0},
                "cursor_velocity_mean": {"mean": 100.0, "std": 20.0},
                "session_duration": {"mean": 300.0, "std": 50.0},
                "navigation_entropy": {"mean": 2.0, "std": 0.5},
            },
            session_count=1,
        )
        self.assertEqual(result["risk_band"], "HIGH")
        self.assertGreaterEqual(result["risk_score"], 71)

    def test_medium_risk(self):
        result = self.engine.evaluate(
            ml_score=50.0,
            features={
                "typing_speed_mean": 5.0,
                "cursor_velocity_mean": 100.0,
                "session_duration": 300.0,
                "total_interactions": 20,
                "backspace_rate": 0.03,
                "direction_entropy": 0.8,
                "key_press_freq_entropy": 1.5,
                "navigation_entropy": 1.0,
                "time_of_day": 0.5,
            },
            session_count=5,
        )
        self.assertIn(result["risk_band"], ["LOW", "MEDIUM"])

    def test_evaluate_with_details(self):
        result = self.engine.evaluate_with_details(
            ml_score=30.0,
            features={
                "typing_speed_mean": 5.0,
                "cursor_velocity_mean": 100.0,
                "session_duration": 300.0,
                "total_interactions": 50,
                "backspace_rate": 0.05,
                "direction_entropy": 1.5,
                "key_press_freq_entropy": 2.0,
                "navigation_entropy": 1.0,
                "time_of_day": 0.5,
            },
            user_baseline={
                "typing_speed_mean": {"mean": 5.0, "std": 1.0},
                "cursor_velocity_mean": {"mean": 100.0, "std": 20.0},
            },
            session_count=10,
        )
        self.assertIn("rule_details", result)
        self.assertIn("heuristic_details", result)

    def test_decision_mapping(self):
        low = self.engine._get_decision("LOW")
        self.assertEqual(low, "ALLOW")
        med = self.engine._get_decision("MEDIUM")
        self.assertEqual(med, "REQUEST_MFA")
        high = self.engine._get_decision("HIGH")
        self.assertEqual(high, "BLOCK_AND_ALERT")


class TestExplainer(unittest.TestCase):
    def setUp(self):
        self.explainer = Explainer()

    def test_explain_low_risk(self):
        risk_result = {
            "risk_score": 15.0,
            "risk_band": "LOW",
            "rule_details": [],
            "heuristic_details": [],
        }
        features = {
            "typing_speed_mean": 5.0,
            "cursor_velocity_mean": 100.0,
            "session_duration": 300.0,
        }
        result = self.explainer.explain(risk_result, features, ml_score=10.0)
        self.assertIn("reasons", result)
        self.assertIn("risk_band", result)
        self.assertEqual(result["risk_band"], "LOW")

    def test_explain_high_risk(self):
        risk_result = {
            "risk_score": 85.0,
            "risk_band": "HIGH",
            "rule_details": [
                {"rule": "untrusted_device", "points": 15},
            ],
            "heuristic_details": [
                {"rule": "automated_mouse_pattern", "points": 30, "entropy": 0.1},
            ],
        }
        features = {
            "typing_speed_mean": 50.0,
            "cursor_velocity_mean": 2000.0,
            "session_duration": 10.0,
            "direction_entropy": 0.1,
        }
        baseline = {
            "typing_speed_mean": {"mean": 5.0, "std": 1.0},
            "cursor_velocity_mean": {"mean": 100.0, "std": 20.0},
            "session_duration": {"mean": 300.0, "std": 50.0},
        }
        result = self.explainer.explain(risk_result, features, baseline, ml_score=80.0)
        self.assertGreater(len(result["reasons"]), 0)
        self.assertEqual(result["risk_band"], "HIGH")
        self.assertIn("feature_contributions", result)

    def test_cold_start_explain(self):
        risk_result = {"risk_score": 50.0, "risk_band": "MEDIUM", "ml_score": 50.0}
        features = {"total_interactions": 3}
        result = self.explainer.explain_cold_start(risk_result, features)
        self.assertGreater(len(result["reasons"]), 0)
        self.assertIn("note", result)


class TestBehavioralProfile(unittest.TestCase):
    def setUp(self):
        self.config = MLConfig()
        self.config.profile_storage_path = tempfile.mkdtemp()

    def test_create_and_save_profile(self):
        manager = BehavioralProfileManager(self.config)
        profile = manager.get_or_create_profile("test_user")
        self.assertTrue(profile.cold_start)
        self.assertEqual(profile.user_id, "test_user")

        profile.session_count = 10
        profile.cold_start = False
        manager.save_profile(profile)

        loaded = manager.get_profile("test_user")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.session_count, 10)
        self.assertFalse(loaded.cold_start)

    def test_add_risk_event(self):
        manager = BehavioralProfileManager(self.config)
        manager.add_risk_event("test_user", 85.0, "HIGH")
        profile = manager.get_profile("test_user")
        self.assertEqual(len(profile.risk_history), 1)
        self.assertEqual(profile.risk_history[0][1], 85.0)
        self.assertEqual(profile.risk_history[0][2], "HIGH")

    def test_device_fingerprints(self):
        manager = BehavioralProfileManager(self.config)
        manager.add_device_fingerprint("test_user", "fp123")
        manager.add_device_fingerprint("test_user", "fp456")
        devices = manager.get_trusted_devices("test_user")
        self.assertEqual(len(devices), 2)
        self.assertIn("fp123", devices)

    def test_update_drift_status(self):
        manager = BehavioralProfileManager(self.config)
        manager.update_drift_status("test_user", "WARNING")
        profile = manager.get_profile("test_user")
        self.assertEqual(profile.drift_status, "WARNING")

    def test_get_all_user_ids(self):
        manager = BehavioralProfileManager(self.config)
        manager.get_or_create_profile("user_a")
        manager.get_or_create_profile("user_b")
        users = manager.get_all_user_ids()
        self.assertIn("user_a", users)
        self.assertIn("user_b", users)

    def test_serialization_roundtrip(self):
        profile = BehavioralProfile(
            user_id="roundtrip",
            profile_version=3,
            model_version="v2",
            session_count=15,
            feature_statistics={"typing_speed": {"mean": 5.0, "std": 1.0}},
            device_fingerprints=["fp1", "fp2"],
            risk_history=[(datetime.utcnow(), 30.0, "LOW")],
            drift_status="WARNING",
            cold_start=False,
        )
        data = profile.to_dict()
        restored = BehavioralProfile.from_dict(data)
        self.assertEqual(restored.user_id, "roundtrip")
        self.assertEqual(restored.profile_version, 3)
        self.assertEqual(restored.model_version, "v2")
        self.assertEqual(restored.session_count, 15)
        self.assertEqual(len(restored.device_fingerprints), 2)
        self.assertEqual(len(restored.risk_history), 1)
        self.assertEqual(restored.drift_status, "WARNING")
        self.assertFalse(restored.cold_start)


class TestModelRegistry(unittest.TestCase):
    def setUp(self):
        self.config = MLConfig()
        self.config.registry_path = tempfile.mkdtemp()
        self.registry = ModelRegistry(self.config)

    def test_register_and_get(self):
        self.registry.register_model("user1", 1, "/path/to/model.pkl", {"auc": 0.95})
        entry = self.registry.get_active_model("user1")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.version, 1)

    def test_versioning(self):
        self.registry.register_model("user1", 1, "/path/v1.pkl")
        self.registry.register_model("user1", 2, "/path/v2.pkl")
        active = self.registry.get_active_model("user1")
        self.assertEqual(active.version, 2)

        old = self.registry.get_model("user1", 1)
        self.assertIsNotNone(old)
        self.assertEqual(old.status, "archived")

    def test_rollback(self):
        self.registry.register_model("user1", 1, "/path/v1.pkl")
        self.registry.register_model("user1", 2, "/path/v2.pkl")
        success = self.registry.rollback("user1", 1)
        self.assertTrue(success)
        active = self.registry.get_active_model("user1")
        self.assertEqual(active.version, 1)

    def test_update_metrics(self):
        self.registry.register_model("user1", 1, "/path/v1.pkl")
        self.registry.update_metrics("user1", 1, {"f1": 0.90})
        entry = self.registry.get_model("user1", 1)
        self.assertEqual(entry.metrics.get("f1"), 0.90)

    def test_delete_user_models(self):
        self.registry.register_model("user1", 1, "/path/v1.pkl")
        self.registry.delete_user_models("user1")
        self.assertIsNone(self.registry.get_active_model("user1"))

    def test_summary_stats(self):
        self.registry.register_model("user1", 1, "/path/v1.pkl")
        self.registry.register_model("user1", 2, "/path/v2.pkl")
        self.registry.register_model("user2", 1, "/path/v1.pkl")
        stats = self.registry.get_summary_stats()
        self.assertEqual(stats["total_users"], 2)
        self.assertEqual(stats["total_models"], 3)
        self.assertEqual(stats["active_models"], 2)


class TestEvaluation(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.RandomState(42)
        self.y_true = np.array([0] * 80 + [1] * 20)
        self.y_scores = np.concatenate([
            self.rng.randn(80) * 0.5,
            self.rng.randn(20) * 0.5 + 1.0,
        ])

    def test_evaluate_binary(self):
        metrics = Evaluator.evaluate_binary(self.y_true, self.y_scores)
        self.assertIn("roc_auc", metrics)
        self.assertIn("accuracy", metrics)
        self.assertIn("f1", metrics)
        self.assertIn("precision", metrics)
        self.assertIn("recall", metrics)
        self.assertGreater(metrics["roc_auc"], 0.5)

    def test_evaluate_binary_single_class(self):
        metrics = Evaluator.evaluate_binary(np.zeros(50), np.random.randn(50))
        self.assertIn("accuracy", metrics)

    def test_roc_curve(self):
        curve = Evaluator.compute_roc_curve(self.y_true, self.y_scores)
        self.assertIn("fpr", curve)
        self.assertIn("tpr", curve)
        self.assertIn("auc", curve)
        self.assertGreater(curve["auc"], 0.5)

    def test_pr_curve(self):
        curve = Evaluator.compute_pr_curve(self.y_true, self.y_scores)
        self.assertIn("precision", curve)
        self.assertIn("recall", curve)
        self.assertIn("average_precision", curve)

    def test_optimal_threshold(self):
        result = Evaluator.find_optimal_threshold(self.y_true, self.y_scores)
        self.assertIn("threshold", result)
        self.assertIn("method", result)

    def test_optimal_threshold_f1(self):
        result = Evaluator.find_optimal_threshold(self.y_true, self.y_scores, method="f1")
        self.assertIn("threshold", result)
        self.assertEqual(result["method"], "f1")

    def test_statistical_significance(self):
        scores_a = np.random.randn(100) + 0.5
        scores_b = np.random.randn(100)
        result = Evaluator.statistical_significance(scores_a, scores_b, test="mannwhitney")
        self.assertIn("p_value", result)
        self.assertIn("significant", result)

    def test_statistical_significance_wilcoxon(self):
        scores_a = np.random.randn(100)
        scores_b = np.random.randn(100)
        result = Evaluator.statistical_significance(scores_a, scores_b, test="wilcoxon")
        self.assertIn("p_value", result)

    def test_compare_models_insufficient(self):
        result = Evaluator.compare_models({"m1": {"auc": 0.9}})
        self.assertIn("error", result)


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.config = MLConfig()
        self.config.model_storage_path = tempfile.mkdtemp()
        self.config.profile_storage_path = tempfile.mkdtemp()
        self.config.registry_path = tempfile.mkdtemp()

        self.feature_engine = FeatureEngine(self.config)
        self.global_model = GlobalModel(self.config)
        self.profile_manager = BehavioralProfileManager(self.config)
        self.model_registry = ModelRegistry(self.config)
        self.training_pipeline = TrainingPipeline(
            self.config, self.feature_engine,
            self.profile_manager, self.model_registry, self.global_model,
        )
        self.inference_pipeline = InferencePipeline(
            self.config, self.feature_engine,
            self.global_model, self.profile_manager,
        )
        self.risk_engine = HybridRiskEngine(self.config)
        self.explainer = Explainer()

    def _make_session(self, n_events=15):
        events = []
        t = 1000.0
        for i in range(n_events):
            events.append({"type": "keydown", "timestamp": t, "key": chr(97 + (i % 26))})
            t += 50 + (i % 10)
            events.append({"type": "keyup", "timestamp": t + 80, "key": chr(97 + (i % 26))})
            t += 100
            events.append({"type": "mousemove", "timestamp": t, "x": float(100 + i * 3), "y": float(200 + i * 2)})
            t += 16
        events.append({"type": "mousedown", "timestamp": t, "button": 0})
        return events

    def test_end_to_end(self):
        sessions = [self._make_session(20) for _ in range(6)]

        self.training_pipeline.ensure_global_model(sessions)
        self.training_pipeline.train_for_user("integration_user", sessions)

        test_session = self._make_session(15)
        inference_result = self.inference_pipeline.score("integration_user", test_session)

        risk_result = self.risk_engine.evaluate(
            ml_score=inference_result["ml_score"],
            features=inference_result["features"],
            session_count=6,
        )

        explanation = self.explainer.explain(
            risk_result,
            inference_result["features"],
            ml_score=inference_result["ml_score"],
        )

        self.assertIn("ml_score", inference_result)
        self.assertIn("risk_score", risk_result)
        self.assertIn("reasons", explanation)
        self.assertIn("feature_contributions", explanation)

        profile = self.profile_manager.get_profile("integration_user")
        self.assertIsNotNone(profile)
        self.assertFalse(profile.cold_start)

        registry_entry = self.model_registry.get_active_model("integration_user")
        self.assertIsNotNone(registry_entry)


if __name__ == "__main__":
    unittest.main()
