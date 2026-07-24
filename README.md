# AI-Powered Behavioral Biometric Authentication and Fraud Prevention Banking Platform

An enterprise-grade banking platform that uses behavioral biometrics — how users type, move their mouse, scroll, and interact with devices — to continuously authenticate users and detect fraud in real time. Combines unsupervised anomaly detection (Isolation Forest, One-Class SVM, Autoencoders) with a hybrid risk engine and explainable AI to provide adaptive, context-aware security.

## Architecture

```
                              Client Layer
  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐  ┌────────────┐
  │  Web App      │  │  Mobile App   │  │   Web SDK         │  │ Mobile SDK │
  │  (Next.js)   │  │  (Flutter)    │  │  (JS Tracker)    │  │  (Flutter)  │
  └──────┬───────┘  └───────┬───────┘  └────────┬─────────┘  └─────┬──────┘
         └──────────────────┴───────────────────┴──────────────────┘
                                    │ HTTPS/WSS
                                    ▼
                         API Gateway (Nginx)
                   Rate Limiting · SSL · Reverse Proxy
                                    │
                                    ▼
                         Application Layer (FastAPI)
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
  │  Auth API    │  │ Banking API  │  │ Behavioral   │  │   Risk & Fraud   │
  │  JWT/MFA/OTP │  │ Transfer/    │  │ Event Ingest │  │   Assessment API │
  │              │  │ Beneficiary  │  │ Profile Mgmt │  │   Explainability │
  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘
         └─────────────────┴─────────────────┴────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │         Celery Workers         │
                    │  Event Processing · ML Tasks   │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                         Machine Learning Layer
  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────────────────┐
  │ Feature Engine  │  │  Anomaly Models   │  │   Hybrid Risk Engine         │
  │ 36 Features     │  │  Isolation Forest │  │   ML Weight (65%)            │
  │ Keystroke/Mouse │  │  One-Class SVM    │  │   Rule Weight (25%)          │
  │ Session/Mobile  │  │  Autoencoder      │  │   Heuristic Weight (10%)     │
  └────────┬────────┘  └────────┬─────────┘  └────────────────┬──────────────┘
           └────────────────────┴─────────────────────────────┘
                                    │
  ┌──────────────────┐  ┌────────────────────┐  ┌────────────────────────────┐
  │ Drift Detector   │  │ Behavioral Profile │  │  Explainer (XAI)           │
  │ PSI/KL Divergence│  │ Manager            │  │  Feature Contribution      │
  │ Concept Drift    │  │ Cold Start Mgmt    │  │  Human-Readable Reasons    │
  └──────────────────┘  └────────────────────┘  └────────────────────────────┘
                                    │
                                    ▼
                              Data Layer
  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────────────┐
  │  PostgreSQL 16    │  │   Redis 7        │  │  Model/Profile Store       │
  │  All persistent  │  │  Cache/Broker    │  │  Pickle/JSON on Disk       │
  │  21 tables       │  │  Session Store   │  │  Model Registry             │
  └──────────────────┘  └──────────────────┘  └────────────────────────────┘
                                    │
                                    ▼
                        Observability & Monitoring
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
  │  Prometheus  │  │   Grafana    │  │  ELK Stack   │  │  Alertmanager    │
  │  Metrics     │  │  Dashboards  │  │  Logging     │  │  Alerts          │
  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘
```

## Features

### Customer Banking Application
- Full banking dashboard with accounts, transactions, transfers, bill payments
- Card management (freeze/unfreeze, limit controls)
- Loan applications, EMI calculator, loan schedule viewer
- Beneficiary management with per-beneficiary limits
- UPI, internal, and external (NEFT/RTGS/IMPS) transfers
- Real-time balance and transaction history with advanced filtering

