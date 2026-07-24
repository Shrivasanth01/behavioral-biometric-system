import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime


class Explainer:
    def __init__(self):
        self._reason_templates = {
            "typing_speed": "Typing speed {direction} {pct:.0f}% than personal baseline of {baseline:.1f}ms",
            "mouse_velocity": "Mouse movement speed {direction} {pct:.0f}% than historical average of {baseline:.1f} px/ms",
            "mouse_entropy": "Mouse movement entropy {direction} than historical pattern ({value:.2f} vs {baseline:.2f})",
            "session_duration": "Session duration ({value:.0f}s) is {sigma:.1f}{sigma_symbol} below mean session duration ({baseline:.0f}s)",
            "device_fingerprint": "New device fingerprint detected (not in trusted devices)",
            "key_hold": "Key hold duration {direction} {pct:.0f}% than personal baseline of {baseline:.1f}ms",
            "backspace_rate": "Backspace rate {direction} than usual ({value:.3f} vs {baseline:.3f})",
            "navigation_entropy": "Navigation pattern {direction} from historical behavior (entropy {value:.2f} vs {baseline:.2f})",
            "time_of_day": "Login at unusual time ({hour:.0f}:00)",
            "interaction_density": "Interaction density {direction} {pct:.0f}% than typical ({value:.3f} vs {baseline:.3f} events/sec)",
            "click_frequency": "Click frequency {direction} {pct:.0f}% than baseline ({value:.2f} vs {baseline:.2f} clicks/sec)",
            "scroll_speed": "Scroll speed {direction} {pct:.0f}% than normal ({value:.2f} vs {baseline:.2f} px/ms)",
            "direction_entropy": "Movement direction entropy unusually low ({value:.2f}), suggesting automation",
            "idle_time_ratio": "Idle time ratio ({value:.3f}) inconsistent with human behavior pattern",
            "too_few_interactions": "Too few interactions ({value}) to establish behavioral baseline",
            "perfect_typing": "Perfect typing pattern with zero errors detected",
        }

    def explain(
        self,
        risk_result: Dict[str, Any],
        features: Dict[str, float],
        user_baseline: Optional[Dict[str, Dict[str, float]]] = None,
        ml_score: float = 0.0,
    ) -> Dict[str, Any]:
        reasons = []
        feature_contributions = {}
        total_risk = risk_result.get("risk_score", 50)

        feature_scores = self._compute_feature_impact(features, user_baseline)
        sorted_features = sorted(
            feature_scores.items(),
            key=lambda x: abs(x[1]),
            reverse=True,
        )

        top_features = sorted_features[:6]
        for feat_name, impact in top_features:
            if abs(impact) < 0.01:
                continue
            reason = self._generate_reason(feat_name, features, user_baseline, impact)
            if reason:
                reasons.append(reason)
            feature_contributions[feat_name] = round(impact, 2)

        rule_details = risk_result.get("rule_details", [])
        for rule in rule_details:
            rule_name = rule.get("rule", "")
            if rule_name == "untrusted_device":
                reasons.append(self._reason_templates["device_fingerprint"])
                feature_contributions["device_match"] = -0.15
            elif rule_name == "too_few_interactions":
                val = rule.get("interactions", 0)
                reasons.append(self._reason_templates["too_few_interactions"].format(value=val))
                feature_contributions["total_interactions"] = -0.20

        heuristic_details = risk_result.get("heuristic_details", [])
        for h in heuristic_details:
            if h.get("rule") == "perfect_typing":
                reasons.append(self._reason_templates["perfect_typing"])
                feature_contributions["backspace_rate"] = -0.10
            if h.get("rule") == "automated_mouse_pattern":
                entropy = h.get("entropy", 0)
                reasons.append(self._reason_templates["direction_entropy"].format(value=entropy))
                feature_contributions["direction_entropy"] = -0.25

        if not reasons:
            if total_risk <= 30:
                reasons.append("Behavioral pattern matches historical profile within normal range")
            elif total_risk <= 70:
                reasons.append("Minor deviations from baseline behavioral pattern detected")
            else:
                reasons.append("Significant behavioral deviations from established pattern")

        risk_band = risk_result.get("risk_band", "MEDIUM")

        return {
            "risk_score": round(total_risk, 1),
            "risk_band": risk_band,
            "reasons": reasons[:8],
            "feature_contributions": dict(
                sorted(
                    feature_contributions.items(),
                    key=lambda x: abs(x[1]),
                    reverse=True,
                )[:10]
            ),
            "ml_score": round(ml_score, 1),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def explain_cold_start(
        self,
        risk_result: Dict[str, Any],
        features: Dict[str, float],
    ) -> Dict[str, Any]:
        reasons = [
            "Cold start: insufficient session history for personal model",
            "Using global model trained on aggregate population data",
        ]
        total_interactions = features.get("total_interactions", 0)
        if total_interactions < 5:
            reasons.append(f"Only {int(total_interactions)} interactions detected in this session")

        return {
            "risk_score": round(risk_result.get("risk_score", 50), 1),
            "risk_band": risk_result.get("risk_band", "MEDIUM"),
            "reasons": reasons,
            "feature_contributions": {},
            "ml_score": round(risk_result.get("ml_score", 50), 1),
            "timestamp": datetime.utcnow().isoformat(),
            "note": "This decision uses the global model. Risk assessment accuracy will improve as more sessions are collected.",
        }

    def _compute_feature_impact(
        self,
        features: Dict[str, float],
        baseline: Optional[Dict[str, Dict[str, float]]],
    ) -> Dict[str, float]:
        impacts = {}
        if not baseline:
            return impacts

        for feat_name, value in features.items():
            if feat_name not in baseline:
                continue
            stats = baseline[feat_name]
            mean_v = stats.get("mean", 0)
            std_v = stats.get("std", 1)
            if std_v < 1e-8:
                continue

            z_score = (value - mean_v) / std_v
            impact = np.tanh(z_score / 3.0) * -1.0
            impacts[feat_name] = round(float(impact), 4)

        return impacts

    def _generate_reason(
        self,
        feature_name: str,
        features: Dict[str, float],
        baseline: Optional[Dict[str, Dict[str, float]]],
        impact: float,
    ) -> Optional[str]:
        if not baseline or feature_name not in baseline:
            return None

        value = features.get(feature_name, 0)
        stats = baseline[feature_name]
        mean_v = stats.get("mean", 0)
        std_v = stats.get("std", 1)

        if std_v < 1e-8:
            return None

        direction = "faster" if impact < 0 else "slower"
        if impact < 0:
            direction = "higher" if value > mean_v else "lower"
        else:
            direction = "higher" if value > mean_v else "lower"

        pct_change = abs((value - mean_v) / max(mean_v, 1e-8)) * 100
        sigma = abs(value - mean_v) / std_v

        template = self._reason_templates.get(feature_name)
        if template:
            try:
                return template.format(
                    direction=direction,
                    pct=min(pct_change, 999),
                    baseline=mean_v,
                    value=value,
                    sigma=sigma,
                    sigma_symbol="σ" if sigma > 0 else "",
                    hour=(features.get("time_of_day", 0) * 24),
                )
            except (KeyError, ValueError):
                pass

        if sigma > 2.0:
            return f"{feature_name.replace('_', ' ').title()} is {sigma:.1f}σ from baseline ({value:.2f} vs {mean_v:.2f})"

        return None
