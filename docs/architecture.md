# System Architecture

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                  CLIENT LAYER                                            │
│                                                                                          │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐   │
│  │     Banking Web App     │  │   Security Dashboard    │  │  Mobile Banking App     │   │
│  │     (Next.js 14)        │  │   (Next.js 14)          │  │  (Flutter 3)            │   │
│  │                         │  │                         │  │                         │   │
│  │  • Account Dashboard    │  │  • Risk Heatmaps        │  │  • Touch Gesture SDK   │   │
│  │  • Transfer Flow        │  │  • Fraud Alert Queue    │  │  • Sensor Integration  │   │
│  │  • Web SDK Tracker      │  │  • Model Health         │  │  • Mobile SDK Built In │   │
│  │  • MFA Setup            │  │  • Audit Log Viewer     │  │  • Push Notifications  │   │
│  └───────────┬─────────────┘  └───────────┬─────────────┘  └───────────┬─────────────┘   │
└──────────────┼────────────────────────────┼────────────────────────────┼─────────────────┘
               │                            │                            │
               └────────────────────────────┼────────────────────────────┘
                                            │ HTTPS / WSS
                                            ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                  API GATEWAY LAYER                                       │
│                                                                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐    │
│  │                                    NGINX                                          │    │
│  │                                                                                   │    │
│  │  • SSL Termination (TLS 1.3)    • Rate Limiting (per-IP, per-endpoint)            │    │
│  │  • Reverse Proxy                • Request/Response Compression (gzip)             │    │
│  │  • Static Asset Serving         • WebSocket Proxy (for real-time alerts)          │    │
│  │  • CORS Headers                 • Access Logs to stdout                           │    │
│  └──────────────────┬───────────────────────────────────────────────────────────────┘    │
└─────────────────────┼────────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                              APPLICATION LAYER (FastAPI)                                  │
│                                                                                          │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────┐  │
│  │   Auth Module   │  │  Banking Module │  │  Behavioral    │  │  Risk & Fraud Module  │  │
│  │                 │  │                 │  │  Module        │  │                        │  │
│  │ • POST /register│  │ • GET /accounts│  │ • POST /events │  │ • POST /risk/assess   │  │
│  │ • POST /login   │  │ • POST /txn    │  │ • POST /batch  │  │ • GET /risk/explain   │  │
│  │ • POST /refresh │  │ • GET /txn     │  │ • GET /profile │  │ • GET /risk/alerts    │  │
│  │ • POST /verify  │  │ • CRUD /bens   │  │ • GET /history │  │ • GET /dashboard/*    │  │
│  │ • POST /setup   │  │ • CRUD /cards  │  │                │  │                        │  │
│  │ • POST /me      │  │ • CRUD /loans  │  │                │  │                        │  │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘  └────────────┬───────────┘  │
│           │                   │                   │                       │              │
│           └───────────────────┴───────────────────┴───────────────────────┘              │
│                                     │                                                    │
│           ┌─────────────────────────┴──────────────────────────────────┐                  │
│           │              Middleware Stack                              │                  │
│           │  • JWTAuthMiddleware    • RateLimitMiddleware              │                  │
│           │  • AuditLogMiddleware   • CORSMiddleware                   │                  │
│           │  • PrometheusMetrics    • OpenTelemetry (optional)         │                  │
│           └─────────────────────────┬──────────────────────────────────┘                  │
│                                     │                                                    │
│           ┌─────────────────────────┴──────────────────────────────────┐                  │
│           │              Background Tasks (Celery)                     │                  │
│           │                                                           │                  │
│           │  • process_behavioral_events   • retrain_user_model       │                  │
│           │  • retrain_global_model        • detect_drift             │                  │
│           │  • process_fraud_alert         • send_notification        │                  │
│           │  • cleanup_expired_tokens                                 │                  │
│           └───────────────────────────────────────────────────────────┘                  │
└─────────────────────────────┼────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                              MACHINE LEARNING LAYER                                      │
│                                                                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐    │
│  │                              Feature Engineering                                   │    │
│  │                                                                                   │    │
│  │  Raw Events -> Preprocess -> Extract Keystroke Features (10) ->                   │    │
│  │                  Extract Mouse Features (12) ->                                    │    │
│  │                  Extract Session Features (8) ->                                   │    │
│  │                  Extract Mobile Features (6) ->                                    │    │
│  │                  Normalize -> Feature Vector (36-dim)                              │    │
│  └──────────────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                                   │
│  ┌──────────────────────────────────┴──────────────────────────────────────────────────┐ │
│  │                              Model Training Pipeline                                 │ │
│  │                                                                                      │ │
│  │  ┌─────────────────────────┐    ┌───────────────────────────────────────────────┐    │ │
│  │  │     Global Model        │    │         Per-User Models                        │    │ │
│  │  │                         │    │                                               │    │ │
│  │  │  • 10 Isolation Forests │    │  • Isolation Forest (primary)                 │    │ │
│  │  │  • Bootstrap aggregated │    │  • One-Class SVM (optional)                   │    │ │
│  │  │  • Population baseline  │    │  • Autoencoder (optional, TF)                 │    │ │
│  │  │  • Cold-start fallback  │    │  • Adaptive thresholding                      │    │ │
│  │  └─────────────────────────┘    │  • Session-based retraining                   │    │ │
│  │                                 └───────────────────────────────────────────────┘    │ │
│  └──────────────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                                   │
│  ┌──────────────────────────────────┴──────────────────────────────────────────────────┐ │
│  │                              Inference & Risk                                        │ │
│  │                                                                                      │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  ┌────────────────┐   │ │
│  │  │  User Model     │→│  ML Score       │→│  Risk Engine   │→│  Explainability│   │ │
│  │  │  Prediction     │  │  0-100          │  │  Hybrid(65/25/10)│  │  Feature       │   │ │
│  │  └─────────────────┘  └─────────────────┘  └───────┬────────┘  │  Contributions │   │ │
│  │  ┌─────────────────┐                    ┌──────────┴──┐       └────────────────┘   │ │
│  │  │  Global Model   │                    │ Risk Bands  │                             │ │
│  │  │  (fallback)     │                    │ LOW/MED/HIGH│                             │ │
│  │  └─────────────────┘                    └──────┬──────┘                             │ │
│  │                                                 ▼                                   │ │
│  │                                         ALLOW / MFA / BLOCK                         │ │
│  └──────────────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                                   │
│  ┌──────────────────────────────────┴──────────────────────────────────────────────────┐ │
│  │                              Monitoring & Drift                                     │ │
│  │                                                                                      │ │
│  │  • PSI (Population Stability Index) per feature     • KL Divergence monitoring      │ │
│  │  • Accuracy degradation detection                   • Feature-level drift tracking   │ │
│  │  • Automated retraining triggers                    • Drift severity classification  │ │
│  └──────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────┼────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                    DATA LAYER                                            │
│                                                                                          │
│  ┌────────────────────────────────────────────────────────────────────────────────┐      │
│  │                              PostgreSQL 16                                      │      │
│  │                                                                                  │      │
│  │  21 Tables: users, accounts, transactions, behavioral_events, behavioral_features,│     │
│  │  behavioral_profiles, risk_scores, fraud_alerts, explainability_results,         │      │
│  │  device_fingerprints, sessions, cards, beneficiaries, loans, loan_emi_schedule,  │      │
│  │  ml_models, model_drift_logs, retraining_queue, mfa_tokens, refresh_tokens,     │      │
│  │  audit_logs, schema_migrations                                                   │      │
│  │                                                                                  │      │
│  │  Features: ASync access (asyncpg), connection pooling, JSONB columns,           │      │
│  │  GIN indexes for JSONB, composite indexes, partial indexes, triggers            │      │
│  └────────────────────────────────────────────────────────────────────────────────┘      │
│                                                                                          │
│  ┌─────────────────────────────────┐  ┌────────────────────────────────────────────┐     │
│  │           Redis 7               │  │        File System (Model/Profile Store)   │     │
│  │                                 │  │                                            │     │
│  │  • Cache (model/profiles)      │  │  • Pickle model files (per-user, global)   │     │
│  │  • Celery message broker       │  │  • JSON profile files (behavioral profiles) │     │
│  │  • Session store               │  │  • Model registry (versioned JSON)         │     │
│  │  • Rate limiter counters       │  │  • Training history                        │     │
│  │  • Real-time pub/sub           │  │                                            │     │
│  └─────────────────────────────────┘  └────────────────────────────────────────────┘     │
└─────────────────────────────┼────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                              OBSERVABILITY & MONITORING                                   │
│                                                                                          │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────┐  │
│  │   Prometheus   │  │    Grafana     │  │  ELK Stack     │  │     Alertmanager       │  │
│  │                │  │                │  │                │  │                        │  │
│  │ • HTTP metrics │  │ • System dash  │  │ • App logs    │  │ • Email alerts         │  │
│  │ • ML metrics   │  │ • ML dash      │  │ • Audit logs  │  │ • PagerDuty/Slack      │  │
│  │ • DB metrics   │  │ • Fraud dash   │  │ • Error logs  │  │ • Webhook integrations │  │
│  │ • Redis metrics│  │ • Alert rules  │  │ • Access logs │  │ • Silence management   │  │
│  └────────────────┘  └────────────────┘  └────────────────┘  └────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Banking Application (`frontend/`)

A Next.js 14 application with App Router providing the customer-facing banking interface. Built with TypeScript, Tailwind CSS, and server/client component architecture.

**Key Components:**
- **Auth Module**: Login/register pages with MFA challenge flow, behavioral SDK initialization on login
- **Dashboard**: Real-time account summary, mini-statement, behavioral trust score indicator
- **Transfer Module**: Multi-step transfer initiation with behavioral verification step (trust meter animation), supports internal, external (NEFT/RTGS/IMPS), and UPI transfers
- **Cards Module**: Card listing with masking, freeze/unfreeze toggle, daily/monthly limit controls
- **Loans Module**: Loan application form, EMI calculator with amortization schedule viewer
- **Beneficiary Management**: CRUD with validation, per-beneficiary limits, approval workflows

**Behavioral Integration:**
- `BehavioralTracker` (Web SDK) initialized on successful authentication
- Tracks all user interactions during banking sessions
- Sends batched event data to `/api/events` every 5 seconds
- Device fingerprint collected on first load and stored in session

### 2. Security Dashboard (`security-dashboard/`)

A separate Next.js 14 application for fraud analysts and administrators. Provides real-time monitoring and investigation tools.

**Key Components:**
- **Executive Overview**: Summary cards (total users, alerts by severity, avg risk score, blocked transactions today), trend charts
- **Alert Management**: Table with severity badges, status filters, bulk actions, assign-to flow
- **User Investigation**: Search by email/ID, view user profile, behavioral timeline, risk history chart, device inventory
- **Session Timeline**: Event replay viewer with feature contribution breakdow, anomaly score visualization
- **ML Health**: Model version tracker, drift indicators, retraining history, accuracy metrics
- **Audit Logs**: Full-text search, action type filter, date range, export to CSV

### 3. Backend API (`backend/`)

FastAPI application with async support, serving as the central orchestration layer.

**API Route Structure:**
- `/api/auth/*` - Authentication, MFA, password management
- `/api/accounts/*` - Account listing and details
- `/api/transactions/*` - Transfer creation and history
- `/api/cards/*` - Card management
- `/api/loans/*` - Loan applications and EMI
- `/api/beneficiaries/*` - Beneficiary CRUD
- `/api/events/*` - Behavioral event ingestion (single and batch)
- `/api/risk/*` - Risk assessment, explainability, fraud alerts, dashboard
- `/api/admin/*` - User management, model management, audit logs

**Middleware Stack:**
- **JWTAuthMiddleware**: Validates JWT access tokens, extracts user context, supports optional auth for event ingestion
- **RateLimitMiddleware**: Per-IP and per-endpoint rate limiting using Redis, configurable windows and limits
- **AuditLogMiddleware**: Logs all state-changing operations with before/after values
- **CORSMiddleware**: Configurable allowed origins for web clients
- **PrometheusMetrics**: HTTP request count, duration histograms, ML model metrics

**Celery Task Queue:**
- `process_behavioral_events` - Async event processing and profile update
- `retrain_user_model` - Per-user model retraining triggered by session count or schedule
- `retrain_global_model` - Global model retraining from aggregate user data
- `detect_drift` - Scheduled drift detection across all user profiles
- `process_fraud_alert` - Alert enrichment and severity classification
- `send_notification` - Email/SMS OTP and transaction alerts
- `cleanup_expired_tokens` - Daily cleanup of expired tokens and old log entries

### 4. ML Engine (`ml/`)

The core machine learning module, independent of the web framework and designed for both synchronous and asynchronous usage.

**Modules:**

| Module | Responsibility |
|---|---|
| `feature_engineering.py` | Transforms raw event tuples into 36-dimensional feature vectors |
| `models/user_model.py` | Per-user Isolation Forest with optional One-Class SVM and Autoencoder |
| `models/global_model.py` | Ensemble of Isolation Forests trained on aggregate population data |
| `training_pipeline.py` | Orchestrates model training with cold-start management, versioning |
| `inference_pipeline.py` | Real-time scoring with model caching (TTL-based), fallback to global |
| `risk_engine.py` | Hybrid risk scoring combining ML, rules, and heuristics |
| `explainability.py` | Generates human-readable explanations with feature contributions |
| `drift_detection.py` | PSI/KL divergence monitoring, concept drift detection |
| `behavioral_profile.py` | Manages per-user behavioral profiles (file-based JSON persistence) |
| `model_registry.py` | Versioned model registry with rollback and metrics tracking |
| `evaluation.py` | ROC/PR curves, cross-validation, model comparison, optimal threshold |
| `config.py` | Centralized ML configuration with dataclasses |
| `utils.py` | Statistical utilities (entropy, PSI, KL divergence, normalization) |

### 5. Behavioral SDKs (`client_sdk/`)

**Web SDK (`client_sdk/web/tracker.js`):**
- Pure JavaScript class (`BehavioralTracker`) with no external dependencies
- Event types captured: keydown, keyup, mousemove (throttled), mousedown, mouseup, click, contextmenu, dblclick, touchstart, touchmove, touchend, scroll, wheel, focus, blur, focusin, focusout, copy, cut, paste, resize, visibilitychange, popstate, beforeunload
- Device fingerprinting: Canvas 2D rendering, WebGL renderer info, AudioContext frequency data, installed font detection (24 fonts tested), screen properties, hardware concurrency, device memory, SHA-256 combined hash
- Batching: configurable interval (default 5s), max batch size (default 50), exponential backoff retry (max 3 attempts), sendBeacon fallback for page unload
- Session management: auto-generated UUID session IDs, activity-based timeouts (default 30 min), freeze/resume on tab visibility changes
- Public API: `start()`, `stop()`, `getPayload()`, `submit()`, `getFingerprint()`, `getSessionId()`, `clearEvents()`, `getEventCount()`, `onEvent()`, `offEvent()`, `destroy()`

**Mobile SDK (`client_sdk/mobile/`):**
- Native Android and iOS SDK wrappers for Flutter integration
- Captures touch gestures (start/move/end with coordinates, pressure, radius, rotation)
- Sensor data: accelerometer, gyroscope (for device orientation and hand movement patterns)
- Multi-touch detection for gesture complexity analysis
- Biometric integration with platform-local auth (fingerprint, Face ID)

### 6. Database Layer

PostgreSQL 16 with 21 tables covering all banking, behavioral, and ML operations.

**Key Tables:**

| Table | Purpose | Key Columns |
|---|---|---|
| `users` | User accounts and credentials | uuid, email, password_hash, role, mfa_secret |
| `device_fingerprints` | Registered device fingerprints | device_id, user_id, canvas/audio/webgl hashes, is_trusted |
| `accounts` | Bank accounts | account_number, type, balance, status |
| `cards` | Debit/credit cards | masked_number, card_hash, daily/monthly limits |
| `transactions` | All financial transactions | amount, type, status, counterparty, reference, UTC timestamp |
| `beneficiaries` | Saved beneficiaries | beneficiary_account, max_limit, approval_required |
| `loans` | Loan accounts | principal, interest_rate, tenure, outstanding, EMI |
| `behavioral_events` | Raw behavioral event data | event_type, event_data (JSONB), client_timestamp, session_id |
| `behavioral_features` | Extracted feature vectors | feature_set, mouse/keystroke/touch JSONB, combined_vector |
| `behavioral_profiles` | User behavioral baselines | keystroke/mouse/navigation/touch patterns (JSONB) |
| `risk_scores` | Risk assessment results | score, level, feature_contributions (JSONB), model_version |
| `fraud_alerts` | Generated fraud alerts | type, severity, status, reason_codes, anomaly_details |
| `explainability_results` | Explainability records | explanation_type, reason_codes, top_features, shap_values |
| `ml_models` | Model metadata and binary | model_type, algorithm, metrics, is_production |
| `model_drift_logs` | Drift detection history | drift_type, score, drifted_features, window range |
| `audit_logs` | Immutable audit trail | action, entity, old/new_values, ip, user_agent |

### 7. Infrastructure

**Container Architecture:**
- All services run in Docker containers orchestrated by Docker Compose
- Shared network `bbs-network` for inter-service communication
- Persistent volumes for databases, models, and monitoring data
- Health checks on every service with configurable intervals and retries

**Service Dependencies:**
```
                 ┌──────────┐
                 │   Nginx  │
                 └────┬─────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────┴────┐  ┌────┴────┐  ┌─────┴─────┐
   │ Frontend│  │ Backend │  │  Security │
   │ :3000   │  │ :8000   │  │ Dashboard │
   └─────────┘  └────┬────┘  │ :3001     │
                      │      └───────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────┴────┐  ┌────┴────┐  ┌─────┴─────┐
   │Postgres │  │  Redis  │  │ ML Service│
   │ :5432   │  │ :6379   │  │ :8001     │
   └─────────┘  └─────────┘  └───────────┘
```

## Data Flow

### Authentication Flow

```
User                    Browser/App               Backend API               ML Engine              Database
 │                         │                         │                        │                    │
 │  Enter credentials      │                         │                        │                    │
 │────────────────────────►│                         │                        │                    │
 │                         │  POST /api/auth/login    │                        │                    │
 │                         │────────────────────────►│                        │                    │
 │                         │                         │  Validate credentials  │                    │
 │                         │                         │───────────────────────►│                    │
 │                         │                         │  Verify password       │                    │
 │                         │                         │──────────────────────────────────────────────►│
 │                         │                         │◄──────────────────────────────────────────────│
 │                         │                         │                        │                    │
 │                         │                         │  Check MFA enabled?    │                    │
 │                         │                         │◄──────────────────────►│                    │
 │                         │                         │                        │                    │
 │                         │  MFA Challenge (if req) │                        │                    │
 │                         │◄────────────────────────│                        │                    │
 │  MFA Code Entry         │                         │                        │                    │
 │────────────────────────►│                         │                        │                    │
 │                         │  POST /api/auth/verify   │                        │                    │
 │                         │────────────────────────►│                        │                    │
 │                         │                         │  Verify TOTP/OTP       │                    │
 │                         │                         │──────────────────────────────────────────────►│
 │                         │                         │◄──────────────────────────────────────────────│
 │                         │                         │                        │                    │
 │                         │                         │  Generate JWT          │                    │
 │                         │                         │  Create session        │                    │
 │                         │                         │──────────────────────────────────────────────►│
 │                         │                         │                        │                    │
 │                         │  JWT + Session          │                        │                    │
 │                         │◄────────────────────────│                        │                    │
 │                         │                         │                        │                    │
 │  [App Initializes SDK]  │                         │                        │                    │
 │◄────────────────────────│                         │                        │                    │
 │                         │                         │                        │                    │
 │  User interacts         │                         │                        │                    │
 │  (type, click, scroll)  │                         │                        │                    │
 │────────────────────────►│                         │                        │                    │
 │                         │  POST /api/events (batch)│                       │                    │
 │                         │────────────────────────►│                        │                    │
 │                         │                         │  Store behavioral      │                    │
 │                         │                         │  events                │                    │
 │                         │                         │──────────────────────────────────────────────►│
 │                         │                         │                        │                    │
 │                         │                         │  Celery: process events│                    │
 │                         │                         │───────────────────────►│                    │
 │                         │                         │                        │  Feature extract   │
 │                         │                         │                        │  Model score       │
 │                         │                         │                        │  Risk assessment   │
 │                         │                         │                        │  Update profile    │
 │                         │                         │◄───────────────────────│                    │
 │                         │                         │──────────────────────────────────────────────►│
```

### Transaction Flow

```
User                Frontend              Backend API            ML Engine            DB
 │                     │                      │                    │                 │
 │  Initiate transfer  │                      │                    │                 │
 │────────────────────►│                      │                    │                 │
 │                     │  POST /txn/transfer  │                    │                 │
 │                     │─────────────────────►│                    │                 │
 │                     │                      │  Validate balance  │                 │
 │                     │                      │──────────────────────────────►       │
 │                     │                      │◄──────────────────────────────       │
 │                     │                      │                    │                 │
 │                     │                      │  Request risk      │                 │
 │                     │                      │  assessment        │                 │
 │                     │                      │───────────────────►│                 │
 │                     │                      │                    │  Load profile   │
 │                     │                      │                    │─────────────►   │
 │                     │                      │                    │◄──────────────   │
 │                     │                      │                    │                 │
 │                     │                      │                    │  Extract feats  │
 │                     │                      │                    │  Score model    │
 │                     │                      │                    │  Evaluate rules │
 │                     │                      │                    │  Compute risk   │
 │                     │                      │                    │                 │
 │                     │                      │◄───────────────────│                 │
 │                     │                      │                    │                 │
 │                     │                      │  Risk Assessment   │                 │
 │                     │                      │  Result            │                 │
 │                     │                      │                    │                 │
 │    ┌────────────────┴──────────────────────┴────────────────────┴─────────────┐  │
 │    │  Risk Band Decision:                                                     │  │
 │    │  LOW (0-30)   -> ALLOW -> Execute transaction                            │  │
 │    │  MEDIUM (31-70)-> MFA  -> Prompt OTP -> Execute if verified              │  │
 │    │  HIGH (71-100) -> BLOCK -> Alert fraud team -> Notify user               │  │
 │    └──────────────────────────────────────────────────────────────────────────┘  │
 │                     │                      │                    │                 │
 │  MFA (if MEDIUM)    │                      │                    │                 │
 │◄────────────────────│                      │                    │                 │
 │  Enter OTP          │                      │                    │                 │
 │────────────────────►│  POST /auth/verify   │                    │                 │
 │                     │─────────────────────►│                    │                 │
 │                     │                      │  Verify MFA        │                 │
 │                     │                      │──────────────────────────────►       │
 │                     │                      │◄──────────────────────────────       │
 │                     │                      │                    │                 │
 │                     │                      │  Execute transfer  │                 │
 │                     │                      │──────────────────────────────►       │
 │                     │                      │◄──────────────────────────────       │
 │                     │                      │                    │                 │
 │  Success/Failure    │                      │                    │                 │
 │◄────────────────────│                      │                    │                 │
```

### Behavioral Learning Flow

```
User SDK          Event Ingestion        Celery Worker         ML Engine              Profile Store
   │                    │                     │                    │                      │
   │─── Raw Events ───►│                     │                    │                      │
   │  (batched)        │  Store events       │                    │                      │
   │                   │ ────────────────────────────────────────►│                      │
   │                   │                     │                    │                      │
   │                   │  Queue process      │                    │                      │
   │                   │────────────────────►│                    │                      │
   │                   │                     │                    │                      │
   │                   │                     │  Fetch events      │                      │
   │                   │                     │───────────────────►│                      │
   │                   │                     │                    │                      │
   │                   │                     │  Extract features  │                      │
   │                   │                     │  36-dim vector     │                      │
   │                   │                     │                    │                      │
   │                   │                     │  Load user model   │                      │
   │                   │                     │───────────────────►│                      │
   │                   │                     │  Score features    │                      │
   │                   │                     │  Update profile    │                      │
   │                   │                     │──────────────────────────────────────────►│
   │                   │                     │                    │                      │
   │                   │                     │  Check retrain?   │                      │
   │                   │                     │  (every 10 sess)  │                      │
   │                   │                     │  If yes:           │                      │
   │                   │                     │  ┌─────────────────┴─────────────┐        │
   │                   │                     │  │ • Gather previous features   │        │
   │                   │                     │  │ • Concatenate with new       │        │
   │                   │                     │  │ • Train Isolation Forest     │        │
   │                   │                     │  │ • Compute adaptive threshold │        │
   │                   │                     │  │ • Persist model to disk      │        │
   │                   │                     │  │ • Update model registry      │        │
   │                   │                     │  │ • Update profile version     │        │
   │                   │                     │  └──────────────────────────────┘        │
   │                   │                     │──────────────────────────────────────────►│
```

## Security Architecture

### Authentication
- **JWT Access Tokens**: HS256-signed, 30-minute expiry, contain user_id, role, session_id
- **JWT Refresh Tokens**: Opaque tokens stored hashed in DB, 7-day expiry, rotation on use
- **MFA**: TOTP (RFC 6238) via authenticator apps, SMS/Email OTP as backup, device-bound session verification
- **Password Security**: Bcrypt hashing (12 rounds), minimum 8 chars with upper/lower/digit/special requirements

### Authorization
- **RBAC**: Three roles - `customer` (self-service), `analyst` (fraud investigation), `admin` (system management)
- **Endpoint Protection**: `get_current_user` for basic auth, `require_analyst`/`require_admin` decorators for privileged endpoints
- **Resource Isolation**: Users can only access their own accounts, transactions, and behavioral data

### Data Protection
- **In Transit**: TLS 1.3 enforced at Nginx gateway, all service communication over internal Docker network
- **At Rest**: Disk-level encryption recommended, card numbers stored as irreversible hashes, CVV never stored
- **PII Handling**: Behavioral events exclude form values (only field selectors are captured), timestamps relative
- **Audit Trail**: Immutable audit_logs table records all state changes with before/after values, IP addresses

### Rate Limiting
- Default: 100 requests per 60-second window per IP
- Auth endpoints: 5 requests per 60-second window
- Behavioral ingestion: 1000 events per 60-second window per session
- Implemented via Redis-backed sliding window counter

## Deployment Architecture

See [Deployment Guide](deployment.md) for full production deployment details.
