import numpy as np
import logging
from typing import Optional, List, Dict, Tuple, Any
from datetime import datetime, timedelta
import threading

from ml.config import MLConfig
from ml.feature_engineering import FeatureEngine
from ml.models.user_model import UserModel
from ml.models.global_model import GlobalModel
from ml.behavioral_profile import BehavioralProfileManager

logger = logging.getLogger(__name__)


class ModelCacheEntry:
    def __init__(self, model: UserModel, ttl_seconds: int = 3600):
        self.model = model
        self.created_at = datetime.utcnow()
        self.ttl_seconds = ttl_seconds

    @property
    def is_expired(self) -> bool:
        return (datetime.utcnow() - self.created_at).total_seconds() > self.ttl_seconds


class InferencePipeline:
    def __init__(
        self,
        config: Optional[MLConfig] = None,
        feature_engine: Optional[FeatureEngine] = None,
        global_model: Optional[GlobalModel] = None,
        profile_manager: Optional[BehavioralProfileManager] = None,
    ):
        self.config = config or MLConfig()
        self.feature_engine = feature_engine or FeatureEngine(self.config)
        self.global_model = global_model or GlobalModel(self.config)
        self.profile_manager = profile_manager or BehavioralProfileManager(self.config)
        self._model_cache: Dict[str, ModelCacheEntry] = {}
        self._cache_lock = threading.Lock()
        self._global_loaded = False

    def score(
        self,
        user_id: str,
        events: List[Dict],
        include_mobile: bool = False,
        device_fingerprint: Optional[str] = None,
    ) -> Dict[str, Any]:
        features = self.feature_engine.extract_all(events, include_mobile=include_mobile)
        feature_vec = np.array([list(features.values())], dtype=np.float64)

        user_model = self._load_user_model(user_id)
        profile = self.profile_manager.get_or_create_profile(user_id)

        anomaly_score = 50.0
        feature_contributions = {}
        model_source = "global"

        if user_model is not None and not profile.cold_start:
            try:
                anomaly_score, feature_contributions = user_model.predict(feature_vec)
                model_source = f"personal_v{user_model.version}"
            except Exception as e:
                logger.warning(f"User model prediction failed for {user_id}: {e}")
                anomaly_score, _ = self._global_predict(feature_vec)
                model_source = "global_fallback"
        else:
            anomaly_score, _ = self._global_predict(feature_vec)
            model_source = "global"

        normalized_score = round(float(anomaly_score), 2)
        normalized_score = max(0.0, min(100.0, normalized_score))

        return {
            "user_id": user_id,
            "ml_score": normalized_score,
            "feature_contributions": feature_contributions,
            "model_source": model_source,
            "features": features,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def score_batch(
        self,
        user_id: str,
        event_batches: List[List[Dict]],
        include_mobile: bool = False,
    ) -> List[Dict[str, Any]]:
        return [
            self.score(user_id, batch, include_mobile=include_mobile)
            for batch in event_batches
        ]

    def _global_predict(self, feature_vec: np.ndarray) -> Tuple[float, float]:
        if not self._global_loaded:
            self._global_loaded = self.global_model.load()
        if self._global_loaded:
            try:
                return self.global_model.predict(feature_vec)
            except Exception:
                pass
        return 50.0, 0.0

    def _load_user_model(self, user_id: str) -> Optional[UserModel]:
        with self._cache_lock:
            if user_id in self._model_cache:
                entry = self._model_cache[user_id]
                if not entry.is_expired:
                    return entry.model
                del self._model_cache[user_id]

        profile = self.profile_manager.get_profile(user_id)
        if profile is None or profile.cold_start:
            return None

        model = UserModel(user_id, self.config)
        if model.load():
            with self._cache_lock:
                if len(self._model_cache) >= self.config.cache.max_cached_models:
                    oldest_key = min(
                        self._model_cache.keys(),
                        key=lambda k: self._model_cache[k].created_at,
                    )
                    del self._model_cache[oldest_key]
                self._model_cache[user_id] = ModelCacheEntry(
                    model, self.config.cache.model_cache_ttl_seconds
                )
            return model
        return None

    def invalidate_cache(self, user_id: Optional[str] = None):
        with self._cache_lock:
            if user_id:
                self._model_cache.pop(user_id, None)
            else:
                self._model_cache.clear()

    def get_cached_user_ids(self) -> List[str]:
        with self._cache_lock:
            return list(self._model_cache.keys())
