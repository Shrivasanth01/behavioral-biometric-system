import json
import os
import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from threading import Lock

from ml.config import MLConfig

logger = logging.getLogger(__name__)


class ModelRegistryEntry:
    def __init__(
        self,
        user_id: str,
        version: int,
        model_path: str,
        created_at: Optional[datetime] = None,
        metrics: Optional[Dict[str, float]] = None,
        status: str = "active",
    ):
        self.user_id = user_id
        self.version = version
        self.model_path = model_path
        self.created_at = created_at or datetime.utcnow()
        self.metrics = metrics or {}
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "version": self.version,
            "model_path": self.model_path,
            "created_at": self.created_at.isoformat(),
            "metrics": self.metrics,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelRegistryEntry":
        created_at = None
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                created_at = None
        return cls(
            user_id=data["user_id"],
            version=data["version"],
            model_path=data["model_path"],
            created_at=created_at or datetime.utcnow(),
            metrics=data.get("metrics", {}),
            status=data.get("status", "active"),
        )


class ModelRegistry:
    def __init__(self, config: Optional[MLConfig] = None):
        self.config = config or MLConfig()
        self._entries: Dict[str, List[ModelRegistryEntry]] = {}
        self._lock = Lock()
        self._load_registry()

    @property
    def _registry_path(self) -> str:
        return os.path.join(self.config.registry_path, "model_registry.json")

    def register_model(
        self,
        user_id: str,
        version: int,
        model_path: str,
        metrics: Optional[Dict[str, float]] = None,
    ) -> ModelRegistryEntry:
        entry = ModelRegistryEntry(
            user_id=user_id,
            version=version,
            model_path=model_path,
            metrics=metrics or {},
            status="active",
        )

        with self._lock:
            if user_id not in self._entries:
                self._entries[user_id] = []
            for existing in self._entries[user_id]:
                existing.status = "archived"
            self._entries[user_id].append(entry)
            self._persist_registry()

        logger.info(f"Registered model v{version} for user {user_id}")
        return entry

    def get_active_model(self, user_id: str) -> Optional[ModelRegistryEntry]:
        with self._lock:
            entries = self._entries.get(user_id, [])
            for entry in reversed(entries):
                if entry.status == "active":
                    return entry
        return None

    def get_model(self, user_id: str, version: int) -> Optional[ModelRegistryEntry]:
        with self._lock:
            entries = self._entries.get(user_id, [])
            for entry in entries:
                if entry.version == version:
                    return entry
        return None

    def get_all_versions(self, user_id: str) -> List[ModelRegistryEntry]:
        with self._lock:
            return list(self._entries.get(user_id, []))

    def rollback(self, user_id: str, version: int) -> bool:
        with self._lock:
            entries = self._entries.get(user_id, [])
            target = None
            for entry in entries:
                if entry.version == version:
                    target = entry
                    entry.status = "active"
                else:
                    entry.status = "archived"

            if target:
                self._persist_registry()
                logger.info(f"Rolled back user {user_id} to model v{version}")
                return True
        return False

    def update_metrics(self, user_id: str, version: int, metrics: Dict[str, float]):
        with self._lock:
            entries = self._entries.get(user_id, [])
            for entry in entries:
                if entry.version == version:
                    entry.metrics.update(metrics)
                    self._persist_registry()
                    return

    def delete_user_models(self, user_id: str):
        with self._lock:
            self._entries.pop(user_id, None)
            self._persist_registry()

    def get_all_active_models(self) -> Dict[str, ModelRegistryEntry]:
        active = {}
        with self._lock:
            for user_id, entries in self._entries.items():
                for entry in reversed(entries):
                    if entry.status == "active":
                        active[user_id] = entry
                        break
        return active

    def get_model_count(self) -> int:
        with self._lock:
            return sum(len(entries) for entries in self._entries.values())

    def get_active_model_count(self) -> int:
        return len(self.get_all_active_models())

    def get_user_count(self) -> int:
        with self._lock:
            return len(self._entries)

    def get_summary_stats(self) -> Dict[str, Any]:
        with self._lock:
            total = sum(len(entries) for entries in self._entries.values())
            active = self.get_active_model_count()
            return {
                "total_models": total,
                "active_models": active,
                "total_users": len(self._entries),
                "archived_models": total - active,
            }

    def _persist_registry(self):
        os.makedirs(os.path.dirname(self._registry_path), exist_ok=True)
        data = {}
        for user_id, entries in self._entries.items():
            data[user_id] = [e.to_dict() for e in entries]
        with open(self._registry_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _load_registry(self):
        if not os.path.exists(self._registry_path):
            return
        try:
            with open(self._registry_path, "r") as f:
                data = json.load(f)
            for user_id, entries_data in data.items():
                self._entries[user_id] = [
                    ModelRegistryEntry.from_dict(e) for e in entries_data
                ]
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to load model registry: {e}")
