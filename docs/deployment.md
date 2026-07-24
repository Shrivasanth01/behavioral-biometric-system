# Deployment Guide

## Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|---|---|---|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16 GB |
| Disk | 50 GB SSD | 100 GB+ SSD |
| Docker | 24.0+ | 24.0+ |
| Docker Compose | 2.23+ | 2.23+ |
| Network | Broadband | Dedicated connection |

### Software Requirements

- Docker and Docker Compose (for containerized deployment)
- Git (for repository access)
- OpenSSL (for SSL certificate generation)
- 3 available domain names (or subdomains):
  - `app.bbs-platform.com` - Customer banking application
  - `dashboard.bbs-platform.com` - Security analyst dashboard
  - `api.bbs-platform.com` - Backend API

### SSL Certificates

Generate or obtain SSL certificates for your domains:

```bash
# Self-signed certificates (development only)
mkdir -p docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/bbs-platform.key \
  -out docker/nginx/ssl/bbs-platform.crt \
  -subj "/C=US/ST=NY/L=New York/O=BioBank/CN=*.bbs-platform.com"

# Let's Encrypt (production - using certbot)
certbot certonly --standalone -d "*.bbs-platform.com" --non-interactive --agree-tos -m admin@bbs-platform.com
cp /etc/letsencrypt/live/bbs-platform.com/fullchain.pem docker/nginx/ssl/
cp /etc/letsencrypt/live/bbs-platform.com/privkey.pem docker/nginx/ssl/
```

## Environment Setup

### Create Environment File

```bash
cp .env.example .env
```

### Required Environment Variables

```bash
# === Database ===
POSTGRES_PASSWORD=bbs_secure_password_2024!
REDIS_PASSWORD=bbs_redis_pass_2024!

# === Application ===
SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=production
LOG_LEVEL=info
CORS_ORIGINS=https://app.bbs-platform.com,https://dashboard.bbs-platform.com
SENTRY_DSN=https://your-sentry-dsn@sentry.io/123456

# === ML Service ===
ML_BATCH_SIZE=64

# === Monitoring ===
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 16)

# === Mobile Push Notifications (if using) ===
# FCM_SERVER_KEY=your_fcm_server_key
# APNS_KEY_ID=your_apns_key_id
# APNS_TEAM_ID=your_apns_team_id
```

### Environment File (.env) Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `POSTGRES_PASSWORD` | Yes | - | PostgreSQL password |
| `REDIS_PASSWORD` | Yes | - | Redis password |
| `SECRET_KEY` | Yes | - | JWT signing secret (min 32 bytes) |
| `ENVIRONMENT` | No | `production` | Runtime environment |
| `LOG_LEVEL` | No | `info` | Logging level (debug, info, warning, error) |
| `CORS_ORIGINS` | Yes | - | Comma-separated allowed origins |
| `SENTRY_DSN` | No | - | Sentry error tracking DSN |
| `ML_BATCH_SIZE` | No | `64` | ML inference batch size |
| `GRAFANA_ADMIN_USER` | No | `admin` | Grafana admin username |
| `GRAFANA_ADMIN_PASSWORD` | No | `admin` | Grafana admin password |

## Database Setup

### Automated Migration

```bash
# Run all pending migrations
docker compose -f docker/docker-compose.yml exec backend alembic upgrade head

# Rollback one migration
docker compose -f docker/docker-compose.yml exec backend alembic downgrade -1

# Check migration status
docker compose -f docker/docker-compose.yml exec backend alembic current
```

### Manual Schema Application

```bash
# Apply schema directly
docker compose -f docker/docker-compose.yml exec -T postgres \
  psql -U bbs_user -d bbs_platform < database/schema.sql
```

### Seed Data

```bash
# Load seed data for development/demo
docker compose -f docker/docker-compose.yml exec backend python -m scripts.seed_data

# This creates:
# - 1 admin user: admin@bbs.com / admin123
# - 1 analyst user: analyst@bbs.com / analyst123
# - 5 customer users with accounts, cards, and transaction history
# - Sample behavioral profiles and risk scores
# - 1 pre-trained global ML model
```

