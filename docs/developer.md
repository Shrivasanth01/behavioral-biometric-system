# Developer Guide

## Development Setup

### Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Backend development |
| Node.js | 18+ | Frontend/dashboard development |
| Flutter | 3+ | Mobile development |
| Docker | 24+ | Containerized services |
| PostgreSQL | 16 | Database (or use Docker) |
| Redis | 7 | Cache/broker (or use Docker) |
| Git | 2.40+ | Version control |
| VS Code | Latest | Recommended IDE |

### Clone and Initialize

```bash
git clone https://github.com/your-org/behavioral-biometric-bank.git
cd behavioral-biometric-bank
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest pytest-asyncio pytest-cov black ruff mypy

# Configure environment
cp .env.example .env
# Edit .env with local settings (defaults work with Docker services)
```

**Environment file (`.env`):**
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/biometric_bank
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
SECRET_KEY=dev-secret-key-do-not-use-in-production
ENVIRONMENT=development
LOG_LEVEL=debug
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
```

**Environment file (`frontend/.env.local`):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/ws
```

### Security Dashboard Setup

```bash
cd security-dashboard
npm install
cp .env.local.example .env.local
```

### Mobile Setup

```bash
cd mobile
flutter pub get

# For iOS
cd ios && pod install && cd ..

# Run on device/emulator
flutter run
```

### Docker Services (Development)

```bash
# Start only infrastructure services
docker compose -f docker/docker-compose.yml up -d postgres redis

# Run backend and frontend locally (with hot reload)
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

## Project Structure

### Backend (`backend/`)

```
backend/
├── app/
│   ├── api/                    # API route handlers (one file per domain)
│   │   ├── __init__.py
│   │   ├── auth.py             # Login, register, MFA, password reset
│   │   ├── banking.py          # Accounts, transfers, beneficiaries, cards, loans
│   │   ├── behavioral.py       # Event ingestion, profiles, history
│   │   ├── risk.py             # Risk assessment, alerts, explainability, dashboard
│   │   └── admin.py            # User management, models, audit logs
│   ├── middleware/              # FastAPI middleware
│   │   ├── __init__.py
│   │   ├── auth.py             # JWT authentication, role-based authorization
│   │   ├── audit.py            # Audit logging for state changes
│   │   └── rate_limit.py       # Redis-backed rate limiting
│   ├── models/                  # SQLAlchemy ORM models (one file per entity)
│   │   ├── __init__.py
│   │   ├── user.py             # User, device_fingerprints, sessions
│   │   ├── account.py          # Bank accounts
│   │   ├── transaction.py      # Financial transactions
│   │   ├── card.py             # Debit/credit cards
│   │   ├── beneficiary.py      # Saved beneficiaries
│   │   ├── loan.py             # Loans and EMI schedules
│   │   └── behavioral.py       # Events, features, profiles, risk scores, alerts
│   ├── schemas/                 # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── auth.py             # Auth-related schemas
│   │   ├── banking.py          # Banking-related schemas
│   │   ├── behavioral.py       # Behavioral event schemas
│   │   ├── risk.py             # Risk/fraud schemas
│   │   └── user.py             # User profile schemas
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication, MFA, token management
│   │   ├── banking_service.py  # Account ops, transfers, cards, loans
│   │   ├── behavioral_service.py # Event processing, profile management
│   │   ├── risk_service.py     # Risk assessment, alerting, explainability
│   │   └── notification_service.py # Email, SMS, push notifications
│   ├── __init__.py
│   ├── config.py               # Application settings (pydantic-settings)
│   ├── database.py             # Async engine, session factory, init/close
│   ├── exceptions.py           # Custom exception classes with error codes
│   ├── main.py                 # FastAPI app factory, middleware registration
│   ├── tasks.py                # Celery task definitions
│   └── utils.py                # Shared utilities (validators, generators)
├── alembic/                    # Database migrations
│   ├── versions/               # Migration scripts (auto-generated)
│   ├── env.py                  # Alembic environment config
│   ├── script.py.mako          # Migration template
│   └── README
├── alembic.ini                 # Alembic configuration
├── requirements.txt            # Python dependencies
└── Dockerfile                  # Multi-stage Docker build
```

### ML Engine (`ml/`)

```
ml/
├── models/
│   ├── __init__.py             # Exports UserModel, GlobalModel
│   ├── user_model.py           # Isolation Forest + SVM + Autoencoder per user
│   └── global_model.py         # Ensemble of Isolation Forests (population)
├── __init__.py                 # Exports all public classes
├── config.py                   # MLConfig with FeatureConfig, ModelHyperparams, RiskConfig
├── feature_engineering.py      # 36-feature extraction from raw events
├── training_pipeline.py        # Cold-start management, training orchestration
├── inference_pipeline.py       # Real-time scoring with caching
├── risk_engine.py              # Hybrid ML + rules + heuristics assessment
├── explainability.py           # Feature contribution-based explanations
├── drift_detection.py          # PSI, KL divergence, concept drift monitoring
├── behavioral_profile.py       # Per-user behavioral profile persistence
├── model_registry.py           # Versioned model storage with rollback
├── evaluation.py               # Model metrics, cross-validation, comparison
└── utils.py                    # NumPy/scipy utilities for feature engineering
```

### Frontend (`frontend/`)

```
frontend/
├── app/                        # Next.js 14 App Router
│   ├── (auth)/                 # Auth-related pages (login, register, MFA)
│   ├── (dashboard)/            # Main banking dashboard
│   │   ├── accounts/           # Account details and transactions
│   │   ├── transfer/           # Transfer initiation flow
│   │   ├── cards/              # Card management
│   │   ├── loans/              # Loans and EMI
│   │   └── beneficiaries/      # Beneficiary management
│   ├── layout.tsx              # Root layout with providers
│   └── page.tsx                # Landing/splash page
├── components/                 # Reusable React components
│   ├── auth/                   # LoginForm, RegisterForm, MFAChallenge
│   ├── dashboard/              # AccountCard, TransactionList, TrustScoreMeter
│   ├── transfer/               # TransferForm, BeneficiarySelect, Confirmation
│   ├── cards/                  # CardView, FreezeToggle, LimitSlider
│   ├── loans/                  # LoanCard, EMIChart, Calculator
│   ├── ui/                     # Button, Input, Modal, Tabs, Badge, Table
│   └── layout/                 # Sidebar, Header, Footer, Navigation
├── hooks/                      # Custom React hooks
│   ├── useAuth.ts              # Authentication state and token management
│   ├── useBehavioralTracker.ts # Web SDK initialization and lifecycle
│   ├── useAccounts.ts          # Account data fetching
│   └── usePagination.ts        # Paginated data fetching
├── lib/                        # Utilities
│   ├── api.ts                  # Axios/fetch wrapper with JWT interceptor
│   ├── constants.ts            # API endpoints, route paths
│   ├── formatters.ts           # Currency, date, number formatters
│   └── validators.ts           # Client-side form validation
├── types/                      # TypeScript type definitions
│   ├── api.ts                  # API response types
│   ├── banking.ts              # Account, transaction, card types
│   └── auth.ts                 # User, login, MFA types
├── public/                     # Static assets
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## Coding Standards

