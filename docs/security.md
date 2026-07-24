# Security Architecture

## Overview

The Behavioral Biometric Banking Platform implements a defense-in-depth security strategy spanning authentication, authorization, data protection, network security, monitoring, and compliance. Behavioral biometrics serve as an additional continuous authentication layer rather than a replacement for traditional security controls.

## Authentication

### Password-Based Authentication

- Passwords hashed with **bcrypt** (12 rounds) via `backend/app/config.py`
- Minimum password policy enforced:
  - 8+ character minimum
  - Requires uppercase, lowercase, number, and special character
  - Configurable via `PASSWORD_MIN_LENGTH`, `PASSWORD_REQUIRE_*` settings
- Account lockout after repeated failed attempts (`MAX_LOGIN_ATTEMPTS`)
- Failed attempts tracked in `users.failed_login_attempts` column (schema line 44)

### JWT Token Architecture

```python
# backend/app/middleware/auth.py
Access token:  HS256, 30min expiry, contains { sub, role, iat, exp, iss, type }
Refresh token: HS256, 7 day expiry, contains { sub, iat, exp, iss, type }
Temp token:    HS256, 5min expiry,  contains { sub, mfa_method, iat, exp, iss, type }
```

- All tokens include `iss` (issuer = "biometric-bank") and `type` claim
- Refresh tokens are one-time-use with rotation (via `replaced_by` foreign key in schema)
- Token validation occurs on every protected endpoint via `get_current_user` dependency
- Decoded token payload provides `user_id` used for DB lookup; token alone is insufficient (user could be suspended/locked)

### Multi-Factor Authentication (MFA)

| Method | Implementation | Configuration |
|--------|---------------|---------------|
| TOTP | `pyotp.TOTP` with `valid_window=1` | `MFA_TOTP_VALIDITY_WINDOW` |
| SMS | 5-minute expiry OTP | `MFA_SMS_EXPIRY_SECONDS: 300` |
| Email | 5-minute expiry OTP | `MFA_EMAIL_EXPIRY_SECONDS: 300` |

- MFA tokens stored in `mfa_tokens` table with hashed codes
- Max 5 attempts per token; locks after `MFA_MAX_ATTEMPTS`
- Backup codes supported for account recovery
- MFA session state tracked via `sessions.is_mfa_verified` and `sessions.mfa_verified_at`

## Authorization

### Role-Based Access Control (RBAC)

Three roles defined in `users.role` with check constraint:

| Role | Permissions |
|------|-------------|
| `customer` | Own accounts, transfers, cards, loans, own profile |
| `analyst` | View dashboard, fraud alerts, risk scores, user investigations |
| `admin` | All analyst permissions + user management, model management, audit logs |

Enforcement via middleware decorators (`backend/app/middleware/auth.py:54-63`):

```python
require_admin = require_role(UserRole.ADMIN)
require_analyst = require_role(UserRole.ANALYST, UserRole.ADMIN)
```

### Resource-Level Authorization

- Banking operations filter by `current_user.id` to prevent cross-user access
- Session tokens are bound to specific devices via `device_fingerprint_id`
- Beneficiary operations scoped to owning user
- Admin endpoints require explicit admin role check

## Data Protection

### Encryption at Rest

| Data | Protection |
|------|------------|
| Passwords | bcrypt (12 rounds) |
| MFA secrets | Encrypted in `users.mfa_secret` |
| Card numbers | Hashed in `cards.card_hash`; only `last_four_digits` and `masked_card_number` stored plaintext |
| CVV | Hashed in `cards.cvv_hash` |
| Session tokens | Full token stored (512 char) for lookup; `sessions.session_token` |
| Refresh tokens | SHA-256 hash stored in `refresh_tokens.token_hash`; raw token never persisted |
| PII fields | JSONB `metadata` columns available for field-level encryption |
| Model data | Pickle-serialized model bytes stored in `ml_models.model_data` |

### Encryption in Transit

- All API endpoints served exclusively over HTTPS (TLS 1.2+)
- Nginx configuration in `docker/nginx/` enforces TLS termination
- HSTS headers included in production configuration
- CORS restricted to known origins (configurable via `CORS_ORIGINS`)

## Session Management

Sessions are tracked in the `sessions` table with the following lifecycle:

1. Created on login with `session_token`, `ip_address`, `user_agent`, `device_fingerprint_id`
2. MFA status tracked via `is_mfa_verified` flag
3. `last_activity_at` updated on each request
4. `expires_at` enforced at middleware level
5. Explicit `logged_out_at` on logout
6. Indexed for cleanup: `idx_sessions_expires` filters active sessions

Session timeout: configurable via `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` (default 30 min). Inactivity session timeout is client-enforced via `sessionTimeout: 1800000` (30 min) in the web SDK.

## Behavioral Security Controls

### Device Fingerprinting

