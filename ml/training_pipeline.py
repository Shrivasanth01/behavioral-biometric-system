import numpy as np
import pandas as pd
import logging
from typing import Optional, List, Dict, Tuple, Any
from datetime import datetime

from ml.config import MLConfig
from ml.feature_engineering import FeatureEngine
from ml.models.user_model import UserModel
from ml.models.global_model import GlobalModel
from ml.behavioral_profile import BehavioralProfileManager
from ml.model_registry import ModelRegistry

logger = logging.getLogger(__name__)


class TrainingPipeline:
    def __init__(
        self,
        config: Optional[MLConfig] = None,
        feature_engine: Optional[FeatureEngine] = None,
        profile_manager: Optional[BehavioralProfileManager] = None,
        model_registry: Optional[ModelRegistry] = None,
        global_model: Optional[GlobalModel] = None,
    ):
        self.config = config or MLConfig()
        self.feature_engine = feature_engine or FeatureEngine(self.config)
        self.profile_manager = profile_manager or BehavioralProfileManager(self.config)
        self.model_registry = model_registry or ModelRegistry(self.config)
        self.global_model = global_model or GlobalModel(self.config)
        self._is_global_loaded = False

    def ensure_global_model(self, event_batches: Optional[List[List[Dict]]] = None):
        if self._is_global_loaded:
            return True
        loaded = self.global_model.load()
        if loaded:
            self._is_global_loaded = True
            return True
        if event_batches and len(event_batches) >= 10:
            logger.info("Training new global model")
            features_df = self.feature_engine.extract_batch(event_batches)
            features = features_df.values.astype(np.float64)
            self.global_model.train(features)
            self.global_model.save()
            self._is_global_loaded = True
            return True
        return False

    def train_for_user(
        self,
        user_id: str,
        event_batches: List[List[Dict]],
        session_risk_scores: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        profile = self.profile_manager.get_or_create_profile(user_id)
        session_risk_scores = session_risk_scores or [0.0] * len(event_batches)

        low_risk_batches = []
        for i, (batch, risk) in enumerate(zip(event_batches, session_risk_scores)):
            if risk <= self.config.risk.medium_risk_max:
                low_risk_batches.append(batch)
            else:
                logger.info(f"Skipping high-risk session {i} for user {user_id}")

        if not low_risk_batches:
            return {"trained": False, "reason": "no_low_risk_sessions"}

        features_df = self.feature_engine.extract_batch(low_risk_batches)
        features = features_df.values.astype(np.float64)

        session_count = len(low_risk_batches)
        result = {"trained": False, "version": None, "model_type": None}

        if session_count < self.config.training.min_sessions_for_personal_model:
            result["reason"] = "cold_start"
            result["message"] = f"Need {self.config.training.min_sessions_for_personal_model - session_count} more sessions"
            profile.cold_start = True
        else:
            model = UserModel(user_id, self.config)
            model_exists = model.load()

            if model_exists:
                existing_features = self._load_previous_features(user_id)
                if existing_features is not None:
                    features = np.vstack([existing_features, features])
                features = features[-self.config.training.max_training_samples:]

            train_result = model.train(features)
            model.save()

            profile.profile_version += 1
            profile.model_version = f"v{model.version}"
            profile.session_count = len(event_batches)
            profile.last_trained_at = datetime.utcnow()
            profile.cold_start = False

            feature_stats = self._compute_feature_stats(features, features_df.columns.tolist())
            profile.feature_statistics = feature_stats

            self.profile_manager.save_profile(profile)

            self.model_registry.register_model(
                user_id=user_id,
                version=model.version,
                model_path=model.model_path,
                metrics={
                    "n_samples": model.n_samples,
                    "threshold": float(model.threshold),
                    "session_count": session_count,
                },
            )

            result["trained"] = True
            result["version"] = model.version
            result["model_type"] = model.model_type
            result["n_samples"] = model.n_samples
            result["threshold"] = float(model.threshold)

        return result

    def retrain_if_needed(
        self,
        user_id: str,
        event_batches: List[List[Dict]],
        session_risk_scores: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        profile = self.profile_manager.get_or_create_profile(user_id)
        if profile.cold_start:
            return self.train_for_user(user_id, event_batches, session_risk_scores)

        if profile.session_count % self.config.training.retrain_interval_sessions == 0:
            return self.train_for_user(user_id, event_batches, session_risk_scores)

        return {"trained": False, "reason": "retrain_not_due"}

    def retrain_global_model(self, all_user_batches: Dict[str, List[List[Dict]]]) -> Dict[str, Any]:
        all_features = []
        for user_id, batches in all_user_batches.items():
            profile = self.profile_manager.get_profile(user_id)
            if profile and not profile.cold_start:
                features_df = self.feature_engine.extract_batch(batches)
                all_features.append(features_df.values)

        if not all_features:
            return {"trained": False, "reason": "no_data"}

        combined = np.vstack(all_features)
        if combined.shape[0] < 10:
            return {"trained": False, "reason": "insufficient_data"}

        result = self.global_model.train(combined)
        self.global_model.save()
        self._is_global_loaded = True
        return {"trained": True, **result}

    def get_fallback_score(self, events: List[Dict]) -> float:
        features = self.feature_engine.extract_all(events)
        feature_vec = np.array([list(features.values())], dtype=np.float64)
        try:
            score, _ = self.global_model.predict(feature_vec)
            return score
        except RuntimeError:
            return 50.0

    def _load_previous_features(self, user_id: str) -> Optional[np.ndarray]:
        try:
            model = UserModel(user_id, self.config)
            if model.load():
                history = model.training_history
                if history:
                    return None
                return None
        except Exception:
            pass
        return None

    def _compute_feature_stats(
        self,
        features: np.ndarray,
        feature_names: List[str],
    ) -> Dict[str, Dict[str, float]]:
        stats = {}
        for i, name in enumerate(feature_names):
            col = features[:, i]
            stats[name] = {
                "mean": float(np.mean(col)),
                "std": float(np.std(col)),
                "min": float(np.min(col)),
                "max": float(np.max(col)),
                "p25": float(np.percentile(col, 25)),
                "p50": float(np.percentile(col, 50)),
                "p75": float(np.percentile(col, 75)),
            }
        return stats