### Python (Backend & ML)

- **Style**: PEP 8 compliant, line length 120 characters
- **Formatting**: Black with default settings
- **Import Order**: standard library, third-party, local (alphabetical within groups)
- **Type Hints**: Required for all function signatures
- **Docstrings**: Google style for public functions, 1-line for private
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes, `SCREAMING_SNAKE` for constants
- **Error Handling**: Use custom exception classes from `app.exceptions`, never catch bare `Exception`

**Example:**
```python
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.exceptions import NotFoundException
from app.models.user import User


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> Optional[User]:
    """Retrieve a user by email address.

    Args:
        db: Database session.
        email: User's email address.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
```

### TypeScript (Frontend & Dashboard)

- **Style**: ESLint with recommended TypeScript rules
- **Formatting**: Prettier with 100 char width
- **Naming**: `camelCase` for variables/functions, `PascalCase` for components/types/interfaces, `SCREAMING_SNAKE` for constants
- **Components**: Functional components with hooks, named exports
- **Types**: Prefer `interface` over `type` for object shapes
- **State Management**: React hooks (useState, useReducer) + Context for global state
- **API Calls**: Centralized `api.ts` client with interceptors for auth token injection

**Example:**
```typescript
// types/banking.ts
export interface Account {
  id: number;
  uuid: string;
  accountNumber: string;
  accountType: 'savings' | 'current';
  currency: string;
  balance: string;
  availableBalance: string;
  status: 'active' | 'dormant' | 'closed' | 'frozen';
  openedAt: string;
}

// hooks/useAccounts.ts
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { Account } from '@/types/banking';

export function useAccounts() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/accounts')
      .then((res) => setAccounts(res.data.items))
      .finally(() => setLoading(false));
  }, []);

  return { accounts, loading };
}
```

