import sys
import os
import json

try:
    import numpy as np
except ImportError:
    import random as _py_random
    class _DummyRandomState:
        def __init__(self, seed=42):
            self._rng = _py_random.Random(seed)
        def randint(self, a, b):
            return self._rng.randint(a, b)
        def random(self):
            return self._rng.random()
        def randn(self, r, c):
            return [[self._rng.random() for _ in range(c)] for _ in range(r)]
    class _DummyRandom:
        RandomState = _DummyRandomState
    class _DummyNP:
        random = _DummyRandom()
    np = _DummyNP()

import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import AsyncGenerator, Generator, Optional, Any
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt

try:
    from ml.config import MLConfig
    from ml.feature_engineering import FeatureEngine
    from ml.models.user_model import UserModel
    from ml.models.global_model import GlobalModel
    from ml.training_pipeline import TrainingPipeline
    from ml.inference_pipeline import InferencePipeline
    from ml.drift_detection import DriftDetector
    from ml.risk_engine import HybridRiskEngine
    from ml.explainability import Explainer
    from ml.behavioral_profile import BehavioralProfile, BehavioralProfileManager
    from ml.model_registry import ModelRegistry
    from ml.evaluation import Evaluator
except (ImportError, ModuleNotFoundError):
    MLConfig = FeatureEngine = UserModel = GlobalModel = TrainingPipeline = None
    InferencePipeline = DriftDetector = HybridRiskEngine = Explainer = None
    BehavioralProfile = BehavioralProfileManager = ModelRegistry = Evaluator = None


os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["JWT_SECRET_KEY"] = "test_secret_key_not_for_production"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["PROMETHEUS_ENABLED"] = "false"


@pytest.fixture(scope="session")
def app() -> FastAPI:
    from app.main import app as _app
    _app.state.testing = True
    return _app


@pytest.fixture(scope="session")
def test_client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    from app.middleware.rate_limit import rate_limiter
    rate_limiter._windows.clear()


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        echo=False,
    )
    from app.database import Base
    import app.models.user
    import app.models.behavioral
    import app.models.transaction
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_sqlite_test_db():
    engine = create_async_engine("sqlite+aiosqlite:///./test.db", echo=False)
    from app.database import Base
    import app.models.user
    import app.models.behavioral
    import app.models.transaction
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    yield
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except OSError:
            pass


@pytest_asyncio.fixture
async def db_session(test_db: AsyncSession) -> AsyncSession:
    return test_db


@pytest.fixture
def mock_db(app: FastAPI):
    from app.database import get_db
    db = AsyncMock(spec=AsyncSession)
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    db.add_all = MagicMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.close = AsyncMock()

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield db
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def ml_config() -> MLConfig:
    import tempfile
    config = MLConfig()
    config.model_storage_path = tempfile.mkdtemp()
    config.profile_storage_path = tempfile.mkdtemp()
    config.registry_path = tempfile.mkdtemp()
    return config


@pytest.fixture
def feature_engine() -> FeatureEngine:
    return FeatureEngine()


@pytest.fixture
def user_model(ml_config: MLConfig) -> UserModel:
    return UserModel("test_user", ml_config)


@pytest.fixture
def global_model(ml_config: MLConfig) -> GlobalModel:
    return GlobalModel(ml_config)


@pytest.fixture
def profile_manager(ml_config: MLConfig) -> BehavioralProfileManager:
    return BehavioralProfileManager(ml_config)


@pytest.fixture
def model_registry(ml_config: MLConfig) -> ModelRegistry:
    return ModelRegistry(ml_config)


@pytest.fixture
def training_pipeline(
    ml_config: MLConfig,
    feature_engine: FeatureEngine,
    profile_manager: BehavioralProfileManager,
    model_registry: ModelRegistry,
    global_model: GlobalModel,
) -> TrainingPipeline:
    return TrainingPipeline(ml_config, feature_engine, profile_manager, model_registry, global_model)


@pytest.fixture
def inference_pipeline(
    ml_config: MLConfig,
    feature_engine: FeatureEngine,
    global_model: GlobalModel,
    profile_manager: BehavioralProfileManager,
) -> InferencePipeline:
    return InferencePipeline(ml_config, feature_engine, global_model, profile_manager)


@pytest.fixture
def risk_engine() -> HybridRiskEngine:
    return HybridRiskEngine()


@pytest.fixture
def explainer() -> Explainer:
    return Explainer()


@pytest.fixture
def drift_detector() -> DriftDetector:
    return DriftDetector()


@pytest.fixture
def evaluator() -> Evaluator:
    return Evaluator()