The web SDK (`client_sdk/web/tracker.js:498-610`) collects 20+ device attributes:

- User agent, platform, language
- Screen properties (resolution, color depth, pixel ratio)
- Hardware: `navigator.hardwareConcurrency`, `navigator.deviceMemory`
- Canvas fingerprint (2D rendering with specific text/shapes)
- WebGL vendor, renderer, version
- AudioContext oscillator fingerprint
- Installed font detection (24 font list)
- Combined SHA-256 hash of all components

Stored in `device_fingerprints` table. Trusted device list maintained per user in `BehavioralProfile.device_fingerprints`.

### Continuous Authentication

- Behavioral events captured throughout the session (not just at login)
- Risk score recalculated on each sensitive action
- Session risk timeline available for forensic analysis
- Trust score exposed to client for UI adaptation

### Risk-Based Action Rules

| Risk Band | Score Range | Action |
|-----------|-------------|--------|
| LOW | 0-30 | Allow without additional checks |
| MEDIUM | 31-70 | Request MFA verification |
| HIGH | 71-100 | Block and create fraud alert |

## Compliance & Audit

### Audit Logging

Every security-relevant action is logged via `audit_logger` decorator (`backend/app/middleware/audit.py`):

| Audit Event | Endpoint | Data Captured |
|-------------|----------|---------------|
| User registration | `POST /api/auth/register` | email |
| Login | `POST /api/auth/login` | email |
| MFA verification | `POST /api/auth/verify-mfa` | (none logged) |
| Password reset | `POST /api/auth/reset-password` | (token, not raw) |
| Transfer | `POST /api/transactions/*` | amount, reference |
| Beneficiary CRUD | `POST/PUT/DELETE /api/beneficiaries/*` | beneficiary name |
| Card operations | `POST/PUT /api/cards/*` | card_id |
| Risk assessment | `POST /api/risk/assess` | risk_score, risk_band |
| Alert status change | `PUT /api/risk/alerts/{id}/status` | new status |

Audit logs stored in `audit_logs` table (schema lines 759-794) with indexes on:
- `user_id`, `action`, `entity_type`
- `severity`, `created_at`
- GIN index on `changes` JSONB for full-text search

### Data Retention

- Risk history: last 500 entries retained per user in profile
- Session data: retained for regulatory period (configurable)
- Audit logs: no automatic purging (admin-managed)
- Behavioral event data: indexed for time-range queries
- Model training data: retained for reproducibility

## Model Security

### Adversarial Robustness

- Ensemble of 10 Isolation Forest models reduces single-model vulnerability
- Feature normalization prevents adversarial scaling attacks
- Adaptive threshold (`k=2.5`) adjusts to distribution shifts
- PSI-based drift detection (`psi_warning_threshold: 0.10`) identifies distribution changes
- Training data filtered: only low-risk sessions used (`risk <= medium_risk_max`)

### Model Storage

- Models stored as pickle files in `model_store/` directory tree
- Model registry tracks all versions with metadata
- Rollback capability: `ModelRegistry.rollback(user_id, version)`
- Production models tracked via `is_production` flag in `ml_models` table

## Rate Limiting

| Endpoint Group | Rate Limit | Window |
|----------------|------------|--------|
| Auth endpoints | 5 requests | 60 seconds |
| All other endpoints | 100 requests | 60 seconds |

Configured in `backend/app/config.py` (`RATE_LIMIT_AUTH_ENDPOINTS`, `RATE_LIMIT_DEFAULT`). Enforced via `backend/app/middleware/rate_limit.py`.

## Network Security

- API gateway rate limiting at Nginx level
- CORS restricted to specific origins
- IP-based geolocation tracking on sessions and transactions
- Suspicious hour detection (22:00-05:59) adds risk points
- Transaction velocity checks: max 5 transactions in 5 minutes

## Security Headers (Recommended Nginx Configuration)

```nginx
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
add_header X-Content-Type-Options nosniff;
add_header X-Frame-Options DENY;
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy strict-origin-when-cross-origin;
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';";
```

## Incident Response Flow

1. Risk engine flags session as HIGH → fraud alert created
2. Alert pushed to Security Dashboard via Redis Pub/Sub
3. Analyst investigates using session replay and behavioral profile
4. Actions available: dismiss as false positive, mark resolved, lock user account
5. High/critical alerts trigger email/SMS notification to user
6. All actions logged to audit trail

## Security Compliance Mapping

| Requirement | Implementation |
|-------------|---------------|
| OWASP Top 10 (2021) | Input validation, parameterized queries, rate limiting, JWT security, CORS |
| PSD2/SCA | MFA enforcement on sensitive transactions, risk-based authentication |
| GDPR | Audit logging, data retention limits, user data export capability |
| PCI DSS | Card data hashing, masked display, CVV hashing, access controls |
| SOX | Immutable audit logs, role-based access, change tracking |