### Dart (Mobile)

- **Style**: flutter_lints (official linter rules)
- **Formatting**: `dart format` with default settings
- **Naming**: `camelCase` for variables/functions, `PascalCase` for classes, `lowercase_with_underscores` for libraries/packages
- **State Management**: Provider pattern
- **API Calls**: Centralized HTTP client in `services/api_service.dart`

### Commit Messages

```
<type>(<scope>): <subject>

[optional body]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`
**Scopes:** `backend`, `frontend`, `ml`, `mobile`, `sdk`, `dashboard`, `docs`, `infra`

**Examples:**
```
feat(ml): add swipe velocity features for mobile touch data
fix(backend): handle null device fingerprint in risk assessment
docs(api): add request/response schemas for transfer endpoint
refactor(frontend): extract TransferForm into reusable component
```

### Branch Naming

```
<type>/<description>
```

**Examples:**
```
feat/mobile-swipe-features
fix/null-riskscore-handling
docs/api-transfer-schemas
refactor/transfer-form-component
```

### Code Review Process

1. Create feature branch from `main`
2. Implement changes with tests
3. Run linting and type checking locally:
   ```bash
   # Backend
   cd backend && ruff check . && mypy .

   # Frontend
   cd frontend && npm run lint && npm run typecheck
   ```
4. Push branch and create pull request
5. PR title follows commit message format
6. At least 1 reviewer approval required
7. All CI checks must pass (lint, test, build)
8. Squash-merge to `main`

## Testing

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_risk_engine.py -v

# Run with markers
pytest -m "not integration" -v

# ML tests
cd ml
pytest ../tests/test_ml.py -v

# Frontend tests
cd frontend
npm run test

# Mobile tests
cd mobile
flutter test
```

### Writing Tests

**Backend test structure:**
```python
# tests/test_auth_service.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_register_creates_user():
    # Arrange
    mock_db = AsyncMock()
    service = AuthService(mock_db)
    email = "test@example.com"
    password = "SecureP@ss123"

    # Act
    user = await service.register(email, password)

    # Assert
    assert user.email == email
    mock_db.add.assert_called_once()
    mock_db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_with_invalid_credentials_raises():
    mock_db = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    service = AuthService(mock_db)

    with pytest.raises(UnauthorizedException):
        await service.login("wrong@email.com", "wrongpass")
```

**ML test structure:**
```python
# tests/test_ml.py
import numpy as np
import pytest
from ml.feature_engineering import FeatureEngine
from ml.models.user_model import UserModel


def test_feature_extraction_keystroke():
    engine = FeatureEngine()
    events = [
        {"type": "keydown", "key": "a", "timestamp": 0},
        {"type": "keyup", "key": "a", "timestamp": 80},
        {"type": "keydown", "key": "b", "timestamp": 200},
        {"type": "keyup", "key": "b", "timestamp": 280},
    ]
    features = engine.extract_all(events)
    assert "typing_speed_mean" in features
    assert features["key_hold_mean"] > 0


def test_user_model_train_and_predict():
    model = UserModel("test_user")
    X = np.random.randn(50, 36)
    result = model.train(X)
    assert result["version"] == 1

    score, contributions = model.predict(np.random.randn(1, 36))
    assert 0 <= score <= 100
    assert len(contributions) > 0
```

### Test Coverage Requirements

| Module | Minimum Coverage |
|---|---|
| Backend services | 85% |
| Backend API routes | 80% |
| ML engine | 90% |
| Frontend components | 70% |
| Mobile | 60% |

## CI Pipeline

The CI pipeline runs on every push and pull request:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: biometric_bank
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports: [5432:5432]
      redis:
        image: redis:7-alpine
        ports: [6379:6379]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: pip install -r backend/requirements.txt
      - run: pip install pytest pytest-asyncio pytest-cov ruff mypy
      - run: ruff check backend/
      - run: mypy backend/
      - run: pytest tests/ -v --cov=backend --cov-report=xml

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "18"
          cache: npm
          cache-dependency-path: frontend/package.json
      - run: npm ci
        working-directory: frontend
      - run: npm run lint
        working-directory: frontend
      - run: npm run build
        working-directory: frontend

  ml:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: pip install -r backend/requirements.txt
      - run: pip install scikit-learn numpy pandas scipy tensorflow-cpu
      - run: pytest tests/test_ml.py -v --cov=ml --cov-report=xml
```

## Building

### Docker Images