def make_keystroke_events(n: int = 20, rng: Any = None) -> list:
    if rng is None:
        rng = np.random.RandomState(42)
    events = []
    t = 1000.0
    for i in range(n):
        events.append({"type": "keydown", "timestamp": t, "key": chr(97 + (i % 26))})
        t += 50 + rng.randint(-10, 10)
        events.append({"type": "keyup", "timestamp": t + 80, "key": chr(97 + (i % 26))})
        t += 100
    events.append({"type": "keydown", "timestamp": t, "key": "Backspace"})
    return events


def make_mouse_events(n: int = 30, rng: Any = None) -> list:
    if rng is None:
        rng = np.random.RandomState(42)
    events = []
    t = 2000.0
    x, y = 100.0, 100.0
    for i in range(n):
        events.append({"type": "mousemove", "timestamp": t, "x": x, "y": y})
        x += rng.randint(-20, 20)
        y += rng.randint(-20, 20)
        t += 16.0 + rng.random() * 10
    events.append({"type": "mousedown", "timestamp": t, "button": 0})
    events.append({"type": "mouseup", "timestamp": t + 50, "button": 0})
    return events


def make_session_events(n_events: int = 15, rng: Any = None) -> list:
    if rng is None:
        rng = np.random.RandomState(42)
    events = []
    t = 1000.0
    for i in range(n_events):
        events.append({"type": "keydown", "timestamp": t, "key": chr(97 + (i % 26))})
        t += 50 + (i % 10)
        events.append({"type": "keyup", "timestamp": t + 80, "key": chr(97 + (i % 26))})
        t += 100
        events.append({"type": "mousemove", "timestamp": t, "x": float(100 + i * 3), "y": float(200 + i * 2)})
        t += 16
    events.append({"type": "mousedown", "timestamp": t, "button": 0})
    return events


@pytest.fixture
def sample_behavioral_events() -> list:
    return make_session_events(15)


@pytest.fixture
def sample_features() -> dict:
    engine = FeatureEngine()
    return engine.extract_all(make_session_events(20))


@pytest.fixture
def trained_global_model(global_model: GlobalModel) -> GlobalModel:
    rng = np.random.RandomState(42)
    features = rng.randn(100, 36)
    global_model.train(features)
    return global_model


@pytest.fixture
def trained_user_model(user_model: UserModel) -> UserModel:
    rng = np.random.RandomState(42)
    features = rng.randn(50, 36)
    user_model.train(features)
    return user_model


def create_test_user_orm(session, **kwargs):
    from app.models.user import User, UserRole, UserStatus
    user = User(
        email=kwargs.get("email", "test@example.com"),
        phone=kwargs.get("phone", "+919876543210"),
        password_hash=kwargs.get("password_hash", "$2b$12$dummy_hash_for_testing_purposes_only"),
        full_name=kwargs.get("full_name", "Test User"),
        role=kwargs.get("role", UserRole.CUSTOMER),
        status=kwargs.get("status", UserStatus.ACTIVE),
        device_fingerprints=kwargs.get("device_fingerprints", []),
        trusted_devices=kwargs.get("trusted_devices", []),
        mfa_enabled=kwargs.get("mfa_enabled", False),
    )
    session.add(user)
    return user


@pytest.fixture
def admin_user() -> dict:
    return {
        "id": 1,
        "email": "admin@bank.com",
        "phone": "+919999999999",
        "full_name": "Admin User",
        "role": "ADMIN",
        "status": "ACTIVE",
        "mfa_enabled": False,
    }


@pytest.fixture
def customer_user() -> dict:
    return {
        "id": 2,
        "email": "customer@bank.com",
        "phone": "+918888888888",
        "full_name": "Customer User",
        "role": "CUSTOMER",
        "status": "ACTIVE",
        "mfa_enabled": False,
    }


def generate_jwt_token(user_id: int, role: str = "CUSTOMER", secret: str = None) -> str:
    from app.config import settings
    now = datetime.now(timezone.utc)
    expire = now.timestamp() + 3600
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now.timestamp(),
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "type": "access",
    }
    return jwt.encode(payload, secret or settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def auth_headers(customer_user: dict) -> dict:
    token = generate_jwt_token(customer_user["id"], customer_user["role"])
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(admin_user: dict) -> dict:
    token = generate_jwt_token(admin_user["id"], admin_user["role"])
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def celery_app():
    with patch("app.tasks.celery_app") as mock:
        mock.task = lambda *a, **kw: lambda f: f
        mock.delay = MagicMock()
        yield mock
