import pytest
import numpy as np
from ml.feature_engineering import FeatureEngine
from ml.config import MLConfig, FeatureConfig


class TestKeystrokeFeatures:
    @pytest.fixture
    def engine(self):
        return FeatureEngine()

    def _make_keystroke_events(self, n=20, rng=None):
        if rng is None:
            rng = np.random.RandomState(42)
        events = []
        t = 1000.0
        for i in range(n):
            events.append({"type": "keydown", "timestamp": t, "key": chr(97 + (i % 26))})
            t += 50 + rng.randint(-10, 10)
            events.append({"type": "keyup", "timestamp": t + 80, "key": chr(97 + (i % 26))})
            t += 100
        events.append({"type": "keydown", "timestamp": t, "key": "Backspace"})
        return events

    def test_typing_speed_features(self, engine):
        events = self._make_keystroke_events(30)
        features = engine._extract_keystroke_features(engine._preprocess(events) if hasattr(engine, '_preprocess') else None)
        if features is None:
            features = engine.extract_all(events)
        assert features.get("typing_speed_mean", 0) > 0
        assert features.get("typing_speed_std", 0) >= 0

    def test_hold_durations(self, engine):
        events = self._make_keystroke_events(20)
        features = engine.extract_all(events)
        assert features.get("key_hold_mean", 0) >= 0
        assert features.get("key_hold_std", 0) >= 0

    def test_backspace_rate(self, engine):
        events = self._make_keystroke_events(10)
        features = engine.extract_all(events)
        assert features.get("backspace_rate", 0) > 0

    def test_key_entropy(self, engine):
        events = self._make_keystroke_events(50)
        features = engine.extract_all(events)
        assert features.get("key_press_freq_entropy", 0) > 0

    def test_trigram_latency(self, engine):
        events = self._make_keystroke_events(20)
        features = engine.extract_all(events)
        assert features.get("trigram_latency_mean", 0) >= 0

    def test_special_key_ratio(self, engine):
        events = self._make_keystroke_events(10)
        features = engine.extract_all(events)
        assert isinstance(features.get("special_key_ratio", 0), float)

    def test_number_row_freq(self, engine):
        events = self._make_keystroke_events(10)
        features = engine.extract_all(events)
        assert isinstance(features.get("number_row_freq", 0), float)

    def test_error_correction_rate(self, engine):
        events = self._make_keystroke_events(10)
        features = engine.extract_all(events)
        assert isinstance(features.get("error_correction_rate", 0), float)

    def test_single_keystroke(self, engine):
        events = [{"type": "keydown", "timestamp": 1000, "key": "a"}]
        features = engine.extract_all(events)
        for k in engine.feature_config.keystroke_features:
            assert k in features

    def test_no_keyup_events(self, engine):
        events = [{"type": "keydown", "timestamp": 1000, "key": "a"},
                  {"type": "keydown", "timestamp": 1100, "key": "b"}]
        features = engine.extract_all(events)
        assert features.get("key_hold_mean", 0) == 0.0


class TestMouseFeatures:
    @pytest.fixture
    def engine(self):
        return FeatureEngine()

    def _make_mouse_events(self, n=30, rng=None):
        if rng is None:
            rng = np.random.RandomState(42)
        events = []
        t = 2000.0
        x, y = 100.0, 100.0
        for i in range(n):
            events.append({"type": "mousemove", "timestamp": t, "x": x, "y": y})
            x += rng.randint(-20, 20)
            y += rng.randint(-20, 20)
            t += 16.0 + rng.random() * 10
        events.append({"type": "mousedown", "timestamp": t, "button": 0})
        events.append({"type": "mouseup", "timestamp": t + 50, "button": 0})
        return events

    def test_cursor_velocity(self, engine):
        events = self._make_mouse_events(30)
        features = engine.extract_all(events)
        assert features.get("cursor_velocity_mean", 0) >= 0
        assert features.get("cursor_velocity_std", 0) >= 0

    def test_cursor_acceleration(self, engine):
        events = self._make_mouse_events(30)
        features = engine.extract_all(events)
        assert isinstance(features.get("cursor_accel_mean", 0), float)

    def test_path_length(self, engine):
        events = self._make_mouse_events(30)
        features = engine.extract_all(events)
        assert features.get("path_length", 0) > 0

    def test_direction_entropy(self, engine):
        events = self._make_mouse_events(30)
        features = engine.extract_all(events)
        assert features.get("direction_entropy", 0) >= 0

    def test_click_features(self, engine):
        events = self._make_mouse_events(20)
        features = engine.extract_all(events)
        assert features.get("click_frequency", 0) >= 0
        assert isinstance(features.get("double_click_rate", 0), float)

    def test_idle_time_ratio(self, engine):
        events = self._make_mouse_events(20)
        features = engine.extract_all(events)
        assert isinstance(features.get("idle_time_ratio", 0), float)

    def test_no_mouse_events(self, engine):
        events = [{"type": "keydown", "timestamp": 1000, "key": "a"}]
        features = engine.extract_all(events)
        for k in engine.feature_config.mouse_features:
            assert k in features
            assert features[k] == 0.0


