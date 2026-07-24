# Behavioral Biometric System - DevOps Infrastructure

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐
│   Frontend  │     │  Security   │     │     Mobile       │
│  (Next.js)  │     │  Dashboard  │     │    (Flutter)     │
│   :3000     │     │  :3001      │     │                  │
└──────┬──────┘     └──────┬──────┘     └──────────────────┘
       │                   │                    │
       └───────────────────┼────────────────────┘
                          │
                    ┌─────▼──────┐
                    │   Nginx    │
                    │  Reverse   │
                    │   Proxy    │
                    │  :80/443   │
                    └─────┬──────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────▼─────┐   ┌────▼─────┐   ┌─────▼──────┐
    │  Backend  │   │ ML-Service│   │  Celery    │
    │ (FastAPI) │   │ (FastAPI) │   │ Worker/Beat│
    │   :8000   │   │  :8001    │   │            │
    └─────┬─────┘   └────┬─────┘   └─────┬──────┘
          │              │               │
    ┌─────▼─────┐   ┌────▼─────┐         │
    │ PostgreSQL│   │   Redis  │◄────────┘
    │    :5432  │   │   :6379  │
    └───────────┘   └──────────┘

┌─────────────┐   ┌─────────────┐   ┌──────────────────┐
│ Prometheus  │   │   Grafana   │   │  AlertManager    │
│   :9090     │   │   :3000     │   │   :9093          │
└─────────────┘   └─────────────┘   └──────────────────┘

┌─────────────┐   ┌─────────────┐
│ Elasticsearch│  │  Logstash   │
│   :9200     │   │   :5000     │
└─────────────┘   └─────────────┘
```

## Prerequisites

- Docker 24+
- Docker Compose v2.20+
- Git
- 8GB+ RAM (16GB recommended for full stack)
- 20GB+ free disk space

## Quick Start

### Development Environment

```bash
# Clone the repository
git clone https://github.com/your-org/behavioral-biometric-system.git
cd behavioral-biometric-system

# Copy environment file
cp docker/.env.example .env

# Start all services
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Access services:
# - Frontend:       http://localhost:3000
# - Backend API:    http://localhost:8000/api/v1/docs
# - Security Dashboard: http://localhost:3001
# - Grafana:        http://localhost:3002 (admin/admin)
# - Prometheus:     http://localhost:9090
# - AlertManager:   http://localhost:9093
```

### Production Deployment

```bash
# Deploy with production configuration
docker compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d

# Scale services
docker compose up -d --scale backend=3 --scale frontend=2

# Rolling update
docker compose up -d --no-deps --build backend
```

## Service Configuration

### File Structure

```
docker/
├── docker-compose.yml           # Master compose file
├── docker-compose.prod.yml      # Production overrides
├── docker-compose.dev.yml       # Development overrides
├── .env.example                 # Environment template
├── README.md                    # This file
│
├── nginx/
│   ├── Dockerfile               # Custom nginx image
│   ├── nginx.conf               # Production config
│   └── nginx.dev.conf           # Development config
│
├── backend/
│   ├── Dockerfile               # Multi-stage production build
│   └── Dockerfile.dev           # Development with hot reload
│
├── frontend/
│   ├── Dockerfile               # Multi-stage production build
│   └── Dockerfile.dev           # Development with hot reload
│
├── security-dashboard/
│   ├── Dockerfile               # Multi-stage production build
│   └── Dockerfile.dev           # Development with hot reload
│
├── ml/
│   ├── Dockerfile               # ML service production build
│   └── Dockerfile.dev           # ML service development
│
├── mobile/
│   └── Dockerfile               # Flutter build container
│
├── prometheus/
│   ├── prometheus.yml           # Scrape configuration
│   └── alerts.yml               # Alert rules
│
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── prometheus.yml   # Data source config
│   │   └── dashboards/
│   │       └── default.yml      # Dashboard provider
│   └── dashboards/
│       ├── system_overview.json
│       ├── ml_monitoring.json
│       ├── fraud_alerts.json
│       └── api_performance.json
│
├── monitoring/
│   └── alertmanager.yml         # Alert routing configuration
│
├── elk/
│   ├── logstash.conf            # Log pipeline configuration
│   └── elasticsearch.yml        # ES cluster configuration
│
└── scripts/
    ├── init-db.sh               # Database initialization
    ├── seed-db.sh               # Sample data seeding
    ├── backup-db.sh             # Database backup
    └── healthcheck.sh           # System health check
```

## Monitoring & Alerting

### Grafana Dashboards

| Dashboard | Description | Access |
|-----------|-------------|--------|
| System Overview | CPU, memory, disk, network, service status | `/dashboard/monitoring` |
| ML Performance | Model accuracy, latency, fraud scores | `/dashboard/monitoring` |
| Fraud Alerts | Fraud attempts, blocked transactions, risk scores | `/dashboard/monitoring` |
| API Performance | Request rates, latencies, error rates, SLOs | `/dashboard/monitoring` |

### Alert Routing

| Severity | Channel | Response Time |
|----------|---------|---------------|
| Critical | PagerDuty + Slack #bbs-critical | 5 minutes |
| Warning | Slack #bbs-warnings | 1 hour |
| Security | Slack #bbs-security + OpsGenie | 15 minutes |
| Info | Slack #bbs-alerts | Next business day |

## Database Management

### Initialization

The `init-db.sh` script runs automatically on first PostgreSQL startup:
- Creates multiple databases (`bbs_platform`, `bbs_analytics`, `bbs_audit`)
- Installs required extensions (`uuid-ossp`, `pgcrypto`, `pg_stat_statements`)
- Creates schemas for each domain
- Configures performance parameters

### Seeding

```bash
# Run seed script inside the container
docker exec bbs-postgres bash /docker-entrypoint-initdb.d/seed-db.sh