### Backup and Restore

```bash
# Backup
docker compose -f docker/docker-compose.yml exec -T postgres \
  pg_dump -U bbs_user -d bbs_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
cat backup_20240115_000000.sql | docker compose -f docker/docker-compose.yml exec -T postgres \
  psql -U bbs_user -d bbs_platform

# Automated daily backup (crontab)
0 2 * * * cd /opt/bbs && docker compose exec -T postgres pg_dump -U bbs_user bbs_platform > backups/daily_$(date +\%Y\%m\%d).sql && find backups/ -name "*.sql" -mtime +30 -delete
```

## Docker Deployment

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/behavioral-biometric-bank.git
cd behavioral-biometric-bank
```

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env with your production values
nano .env
```

### Step 3: Start Services

```bash
# Build and start all services
docker compose -f docker/docker-compose.yml up -d --build

# Monitor startup
docker compose -f docker/docker-compose.yml logs -f

# Check all services are healthy
docker compose -f docker/docker-compose.yml ps
```

### Step 4: Run Migrations

```bash
docker compose -f docker/docker-compose.yml exec backend alembic upgrade head
```

### Step 5: Load Seed Data (Optional)

```bash
docker compose -f docker/docker-compose.yml exec backend python -m scripts.seed_data
```

### Step 6: Verify Deployment

```bash
# Health check
curl -k https://localhost/health

# Expected response:
# {"status":"healthy","timestamp":"2024-01-15T12:00:00Z","service":"Behavioral Biometric Banking Platform","version":"1.0.0","environment":"production","database":"connected"}

# API docs
curl -k https://localhost/docs

# Frontend
curl -k https://localhost/ -o /dev/null -w "%{http_code}"
```

### Step 7: Configure SSL

Ensure your domain DNS points to the server IP, then:

```bash
# For Let's Encrypt with certbot (requires 80/443 access)
docker compose -f docker/docker-compose.yml stop nginx
certbot certonly --standalone -d "*.bbs-platform.com" --non-interactive --agree-tos -m admin@bbs-platform.com
docker compose -f docker/docker-compose.yml start nginx
```

## Production Deployment

### Kubernetes Deployment (Future)

The application is designed to be Kubernetes-compatible. Key considerations for K8s deployment:

- **StatefulSets** for PostgreSQL and Redis (with persistent volumes)
- **Deployments** for backend, frontend, dashboard, ML service
- **DaemonSet** for Prometheus node exporter
- **Horizontal Pod Autoscaler** for backend and ML service based on CPU/memory
- **ConfigMaps** and **Secrets** for environment configuration
- **Ingress** controller for Nginx functionality
- **PersistentVolumeClaims** for model store, profile store, and database volumes

### Load Balancing

```
                        ┌───────────────┐
                        │  Load Balancer│
                        │  (AWS ALB /   │
                        │   GCP HTTP LB)│
                        └───────┬───────┘
                                │
                   ┌────────────┼────────────┐
                   │            │            │
              ┌────┴────┐ ┌────┴────┐ ┌────┴────┐
              │  Nginx  │ │  Nginx  │ │  Nginx  │
              │  Node 1 │ │  Node 2 │ │  Node 3 │
              └────┬────┘ └────┬────┘ └────┬────┘
                   │            │            │
              ┌────┴────┐ ┌────┴────┐ ┌────┴────┐
              │ Backend │ │ Backend │ │ Backend │
              │ Node 1  │ │ Node 2  │ │ Node 3  │
              └─────────┘ └─────────┘ └─────────┘
```

### SSL/TLS Configuration

```nginx
# docker/nginx/nginx.conf (production)
server {
    listen 443 ssl http2;
    server_name app.bbs-platform.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.3;
    ssl_ciphers TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;

    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Rate limiting
        limit_req zone=auth burst=20 nodelay;
        limit_req zone=api burst=100 nodelay;
    }
}
```

