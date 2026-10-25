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


from pathlib import Path


class UserModel:
    _model_store = Path(MLConfig().model_storage_path)
    _model_cache: Dict[Tuple[Any, Any, str], "UserModel"] = {}

    def __init__(
        self,
        user_id: Any,
        config: Optional[MLConfig] = None,
        model_version: int = 1,
        model_type: str = "isolation_forest",
    ):
        self.user_id = user_id
        self.config = config or MLConfig()
        self.version = model_version
        self.model_version = model_version
        self.model_type = model_type
        self.model: Optional[IsolationForest] = None
        self.autoencoder: Optional[Any] = None
        self.one_class_svm: Optional[OneClassSVM] = None
        self.scaler: StandardScaler = StandardScaler()
        self.threshold: float = 0.0
        self.anomaly_threshold: float = 0.05
        self.trained_at: Optional[datetime] = None
        self.training_history: List[Dict] = []
        self.feature_means: Optional[np.ndarray] = None
        self.feature_stds: Optional[np.ndarray] = None
        self.n_samples: int = 0

    @property
    def is_trained(self) -> bool:
        return self.model is not None or self.one_class_svm is not None or self.autoencoder is not None

    @property
    def _model(self) -> Optional[Any]:
        return self.model or self.one_class_svm or self.autoencoder

    @_model.setter
    def _model(self, value: Any):
        if self.model_type == "one_class_svm":
            self.one_class_svm = value
        elif self.model_type == "autoencoder":
            self.autoencoder = value
        else:
            self.model = value

    @property
    def _model_path(self) -> Path:
        return self._get_model_path(self.user_id, self.version, self.model_type, self.config)

    @property
    def model_path(self) -> str:
        return str(self._model_path)

    @property
    def metadata_path(self) -> str:
        p = self._model_path
        return str(p.parent / f"model_v{self.version}_meta.json")

    @classmethod
    def _get_model_path(
        cls,
        user_id: Any,
        version: int = 1,
        model_type: str = "isolation_forest",
        config: Optional[MLConfig] = None,
    ) -> Path:
        store = Path(config.model_storage_path) if config else Path(cls._model_store)
        return store / f"model_v{version}.pkl"

    def train(
        self,
        features: np.ndarray,
        model_type: Optional[str] = None,
        use_autoencoder: bool = False,
        use_svm: bool = False,
    ) -> Dict[str, Any]:
        features = np.asarray(features, dtype=np.float64)
        if features.ndim == 1:
            features = features.reshape(1, -1)

        mtype = model_type or self.model_type

        min_samples = self.config.min_samples_for_training
        if features.shape[0] < min_samples:
            logger.warning(f"Insufficient samples for training: {features.shape[0]} < {min_samples}")
            return {}

        self.scaler.fit(features)
        scaled = self.scaler.transform(features)
        self.feature_means = np.mean(features, axis=0)
        self.feature_stds = np.std(features, axis=0)
        self.n_samples = features.shape[0]

        hp = self.config.model
        results = {}

        if mtype == "autoencoder":
            self._train_autoencoder(scaled)
            self.model_type = "autoencoder"
            if self.autoencoder is None:
                # Fallback to simple dummy model if TF is missing
                class DummyAE:
                    def predict(self, X):
                        return X
                self.autoencoder = DummyAE()
        elif mtype == "one_class_svm" or use_svm:
            self.one_class_svm = OneClassSVM(
                nu=hp.one_class_svm_nu,
                gamma=hp.one_class_svm_gamma,
            )
            self.one_class_svm.fit(scaled)
            svm_scores = self.one_class_svm.score_samples(scaled)
            results["svm_scores"] = svm_scores.tolist()
            self.model_type = "one_class_svm"
        else:
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

    def predict(self, features: np.ndarray) -> Any:
        if not self.is_trained:
            raise ValueError("Model not trained yet")

        features = np.asarray(features, dtype=np.float64)
        is_single = features.ndim == 1 or (features.ndim == 2 and features.shape[0] == 1)
        if features.ndim == 1:
            features = features.reshape(1, -1)

        scaled = self.scaler.transform(features)

        if self.model is not None:
            raw_scores = self.model.score_samples(scaled)
        elif self.one_class_svm is not None:
            raw_scores = self.one_class_svm.score_samples(scaled)
        elif self.autoencoder is not None:
            if hasattr(self.autoencoder, "predict"):
                recon = self.autoencoder.predict(scaled)
                mse = np.mean((scaled - recon) ** 2, axis=1)
                raw_scores = -mse
            else:
                raw_scores = np.zeros(features.shape[0])
        else:
            raw_scores = np.zeros(features.shape[0])

        normalized_scores = np.clip(1.0 / (1.0 + np.exp(raw_scores)), 0.0, 1.0)

        if is_single:
            return float(normalized_scores[0])
        return normalized_scores

    def _save_model(self) -> Path:
        if not self.is_trained:
            raise ValueError("Cannot save an untrained model")
        p = self._model_path
        os.makedirs(p.parent, exist_ok=True)
        with open(p, "wb") as f:
            pickle.dump(self, f)
        return p

    def save(self) -> str:
        p = self._save_model()
        return str(p)

    @classmethod
    def load(
        cls,
        user_id: Any,
        version: int = 1,
        model_type: str = "isolation_forest",
        config: Optional[MLConfig] = None,
    ) -> Optional["UserModel"]:
        p = cls._get_model_path(user_id, version, model_type, config)
        if not p.exists():
            return None
        try:
            with open(p, "rb") as f:
                obj = pickle.load(f)
            if isinstance(obj, UserModel):
                return obj
            if isinstance(obj, dict):
                inst = cls(user_id=user_id, config=config, model_version=version, model_type=model_type)
                inst.model = obj.get("model")
                inst.one_class_svm = obj.get("one_class_svm")
                inst.autoencoder = obj.get("autoencoder")
                inst.scaler = obj.get("scaler", StandardScaler())
                inst.threshold = obj.get("threshold", 0.0)
                return inst
            return None
        except Exception as e:
            logger.warning(f"Failed to load model from {p}: {e}")
            return None

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
