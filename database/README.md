# Behavioral Biometric Banking Platform — Database

## Architecture Overview

PostgreSQL 15+ database for an enterprise behavioral biometric banking platform. The schema supports real-time fraud detection using behavioral biometrics (keystroke dynamics, mouse movements, touch gestures, navigation patterns), ML model management, and explainable AI outputs.

## Schema Components

### 21 Tables Organized by Domain

| Domain | Tables | Purpose |
|--------|--------|---------|
| **Core Banking** | `users`, `accounts`, `cards`, `beneficiaries` | Customer profiles, financial accounts, payment instruments, saved payees |
| **Lending** | `loans`, `loan_emi_schedule` | Loan origination, EMI tracking, amortization schedules |
| **Transactions** | `transactions` | All financial movements with full audit trail |
| **Behavioral** | `behavioral_events`, `behavioral_features`, `behavioral_profiles` | Raw event ingestion, feature extraction, user behavioral baselines |
| **ML Platform** | `ml_models`, `risk_scores`, `fraud_alerts`, `explainability_results` | Model registry, scoring, alerting, explainability (SHAP/LIME) |
| **ML Ops** | `model_drift_logs`, `retraining_queue` | Drift monitoring, automated retraining pipeline |
| **Auth & Security** | `sessions`, `mfa_tokens`, `refresh_tokens`, `device_fingerprints` | Session management, MFA, token rotation, device identification |
| **Audit** | `audit_logs` | Immutable security event log |
| **Migrations** | `schema_migrations` | Migration version tracking |

## Entity Relationships

```
users ──┬── accounts (1:N)
         ├── cards (1:N)
         ├── beneficiaries (1:N)
         ├── loans (1:N)
         ├── sessions (1:N)
         ├── behavioral_profiles (1:N)
         ├── device_fingerprints (1:N)
         ├── mfa_tokens (1:N)
         ├── refresh_tokens (1:N)
         └── audit_logs (1:N)

accounts ──┬── transactions (1:N)
           ├── cards (1:N)
           └── loans (1:N)

sessions ──┬── behavioral_events (1:N)
           ├── risk_scores (1:N)
           └── transactions (1:N)

transactions ──┬── risk_scores (1:N)
               ├── fraud_alerts (1:N)
               └── explainability_results (1:N)

ml_models ──┬── risk_scores (1:N)
            ├── fraud_alerts (1:N)
            ├── explainability_results (1:N)
            ├── model_drift_logs (1:N)
            └── retraining_queue (1:N)

risk_scores ──┬── fraud_alerts (1:N)
              └── explainability_results (1:N)

fraud_alerts ── explainability_results (1:N)
model_drift_logs ── retraining_queue (1:N)
```

See `er_diagram.md` for the full Mermaid ER diagram.

## Data Types

| Type | Usage |
|------|-------|
| `NUMERIC(18,2)` | All monetary amounts |
| `NUMERIC(5,2)` | Percentages, scores (0-100) |
| `NUMERIC(10,6)` | Small decimal values (drift scores, outlier scores) |
| `NUMERIC(10,7)` | Latitude/longitude coordinates |
| `JSONB` | Flexible metadata, feature vectors, ML configs, audit diffs |
| `UUID` | Public-facing identifiers (never expose serial IDs) |
| `INET` | IP addresses with subnet support |
| `BYTEA` | Serialized ML model binaries (pickle, ONNX) |
| `TEXT[]` | Arrays of reason codes, feature names, IP addresses |
| `TIMESTAMPTZ` | All timestamps with timezone awareness |

## Key Indexing Strategy

- **All foreign keys** are indexed for JOIN performance
- **Partial indexes** on active/flagged records reduce index size
- **Composite indexes** for common query patterns (user+time, type+status)
- **GIN indexes** on JSONB columns for behavioral data and audit changes
- **Covering indexes** where appropriate for index-only scans

## Auto-update Triggers

Every table with an `updated_at` column has a `BEFORE UPDATE` trigger that automatically sets `updated_at = NOW()`. The `behavioral_events` and `audit_logs` tables are append-only and lack this trigger.

## Migration Files

| File | Description |
|------|-------------|
| `migrations/001_initial_schema.sql` | Creates all 21 tables, indexes, constraints, triggers |
| `migrations/002_seed_data.sql` | Seeds 58 users, 100 accounts, 50 transactions, sample ML data |

### Applying Migrations

```bash
# Apply initial schema
psql -U $DB_USER -d $DB_NAME -f database/migrations/001_initial_schema.sql

# Seed reference data
psql -U $DB_USER -d $DB_NAME -f database/migrations/002_seed_data.sql
```

## Security & Audit

- **All** security-relevant actions logged in `audit_logs` with old/new values
- **Passwords** stored as bcrypt hashes in `users.password_hash`
- **Card PANs** never stored in plaintext; `card_hash` stores hashed PAN, `masked_card_number` for display
- **Tokens** stored as hashes (`token_hash`, `token_code_hash`) — never plaintext
- **JWT refresh tokens** support rotation: `replaced_by` FK tracks token chaining
- **MFA tokens** have configurable `max_attempts` and auto-expiry via `expires_at`

## Behavioral Biometrics Data Flow

```
User Action → behavioral_events (raw) → behavioral_features (extraction)
                                                              ↓
                                            behavioral_profiles (baseline)
                                                              ↓
                                            ml_models → risk_scores (scoring)
                                                              ↓
                                            fraud_alerts (threshold breach)
                                                              ↓
                                            explainability_results (SHAP/LIME)
```

## Partitioning Strategy (Production)

For production deployments, consider partitioning:

- **`transactions`** — Range partition by `created_at` (monthly)
- **`behavioral_events`** — Range partition by `created_at` (daily/weekly)
- **`audit_logs`** — Range partition by `created_at` (monthly)
- **`risk_scores`** — Range partition by `created_at` (monthly)

## Maintenance Queries

```sql
-- Check table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Vacuum analyze (schedule via cron)
VACUUM ANALYZE transactions;
VACUUM ANALYZE behavioral_events;

-- Archive old sessions
UPDATE sessions SET is_active = FALSE
WHERE expires_at < NOW() - INTERVAL '90 days';

-- Clean up expired MFA tokens
DELETE FROM mfa_tokens WHERE expires_at < NOW() AND is_valid = TRUE;
```