```bash
# Build all images
docker compose -f docker/docker-compose.yml build

# Build individual images
docker build -f docker/backend/Dockerfile -t bbs-backend:latest .
docker build -f docker/frontend/Dockerfile -t bbs-frontend:latest .
docker build -f docker/ml/Dockerfile -t bbs-ml:latest .

# Tag and push to registry
docker tag bbs-backend:latest registry.bbs-platform.com/bbs-backend:latest
docker push registry.bbs-platform.com/bbs-backend:latest
```

### Mobile Apps

```bash
# Android APK
cd mobile
flutter build apk --release

# Android App Bundle (Play Store)
flutter build appbundle --release

# iOS (requires macOS with Xcode)
flutter build ios --release
```

## Common Tasks

### Adding a New API Endpoint

1. **Define Pydantic schemas** in `backend/app/schemas/`
2. **Create/update service method** in `backend/app/services/`
3. **Add route handler** in the appropriate `backend/app/api/` file
4. **Register router** in `backend/app/main.py` if new file
5. **Add tests** in `tests/`

**Example:**
```python
# backend/app/schemas/banking.py
class BillPaymentRequest(BaseModel):
    account_id: int
    biller_code: str
    amount: Decimal
    scheduled_date: Optional[date] = None

class BillPaymentResponse(BaseModel):
    reference: str
    status: str

# backend/app/services/banking_service.py
async def pay_bill(self, user_id: int, account_id: int, biller_code: str, amount: Decimal) -> dict:
    account = await self._get_account(account_id, user_id)
    if account.balance < amount:
        raise InsufficientBalanceException()
    # ... processing logic
    return {"reference": generate_reference_number(), "status": "completed"}

# backend/app/api/banking.py
@router.post("/bills/pay", response_model=BillPaymentResponse)
async def pay_bill(
    request: Request,
    req: BillPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = BankingService(db)
    result = await service.pay_bill(current_user.id, req.account_id, req.biller_code, req.amount)
    await audit_logger(request, "bill_payment", "transaction", result["reference"], ...)
    return BillPaymentResponse(**result)
```

### Adding a New Database Migration

```bash
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "add_bill_payments_table"

# Review the generated migration
cat alembic/versions/abc123_add_bill_payments_table.py

# Apply migration
alembic upgrade head
```

### Adding a New ML Feature

1. **Define feature name** in `ml/config.py` `FeatureConfig`
2. **Implement extraction** in the appropriate method of `FeatureEngine`
3. **Add normalization** handling in `ml/utils.py` if needed
4. **Update tests** in `tests/test_ml.py`
5. **Retrain existing models** to incorporate new feature dimensions

**Example:**
```python
# In ml/config.py FeatureConfig
mouse_features: List[str] = field(default_factory=lambda: [
    # ... existing features
    "scroll_acceleration",  # new feature
])

# In ml/feature_engineering.py FeatureEngine._extract_mouse_features()
if not scroll_events.empty:
    scroll_deltas = scroll_events.get("delta_y", 0).values.astype(np.float64)
    if len(scroll_deltas) > 2:
        scroll_accels = np.diff(np.abs(scroll_deltas))
        features["scroll_acceleration"] = float(np.mean(scroll_accels))
    else:
        features["scroll_acceleration"] = 0.0
```

### Adding a New UI Component

1. **Create component file** in `frontend/components/<category>/`
2. **Define TypeScript interfaces** in `frontend/types/`
3. **Add stories/test** (if applicable)
4. **Export from barrel file**
5. **Import and use in page**

**Example:**
```tsx
// frontend/components/ui/TrustScoreMeter.tsx
'use client';

import { cn } from '@/lib/utils';

interface TrustScoreMeterProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export function TrustScoreMeter({ score, size = 'md', showLabel = true }: TrustScoreMeterProps) {
  const color = score <= 30 ? 'text-green-500' : score <= 70 ? 'text-yellow-500' : 'text-red-500';

  return (
    <div className={cn('flex items-center gap-2', size === 'sm' && 'scale-75')}>
      <div className="relative w-16 h-16">
        <svg viewBox="0 0 36 36" className="w-full h-full">
          <path
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="3"
          />
          <path
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeDasharray={`${score}, 100`}
            className={color}
          />
        </svg>
        <span className={cn('absolute inset-0 flex items-center justify-center text-sm font-bold', color)}>
          {score}
        </span>
      </div>
      {showLabel && <span className="text-sm text-gray-600">Trust Score</span>}
    </div>
  );
}
```
