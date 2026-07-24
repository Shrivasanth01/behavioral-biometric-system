# Behavioral Biometric Banking Platform - Test Suite

## How to Run Tests

### Prerequisites
```bash
pip install -r backend/requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx pytest-mock pytest-xdist
```

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=. --cov-report=term-missing --cov-report=html:coverage_html
```

### Run Specific Test Modules
```bash
pytest tests/test_ml/
pytest tests/test_backend/
pytest tests/test_integration/
pytest tests/test_security/
```

### Run Tests in Parallel
```bash
pytest -n auto
```

### Run Tests with Verbose Output
```bash
pytest -v --tb=short
```

## Test Structure

```
tests/
  __init__.py              # Package init, adds project root to sys.path
  conftest.py              # Shared pytest fixtures (DB, client, auth, ML models)
  README.md                # This file

  test_backend/            # Backend API and service tests
    test_auth.py           # Authentication endpoints (20+ tests)
    test_banking.py        # Banking endpoints (20+ tests)
    test_behavioral.py     # Behavioral event endpoints (15+ tests)
    test_risk.py           # Risk engine endpoints (15+ tests)
    test_middleware.py     # Middleware tests

  test_ml/                 # ML engine tests
    test_feature_engineering.py  # Feature extraction (15+ tests)
    test_models.py         # Model training/inference (15+ tests)
    test_training_pipeline.py   # Training pipeline tests
    test_risk_engine.py    # Risk engine scoring tests
    test_explainability.py # Explanation generation tests
    test_drift_detection.py     # Drift detection tests
    test_behavioral_profile.py  # Profile management tests

  test_integration/        # End-to-end integration tests
    test_auth_flow.py      # Full authentication flows
    test_transaction_flow.py    # Full transaction flows
    test_behavioral_learning_flow.py  # ML learning lifecycle
    test_fraud_detection_flow.py     # Fraud detection scenarios

  test_security/           # Security-focused tests
    test_authentication.py # JWT, MFA, brute force
    test_authorization.py  # RBAC, privilege escalation, IDOR
    test_api_security.py   # Injection, XSS, CSRF, rate limiting

  test_frontend/           # Frontend component tests
    components.test.tsx    # React component tests (Jest)

  test_mobile/             # Mobile app tests
    widget_test.dart       # Flutter widget tests (flutter_test)
```

## Coverage Requirements

- **Overall**: Minimum 80% code coverage
- **ML Engine**: Minimum 90% coverage
- **Backend API**: Minimum 85% coverage
- **Critical paths**: 100% coverage (auth, risk assessment, fraud detection)

### Coverage Configuration
See `.coveragerc` for detailed coverage configuration including:
- Source paths to include
- File patterns to exclude
- Per-module coverage thresholds

## CI Integration

### GitHub Actions (`.github/workflows/test.yml`)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env: { POSTGRES_DB: test, POSTGRES_PASSWORD: test }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5 with { python-version: "3.12" }
      - run: pip install -r backend/requirements.txt
      - run: pip install pytest pytest-asyncio pytest-cov httpx
      - run: pytest --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v3
```

### Pre-commit Hook
```bash
# pre-commit
# Run tests before every commit
#!/bin/sh
pytest tests/test_ml/ --tb=short -q || exit 1
```

## Test Database Strategy

- **Unit tests**: Use mocked SQLAlchemy sessions
- **Integration tests**: Use SQLite in-memory database
- **ML tests**: Use temporary directories for model/profile storage

## Writing Tests

### Guidelines
1. Each test function tests exactly one behavior
2. Use descriptive test names following `test_<feature>_<scenario>_<expected>`
3. Parametrize tests where appropriate
4. Mock all external services (DB, Celery, Redis, email/SMS)
5. Clean up test data after each test
6. Use factories/fixtures to reduce boilerplate
