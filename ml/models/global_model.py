import numpy as np
import pickle
import os
import json
import logging
from typing import Optional, List, Dict, Tuple, Any
from datetime import datetime

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from ml.config import MLConfig

logger = logging.getLogger(__name__)


class GlobalModel:
    def __init__(self, config: Optional[MLConfig] = None):
        self.config = config or MLConfig()
        self.ensemble: List[IsolationForest] = []
        self.scaler: StandardScaler = StandardScaler()
        self.threshold: float = 0.0
        self.version: int = 0
        self.trained_at: Optional[datetime] = None
        self.n_samples: int = 0
        self.feature_means: Optional[np.ndarray] = None
        self.feature_stds: Optional[np.ndarray] = None
        self.performance_metrics: Dict[str, float] = {}

    @property
    def model_path(self) -> str:
        return os.path.join(
            self.config.model_storage_path,
            "_global_",
            f"global_model_v{self.version}.pkl",
        )

    @property
    def metadata_path(self) -> str:
        return os.path.join(
            self.config.model_storage_path,
            "_global_",
            f"global_model_v{self.version}_meta.json",
        )

    def train(self, features: np.ndarray) -> Dict[str, Any]:
        features = np.asarray(features, dtype=np.float64)
        if features.ndim == 1:
            features = features.reshape(1, -1)
        if features.shape[0] < 10:
            raise ValueError(f"Need at least 10 samples for global model, got {features.shape[0]}")

        self.scaler.fit(features)
        scaled = self.scaler.transform(features)
        self.feature_means = np.mean(features, axis=0)
        self.feature_stds = np.std(features, axis=0)
        self.n_samples = features.shape[0]

        hp = self.config.model
        n_estimators = hp.ensemble_n_estimators
        subsample = max(int(features.shape[0] * hp.ensemble_subsample_ratio), 10)

        self.ensemble = []
        all_scores = []

        for i in range(n_estimators):
            rng = np.random.RandomState(42 + i)
            indices = rng.choice(features.shape[0], size=subsample, replace=True)
            subset = scaled[indices]

            model = IsolationForest(
                n_estimators=hp.isolation_forest_n_estimators // max(n_estimators // 5, 1),
                max_samples=min(hp.isolation_forest_max_samples, subset.shape[0]),
                contamination=hp.isolation_forest_contamination,
                n_jobs=1,
                random_state=42 + i,
            )
            model.fit(subset)
            self.ensemble.append(model)
            all_scores.extend(model.score_samples(subset).tolist())

        all_scores = np.array(all_scores)
        self.threshold = float(np.percentile(all_scores, 5))
        self.version += 1
        self.trained_at = datetime.utcnow()

        results = {
            "version": self.version,
            "n_estimators": len(self.ensemble),
            "n_samples": self.n_samples,
            "threshold": float(self.threshold),
            "trained_at": self.trained_at.isoformat(),
        }
        return results

    def predict(self, features: np.ndarray) -> Tuple[float, float]:
        features = np.asarray(features, dtype=np.float64)
        if features.ndim == 1:
            features = features.reshape(1, -1)

        if not self.ensemble:
            raise RuntimeError("Global model not trained yet")

        scaled = self.scaler.transform(features)

        scores = []
        for model in self.ensemble:
            scores.append(model.score_samples(scaled)[0])

        mean_score = float(np.mean(scores))
        std_score = float(np.std(scores)) if len(scores) > 1 else 0.0
        normalized = self._normalize_anomaly_score(mean_score)

        return normalized, mean_score

    def score_batch(self, features: np.ndarray) -> np.ndarray:
        features = np.asarray(features, dtype=np.float64)
        if not self.ensemble:
            raise RuntimeError("Global model not trained yet")
        scaled = self.scaler.transform(features)
        all_scores = np.zeros((features.shape[0], len(self.ensemble)))
        for i, model in enumerate(self.ensemble):
            all_scores[:, i] = model.score_samples(scaled)
        mean_scores = np.mean(all_scores, axis=1)
        return np.array([self._normalize_anomaly_score(s) for s in mean_scores])

    def save(self) -> str:
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump({
                "version": self.version,
                "ensemble": self.ensemble,
                "scaler": self.scaler,
                "threshold": self.threshold,
                "feature_means": self.feature_means,
                "feature_stds": self.feature_stds,
                "n_samples": self.n_samples,
                "performance_metrics": self.performance_metrics,
            }, f)

        metadata = {
            "version": self.version,
            "n_estimators": len(self.ensemble),
            "trained_at": self.trained_at.isoformat() if self.trained_at else None,
            "threshold": float(self.threshold),
            "n_samples": self.n_samples,
            "performance_metrics": self.performance_metrics,
        }
        with open(self.metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return self.model_path

    def load(self) -> bool:
        import glob as glob_mod
        pattern = os.path.join(
            self.config.model_storage_path,
            "_global_",
            "global_model_v*.pkl",
        )
        files = sorted(glob_mod.glob(pattern))
        if not files:
            logger.warning("No global model found")
            return False

        latest = files[-1]
        with open(latest, "rb") as f:
            data = pickle.load(f)

        self.ensemble = data.get("ensemble", [])
        self.scaler = data.get("scaler", StandardScaler())
        self.threshold = data.get("threshold", 0.0)
        self.feature_means = data.get("feature_means")
        self.feature_stds = data.get("feature_stds")
        self.n_samples = data.get("n_samples", 0)
        self.performance_metrics = data.get("performance_metrics", {})

        version_str = os.path.basename(latest).replace("global_model_v", "").replace(".pkl", "")
        self.version = int(version_str) if version_str.isdigit() else 0

        meta_path = latest.replace(".pkl", "_meta.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                meta = json.load(f)
            self.trained_at = datetime.fromisoformat(meta["trained_at"]) if meta.get("trained_at") else None

        return True

    def add_performance_metric(self, name: str, value: float):
        self.performance_metrics[name] = value

    def _normalize_anomaly_score(self, raw_score: float) -> float:
        score = float(raw_score)
        if self.threshold != 0:
            normalized = (self.threshold - score) / abs(self.threshold)
        else:
            normalized = -score
        normalized = np.clip(normalized, -1.0, 1.0)
        return (normalized + 1.0) * 50.0

    def get_feature_importance(self) -> Optional[np.ndarray]:
        if not self.ensemble or self.feature_stds is None:
            return None
        return 1.0 / (self.feature_stds + 1e-8)
