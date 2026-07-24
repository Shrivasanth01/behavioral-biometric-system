from pydantic_settings import BaseSettings
from typing import List, Optional
import secrets


class Settings(BaseSettings):
    APP_NAME: str = "Behavioral Biometric Banking Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "sqlite+aiosqlite:///./database/behavioral_system.db"
    DATABASE_SYNC_URL: str = "sqlite:///./database/behavioral_system.db"

    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    JWT_SECRET_KEY: str = secrets.token_hex(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ISSUER: str = "behavioral-biometric-bank"

    MFA_ISSUER_NAME: str = "BioBank"
    MFA_TOTP_VALIDITY_WINDOW: int = 1
    MFA_SMS_EXPIRY_SECONDS: int = 300
    MFA_EMAIL_EXPIRY_SECONDS: int = 300
    MFA_MAX_ATTEMPTS: int = 3
    MFA_LOCKOUT_MINUTES: int = 15

    ML_MODEL_PATH: str = "models/"
    ML_CONFIDENCE_THRESHOLD: float = 0.65
    ML_ANOMALY_THRESHOLD: float = 0.85
    ML_RETRAIN_MIN_SESSIONS: int = 10
    ML_DRIFT_DETECTION_INTERVAL: int = 86400

    RISK_ENGINE_ENABLED: bool = True
    RISK_HIGH_RISK_THRESHOLD: float = 0.7
    RISK_MEDIUM_RISK_THRESHOLD: float = 0.4
    RISK_MAX_DAILY_TRANSACTION: float = 500000.0
    RISK_MAX_SINGLE_TRANSACTION: float = 100000.0
    RISK_DAILY_TRANSACTION_LIMIT: int = 50
    RISK_VELOCITY_CHECK_MINUTES: int = 5
    RISK_VELOCITY_CHECK_COUNT: int = 5

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "https://banking.biobank.com",
        "https://dashboard.biobank.com",
    ]

    PROMETHEUS_ENABLED: bool = True
    OPENTELEMETRY_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "biometric-bank-backend"
    OTEL_EXPORTER_ENDPOINT: str = "http://localhost:4317"

    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_DEFAULT: int = 100
    RATE_LIMIT_WINDOW: int = 60
    RATE_LIMIT_AUTH_ENDPOINTS: int = 5
    RATE_LIMIT_AUTH_WINDOW: int = 60

    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_SPECIAL: bool = True
    PASSWORD_REQUIRE_NUMBER: bool = True
    PASSWORD_REQUIRE_UPPER: bool = True
    PASSWORD_REQUIRE_LOWER: bool = True

    BCRYPT_ROUNDS: int = 12

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
