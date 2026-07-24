import numpy as np
import pickle
import os
import json
import logging
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

from ml.config import MLConfig, ModelHyperparameters, TrainingThresholds

logger = logging.getLogger(__name__)


class UserModel:
    def __init__(
        self,
        user_id: str,
        config: Optional[MLConfig] = None,
    ):
        self.user_id = user_id
        self.config = config or MLConfig()
        self.model_type = "isolation_forest"
        self.model: Optional[IsolationForest] = None
        self.autoencoder: Optional[Any] = None
        self.one_class_svm: Optional[OneClassSVM] = None
        self.scaler: StandardScaler = StandardScaler()
        self.threshold: float = 0.0
        self.version: int = 0
        self.trained_at: Optional[datetime] = None
        self.training_history: List[Dict] = []
        self.feature_means: Optional[np.ndarray] = None
        self.feature_stds: Optional[np.ndarray] = None
        self.n_samples: int = 0

    @property
    def model_path(self) -> str:
        return os.path.join(
            self.config.model_storage_path,
            self.user_id,
            f"model_v{self.version}.pkl",
        )

    @property
    def metadata_path(self) -> str:
        return os.path.join(
            self.config.model_storage_path,
            self.user_id,
            f"model_v{self.version}_meta.json",
        )

    def train(
        self,
        features: np.ndarray,
        model_type: str = "isolation_forest",
        use_autoencoder: bool = False,
        use_svm: bool = False,
    ) -> Dict[str, Any]:
        features = np.asarray(features, dtype=np.float64)
        if features.ndim == 1:
            features = features.reshape(1, -1)
        if features.shape[0] < 3:
            raise ValueError(f"Need at least 3 samples, got {features.shape[0]}")

        self.scaler.fit(features)
        scaled = self.scaler.transform(features)
        self.feature_means = np.mean(features, axis=0)
        self.feature_stds = np.std(features, axis=0)
        self.n_samples = features.shape[0]

        hp = self.config.model
        results = {}

        if model_type == "isolation_forest" or not use_svm:
            self.model = IsolationForest(
                n_estimators=hp.isolation_forest_n_estimators,
                max_samples=min(hp.isolation_forest_max_samples, features.shape[0]),
                contamination=hp.isolation_forest_contamination,
                n_jobs=hp.isolation_forest_n_jobs,
                random_state=42,
            )
            self.model.fit(scaled)
            scores = self.model.score_samples(scaled)
            self.threshold = self._compute_adaptive_threshold(scores)
            results["iforest_scores"] = scores.tolist()
            self.model_type = "isolation_forest"

        if use_svm:
            self.one_class_svm = OneClassSVM(
                nu=hp.one_class_svm_nu,
                gamma=hp.one_class_svm_gamma,
            )
            self.one_class_svm.fit(scaled)
            svm_scores = self.one_class_svm.score_samples(scaled)
            results["svm_scores"] = svm_scores.tolist()

        if use_autoencoder:
            self._train_autoencoder(scaled)

        self.version += 1
        self.trained_at = datetime.utcnow()
        self.training_history.append({
            "version": self.version,
            "timestamp": self.trained_at.isoformat(),
            "n_samples": self.n_samples,
            "threshold": float(self.threshold),
            "model_type": self.model_type,
        })

        results["version"] = self.version
        results["threshold"] = float(self.threshold)
        results["n_samples"] = self.n_samples
        return results

    def predict(self, features: np.ndarray) -> Tuple[float, Dict[str, float]]:
        features = np.asarray(features, dtype=np.float64)
        if features.ndim == 1:
            features = features.reshape(1, -1)

        if self.model is None and self.one_class_svm is None:
            raise RuntimeError("Model not trained yet")

        scaled = self.scaler.transform(features)
        feature_scores = {}

        if self.model is not None:
            raw_score = self.model.score_samples(scaled)[0]
            anomaly_score = self._normalize_anomaly_score(raw_score)
            feature_contributions = self._compute_feature_contributions(features[0], raw_score)
            feature_scores["isolation_forest"] = anomaly_score
        elif self.one_class_svm is not None:
            raw_score = self.one_class_svm.score_samples(scaled)[0]
            anomaly_score = self._normalize_anomaly_score(raw_score)
            feature_contributions = self._compute_feature_contributions(features[0], raw_score)
            feature_scores["one_class_svm"] = anomaly_score
        else:
            anomaly_score = 0.0
            feature_contributions = {}

        return anomaly_score, feature_contributions

    def score_batch(self, features: np.ndarray) -> np.ndarray:
        features = np.asarray(features, dtype=np.float64)
        if self.model is None:
            raise RuntimeError("Model not trained yet")
        scaled = self.scaler.transform(features)
        raw_scores = self.model.score_samples(scaled)
        return np.array([self._normalize_anomaly_score(s) for s in raw_scores])

    def update_threshold(self, new_scores: np.ndarray):
        all_scores = np.concatenate([
            self.model.score_samples(self.scaler.transform(
                np.random.randn(min(100, self.n_samples), len(self.feature_means))
            )),
            new_scores,
        ])
        self.threshold = self._compute_adaptive_threshold(all_scores)

    def save(self) -> str:
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump({
                "user_id": self.user_id,
                "version": self.version,
                "model_type": self.model_type,
                "model": self.model,
                "one_class_svm": self.one_class_svm,
                "autoencoder": self.autoencoder,
                "scaler": self.scaler,
                "threshold": self.threshold,
                "feature_means": self.feature_means,
                "feature_stds": self.feature_stds,
                "n_samples": self.n_samples,
            }, f)

        metadata = {
            "user_id": self.user_id,
            "version": self.version,
            "model_type": self.model_type,
            "trained_at": self.trained_at.isoformat() if self.trained_at else None,
            "threshold": float(self.threshold),
            "n_samples": self.n_samples,
            "feature_means": self.feature_means.tolist() if self.feature_means is not None else None,
            "feature_stds": self.feature_stds.tolist() if self.feature_stds is not None else None,
            "training_history": self.training_history,
        }
        with open(self.metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return self.model_path

    def load(self, version: Optional[int] = None) -> bool:
        if version is not None:
            self.version = version

        model_dir = os.path.join(self.config.model_storage_path, self.user_id)
        if not os.path.exists(model_dir):
            logger.warning(f"Model directory not found at {model_dir}")
            return False

        if version is None:
            import glob as glob_mod
            pattern = os.path.join(model_dir, "model_v*.pkl")
            files = sorted(glob_mod.glob(pattern))
            if not files:
                logger.warning(f"No model files found for {self.user_id}")
                return False
            latest = files[-1]
            version_str = os.path.basename(latest).replace("model_v", "").replace(".pkl", "")
            self.version = int(version_str) if version_str.isdigit() else 0
        path = self.model_path
        if not os.path.exists(path):
            logger.warning(f"Model not found at {path}")
            return False

        with open(path, "rb") as f:
            data = pickle.load(f)

        self.model = data.get("model")
        self.one_class_svm = data.get("one_class_svm")
        self.autoencoder = data.get("autoencoder")
        self.scaler = data.get("scaler", StandardScaler())
        self.threshold = data.get("threshold", 0.0)
        self.feature_means = data.get("feature_means")
        self.feature_stds = data.get("feature_stds")
        self.n_samples = data.get("n_samples", 0)
        self.model_type = data.get("model_type", "isolation_forest")

        meta_path = self.metadata_path
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                meta = json.load(f)
            self.trained_at = datetime.fromisoformat(meta["trained_at"]) if meta.get("trained_at") else None
            self.training_history = meta.get("training_history", [])

        return True

    def get_feature_importance(self) -> Optional[np.ndarray]:
        if self.model is None:
            return None
        if hasattr(self.model, "feature_importances_"):
            return self.model.feature_importances_
        if self.feature_stds is not None:
            return 1.0 / (self.feature_stds + 1e-8)
        return None

    def _compute_adaptive_threshold(self, scores: np.ndarray) -> float:
        k = self.config.training.adaptive_k_multiplier
        mean_s = np.mean(scores)
        std_s = np.std(scores)
        threshold = mean_s - k * std_s
        threshold = max(threshold, self.config.training.adaptive_min_threshold)
        threshold = min(threshold, self.config.training.adaptive_max_threshold)
        return float(threshold)

    def _normalize_anomaly_score(self, raw_score: float) -> float:
        score = float(raw_score)
        if self.threshold != 0:
            normalized = (self.threshold - score) / abs(self.threshold)
        else:
            normalized = -score
        normalized = np.clip(normalized, -1.0, 1.0)
        return (normalized + 1.0) * 50.0

    def _compute_feature_contributions(
        self,
        feature_vector: np.ndarray,
        raw_score: float,
    ) -> Dict[str, float]:
        contributions = {}
        if self.feature_means is None or self.feature_stds is None:
            return contributions

        deviations = (feature_vector - self.feature_means) / (self.feature_stds + 1e-8)
        total_dev = np.sum(np.abs(deviations)) + 1e-8
        direction = -1.0 if raw_score < 0 else 1.0

        cfg = self.config.feature
        all_feats = cfg.all_features
        for i in range(min(len(deviations), len(all_feats))):
            contributions[all_feats[i]] = direction * float(deviations[i] / total_dev)

        return contributions

    def _train_autoencoder(self, scaled: np.ndarray):
        try:
            from tensorflow import keras
            from tensorflow.keras import layers, Model, optimizers
        except ImportError:
            logger.warning("TensorFlow not available, skipping autoencoder")
            return

        n_features = scaled.shape[1]
        encoding_dim = min(self.config.model.autoencoder_encoding_dim, n_features // 2)

        input_layer = keras.Input(shape=(n_features,))
        encoded = layers.Dense(encoding_dim, activation="relu")(input_layer)
        encoded = layers.Dense(max(encoding_dim // 2, 2), activation="relu")(encoded)
        decoded = layers.Dense(encoding_dim, activation="relu")(encoded)
        decoded = layers.Dense(n_features, activation="linear")(decoded)

        autoencoder = Model(inputs=input_layer, outputs=decoded)
        autoencoder.compile(
            optimizer=optimizers.Adam(learning_rate=self.config.model.autoencoder_learning_rate),
            loss="mse",
        )

        autoencoder.fit(
            scaled, scaled,
            epochs=self.config.model.autoencoder_epochs,
            batch_size=self.config.model.autoencoder_batch_size,
            verbose=0,
            shuffle=True,
        )

        self.autoencoder = autoencoder