### Behavioral Biometric SDKs
- **Web SDK**: Captures keyboard (keydown/keyup with meta keys), mouse (move/click/scroll with velocity/acceleration), touch, focus, clipboard, resize, visibility, and navigation events
- **Mobile SDK**: Captures touch gestures (swipe velocity, pressure, duration), device sensors, multi-touch
- **Device Fingerprinting**: Canvas, WebGL, AudioContext, font detection, screen properties, SHA-256 hash
- Automatic batching with configurable intervals, exponential backoff retry, and sendBeacon fallback

### Feature Engineering Engine
Extracts 36 behavioral features across four categories:
- **Keystroke Features (10)**: Typing speed, key hold duration, backspace rate, error correction rate, trigram latency, key press entropy, special key ratio, number row frequency
- **Mouse Features (12)**: Cursor velocity/acceleration (mean/std), path length, direction entropy, click frequency, double-click rate, right-click ratio, scroll speed, idle time ratio
- **Session Features (8)**: Session duration, interaction density, navigation depth/entropy, form focus consistency, time-of-day, day-of-week
- **Mobile Features (6)**: Swipe velocity/acceleration, touch pressure (mean/std), touch duration, gesture complexity, multi-touch ratio

### Machine Learning Engine
- **Global Model**: Ensemble of 10 Isolation Forests trained on aggregate population data for cold-start users
- **User Models**: Personal Isolation Forest per user with adaptive thresholding, optionally augmented with One-Class SVM and Autoencoder
- **Training Pipeline**: Cold start management, session-based retraining every N sessions, automatic feature extraction and normalization
- **Drift Detection**: Population Stability Index (PSI), KL divergence, feature-level drift monitoring, concept drift detection with automated retraining triggers
- **Model Registry**: Versioned model storage with rollback capability, performance metrics tracking, lifecycle management

### Risk Engine
- Hybrid scoring: ML anomaly score (65%) + rule-based deviations (25%) + heuristic indicators (10%)
- **Rules**: Z-score deviation from personal baseline for typing speed, mouse velocity, session duration; unknown device detection; suspicious time-of-day; navigation pattern anomalies
- **Heuristics**: Too-few-interactions, perfect typing pattern, automated mouse patterns, improbable idle ratios
- **Risk Bands**: LOW (0-30) -> ALLOW, MEDIUM (31-70) -> REQUEST_MFA, HIGH (71-100) -> BLOCK_AND_ALERT

### Explainability Engine
- Feature contribution analysis comparing current session against personal baseline
- Human-readable reason generation using 25+ templated explanations
- Cold-start explanations for new users
- Top-K feature impact ranking with normalized contribution scores

### Fraud Monitoring Dashboard
- Real-time risk metric visualization with trend charts
- Fraud alert queue with severity, status, and assignment tracking
- User session timeline viewer with behavioral event replay
- ML model health monitoring (drift status, accuracy trends)

### Mobile Applications
- Cross-platform Flutter mobile banking app
- Native behavioral capture with sensor integration
- Biometric authentication (fingerprint, face ID)
- Push notification support for MFA and transaction alerts

## Technology Stack

### Backend
| Technology | Purpose |
|---|---|
| Python 3.11+ | Primary language |
| FastAPI | REST API framework with async support |
| SQLAlchemy 2.0 (Async) | ORM with PostgreSQL |
| Alembic | Database migrations |
| Celery | Distributed task queue |
| Redis 7 | Caching, message broker, session store |
| PostgreSQL 16 | Primary database |
| Pydantic v2 | Data validation and settings |
| PyOTP | TOTP-based MFA |
| python-jose | JWT token management |

### Machine Learning
| Technology | Purpose |
|---|---|
| scikit-learn | Isolation Forest, One-Class SVM |
| NumPy | Numerical computing |
| SciPy | Statistical functions |
| Pandas | Data manipulation |
| TensorFlow/Keras | Autoencoder (optional) |

### Frontend
| Technology | Purpose |
|---|---|
| Next.js 14 | React framework (App Router) |
| TypeScript | Type safety |
| Tailwind CSS | Utility-first styling |
| Recharts | Data visualization |
| React Hook Form + Zod | Form validation |

