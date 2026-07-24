import numpy as np
import pandas as pd
import logging
from typing import Optional, List, Dict, Tuple, Any
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass

from ml.config import MLConfig, DriftConfig
from ml.utils import compute_psi, compute_kl_divergence

logger = logging.getLogger(__name__)


@dataclass
class DriftReport:
    has_drifted: bool
    psi_value: float
    feature_drift_pct: float
    drifted_features: List[str]
    severity: str
    recommendation: str
    details: Dict[str, Any]


class DriftDetector:
    def __init__(self, config: Optional[MLConfig] = None):
        self.config = config or MLConfig()
        self.drift_config = self.config.drift
        self.reference_distributions: Dict[str, np.ndarray] = {}
        self.monitoring_window: Dict[str, deque] = {}
        self.feature_psi_history: Dict[str, List[float]] = {}
        self.accuracy_history: List[float] = []
        self.alert_history: List[Dict] = []

    def set_reference(self, feature_name: str, values: np.ndarray):
        self.reference_distributions[feature_name] = np.asarray(values, dtype=np.float64).flatten()
        self.monitoring_window[feature_name] = deque(
            maxlen=self.drift_config.monitoring_window_size
        )
        if feature_name not in self.feature_psi_history:
            self.feature_psi_history[feature_name] = []

    def set_reference_batch(self, feature_data: Dict[str, np.ndarray]):
        for name, values in feature_data.items():
            self.set_reference(name, values)

    def add_sample(self, feature_name: str, value: float):
        if feature_name not in self.monitoring_window:
            self.monitoring_window[feature_name] = deque(
                maxlen=self.drift_config.monitoring_window_size
            )
        self.monitoring_window[feature_name].append(value)

    def add_samples(self, feature_name: str, values: np.ndarray):
        for v in values:
            self.add_sample(feature_name, v)

    def add_accuracy_measurement(self, accuracy: float):
        self.accuracy_history.append(accuracy)
        if len(self.accuracy_history) > 1000:
            self.accuracy_history = self.accuracy_history[-500:]

    def check_feature_drift(self, feature_name: str) -> Tuple[float, bool]:
        if (
            feature_name not in self.reference_distributions
            or feature_name not in self.monitoring_window
        ):
            return 0.0, False

        ref = self.reference_distributions[feature_name]
        mon = np.array(list(self.monitoring_window[feature_name]), dtype=np.float64)

        if len(ref) < 10 or len(mon) < self.drift_config.min_drift_samples:
            return 0.0, False

        psi = compute_psi(ref, mon)
        self.feature_psi_history[feature_name].append(psi)
        if len(self.feature_psi_history[feature_name]) > 100:
            self.feature_psi_history[feature_name] = self.feature_psi_history[feature_name][-50:]

        has_drifted = bool(psi > self.drift_config.psi_warning_threshold)
        return psi, has_drifted

    def check_all_features(self) -> DriftReport:
        drifted_features = []
        total_psi = 0.0
        n_checked = 0

        for feature_name in self.reference_distributions:
            psi, drifted = self.check_feature_drift(feature_name)
            total_psi += psi
            n_checked += 1
            if drifted:
                drifted_features.append(feature_name)

        avg_psi = total_psi / max(n_checked, 1)
        feature_drift_pct = len(drifted_features) / max(n_checked, 1)

        if avg_psi > self.drift_config.psi_drift_threshold or feature_drift_pct > 0.5:
            severity = "CRITICAL"
            recommendation = "Immediate retraining required. Concept drift detected."
        elif (
            avg_psi > self.drift_config.psi_warning_threshold
            or feature_drift_pct > self.drift_config.feature_drift_warning_pct
        ):
            severity = "WARNING"
            recommendation = "Monitor closely. Consider retraining at next interval."
        else:
            severity = "STABLE"
            recommendation = "No action required."

        return DriftReport(
            has_drifted=severity != "STABLE",
            psi_value=round(avg_psi, 4),
            feature_drift_pct=round(feature_drift_pct, 4),
            drifted_features=drifted_features,
            severity=severity,
            recommendation=recommendation,
            details=self._build_details(drifted_features, avg_psi),
        )

    def check_accuracy_degradation(
        self,
        recent_accuracy: float,
        baseline_accuracy: float,
    ) -> bool:
        self.add_accuracy_measurement(recent_accuracy)
        degradation = baseline_accuracy - recent_accuracy
        return degradation > self.drift_config.accuracy_degradation_threshold

    def check_population_drift(
        self,
        current_features: np.ndarray,
        reference_features: np.ndarray,
    ) -> DriftReport:
        overall_psi = compute_psi(reference_features.flatten(), current_features.flatten())
        n_features = reference_features.shape[1]
        drifted = []
        for i in range(n_features):
            ref_col = reference_features[:, i]
            cur_col = current_features[:, i]
            psi = compute_psi(ref_col, cur_col)
            if psi > self.drift_config.psi_warning_threshold:
                drifted.append(f"feature_{i}")

        drift_pct = len(drifted) / max(n_features, 1)

        if overall_psi > self.drift_config.psi_drift_threshold or drift_pct > 0.5:
            severity = "CRITICAL"
            recommendation = "Population shift detected. Retrain global model."
        elif overall_psi > self.drift_config.psi_warning_threshold or drift_pct > 0.2:
            severity = "WARNING"
            recommendation = "Mild population shift. Update reference distribution."
        else:
            severity = "STABLE"
            recommendation = "No population drift detected."

        return DriftReport(
            has_drifted=severity != "STABLE",
            psi_value=round(overall_psi, 4),
            feature_drift_pct=round(drift_pct, 4),
            drifted_features=drifted,
            severity=severity,
            recommendation=recommendation,
            details={"overall_psi": round(overall_psi, 4), "drifted_features": drifted},
        )

    def get_user_drift_status(
        self,
        user_id: str,
        current_features: Dict[str, float],
        baseline_stats: Dict[str, Dict[str, float]],
    ) -> DriftReport:
        drifted = []
        max_psi = 0.0

        for feature_name, current_value in current_features.items():
            if feature_name not in baseline_stats:
                continue
            stats = baseline_stats[feature_name]
            mean_v = stats.get("mean", 0)
            std_v = stats.get("std", 1)
            if std_v < 1e-8:
                continue

            z_score = abs(current_value - mean_v) / std_v
            if z_score > 3.0:
                drifted.append(feature_name)

            if feature_name in self.feature_psi_history and self.feature_psi_history[feature_name]:
                psi = self.feature_psi_history[feature_name][-1]
                max_psi = max(max_psi, psi)

        drift_pct = len(drifted) / max(len(current_features), 1)

        if drift_pct > 0.3 or max_psi > self.drift_config.psi_drift_threshold:
            severity = "DRIFTED"
            recommendation = "User behavioral drift detected. Consider retraining."
        elif drift_pct > 0.1 or max_psi > self.drift_config.psi_warning_threshold:
            severity = "WARNING"
            recommendation = "Slight behavioral shift detected. Monitor."
        else:
            severity = "STABLE"
            recommendation = "Behavioral pattern stable."

        return DriftReport(
            has_drifted=severity != "STABLE",
            psi_value=round(max_psi, 4),
            feature_drift_pct=round(drift_pct, 4),
            drifted_features=drifted,
            severity=severity,
            recommendation=recommendation,
            details={
                "max_psi": round(max_psi, 4),
                "drifted_features": drifted,
                "z_scores": {
                    f: round(abs(current_features.get(f, 0) - baseline_stats.get(f, {}).get("mean", 0)) / max(baseline_stats.get(f, {}).get("std", 1), 1e-8), 2)
                    for f in drifted[:10]
                },
            },
        )

    def get_drift_trend(self, feature_name: str) -> Dict[str, Any]:
        history = self.feature_psi_history.get(feature_name, [])
        if len(history) < 2:
            return {
                "trend": "insufficient_data",
                "current_psi": round(history[-1], 4) if history else 0.0,
                "values": history,
            }

        recent = history[-5:]
        older = history[:-5]
        trend_direction = "increasing" if np.mean(recent) > np.mean(older) else "decreasing"
        return {
            "trend": trend_direction,
            "current_psi": round(history[-1], 4),
            "mean_psi": round(np.mean(history), 4),
            "max_psi": round(max(history), 4),
            "values": [round(v, 4) for v in history],
        }

    def clear(self):
        self.reference_distributions.clear()
        self.monitoring_window.clear()
        self.feature_psi_history.clear()
        self.accuracy_history.clear()
        self.alert_history.clear()

    def _build_details(
        self,
        drifted_features: List[str],
        avg_psi: float,
    ) -> Dict[str, Any]:
        return {
            "avg_psi": round(avg_psi, 4),
            "drifted_feature_count": len(drifted_features),
            "drifted_features": drifted_features[:20],
            "feature_details": {
                f: {
                    "current_psi": round(self.feature_psi_history.get(f, [0])[-1], 4)
                    if self.feature_psi_history.get(f) else 0.0,
                }
                for f in drifted_features[:10]
            },
        }