class TestSessionFeatures:
    @pytest.fixture
    def engine(self):
        return FeatureEngine()

    def test_session_duration(self, engine):
        events = [
            {"type": "keydown", "timestamp": 1000, "key": "a"},
            {"type": "keyup", "timestamp": 1080, "key": "a"},
            {"type": "mousemove", "timestamp": 5000, "x": 100, "y": 200},
        ]
        features = engine.extract_all(events)
        assert features.get("session_duration", 0) > 0

    def test_total_interactions(self, engine):
        events = [
            {"type": "keydown", "timestamp": 1000, "key": "a"},
            {"type": "keyup", "timestamp": 1080, "key": "a"},
        ]
        features = engine.extract_all(events)
        assert features.get("total_interactions", 0) == 2

    def test_interaction_density(self, engine):
        events = [
            {"type": "keydown", "timestamp": 1000, "key": "a"},
            {"type": "keyup", "timestamp": 1080, "key": "a"},
            {"type": "mousemove", "timestamp": 2000, "x": 100, "y": 200},
        ]
        features = engine.extract_all(events)
        assert features.get("interaction_density", 0) > 0

    def test_time_of_day_normalized(self, engine):
        events = [{"type": "keydown", "timestamp": 1000, "key": "a"}]
        features = engine.extract_all(events)
        assert 0 <= features.get("time_of_day", 0) <= 1

    def test_day_of_week_normalized(self, engine):
        events = [{"type": "keydown", "timestamp": 1000, "key": "a"}]
        features = engine.extract_all(events)
        assert 0 <= features.get("day_of_week", 0) <= 1

    def test_navigation_depth(self, engine):
        events = [
            {"type": "pageview", "timestamp": 1000, "url": "/login"},
            {"type": "pageview", "timestamp": 2000, "url": "/dashboard"},
            {"type": "pageview", "timestamp": 3000, "url": "/transfer"},
        ]
        features = engine.extract_all(events)
        assert features.get("navigation_depth", 0) >= 3


class TestMobileFeatures:
    @pytest.fixture
    def engine(self):
        return FeatureEngine()

    def _make_touch_events(self, n=10):
        events = []
        t = 1000.0
        for i in range(n):
            events.append({"type": "touchstart", "timestamp": t, "x": 100 + i * 10, "y": 200,
                           "touch_id": 0, "pressure": 0.5})
            events.append({"type": "touchmove", "timestamp": t + 50, "x": 100 + i * 10 + 20, "y": 200 + 10,
                           "touch_id": 0, "pressure": 0.6})
            events.append({"type": "touchend", "timestamp": t + 100, "touch_id": 0})
            t += 200
        return events

    def test_swipe_velocity(self, engine):
        events = self._make_touch_events(10)
        features = engine.extract_all(events, include_mobile=True)
        assert features.get("swipe_velocity_mean", 0) >= 0

    def test_touch_pressure(self, engine):
        events = self._make_touch_events(5)
        features = engine.extract_all(events, include_mobile=True)
        assert features.get("touch_pressure_mean", 0) > 0

    def test_touch_duration(self, engine):
        events = self._make_touch_events(5)
        features = engine.extract_all(events, include_mobile=True)
        assert features.get("touch_duration_mean", 0) >= 0

    def test_no_touch_events(self, engine):
        events = [{"type": "keydown", "timestamp": 1000, "key": "a"}]
        features = engine.extract_all(events, include_mobile=True)
        for k in engine.feature_config.mobile_features:
            assert k in features
            assert features[k] == 0.0