### Monitoring Setup

#### Prometheus

```yaml
# docker/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']

  - job_name: 'ml-service'
    static_configs:
      - targets: ['ml-service:8001']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

#### Grafana Dashboards

Provisioned dashboards are located at `docker/grafana/dashboards/`:
- `bbs-system-overview.json` - System resource usage
- `bbs-ml-metrics.json` - Model health, drift, and accuracy
- `bbs-fraud-metrics.json` - Fraud alerts, risk scores, blocked transactions
- `bbs-business-metrics.json` - User growth, transaction volume, revenue

#### Alert Rules

```yaml
# docker/monitoring/alertmanager.yml
route:
  receiver: 'default'
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
      repeat_interval: 30m
    - match:
        severity: warning
      receiver: 'email'

receivers:
  - name: 'default'
    email_configs:
      - to: 'alerts@bbs-platform.com'
        from: 'monitoring@bbs-platform.com'
        smarthost: 'smtp.sendgrid.net:587'
        auth_username: 'apikey'
        auth_password: 'SG.xxxxx'

  - name: 'pagerduty'
    pagerduty_configs:
      - routing_key: 'your-pagerduty-integration-key'
```

### Logging Configuration (ELK)

```conf
# docker/elk/logstash.conf
input {
  tcp {
    port => 5000
    codec => json_lines
  }
  beats {
    port => 5044
  }
}