# Or manually
docker compose exec postgres bash /docker-entrypoint-initdb.d/seed-db.sh
```

### Backup

```bash
# Manual backup
docker compose exec postgres bash /scripts/backup-db.sh

# Backup with S3 upload
docker compose exec -e S3_BUCKET=my-backups postgres bash /scripts/backup-db.sh

# Backup retention
docker compose exec postgres bash /scripts/backup-db.sh

# Automated backup (via cron)
0 2 * * * cd /app && docker compose exec postgres bash /scripts/backup-db.sh >> /var/log/backup.log 2>&1
```

## Health Checks

```bash
# Run comprehensive health check
docker compose exec nginx bash /scripts/healthcheck.sh

# Quick service status
docker compose ps

# Specific service health
curl http://localhost:8000/api/v1/health
curl http://localhost:3000/api/health
curl http://localhost:8001/health
```

## CI/CD Pipeline

### GitHub Actions Workflows

```yaml
# CI Pipeline (.github/workflows/ci.yml)
# Trigger: push/PR to main/develop
# Jobs:
#   - backend-tests: Unit tests, linting, type checking, security scan
#   - frontend-tests: Unit tests, linting, type checking, build
#   - security-dashboard-tests: Unit tests, linting, type checking, build
#   - ml-tests: Unit tests, model validation
#   - mobile-tests: Flutter analyze, unit tests
#   - docker-build: Build all images, vulnerability scan

# CD Pipeline (.github/workflows/cd.yml)
# Trigger: push to main
# Jobs:
#   - build-and-push: Build multi-arch images, push to registry, generate SBOM
#   - deploy-staging: Automated deploy to staging environment
#   - deploy-production: Canary deploy + full rollout to production
#   - notify: Slack notification + GitHub release
```

### Deployment Strategy

1. **Build**: Multi-arch images (amd64 + arm64) with build cache
2. **Security Scan**: Trivy vulnerability scanning, SBOM generation
3. **Staging**: Automatic deployment on main branch push
4. **Production**: Manual workflow dispatch with canary rollout
   - 10% traffic to canary (5 min observation)
   - Health check verification (error rate < 5%)
   - Full rollout with rolling update
   - Post-deployment smoke tests

## Security

### Network Security

- All internal services on isolated `bbs-network` bridge network
- Only nginx exposes ports 80/443 to the host
- Dashboard and metrics restricted to internal IP ranges
- Rate limiting on all API endpoints

### Container Security

- Non-root users in all containers
- Read-only root filesystem where possible
- No security capabilities
- Resource limits enforced
- Health checks on all services

### Data Security

- Secrets managed via Docker secrets (production)
- Environment variables for development
- SSL/TLS termination at nginx
- CORS whitelist configuration
- CSP headers enforced

## Resource Requirements

| Service | CPU (min/max) | Memory (min/max) | Storage |
|---------|---------------|------------------|---------|
| postgres | 1/2 | 1G/2G | 10GB+ |
| redis | 0.5/1 | 512M/1G | 1GB |
| backend | 1/2 | 512M/1G | - |
| celery-worker | 2/4 | 1G/2G | - |
| celery-beat | 0.25/0.5 | 128M/256M | - |
| frontend | 0.5/1 | 256M/512M | - |
| security-dashboard | 0.5/1 | 256M/512M | - |
| ml-service | 2/4 | 2G/4G | 5GB+ (models) |
| nginx | 0.5/1 | 128M/256M | - |
| prometheus | 0.5/1 | 512M/1G | 30GB (30d) |
| grafana | 0.5/1 | 256M/512M | 1GB |
| elasticsearch | 1/2 | 1G/2G | 20GB+ |
| logstash | 0.5/1 | 512M/1G | - |
| alertmanager | 0.25/0.5 | 128M/256M | 1GB |

**Total (minimum)**: ~4 CPUs, 8GB RAM, 50GB storage
**Total (recommended)**: ~8 CPUs, 16GB RAM, 100GB+ storage

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Port conflicts | Change host ports in `.env` file |
| PostgreSQL won't start | Check `init-db.sh` for syntax errors |
| Redis auth failure | Verify `REDIS_PASSWORD` matches in `.env` |
| Backend can't connect to DB | Wait for PostgreSQL health check to pass |
| Frontend build fails | Check Node version compatibility |
| ML service OOM | Reduce `ML_BATCH_SIZE` or increase memory limit |
| Grafana no data | Check Prometheus data source configuration |
| nginx 502 Bad Gateway | Ensure upstream services are running |

### Debug Mode

```bash
# Start with debug logging
LOG_LEVEL=debug docker compose up -d

# View service logs
docker compose logs -f backend
docker compose logs -f nginx

# Exec into a container
docker compose exec backend bash

# Restart a specific service
docker compose restart celery-worker

# Reset everything (WARNING: destroys data)
docker compose down -v && docker compose up -d
```

## Contributing

1. Follow the coding standards and conventions
2. Update Dockerfiles when adding dependencies
3. Add appropriate Grafana panels for new metrics
4. Add alerting rules for new failure modes
5. Update this documentation for infrastructure changes
6. Run health checks before committing changes
7. Ensure all CI pipeline stages pass

## License

MIT License - See LICENSE file for details
