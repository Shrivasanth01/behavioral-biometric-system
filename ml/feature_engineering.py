import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from scipy.stats import entropy
from ml.config import MLConfig, FeatureConfig
from ml.utils import (
    preprocess_events,
    safe_divide,
    compute_entropy,
    discretize_angle,
    safe_log,
)


class FeatureEngine:
    def __init__(self, config: Optional[MLConfig] = None):
        self.config = config or MLConfig()
        self.feature_config = self.config.feature

    def extract_all(
        self,
        events: List[Dict],
        include_mobile: bool = False,
    ) -> Dict[str, float]:
        df = preprocess_events(events)
        if df.empty:
            return self._empty_features(include_mobile)

        features = {}
        features.update(self._extract_keystroke_features(df))
        features.update(self._extract_mouse_features(df))
        features.update(self._extract_session_features(df))
        if include_mobile:
            features.update(self._extract_mobile_features(df))

        for k in self.feature_config.all_features:
            features.setdefault(k, 0.0)

        return features

    def extract_batch(
        self,
        event_batches: List[List[Dict]],
        include_mobile: bool = False,
    ) -> pd.DataFrame:
        records = []
        for batch in event_batches:
            feats = self.extract_all(batch, include_mobile=include_mobile)
            records.append(feats)
        return pd.DataFrame(records)

    def _empty_features(self, include_mobile: bool) -> Dict[str, float]:
        feats = {k: 0.0 for k in self.feature_config.keystroke_features}
        feats.update({k: 0.0 for k in self.feature_config.mouse_features})
        feats.update({k: 0.0 for k in self.feature_config.session_features})
        feats.update({k: 0.0 for k in self.feature_config.mobile_features})
        return feats

    def _extract_keystroke_features(self, df: pd.DataFrame) -> Dict[str, float]:
        features = {}
        key_events = df[df["type"] == "keydown"].copy()
        keyup_events = df[df["type"] == "keyup"].copy()
        all_key_events = df[df["type"].isin(["keydown", "keyup"])].copy()

        timestamps = all_key_events["timestamp"].values
        if len(timestamps) < 2:
            return {k: 0.0 for k in self.feature_config.keystroke_features}

        inter_key_intervals = np.diff(timestamps)
        typing_speed_mean = safe_divide(1.0, np.mean(inter_key_intervals)) if np.mean(inter_key_intervals) > 0 else 0.0
        features["typing_speed_mean"] = float(typing_speed_mean)
        features["typing_speed_std"] = float(np.std(inter_key_intervals)) if len(inter_key_intervals) > 0 else 0.0

        hold_durations = self._compute_hold_durations(df)
        if len(hold_durations) > 0:
            features["key_hold_mean"] = float(np.mean(hold_durations))
            features["key_hold_std"] = float(np.std(hold_durations))
        else:
            features["key_hold_mean"] = 0.0
            features["key_hold_std"] = 0.0

        total_keys = len(all_key_events)
        backspace_count = len(all_key_events[all_key_events.get("key", "").isin(["Backspace", "Delete"])])
        features["backspace_rate"] = safe_divide(backspace_count, total_keys)
        total_down = len(key_events)
        corrections = len(all_key_events[
            all_key_events.get("key", "").isin(["Backspace", "Delete", "ArrowLeft", "ArrowRight"])
        ])
        features["error_correction_rate"] = safe_divide(corrections, total_keys)

        trigram_latencies = self._compute_trigram_latencies(timestamps)
        features["trigram_latency_mean"] = float(np.mean(trigram_latencies)) if len(trigram_latencies) > 0 else 0.0

        key_freq = all_key_events.get("key", pd.Series()).value_counts()
        key_counts = key_freq.values.astype(np.float64)
        features["key_press_freq_entropy"] = compute_entropy(key_counts) if len(key_counts) > 0 else 0.0

        special_keys = {"Shift", "Control", "Alt", "CapsLock", "Tab", "Escape", "Enter", "Meta", "Ctrl", "AltGr"}
        special_count = len(all_key_events[all_key_events.get("key", "").isin(special_keys)])
        features["special_key_ratio"] = safe_divide(special_count, total_keys)

        number_keys = set(str(i) for i in range(10))
        number_count = len(all_key_events[all_key_events.get("key", "").isin(number_keys)])
        features["number_row_freq"] = safe_divide(number_count, total_keys)

        return features

    def _compute_hold_durations(self, df: pd.DataFrame) -> np.ndarray:
        keydowns = df[df["type"] == "keydown"][["timestamp", "key"]].values
        keyups = df[df["type"] == "keyup"][["timestamp", "key"]].values
        durations = []
        for kd_ts, kd_key in keydowns:
            matching_up = keyups[(keyups[:, 1] == kd_key) & (keyups[:, 0] > kd_ts)]
            if len(matching_up) > 0:
                durations.append(matching_up[0, 0] - kd_ts)
        return np.array(durations, dtype=np.float64)

    def _compute_trigram_latencies(self, timestamps: np.ndarray) -> np.ndarray:
        if len(timestamps) < 4:
            return np.array([])
        latencies = []
        for i in range(len(timestamps) - 3):
            latencies.append(timestamps[i + 3] - timestamps[i])
        return np.array(latencies, dtype=np.float64)

    def _extract_mouse_features(self, df: pd.DataFrame) -> Dict[str, float]:
        features = {}
        mouse_moves = df[df["type"] == "mousemove"].copy()
        mouse_clicks = df[df["type"].isin(["mousedown", "mouseup", "click"])].copy()
        all_mouse = df[df["type"].str.startswith("mouse", na=False)].copy()

        if mouse_moves.empty or len(mouse_moves) < 2:
            return {k: 0.0 for k in self.feature_config.mouse_features}

        xs = mouse_moves.get("x", pd.Series()).values.astype(np.float64)
        ys = mouse_moves.get("y", pd.Series()).values.astype(np.float64)
        ts = mouse_moves["timestamp"].values.astype(np.float64)

        if len(xs) < 2:
            return {k: 0.0 for k in self.feature_config.mouse_features}

        dx = np.diff(xs)
        dy = np.diff(ys)
        dt = np.diff(ts)
        dt = np.clip(dt, 1e-6, None)

        distances = np.sqrt(dx ** 2 + dy ** 2)
        velocities = distances / dt
        accels = np.diff(velocities) / dt[:-1] if len(velocities) > 1 else np.array([])

        features["cursor_velocity_mean"] = float(np.mean(velocities)) if len(velocities) > 0 else 0.0
        features["cursor_velocity_std"] = float(np.std(velocities)) if len(velocities) > 0 else 0.0
        features["cursor_accel_mean"] = float(np.mean(accels)) if len(accels) > 0 else 0.0
        features["cursor_accel_std"] = float(np.std(accels)) if len(accels) > 0 else 0.0
        features["path_length"] = float(np.sum(distances))

        angles = np.degrees(np.arctan2(dy, dx))
        direction_bins = np.array([discretize_angle(a, 8) for a in angles])
        bin_counts = np.bincount(direction_bins, minlength=8).astype(np.float64)
        features["direction_entropy"] = compute_entropy(bin_counts)

        if not mouse_clicks.empty:
            click_ts = mouse_clicks["timestamp"].values.astype(np.float64)
            session_dur = ts[-1] - ts[0] if ts[-1] > ts[0] else 1.0
            features["click_frequency"] = safe_divide(len(click_ts), session_dur)

            click_intervals = np.diff(click_ts)
            double_clicks = np.sum(click_intervals < 0.5) if len(click_intervals) > 0 else 0
            features["double_click_rate"] = safe_divide(double_clicks, len(click_ts))

            right_clicks = len(mouse_clicks[mouse_clicks.get("button", 0) == 2])
            features["right_click_ratio"] = safe_divide(right_clicks, len(mouse_clicks))
        else:
            features["click_frequency"] = 0.0
            features["double_click_rate"] = 0.0
            features["right_click_ratio"] = 0.0

        scroll_events = df[df["type"] == "scroll"].copy()
        if not scroll_events.empty:
            scroll_deltas = scroll_events.get("delta_y", scroll_events.get("delta", 0)).values.astype(np.float64)
            scroll_ts = scroll_events["timestamp"].values.astype(np.float64)
            scroll_dt = np.diff(scroll_ts)
            scroll_dt = np.clip(scroll_dt, 1e-6, None)
            if len(scroll_deltas) > 1:
                scroll_speeds = np.abs(scroll_deltas[:-1]) / scroll_dt
                features["scroll_speed_mean"] = float(np.mean(scroll_speeds))
                direction_changes = np.sum(np.diff(np.sign(scroll_deltas)) != 0)
                features["scroll_direction_changes"] = float(direction_changes)
            else:
                features["scroll_speed_mean"] = 0.0
                features["scroll_direction_changes"] = 0.0
        else:
            features["scroll_speed_mean"] = 0.0
            features["scroll_direction_changes"] = 0.0

        total_time = ts[-1] - ts[0] if ts[-1] > ts[0] else 1.0
        if total_time > 0 and len(dt) > 0:
            idle_threshold = np.percentile(dt, 90) * 2
            idle_time = np.sum(dt[dt > idle_threshold]) if np.any(dt > idle_threshold) else 0
            features["idle_time_ratio"] = safe_divide(idle_time, total_time)
        else:
            features["idle_time_ratio"] = 0.0

        return features

    def _extract_session_features(self, df: pd.DataFrame) -> Dict[str, float]:
        features = {}
        ts = df["timestamp"].values.astype(np.float64)
        if len(ts) < 2:
            return {k: 0.0 for k in self.feature_config.session_features}

        duration = ts[-1] - ts[0]
        features["session_duration"] = float(duration) if duration > 0 else 0.0
        features["total_interactions"] = float(len(df))

        if duration > 0:
            features["interaction_density"] = safe_divide(len(df), duration)
        else:
            features["interaction_density"] = 0.0

        pages = df[df["type"] == "pageview"].copy()
        features["navigation_depth"] = float(len(pages)) if not pages.empty else 1.0

        if not pages.empty:
            page_paths = pages.get("url", pd.Series([f"page_{i}" for i in range(len(pages))]))
            transitions = pd.Series(zip(page_paths[:-1], page_paths[1:]))
            transition_counts = transitions.value_counts().values.astype(np.float64)
            features["navigation_entropy"] = compute_entropy(transition_counts)
        else:
            features["navigation_entropy"] = 0.0

        focus_events = df[df["type"] == "focus"].copy()
        if not focus_events.empty:
            field_ids = focus_events.get("field_id", focus_events.get("element_id", pd.Series()))
            if len(field_ids) > 1:
                consistencies = []
                for i in range(1, len(field_ids)):
                    consistencies.append(1.0 if field_ids.iloc[i] >= field_ids.iloc[i - 1] else 0.0)
                features["form_focus_consistency"] = float(np.mean(consistencies))
            else:
                features["form_focus_consistency"] = 1.0
        else:
            features["form_focus_consistency"] = 1.0

        start_ts = ts[0]
        hour = (start_ts / 3600.0) % 24.0
        features["time_of_day"] = hour / 24.0

        day = int((start_ts / 86400.0) % 7)
        features["day_of_week"] = day / 7.0

        return features

    def _extract_mobile_features(self, df: pd.DataFrame) -> Dict[str, float]:
        features = {}

        touch_events = df[df["type"].isin(["touchstart", "touchmove", "touchend"])].copy()
        if touch_events.empty:
            return {k: 0.0 for k in self.feature_config.mobile_features}

        touch_moves = touch_events[touch_events["type"] == "touchmove"].copy()

        if not touch_moves.empty and len(touch_moves) >= 2:
            xs = touch_moves.get("x", pd.Series([0.0])).values.astype(np.float64)
            ys = touch_moves.get("y", pd.Series([0.0])).values.astype(np.float64)
            ts = touch_moves["timestamp"].values.astype(np.float64)
            dx = np.diff(xs)
            dy = np.diff(ys)
            dt = np.diff(ts)
            dt = np.clip(dt, 1e-6, None)
            velocities = np.sqrt(dx ** 2 + dy ** 2) / dt
            features["swipe_velocity_mean"] = float(np.mean(velocities)) if len(velocities) > 0 else 0.0
            features["swipe_velocity_std"] = float(np.std(velocities)) if len(velocities) > 0 else 0.0
            if len(velocities) > 1:
                accels = np.diff(velocities) / dt[:-1]
                features["swipe_accel_mean"] = float(np.mean(accels)) if len(accels) > 0 else 0.0
            else:
                features["swipe_accel_mean"] = 0.0
        else:
            features["swipe_velocity_mean"] = 0.0
            features["swipe_velocity_std"] = 0.0
            features["swipe_accel_mean"] = 0.0

        if "pressure" in touch_events.columns:
            pressures = touch_events["pressure"].values.astype(np.float64)
        elif "force" in touch_events.columns:
            pressures = touch_events["force"].values.astype(np.float64)
        else:
            pressures = np.full(len(touch_events), 0.5, dtype=np.float64)
        pressures = np.nan_to_num(pressures, nan=0.5)
        features["touch_pressure_mean"] = float(np.mean(pressures))
        features["touch_pressure_std"] = float(np.std(pressures))

        touch_durations = self._compute_touch_durations(touch_events)
        features["touch_duration_mean"] = float(np.mean(touch_durations)) if len(touch_durations) > 0 else 0.0

        if not touch_moves.empty and len(touch_moves) >= 3:
            velocities = np.sqrt(np.diff(xs) ** 2 + np.diff(ys) ** 2) / np.clip(np.diff(ts), 1e-6, None)
            changes_in_velocity = np.sum(np.abs(np.diff(velocities)) > 0.1 * np.mean(velocities)) if len(velocities) > 1 and np.mean(velocities) > 0 else 0
            features["gesture_complexity"] = float(changes_in_velocity)
        else:
            features["gesture_complexity"] = 0.0

        touch_starts = touch_events[touch_events["type"] == "touchstart"]
        total_touches = len(touch_starts)
        if total_touches > 0:
            touches_col = touch_starts.get("touches")
            if touches_col is not None:
                multi_touches = int((touches_col > 1).sum())
            else:
                multi_touches = 0
            features["multi_touch_ratio"] = safe_divide(multi_touches, total_touches)
        else:
            features["multi_touch_ratio"] = 0.0

        return features

    def _compute_touch_durations(self, touch_events: pd.DataFrame) -> np.ndarray:
        starts = touch_events[touch_events["type"] == "touchstart"][["timestamp", "touch_id"]].values
        ends = touch_events[touch_events["type"] == "touchend"][["timestamp", "touch_id"]].values
        durations = []
        for s_ts, s_id in starts:
            matching_end = ends[(ends[:, 1] == s_id) & (ends[:, 0] > s_ts)]
            if len(matching_end) > 0:
                durations.append(matching_end[0, 0] - s_ts)
        return np.array(durations, dtype=np.float64)