class TestEmptyAndEdgeCases:
    @pytest.fixture
    def engine(self):
        return FeatureEngine()

    def test_empty_events_list(self, engine):
        features = engine.extract_all([])
        for k in engine.feature_config.all_features:
            assert k in features
            assert features[k] == 0.0

    def test_single_event(self, engine):
        features = engine.extract_all([{"type": "keydown", "timestamp": 1000, "key": "a"}])
        for k in engine.feature_config.all_features:
            assert k in features

    def test_events_with_nan(self, engine):
        events = [
            {"type": "keydown", "timestamp": float('nan'), "key": "a"},
            {"type": "keyup", "timestamp": 1100, "key": "a"},
        ]
        features = engine.extract_all(events)
        assert all(np.isfinite(v) or v == 0.0 for v in features.values())

    def test_events_with_inf(self, engine):
        events = [
            {"type": "keydown", "timestamp": float('inf'), "key": "a"},
            {"type": "keyup", "timestamp": 1100, "key": "a"},
        ]
        features = engine.extract_all(events)
        assert all(v == 0.0 or np.isfinite(v) for v in features.values())

    def test_unsorted_timestamps(self, engine):
        events = [
            {"type": "keydown", "timestamp": 3000, "key": "c"},
            {"type": "keydown", "timestamp": 1000, "key": "a"},
            {"type": "keydown", "timestamp": 2000, "key": "b"},
        ]
        features = engine.extract_all(events)
        assert features["total_interactions"] == 3
        assert features["session_duration"] >= 0

    def test_missing_event_type(self, engine):
        events = [{"timestamp": 1000}]
        features = engine.extract_all(events)
        assert all(v == 0.0 for v in features.values())


class TestFeatureConsistency:
    @pytest.fixture
    def engine(self):
        return FeatureEngine()

    def test_same_input_same_output(self, engine):
        events = [
            {"type": "keydown", "timestamp": 1000, "key": "a"},
            {"type": "keyup", "timestamp": 1080, "key": "a"},
            {"type": "mousemove", "timestamp": 2000, "x": 100, "y": 200},
        ]
        f1 = engine.extract_all(events)
        f2 = engine.extract_all(events)
        for k in engine.feature_config.all_features:
            assert f1[k] == pytest.approx(f2[k], abs=1e-10), f"Mismatch for {k}: {f1[k]} != {f2[k]}"

    def test_fixed_seed_reproducibility(self, engine):
        rng1 = np.random.RandomState(42)
        events1 = []
        t = 1000.0
        for i in range(10):
            events1.append({"type": "keydown", "timestamp": t, "key": chr(97 + i)})
            t += 50 + rng1.randint(-5, 5)
            events1.append({"type": "keyup", "timestamp": t + 80, "key": chr(97 + i)})
            t += 100

        rng2 = np.random.RandomState(42)
        events2 = []
        t = 1000.0
        for i in range(10):
            events2.append({"type": "keydown", "timestamp": t, "key": chr(97 + i)})
            t += 50 + rng2.randint(-5, 5)
            events2.append({"type": "keyup", "timestamp": t + 80, "key": chr(97 + i)})
            t += 100

        f1 = engine.extract_all(events1)
        f2 = engine.extract_all(events2)
        for k in engine.feature_config.keystroke_features:
            assert f1[k] == pytest.approx(f2[k], abs=1e-10)


class TestFeatureBatch:
    @pytest.fixture
    def engine(self):
        return FeatureEngine()

    def test_extract_batch(self, engine):
        batches = [
            [{"type": "keydown", "timestamp": 1000, "key": "a"}],
            [{"type": "keydown", "timestamp": 2000, "key": "b"},
             {"type": "keyup", "timestamp": 2080, "key": "b"}],
        ]
        df = engine.extract_batch(batches)
        assert len(df) == 2
        assert len(df.columns) >= len(engine.feature_config.keystroke_features + engine.feature_config.mouse_features + engine.feature_config.session_features)

    def test_extract_batch_empty(self, engine):
        df = engine.extract_batch([[], []])
        assert len(df) == 2
        assert (df.values == 0).all()

    def test_extract_batch_mixed_sizes(self, engine):
        batches = [
            [{"type": "keydown", "timestamp": 1000, "key": "a"} for _ in range(5)],
            [{"type": "keydown", "timestamp": 1000, "key": "a"} for _ in range(20)],
        ]
        df = engine.extract_batch(batches)
        assert len(df) == 2
