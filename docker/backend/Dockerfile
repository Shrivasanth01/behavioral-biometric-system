FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY backend/requirements.txt .
COPY backend/requirements-prod.txt .

RUN pip install --no-cache-dir --user --upgrade pip && \
    pip install --no-cache-dir --user \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt -r requirements-prod.txt

FROM python:3.11-slim

RUN groupadd -r bbs && useradd -r -g bbs -d /app -s /sbin/nologin bbs

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* && \
    mkdir -p /app && \
    mkdir -p /app/static && \
    mkdir -p /app/logs

COPY --from=builder /root/.local /usr/local

WORKDIR /app

COPY backend/app/ ./app/
COPY backend/alembic/ ./alembic/
COPY backend/alembic.ini .
COPY backend/pyproject.toml .
COPY backend/scripts/ ./scripts/

RUN find /app -type d -exec chmod 755 {} + && \
    find /app -type f -exec chmod 644 {} + && \
    chmod +x /app/scripts/*.sh

RUN chown -R bbs:bbs /app

USER bbs

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -sf http://localhost:8000/api/v1/health | python -c "import sys,json; sys.exit(0 if json.load(sys.stdin).get('status')=='healthy' else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--limit-max-requests", "10000", "--timeout-graceful-shutdown", "30"]
