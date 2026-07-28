from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import PlainTextResponse
from datetime import datetime, timezone

from app.config import settings
from app.database import init_db, check_db_health, close_db
from app.exceptions import register_exception_handlers
from app.middleware.rate_limit import RateLimitMiddleware
from app.api.auth import router as auth_router
from app.api.banking import router as banking_router
from app.api.behavioral import router as behavioral_router
from app.api.risk import router as risk_router
from app.api.admin import router as admin_router
from app.api.v1_router import mlops_router, audit_router, notifications_router, dashboards_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex(('localhost', 6379))
        s.close()
        if result == 0:
            from app.tasks import detect_drift
            detect_drift.delay()
        else:
            print("INFO: Redis not detected on port 6379; running in standalone DB mode without Celery beat queue.")
    except Exception as e:
        print(f"INFO: Skipped Celery startup queue check: {e}")
    yield
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Banking platform with behavioral biometric risk assessment, ML-powered fraud detection, and real-time security monitoring.",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)


@app.middleware("http")
async def _log_requests(request: Request, call_next):
    try:
        headers = dict(request.headers)
    except Exception:
        headers = {}
    print(f"[DEBUG_REQ] {request.method} {request.url.path} HEADERS: {list(headers.keys())}")
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
    max_age=3600,
)
app.add_middleware(RateLimitMiddleware)


# Development helper: ensure CORS headers are present on all responses
if settings.ENVIRONMENT != "production":
    @app.middleware("http")
    async def _ensure_cors_headers(request: Request, call_next):
        response = await call_next(request)
        origin = request.headers.get("origin")
        if origin and origin in settings.CORS_ORIGINS:
            response.headers.setdefault("Access-Control-Allow-Origin", origin)
        elif settings.CORS_ORIGINS:
            response.headers.setdefault("Access-Control-Allow-Origin", settings.CORS_ORIGINS[0])
        else:
            response.headers.setdefault("Access-Control-Allow-Origin", "*")
            
        response.headers.setdefault("Access-Control-Allow-Credentials", "true")
        response.headers.setdefault("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS, PATCH")
        response.headers.setdefault("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response


# Ensure any OPTIONS preflight to API paths returns 200 so CORSMiddleware can attach headers
@app.options("/{rest_of_path:path}")
async def _preflight(rest_of_path: str):
    return PlainTextResponse("OK")
register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(banking_router)
app.include_router(behavioral_router)
app.include_router(risk_router)
app.include_router(admin_router)

# V1 Domain Microservices
app.include_router(mlops_router)
app.include_router(audit_router)
app.include_router(notifications_router)
app.include_router(dashboards_router)


@app.get("/health")
async def health_check():
    db_healthy = await check_db_health()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_healthy else "disconnected",
    }


@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if settings.PROMETHEUS_ENABLED:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
    import time

    REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
    REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"])

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
        REQUEST_DURATION.labels(method=request.method, endpoint=request.url.path).observe(duration)
        return response

    @app.get("/metrics")
    async def metrics():
        from fastapi.responses import Response
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
