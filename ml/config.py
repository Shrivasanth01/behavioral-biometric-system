import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FeatureConfig:
    keystroke_features: List[str] = field(default_factory=lambda: [
        "typing_speed_mean",
        "typing_speed_std",
        "key_hold_mean",
        "key_hold_std",
        "backspace_rate",
        "error_correction_rate",
        "trigram_latency_mean",
        "key_press_freq_entropy",
        "special_key_ratio",
        "number_row_freq",
    ])
    mouse_features: List[str] = field(default_factory=lambda: [
        "cursor_velocity_mean",
        "cursor_velocity_std",
        "cursor_accel_mean",
        "cursor_accel_std",
        "path_length",
        "direction_entropy",
        "click_frequency",
        "double_click_rate",
        "right_click_ratio",
        "scroll_speed_mean",
        "scroll_direction_changes",
        "idle_time_ratio",
    ])
    session_features: List[str] = field(default_factory=lambda: [
        "session_duration",
        "total_interactions",
        "interaction_density",
        "navigation_depth",
        "navigation_entropy",
        "form_focus_consistency",
        "time_of_day",
        "day_of_week",
    ])
    mobile_features: List[str] = field(default_factory=lambda: [
        "swipe_velocity_mean",
        "swipe_velocity_std",
        "swipe_accel_mean",
        "touch_pressure_mean",
        "touch_pressure_std",
        "touch_duration_mean",
        "gesture_complexity",
        "multi_touch_ratio",
    ])

    @property
    def all_features(self) -> List[str]:
        return (
            self.keystroke_features
            + self.mouse_features
            + self.session_features
            + self.mobile_features
        )

    @property
    def feature_count(self) -> int:
        return len(self.all_features)


@dataclass
class ModelHyperparameters:
    isolation_forest_n_estimators: int = 200
    isolation_forest_max_samples: int = 256
    isolation_forest_contamination: float = 0.05
    isolation_forest_n_jobs: int = -1

    autoencoder_encoding_dim: int = 16
    autoencoder_epochs: int = 100
    autoencoder_batch_size: int = 32
    autoencoder_learning_rate: float = 1e-3

    one_class_svm_nu: float = 0.05
    one_class_svm_gamma: str = "scale"

    ensemble_n_estimators: int = 10
    ensemble_subsample_ratio: float = 0.8


@dataclass
class TrainingThresholds:
    min_sessions_for_personal_model: int = 5
    min_samples_for_training: int = 5
    retrain_interval_sessions: int = 10
    max_training_samples: int = 10000
    anomaly_score_percentile_threshold: float = 95.0
    adaptive_k_multiplier: float = 2.5
    adaptive_min_threshold: float = -0.3
    adaptive_max_threshold: float = 0.5


@dataclass
class DriftConfig:
    psi_warning_threshold: float = 0.10
    psi_drift_threshold: float = 0.25
    feature_drift_warning_pct: float = 0.20
    reference_window_size: int = 100
    monitoring_window_size: int = 50
    accuracy_degradation_threshold: float = 0.10
    min_drift_samples: int = 30


@dataclass
class RiskConfig:
    ml_weight: float = 0.5
    rules_weight: float = 0.2
    heuristic_weight: float = 0.3

    low_risk_max: int = 30
    medium_risk_max: int = 60
    high_risk_min: int = 61

    min_interactions: int = 5
    perfect_typing_bonus: int = 10
    automated_pattern_bonus: int = 30

    typing_speed_std_threshold: float = 2.0
    typing_speed_points: int = 30
    mouse_speed_std_threshold: float = 2.0
    mouse_speed_points: int = 25
    session_duration_percentile: float = 1.0
    session_duration_points: int = 20
    device_fingerprint_points: int = 15
    suspicious_time_points: int = 10
    navigation_entropy_points: int = 20


@dataclass
class CacheConfig:
    model_cache_ttl_seconds: int = 3600
    profile_cache_ttl_seconds: int = 1800
    max_cached_models: int = 100
    max_cached_profiles: int = 1000


@dataclass
class MLConfig:
    _instance: Optional["MLConfig"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.feature = FeatureConfig()
        self.model = ModelHyperparameters()
        self.training = TrainingThresholds()
        self.drift = DriftConfig()
        self.risk = RiskConfig()
        self.cache = CacheConfig()
        self.model_storage_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "model_store"
        )
        self.profile_storage_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "profile_store"
        )
        self.registry_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "model_registry"
        )
        self.log_level = "INFO"
        for p in [self.model_storage_path, self.profile_storage_path, self.registry_path]:
            os.makedirs(p, exist_ok=True)

    @property
    def profile_store(self) -> str:
        return self.profile_storage_path

    @profile_store.setter
    def profile_store(self, value: str):
        self.profile_storage_path = value
        os.makedirs(value, exist_ok=True)

    @property
    def model_store(self) -> str:
        return self.model_storage_path

    @model_store.setter
    def model_store(self, value: str):
        self.model_storage_path = value
        os.makedirs(value, exist_ok=True)

    @property
    def model_dir(self) -> str:
        return self.model_storage_path

    @model_dir.setter
    def model_dir(self, value: str):
        self.model_storage_path = value
        os.makedirs(value, exist_ok=True)

    @property
    def drift_threshold_psi(self) -> float:
        return self.drift.psi_drift_threshold

    @drift_threshold_psi.setter
    def drift_threshold_psi(self, value: float):
        self.drift.psi_drift_threshold = value
        self.drift.psi_warning_threshold = value

    @property
    def min_samples_for_training(self) -> int:
        return self.training.min_samples_for_training

    @min_samples_for_training.setter
    def min_samples_for_training(self, value: int):
        self.training.min_samples_for_training = value

    @property
    def anomaly_threshold(self) -> float:
        return self.training.anomaly_score_percentile_threshold / 100.0

    @anomaly_threshold.setter
    def anomaly_threshold(self, value: float):
        self.training.anomaly_score_percentile_threshold = value * 100.0
