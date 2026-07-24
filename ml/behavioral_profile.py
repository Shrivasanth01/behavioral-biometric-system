import json
import os
import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from threading import Lock

from ml.config import MLConfig

logger = logging.getLogger(__name__)


class BehavioralProfile:
    def __init__(
        self,
        user_id: str,
        profile_version: int = 0,
        model_version: str = "",
        session_count: int = 0,
        last_trained_at: Optional[datetime] = None,
        feature_statistics: Optional[Dict[str, Dict[str, float]]] = None,
        device_fingerprints: Optional[List[str]] = None,
        risk_history: Optional[List[Tuple]] = None,
        drift_status: str = "STABLE",
        cold_start: bool = True,
    ):
        self.user_id = user_id
        self.profile_version = profile_version
        self.model_version = model_version
        self.session_count = session_count
        self.last_trained_at = last_trained_at or datetime.utcnow()
        self.feature_statistics = feature_statistics or {}
        self.device_fingerprints = device_fingerprints or []
        self.risk_history = risk_history or []
        self.drift_status = drift_status
        self.cold_start = cold_start

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "profile_version": self.profile_version,
            "model_version": self.model_version,
            "session_count": self.session_count,
            "last_trained_at": self.last_trained_at.isoformat() if self.last_trained_at else None,
            "feature_statistics": self.feature_statistics,
            "device_fingerprints": self.device_fingerprints,
            "risk_history": [
                {"timestamp": ts.isoformat() if hasattr(ts, "isoformat") else str(ts), "score": s, "band": b}
                for ts, s, b in self.risk_history[-100:]
            ],
            "drift_status": self.drift_status,
            "cold_start": self.cold_start,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BehavioralProfile":
        risk_history = []
        for entry in data.get("risk_history", []):
            try:
                ts = datetime.fromisoformat(entry["timestamp"]) if isinstance(entry.get("timestamp"), str) else datetime.utcnow()
            except (ValueError, TypeError):
                ts = datetime.utcnow()
            risk_history.append((ts, entry.get("score", 0), entry.get("band", "LOW")))

        last_trained = None
        if data.get("last_trained_at"):
            try:
                last_trained = datetime.fromisoformat(data["last_trained_at"])
            except (ValueError, TypeError):
                last_trained = None

        return cls(
            user_id=data.get("user_id", ""),
            profile_version=data.get("profile_version", 0),
            model_version=data.get("model_version", ""),
            session_count=data.get("session_count", 0),
            last_trained_at=last_trained,
            feature_statistics=data.get("feature_statistics", {}),
            device_fingerprints=data.get("device_fingerprints", []),
            risk_history=risk_history,
            drift_status=data.get("drift_status", "STABLE"),
            cold_start=data.get("cold_start", True),
        )


class BehavioralProfileManager:
    def __init__(self, config: Optional[MLConfig] = None):
        self.config = config or MLConfig()
        self._cache: Dict[str, "ProfileCacheEntry"] = {}
        self._lock = Lock()

    def get_profile(self, user_id: str) -> Optional[BehavioralProfile]:
        cached = self._get_cached(user_id)
        if cached:
            return cached

        profile = self._load_from_disk(user_id)
        if profile:
            self._cache_profile(user_id, profile)
        return profile

    def get_or_create_profile(self, user_id: str) -> BehavioralProfile:
        profile = self.get_profile(user_id)
        if profile is None:
            profile = BehavioralProfile(user_id=user_id)
            self.save_profile(profile)
        return profile

    def save_profile(self, profile: BehavioralProfile):
        profile_path = self._profile_path(profile.user_id)
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)

        with open(profile_path, "w") as f:
            json.dump(profile.to_dict(), f, indent=2, default=str)

        self._cache_profile(profile.user_id, profile)

    def delete_profile(self, user_id: str):
        profile_path = self._profile_path(user_id)
        if os.path.exists(profile_path):
            os.remove(profile_path)
        self._evict_cache(user_id)

    def add_risk_event(self, user_id: str, score: float, band: str):
        profile = self.get_or_create_profile(user_id)
        profile.risk_history.append((datetime.utcnow(), score, band))
        if len(profile.risk_history) > 1000:
            profile.risk_history = profile.risk_history[-500:]
        self.save_profile(profile)

    def add_device_fingerprint(self, user_id: str, fingerprint: str):
        profile = self.get_or_create_profile(user_id)
        if fingerprint not in profile.device_fingerprints:
            profile.device_fingerprints.append(fingerprint)
            self.save_profile(profile)

    def get_trusted_devices(self, user_id: str) -> List[str]:
        profile = self.get_profile(user_id)
        if profile:
            return profile.device_fingerprints
        return []

    def update_drift_status(self, user_id: str, drift_status: str):
        profile = self.get_or_create_profile(user_id)
        profile.drift_status = drift_status
        self.save_profile(profile)

    def get_all_user_ids(self) -> List[str]:
        store_path = self.config.profile_storage_path
        if not os.path.exists(store_path):
            return []
        return [
            f.replace("_profile.json", "")
            for f in os.listdir(store_path)
            if f.endswith("_profile.json")
        ]

    def get_profiles_needing_retraining(self, max_sessions: int = 100) -> List[str]:
        all_users = self.get_all_user_ids()
        needs_retrain = []
        for uid in all_users:
            profile = self.get_profile(uid)
            if profile and profile.session_count >= max_sessions:
                needs_retrain.append(uid)
        return needs_retrain

    def get_cold_start_users(self) -> List[str]:
        all_users = self.get_all_user_ids()
        return [uid for uid in all_users if self.get_profile(uid) and self.get_profile(uid).cold_start]

    def _profile_path(self, user_id: str) -> str:
        return os.path.join(
            self.config.profile_storage_path,
            f"{user_id}_profile.json",
        )

    def _load_from_disk(self, user_id: str) -> Optional[BehavioralProfile]:
        profile_path = self._profile_path(user_id)
        if not os.path.exists(profile_path):
            return None
        try:
            with open(profile_path, "r") as f:
                data = json.load(f)
            return BehavioralProfile.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to load profile for {user_id}: {e}")
            return None

    def _get_cached(self, user_id: str) -> Optional[BehavioralProfile]:
        with self._lock:
            entry = self._cache.get(user_id)
            if entry and not entry.is_expired:
                return entry.profile
            if entry:
                del self._cache[user_id]
        return None

    def _cache_profile(self, user_id: str, profile: BehavioralProfile):
        with self._lock:
            if len(self._cache) >= self.config.cache.max_cached_profiles:
                oldest_key = min(
                    self._cache.keys(),
                    key=lambda k: self._cache[k].created_at,
                )
                del self._cache[oldest_key]
            self._cache[user_id] = ProfileCacheEntry(profile, self.config.cache.profile_cache_ttl_seconds)

    def _evict_cache(self, user_id: str):
        with self._lock:
            self._cache.pop(user_id, None)


class ProfileCacheEntry:
    def __init__(self, profile: BehavioralProfile, ttl_seconds: int = 1800):
        self.profile = profile
        self.created_at = datetime.utcnow()
        self.ttl_seconds = ttl_seconds

    @property
    def is_expired(self) -> bool:
        return (datetime.utcnow() - self.created_at).total_seconds() > self.ttl_seconds
