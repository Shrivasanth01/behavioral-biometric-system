import numpy as np
import logging
from typing import Optional, List, Dict, Tuple, Any
from datetime import datetime, time

from ml.config import MLConfig, RiskConfig
from ml.utils import device_fingerprint

logger = logging.getLogger(__name__)


class HybridRiskEngine:
    def __init__(self, config: Optional[MLConfig] = None):
        self.config = config or MLConfig()
        self.risk_config = self.config.risk
        self._device_trust_cache: Dict[str, bool] = {}

    def evaluate(
        self,
        ml_score: float,
        features: Dict[str, float],
        user_baseline: Optional[Dict[str, Dict[str, float]]] = None,
        device_fingerprint_str: Optional[str] = None,
        trusted_devices: Optional[List[str]] = None,
        session_count: int = 0,
    ) -> Dict[str, Any]:
        rules_score = self._evaluate_rules(features, user_baseline, device_fingerprint_str, trusted_devices)
        heuristic_score = self._evaluate_heuristics(features, session_count)

        final_score = (
            self.risk_config.ml_weight * ml_score
            + self.risk_config.rules_weight * rules_score
            + self.risk_config.heuristic_weight * heuristic_score
        )

        final_score = max(0.0, min(100.0, final_score))

        risk_band = self._get_risk_band(final_score)

        return {
            "risk_score": round(final_score, 2),
            "risk_band": risk_band,
            "ml_score": round(ml_score, 2),
            "rules_score": round(rules_score, 2),
            "heuristic_score": round(heuristic_score, 2),
            "components": {
                "ml_weight": self.risk_config.ml_weight,
                "rules_weight": self.risk_config.rules_weight,
                "heuristic_weight": self.risk_config.heuristic_weight,
            },
            "decision": self._get_decision(risk_band),
        }

    def evaluate_with_details(
        self,
        ml_score: float,
        features: Dict[str, float],
        user_baseline: Optional[Dict[str, Dict[str, float]]] = None,
        device_fingerprint_str: Optional[str] = None,
        trusted_devices: Optional[List[str]] = None,
        session_count: int = 0,
    ) -> Dict[str, Any]:
        result = self.evaluate(
            ml_score, features, user_baseline,
            device_fingerprint_str, trusted_devices, session_count,
        )
        rule_details = self._get_rule_details(features, user_baseline, device_fingerprint_str, trusted_devices)
        heuristic_details = self._get_heuristic_details(features, session_count)
        result["rule_details"] = rule_details
        result["heuristic_details"] = heuristic_details
        return result

    def _evaluate_rules(
        self,
        features: Dict[str, float],
        user_baseline: Optional[Dict[str, Dict[str, float]]],
        device_fingerprint_str: Optional[str],
        trusted_devices: Optional[List[str]],
    ) -> float:
        score = 0.0

        if user_baseline:
            typing_speed = features.get("typing_speed_mean", 0)
            typing_baseline = user_baseline.get("typing_speed_mean", {})
            if typing_baseline.get("std", 0) > 0:
                typing_z = abs(typing_speed - typing_baseline.get("mean", 0)) / typing_baseline["std"]
                if typing_z > self.risk_config.typing_speed_std_threshold:
                    score += self.risk_config.typing_speed_points

            mouse_speed = features.get("cursor_velocity_mean", 0)
            mouse_baseline = user_baseline.get("cursor_velocity_mean", {})
            if mouse_baseline.get("std", 0) > 0:
                mouse_z = abs(mouse_speed - mouse_baseline.get("mean", 0)) / mouse_baseline["std"]
                if mouse_z > self.risk_config.mouse_speed_std_threshold:
                    score += self.risk_config.mouse_speed_points

            session_dur = features.get("session_duration", 0)
            dur_baseline = user_baseline.get("session_duration", {})
            if dur_baseline.get("std", 0) > 0:
                dur_z = (dur_baseline.get("mean", 0) - session_dur) / dur_baseline["std"]
                if dur_z > 3.0:
                    score += self.risk_config.session_duration_points

        if device_fingerprint_str and trusted_devices is not None:
            if device_fingerprint_str not in trusted_devices:
                score += self.risk_config.device_fingerprint_points

        hour = features.get("time_of_day", 0.5) * 24
        suspicious_hours = [22, 23, 0, 1, 2, 3, 4, 5]
        if int(hour) in suspicious_hours:
            score += self.risk_config.suspicious_time_points

        nav_entropy = features.get("navigation_entropy", 0)
        if user_baseline:
            nav_baseline = user_baseline.get("navigation_entropy", {})
            if nav_baseline.get("std", 0) > 0:
                nav_z = abs(nav_entropy - nav_baseline.get("mean", 0)) / nav_baseline["std"]
                if nav_z > 2.0:
                    score += self.risk_config.navigation_entropy_points

        return min(score, 100.0)

    def _evaluate_heuristics(self, features: Dict[str, float], session_count: int) -> float:
        score = 0.0
        total_interactions = features.get("total_interactions", 0)

        if total_interactions < self.risk_config.min_interactions:
            score += 50.0

        backspace_rate = features.get("backspace_rate", 0)
        if backspace_rate == 0 and total_interactions > 10:
            score += self.risk_config.perfect_typing_bonus

        direction_entropy = features.get("direction_entropy", 0)
        if direction_entropy < 0.5 and total_interactions > 20:
            score += self.risk_config.automated_pattern_bonus

        key_entropy = features.get("key_press_freq_entropy", 0)
        if key_entropy < 0.3 and total_interactions > 15:
            score += self.risk_config.automated_pattern_bonus

        idle_ratio = features.get("idle_time_ratio", 0)
        if idle_ratio < 0.01 and total_interactions > 20:
            score += 10.0

        return min(score, 100.0)

    def _get_risk_band(self, score: float) -> str:
        if score <= self.risk_config.low_risk_max:
            return "LOW"
        elif score <= self.risk_config.medium_risk_max:
            return "MEDIUM"
        else:
            return "HIGH"

    def _get_decision(self, band: str) -> str:
        if band == "LOW":
            return "ALLOW"
        elif band == "MEDIUM":
            return "REQUEST_MFA"
        else:
            return "BLOCK_AND_ALERT"

    def _get_rule_details(
        self,
        features: Dict[str, float],
        user_baseline: Optional[Dict[str, Dict[str, float]]],
        device_fingerprint_str: Optional[str],
        trusted_devices: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        details = []
        if not user_baseline:
            return details

        typing_speed = features.get("typing_speed_mean", 0)
        typing_baseline = user_baseline.get("typing_speed_mean", {})
        if typing_baseline.get("std", 0) > 0:
            typing_z = abs(typing_speed - typing_baseline.get("mean", 0)) / typing_baseline["std"]
            if typing_z > self.risk_config.typing_speed_std_threshold:
                details.append({
                    "rule": "typing_speed_anomaly",
                    "points": self.risk_config.typing_speed_points,
                    "z_score": round(float(typing_z), 2),
                })

        mouse_speed = features.get("cursor_velocity_mean", 0)
        mouse_baseline = user_baseline.get("cursor_velocity_mean", {})
        if mouse_baseline.get("std", 0) > 0:
            mouse_z = abs(mouse_speed - mouse_baseline.get("mean", 0)) / mouse_baseline["std"]
            if mouse_z > self.risk_config.mouse_speed_std_threshold:
                details.append({
                    "rule": "mouse_speed_anomaly",
                    "points": self.risk_config.mouse_speed_points,
                    "z_score": round(float(mouse_z), 2),
                })

        if device_fingerprint_str and trusted_devices is not None:
            if device_fingerprint_str not in trusted_devices:
                details.append({
                    "rule": "untrusted_device",
                    "points": self.risk_config.device_fingerprint_points,
                })

        return details

    def _get_heuristic_details(
        self,
        features: Dict[str, float],
        session_count: int,
    ) -> List[Dict[str, Any]]:
        details = []
        total_interactions = features.get("total_interactions", 0)

        if total_interactions < self.risk_config.min_interactions:
            details.append({
                "rule": "too_few_interactions",
                "points": 50,
                "interactions": int(total_interactions),
            })

        backspace_rate = features.get("backspace_rate", 0)
        if backspace_rate == 0 and total_interactions > 10:
            details.append({
                "rule": "perfect_typing",
                "points": self.risk_config.perfect_typing_bonus,
            })

        direction_entropy = features.get("direction_entropy", 0)
        if direction_entropy < 0.5 and total_interactions > 20:
            details.append({
                "rule": "automated_mouse_pattern",
                "points": self.risk_config.automated_pattern_bonus,
                "entropy": round(float(direction_entropy), 3),
            })

        return details