### Mobile
| Technology | Purpose |
|---|---|
| Flutter 3+ | Cross-platform framework |
| flutter_secure_storage | Secure credential storage |
| local_auth | Biometric authentication |
| sensors_plus | Sensor access |

### DevOps
| Technology | Purpose |
|---|---|
| Docker & Docker Compose | Containerization |
| Nginx | API gateway, reverse proxy |
| Prometheus + Grafana | Monitoring |
| ELK Stack | Log aggregation |
| Alertmanager | Alert routing |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/behavioral-biometric-bank.git
cd behavioral-biometric-bank

# Start all services
docker compose -f docker/docker-compose.yml up -d

# Run database migrations
docker compose -f docker/docker-compose.yml exec backend alembic upgrade head

# Load seed data
docker compose -f docker/docker-compose.yml exec backend python -m scripts.seed_data

# Verify deployment
curl http://localhost/health
```

### Access URLs

| Service | URL | Default Credentials |
|---|---|---|
| Banking Application | `https://app.bbs-platform.com` | Register via UI |
| Security Dashboard | `https://dashboard.bbs-platform.com` | admin@bbs.com / admin123 |
| API Docs (Swagger) | `https://app.bbs-platform.com/docs` | - |
| Grafana | `https://app.bbs-platform.com/monitoring` | admin / admin |
| Prometheus | `https://app.bbs-platform.com/metrics` | - |

## Project Structure

```
behavioral-biometric-bank/
├── backend/                       # FastAPI backend service
│   ├── app/
│   │   ├── api/                   # API route handlers
│   │   ├── middleware/            # Auth, audit, rate limiting
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # Business logic
│   │   ├── config.py             # Settings
│   │   ├── database.py           # DB connection
│   │   ├── exceptions.py         # Custom exceptions
│   │   ├── main.py               # Entry point
│   │   ├── tasks.py              # Celery tasks
│   │   └── utils.py              # Utilities
│   ├── alembic/                  # Migrations
│   └── Dockerfile
├── ml/                           # ML engine
│   ├── models/                   # Model implementations
│   ├── feature_engineering.py    # Feature extraction
│   ├── training_pipeline.py      # Model training
│   ├── inference_pipeline.py     # Real-time scoring
│   ├── risk_engine.py            # Risk assessment
│   ├── explainability.py         # XAI explanations
│   ├── drift_detection.py        # Drift monitoring
│   ├── behavioral_profile.py     # Profile management
│   ├── model_registry.py         # Model registry
│   ├── evaluation.py             # Model evaluation
│   └── config.py                 # ML configuration
├── frontend/                     # Next.js banking app
├── security-dashboard/           # Next.js fraud dashboard
├── mobile/                       # Flutter mobile app
├── client_sdk/                   # Behavioral tracking SDKs
│   ├── web/                      # JavaScript SDK
│   └── mobile/                   # Native mobile SDK
├── database/                     # Schemas & data
├── docker/                       # Docker configuration
├── tests/                        # Test suite
└── docs/                         # Documentation
```

## Documentation

| Document | Description |
|---|---|
| [System Architecture](docs/architecture.md) | Architecture, components, data flows |
| [API Reference](docs/api.md) | Full API documentation |
| [Deployment Guide](docs/deployment.md) | Production deployment guide |
| [Developer Guide](docs/developer.md) | Setup, standards, contribution |
| [User Guide](docs/user-guide.md) | Customer & analyst manuals |
| [Data Flow Diagrams](docs/data-flow.md) | Mermaid sequence diagrams |
| [Security](docs/security.md) | Auth, compliance, data protection |
| [ML Architecture](docs/ml-architecture.md) | ML pipeline details |
| [Mobile SDK](docs/mobile-sdk.md) | SDK integration guide |

## License

Proprietary - All rights reserved.
