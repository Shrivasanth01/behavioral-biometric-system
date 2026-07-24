FROM python:3.14-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY ml-service/requirements.txt .
COPY ml-service/requirements-prod.txt .

RUN pip install --no-cache-dir --user --upgrade pip && \
    pip install --no-cache-dir --user \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt -r requirements-prod.txt

FROM python:3.14-slim

RUN groupadd -r bbs-ml && useradd -r -g bbs-ml -d /app -s /sbin/nologin bbs-ml

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/* && \
    mkdir -p /app && \
    mkdir -p /app/models && \
    mkdir -p /app/logs

COPY --from=builder /root/.local /usr/local

WORKDIR /app

COPY ml-service/app/ ./app/
COPY ml-service/models/ ./models/
COPY ml-service/scripts/ ./scripts/

RUN find /app -type d -exec chmod 755 {} + && \
    find /app -type f -exec chmod 644 {} + && \
    chmod +x /app/scripts/*.sh && \
    chown -R bbs-ml:bbs-ml /app && \
    chmod 775 /app/models

USER bbs-ml

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -sf http://localhost:8001/health | python -c "import sys,json; sys.exit(0 if json.load(sys.stdin).get('status')=='healthy' else 1)"

VOLUME ["/app/models"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2", "--limit-max-requests", "5000"]