filter {
  if [service] == "backend" {
    mutate {
      add_field => { "index_prefix" => "bbs-backend" }
    }
  }
  if [service] == "ml-service" {
    mutate {
      add_field => { "index_prefix" => "bbs-ml" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "%{index_prefix}-%{+YYYY.MM.dd}"
  }
}
```

### Backup Configuration

```bash
# /etc/cron.d/bbs-backup
# Database backup at 2 AM daily
0 2 * * * root /opt/bbs/scripts/backup.sh

# Model store backup every 6 hours
0 */6 * * * root /opt/bbs/scripts/backup-models.sh

# Cleanup old backups (keep 30 days)
0 3 * * * root find /opt/bbs/backups -name "*.sql" -mtime +30 -delete
```

### Disaster Recovery

**Recovery Point Objective (RPO):** 1 hour (with streaming replication)
**Recovery Time Objective (RTO):** 30 minutes

**Procedure:**

1. **Infrastructure failure:**
```bash
# On new primary server
git clone https://github.com/your-org/behavioral-biometric-bank.git
cd behavioral-biometric-bank
docker compose -f docker/docker-compose.yml up -d postgres redis
cat /backup/latest.sql | docker compose exec -T postgres psql -U bbs_user bbs_platform
docker compose -f docker/docker-compose.yml up -d
```

2. **Database corruption:**
```bash
# Stop application, restore from backup, reapply recent logs
docker compose stop backend ml-service
docker compose exec postgres psql -U bbs_user -c "SELECT pg_switch_wal();"
cat /backup/pre-corruption.sql | docker compose exec -T postgres psql -U bbs_user bbs_platform
docker compose start backend ml-service
```

3. **Complete region failure:**
- Maintain warm standby in secondary region
- Use PostgreSQL streaming replication to secondary
- Regular file-based backup sync for model store
- DNS failover to secondary region's load balancer

## Scaling

### Horizontal Scaling Strategies

| Component | Strategy | Notes |
|---|---|---|
| Backend API | Multiple containers behind Nginx | Stateless, scales linearly |
| Celery Workers | Increase worker count and concurrency | Up to 8 workers per host |
| ML Service | Multiple instances behind load balancer | Model cache requires Redis |
| Frontend | CDN + multiple containers | Static assets via CDN |
| PostgreSQL | Read replicas for analytics | Primary handles writes |
| Redis | Redis Cluster (data sharding) | For high-throughput caching |

### Database Replication

```yaml
# docker-compose.yml (production extension)
services:
  postgres-primary:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: bbs_platform
      POSTGRES_USER: bbs_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-primary:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  postgres-replica:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: bbs_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-replica:/var/lib/postgresql/data
    depends_on:
      - postgres-primary
    command: >
      bash -c "until pg_basebackup -h postgres-primary -D /var/lib/postgresql/data -U replicator -v -P --wal-method=stream; do sleep 5; done;
      echo 'primary_conninfo = host=postgres-primary port=5432 user=replicator password=replicator_pass' >> /var/lib/postgresql/data/postgresql.auto.conf;
      pg_ctl start -D /var/lib/postgresql/data;"
```

### Caching Strategies

**Redis Cache Layers:**

| Cache | TTL | Purpose | Invalidation |
|---|---|---|---|
| User Profiles | 30 min | Behavioral profile data | On profile update |
| User Models | 60 min | Loaded ML model objects | On retraining |
| Session Data | Until expiry | Active session state | On logout/timeout |
| Rate Limit Counters | Per window | Request rate tracking | Auto-expiry |
| Device Trust Status | 24 hours | Cached device trust check | On device removal |

**CDN Configuration:**

```nginx
# Static asset caching
location /_next/static/ {
    proxy_cache bbs-cache;
    proxy_cache_valid 200 60m;
    proxy_cache_use_stale error timeout updating;
    proxy_pass http://frontend:3000;
}

location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Model Store Scaling

For high-traffic deployments, replace the file-system-based model store with object storage:

```python
# ml/config.py extension for S3-compatible storage
import boto3

class S3ModelStorage:
    def __init__(self, bucket: str = "bbs-models"):
        self.s3 = boto3.client("s3")
        self.bucket = bucket

    def save_model(self, user_id: str, model_data: bytes):
        self.s3.put_object(
            Bucket=self.bucket,
            Key=f"models/{user_id}/model.pkl",
            Body=model_data,
        )

    def load_model(self, user_id: str) -> Optional[bytes]:
        try:
            obj = self.s3.get_object(
                Bucket=self.bucket,
                Key=f"models/{user_id}/model.pkl",
            )
            return obj["Body"].read()
        except ClientError:
            return None
```

## Health Check Reference

All services expose health check endpoints:

| Service | Endpoint | Expected Response |
|---|---|---|
| Backend | `GET /health` | `{"status":"healthy","database":"connected"}` |
| ML Service | `GET /health` | `{"status":"ok","model_loaded":true}` |
| Frontend | `GET /api/health` | HTTP 200 |
| PostgreSQL | `pg_isready` | `localhost:5432 - accepting connections` |
| Redis | `PING` | `+PONG` |
| Elasticsearch | `GET /_cluster/health` | `{"status":"green"}` |
| Prometheus | `GET /-/ready` | HTTP 200 |
| Grafana | `GET /api/health` | `{"database":"ok"}` |

## Troubleshooting

### Common Issues

**Backend fails to start:**
```bash
# Check database connectivity
docker compose logs backend | grep -i error
docker compose exec postgres pg_isready -U bbs_user

# Verify migrations are up to date
docker compose exec backend alembic check
```

**ML Service fails to load model:**
```bash
# Check model directory permissions
docker compose exec ml-service ls -la /app/models/
docker compose logs ml-service

# Retrain global model
curl -X POST https://api.bbs-platform.com/api/admin/models/retrain \
  -H "Authorization: Bearer <admin_token>"
```

**High latency on risk assessment:**
```bash
# Check Redis connectivity and cache hit rates
docker compose exec redis redis-cli INFO stats | grep keyspace
docker compose logs backend | grep "risk_assessment"

# Increase cache TTL if needed
docker compose exec backend python -c "from app.config import settings; print(settings.MODEL_CACHE_TTL)"
```

**Celery tasks not processing:**
```bash
# Check worker status
docker compose logs celery-worker | tail -50
docker compose exec redis redis-cli LLEN celery | wc -l

# Restart worker
docker compose restart celery-worker
```
