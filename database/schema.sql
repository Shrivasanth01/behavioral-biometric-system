-- ============================================================================
-- Behavioral Biometric Banking Platform - Complete PostgreSQL Schema
-- ============================================================================
-- This schema defines all tables, constraints, indexes, and triggers for
-- an enterprise-grade behavioral biometric banking system.
-- ============================================================================

BEGIN;

-- ============================================================================
-- SCHEMA MIGRATIONS TRACKING
-- ============================================================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    description TEXT
);

-- ============================================================================
-- TRIGGER FUNCTION: Auto-update updated_at column
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 1. USERS
-- ============================================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL DEFAULT 'customer'
        CHECK (role IN ('customer', 'analyst', 'admin')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_locked BOOLEAN NOT NULL DEFAULT FALSE,
    failed_login_attempts INT NOT NULL DEFAULT 0
        CHECK (failed_login_attempts >= 0),
    last_login_at TIMESTAMPTZ,
    last_login_ip INET,
    preferred_language VARCHAR(10) NOT NULL DEFAULT 'en',
    two_factor_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_uuid ON users(uuid);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- ============================================================================
-- 2. DEVICE FINGERPRINTS
-- ============================================================================
CREATE TABLE device_fingerprints (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    device_id VARCHAR(255) NOT NULL,
    device_type VARCHAR(50),
    device_manufacturer VARCHAR(100),
    device_model VARCHAR(100),
    os VARCHAR(100),
    os_version VARCHAR(50),
    browser VARCHAR(100),
    browser_version VARCHAR(50),
    screen_resolution VARCHAR(20),
    color_depth INT,
    timezone VARCHAR(50),
    language VARCHAR(20),
    installed_fonts TEXT[],
    webgl_fingerprint VARCHAR(255),
    canvas_fingerprint VARCHAR(255),
    audio_fingerprint VARCHAR(255),
    hardware_concurrency INT,
    device_memory NUMERIC(5,1),
    touch_support BOOLEAN,
    ip_addresses INET[],
    is_trusted BOOLEAN NOT NULL DEFAULT FALSE,
    trust_score NUMERIC(5,2) CHECK (trust_score >= 0 AND trust_score <= 100),
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_device_fingerprints_user_id ON device_fingerprints(user_id);
CREATE INDEX idx_device_fingerprints_device_id ON device_fingerprints(device_id);
CREATE UNIQUE INDEX idx_device_fingerprints_user_device
    ON device_fingerprints(user_id, device_id) WHERE user_id IS NOT NULL;

-- ============================================================================
-- 3. ACCOUNTS
-- ============================================================================
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_number VARCHAR(20) NOT NULL UNIQUE,
    account_type VARCHAR(20) NOT NULL
        CHECK (account_type IN ('savings', 'current')),
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    balance NUMERIC(18,2) NOT NULL DEFAULT 0.00
        CHECK (balance >= 0),
    available_balance NUMERIC(18,2) NOT NULL DEFAULT 0.00
        CHECK (available_balance >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'dormant', 'closed', 'frozen')),
    opened_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_accounts_account_number ON accounts(account_number);
CREATE INDEX idx_accounts_uuid ON accounts(uuid);
CREATE INDEX idx_accounts_type_status ON accounts(account_type, status);
CREATE INDEX idx_accounts_user_type ON accounts(user_id, account_type);

-- ============================================================================
-- 4. CARDS
-- ============================================================================
CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    account_id INT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    card_type VARCHAR(10) NOT NULL
        CHECK (card_type IN ('credit', 'debit')),
    card_network VARCHAR(20) NOT NULL
        CHECK (card_network IN ('visa', 'mastercard', 'amex', 'rupay', 'discover')),
    card_holder_name VARCHAR(255) NOT NULL,
    masked_card_number VARCHAR(20) NOT NULL,
    card_hash VARCHAR(255) NOT NULL,
    last_four_digits VARCHAR(4) NOT NULL,
    expiry_date DATE NOT NULL,
    cvv_hash VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'frozen', 'cancelled', 'expired', 'lost', 'stolen')),
    is_frozen BOOLEAN NOT NULL DEFAULT FALSE,
    daily_limit NUMERIC(18,2),
    transaction_limit NUMERIC(18,2),
    monthly_limit NUMERIC(18,2),
    daily_used NUMERIC(18,2) NOT NULL DEFAULT 0.00
        CHECK (daily_used >= 0),
    monthly_used NUMERIC(18,2) NOT NULL DEFAULT 0.00
        CHECK (monthly_used >= 0),
    is_international_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    is_contactless_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    is_ecommerce_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    pin_attempts INT NOT NULL DEFAULT 0
        CHECK (pin_attempts >= 0),
    issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    activated_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cards_account_id ON cards(account_id);
CREATE INDEX idx_cards_user_id ON cards(user_id);
CREATE INDEX idx_cards_type_status ON cards(card_type, status);
CREATE INDEX idx_cards_status ON cards(status);
CREATE INDEX idx_cards_expiry ON cards(expiry_date) WHERE status = 'active';
CREATE INDEX idx_cards_type_network ON cards(card_type, card_network);

-- ============================================================================
-- 5. BENEFICIARIES
-- ============================================================================
CREATE TABLE beneficiaries (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    beneficiary_name VARCHAR(255) NOT NULL,
    beneficiary_account VARCHAR(50) NOT NULL,
    beneficiary_bank VARCHAR(255),
    beneficiary_branch VARCHAR(255),
    ifsc_code VARCHAR(20),
    swift_code VARCHAR(20),
    nickname VARCHAR(100),
    relationship VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    max_limit NUMERIC(18,2)
        CHECK (max_limit IS NULL OR max_limit > 0),
    daily_limit NUMERIC(18,2)
        CHECK (daily_limit IS NULL OR daily_limit > 0),
    approval_required BOOLEAN NOT NULL DEFAULT FALSE,
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_beneficiary_user_account UNIQUE (user_id, beneficiary_account)
);

CREATE INDEX idx_beneficiaries_user_id ON beneficiaries(user_id);
CREATE INDEX idx_beneficiaries_is_active ON beneficiaries(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_beneficiaries_account ON beneficiaries(beneficiary_account);

-- ============================================================================
-- 6. LOANS
-- ============================================================================
CREATE TABLE loans (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    account_id INT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    loan_type VARCHAR(50) NOT NULL
        CHECK (loan_type IN ('personal', 'home', 'auto', 'education', 'business')),
    loan_reference VARCHAR(50) NOT NULL UNIQUE,
    principal_amount NUMERIC(18,2) NOT NULL
        CHECK (principal_amount > 0),
    interest_rate NUMERIC(5,2) NOT NULL
        CHECK (interest_rate > 0),
    interest_type VARCHAR(20) NOT NULL DEFAULT 'fixed'
        CHECK (interest_type IN ('fixed', 'floating')),
    tenure_months INT NOT NULL
        CHECK (tenure_months > 0 AND tenure_months <= 480),
    emi_amount NUMERIC(18,2) NOT NULL
        CHECK (emi_amount > 0),
    outstanding_amount NUMERIC(18,2) NOT NULL
        CHECK (outstanding_amount >= 0),
    paid_amount NUMERIC(18,2) NOT NULL DEFAULT 0.00
        CHECK (paid_amount >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('pending', 'active', 'closed', 'defaulted', 'foreclosed')),
    disbursed_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    next_emi_date DATE,
    last_emi_paid_at TIMESTAMPTZ,
    collateral_details JSONB,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_loans_account_id ON loans(account_id);
CREATE INDEX idx_loans_user_id ON loans(user_id);
CREATE INDEX idx_loans_status ON loans(status);
CREATE INDEX idx_loans_loan_reference ON loans(loan_reference);
CREATE INDEX idx_loans_type_status ON loans(loan_type, status);
CREATE INDEX idx_loans_outstanding ON loans(outstanding_amount DESC) WHERE status = 'active';

-- ============================================================================
-- 7. SESSIONS
-- ============================================================================
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(512) NOT NULL UNIQUE,
    ip_address INET,
    user_agent TEXT,
    device_fingerprint_id INT REFERENCES device_fingerprints(id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_mfa_verified BOOLEAN NOT NULL DEFAULT FALSE,
    mfa_verified_at TIMESTAMPTZ,
    logged_in_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    logged_out_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_token ON sessions(session_token);
CREATE INDEX idx_sessions_active ON sessions(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_sessions_expires ON sessions(expires_at) WHERE is_active = TRUE;
CREATE INDEX idx_sessions_device_fingerprint ON sessions(device_fingerprint_id);
CREATE INDEX idx_sessions_last_activity ON sessions(last_activity_at DESC) WHERE is_active = TRUE;

-- ============================================================================
-- 8. TRANSACTIONS
-- ============================================================================
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    account_id INT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    card_id INT REFERENCES cards(id) ON DELETE SET NULL,
    session_id INT REFERENCES sessions(id) ON DELETE SET NULL,
    transaction_type VARCHAR(20) NOT NULL
        CHECK (transaction_type IN ('transfer', 'payment', 'recharge', 'withdrawal', 'deposit', 'emi_payment')),
    amount NUMERIC(18,2) NOT NULL
        CHECK (amount > 0),
    fee NUMERIC(18,2) NOT NULL DEFAULT 0.00
        CHECK (fee >= 0),
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    reference_number VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'completed', 'failed', 'reversed', 'flagged')),
    failure_reason TEXT,
    counterparty_name VARCHAR(255),
    counterparty_account VARCHAR(50),
    counterparty_bank VARCHAR(255),
    category VARCHAR(50),
    latitude NUMERIC(10,7)
        CHECK (latitude IS NULL OR (latitude >= -90 AND latitude <= 90)),
    longitude NUMERIC(10,7)
        CHECK (longitude IS NULL OR (longitude >= -180 AND longitude <= 180)),
    ip_address INET,
    is_international BOOLEAN NOT NULL DEFAULT FALSE,
    is_flagged BOOLEAN NOT NULL DEFAULT FALSE,
    processed_at TIMESTAMPTZ,
    reversed_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_card_id ON transactions(card_id);
CREATE INDEX idx_transactions_session_id ON transactions(session_id);
CREATE INDEX idx_transactions_reference ON transactions(reference_number);
CREATE INDEX idx_transactions_uuid ON transactions(uuid);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX idx_transactions_account_created ON transactions(account_id, created_at DESC);
CREATE INDEX idx_transactions_type_status ON transactions(transaction_type, status);
CREATE INDEX idx_transactions_flagged ON transactions(is_flagged) WHERE is_flagged = TRUE;
CREATE INDEX idx_transactions_completed_date ON transactions(created_at) WHERE status = 'completed';
CREATE INDEX idx_transactions_amount ON transactions(amount);

-- ============================================================================
-- 9. LOAN EMI SCHEDULE
-- ============================================================================
CREATE TABLE loan_emi_schedule (
    id SERIAL PRIMARY KEY,
    loan_id INT NOT NULL REFERENCES loans(id) ON DELETE CASCADE,
    emi_number INT NOT NULL,
    due_date DATE NOT NULL,
    amount NUMERIC(18,2) NOT NULL
        CHECK (amount > 0),
    principal_component NUMERIC(18,2) NOT NULL
        CHECK (principal_component >= 0),
    interest_component NUMERIC(18,2) NOT NULL
        CHECK (interest_component >= 0),
    balance_after NUMERIC(18,2)
        CHECK (balance_after IS NULL OR balance_after >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'paid', 'overdue', 'defaulted')),
    paid_at TIMESTAMPTZ,
    paid_amount NUMERIC(18,2)
        CHECK (paid_amount IS NULL OR paid_amount >= 0),
    payment_transaction_id INT REFERENCES transactions(id) ON DELETE SET NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_loan_emi UNIQUE (loan_id, emi_number)
);

CREATE INDEX idx_loan_emi_schedule_loan_id ON loan_emi_schedule(loan_id);
CREATE INDEX idx_loan_emi_schedule_status ON loan_emi_schedule(status);
CREATE INDEX idx_loan_emi_schedule_due_date ON loan_emi_schedule(due_date) WHERE status IN ('pending', 'overdue');
CREATE INDEX idx_loan_emi_schedule_payment ON loan_emi_schedule(payment_transaction_id);

-- ============================================================================
-- 10. BEHAVIORAL EVENTS
-- ============================================================================
CREATE TABLE behavioral_events (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id INT REFERENCES sessions(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL DEFAULT '{}',
    client_timestamp TIMESTAMPTZ NOT NULL,
    server_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    time_diff_ms INT,
    page_url TEXT,
    element_selector VARCHAR(500),
    action VARCHAR(100),
    value_hash VARCHAR(255),
    coordinates JSONB,
    window_size JSONB,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_behavioral_events_user_id ON behavioral_events(user_id);
CREATE INDEX idx_behavioral_events_session_id ON behavioral_events(session_id);
CREATE INDEX idx_behavioral_events_type ON behavioral_events(event_type);
CREATE INDEX idx_behavioral_events_name ON behavioral_events(event_name);
CREATE INDEX idx_behavioral_events_created ON behavioral_events(created_at DESC);
CREATE INDEX idx_behavioral_events_user_time ON behavioral_events(user_id, created_at DESC);
CREATE INDEX idx_behavioral_events_user_type ON behavioral_events(user_id, event_type);
CREATE INDEX idx_behavioral_events_lookup ON behavioral_events(user_id, session_id, event_type);
CREATE INDEX idx_behavioral_events_gin ON behavioral_events USING GIN (event_data jsonb_path_ops);

-- ============================================================================
-- 11. BEHAVIORAL FEATURES
-- ============================================================================
CREATE TABLE behavioral_features (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id INT REFERENCES sessions(id) ON DELETE SET NULL,
    source_event_group_id INT REFERENCES behavioral_events(id) ON DELETE SET NULL,
    feature_version VARCHAR(20) NOT NULL DEFAULT '1.0',
    feature_set VARCHAR(100) NOT NULL,
    mouse_features JSONB DEFAULT '{}',
    keystroke_features JSONB DEFAULT '{}',
    touch_features JSONB DEFAULT '{}',
    navigation_features JSONB DEFAULT '{}',
    device_features JSONB DEFAULT '{}',
    temporal_features JSONB DEFAULT '{}',
    combined_vector JSONB,
    feature_dimension INT,
    is_outlier BOOLEAN NOT NULL DEFAULT FALSE,
    outlier_score NUMERIC(10,6),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_behavioral_features_user_id ON behavioral_features(user_id);
CREATE INDEX idx_behavioral_features_session_id ON behavioral_features(session_id);
CREATE INDEX idx_behavioral_features_event_group ON behavioral_features(source_event_group_id);
CREATE INDEX idx_behavioral_features_version ON behavioral_features(feature_version);
CREATE INDEX idx_behavioral_features_set ON behavioral_features(feature_set);
CREATE INDEX idx_behavioral_features_created ON behavioral_features(created_at DESC);
CREATE INDEX idx_behavioral_features_user_session ON behavioral_features(user_id, session_id);
CREATE INDEX idx_behavioral_features_outlier ON behavioral_features(is_outlier) WHERE is_outlier = TRUE;
CREATE INDEX idx_behavioral_features_gin ON behavioral_features USING GIN (combined_vector jsonb);

-- ============================================================================
-- 12. BEHAVIORAL PROFILES
-- ============================================================================
CREATE TABLE behavioral_profiles (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    profile_version VARCHAR(20) NOT NULL DEFAULT '1.0',
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'learning', 'stale', 'archived')),
    confidence_score NUMERIC(5,2)
        CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100)),
    total_events_analyzed INT NOT NULL DEFAULT 0
        CHECK (total_events_analyzed >= 0),
    total_sessions_analyzed INT NOT NULL DEFAULT 0
        CHECK (total_sessions_analyzed >= 0),
    mouse_pattern JSONB DEFAULT '{}',
    keystroke_pattern JSONB DEFAULT '{}',
    navigation_pattern JSONB DEFAULT '{}',
    touch_pattern JSONB DEFAULT '{}',
    temporal_pattern JSONB DEFAULT '{}',
    device_pattern JSONB DEFAULT '{}',
    behavioral_biometrics JSONB DEFAULT '{}',
    baseline_deviation NUMERIC(10,6),
    last_calculated_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_profile_version UNIQUE (user_id, profile_version)
);

CREATE INDEX idx_behavioral_profiles_user_id ON behavioral_profiles(user_id);
CREATE INDEX idx_behavioral_profiles_status ON behavioral_profiles(status);
CREATE INDEX idx_behavioral_profiles_confidence ON behavioral_profiles(confidence_score DESC);
CREATE INDEX idx_behavioral_profiles_gin ON behavioral_profiles USING GIN (behavioral_biometrics jsonb);

-- ============================================================================
-- 13. ML MODELS
-- ============================================================================
CREATE TABLE ml_models (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    model_name VARCHAR(255) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL
        CHECK (model_type IN ('anomaly_detection', 'classification', 'regression', 'clustering', 'feature_extractor')),
    algorithm VARCHAR(100) NOT NULL,
    model_data BYTEA NOT NULL,
    model_metadata JSONB DEFAULT '{}',
    feature_importance JSONB DEFAULT '{}',
    performance_metrics JSONB DEFAULT '{}',
    training_data_range JSONB,
    training_samples INT
        CHECK (training_samples IS NULL OR training_samples > 0),
    validation_score NUMERIC(10,6),
    test_score NUMERIC(10,6),
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    is_production BOOLEAN NOT NULL DEFAULT FALSE,
    trained_by INT REFERENCES users(id) ON DELETE SET NULL,
    trained_at TIMESTAMPTZ,
    deployed_at TIMESTAMPTZ,
    retired_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_model_version UNIQUE (model_name, model_version)
);

CREATE INDEX idx_ml_models_name ON ml_models(model_name);
CREATE INDEX idx_ml_models_type ON ml_models(model_type);
CREATE INDEX idx_ml_models_active ON ml_models(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_ml_models_production ON ml_models(is_production) WHERE is_production = TRUE;
CREATE INDEX idx_ml_models_algorithm ON ml_models(algorithm);

-- ============================================================================
-- 14. RISK SCORES
-- ============================================================================
CREATE TABLE risk_scores (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_id INT REFERENCES transactions(id) ON DELETE SET NULL,
    session_id INT REFERENCES sessions(id) ON DELETE SET NULL,
    model_id INT REFERENCES ml_models(id) ON DELETE SET NULL,
    score_type VARCHAR(50) NOT NULL
        CHECK (score_type IN ('transaction', 'session', 'login', 'transfer', 'behavioral', 'device', 'composite')),
    risk_score NUMERIC(5,2) NOT NULL
        CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_level VARCHAR(20) NOT NULL
        CHECK (risk_level IN ('very_low', 'low', 'medium', 'high', 'critical')),
    confidence NUMERIC(5,2)
        CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 100)),
    feature_contributions JSONB DEFAULT '{}',
    model_version VARCHAR(50),
    execution_time_ms INT
        CHECK (execution_time_ms IS NULL OR execution_time_ms >= 0),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_risk_scores_user_id ON risk_scores(user_id);
CREATE INDEX idx_risk_scores_transaction_id ON risk_scores(transaction_id);
CREATE INDEX idx_risk_scores_session_id ON risk_scores(session_id);
CREATE INDEX idx_risk_scores_model_id ON risk_scores(model_id);
CREATE INDEX idx_risk_scores_type ON risk_scores(score_type);
CREATE INDEX idx_risk_scores_level ON risk_scores(risk_level);
CREATE INDEX idx_risk_scores_created ON risk_scores(created_at DESC);
CREATE INDEX idx_risk_scores_user_type ON risk_scores(user_id, score_type);
CREATE INDEX idx_risk_scores_user_level ON risk_scores(user_id, risk_level);
CREATE INDEX idx_risk_scores_gin ON risk_scores USING GIN (feature_contributions jsonb);

-- ============================================================================
-- 15. FRAUD ALERTS
-- ============================================================================
CREATE TABLE fraud_alerts (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_id INT REFERENCES transactions(id) ON DELETE SET NULL,
    session_id INT REFERENCES sessions(id) ON DELETE SET NULL,
    risk_score_id INT REFERENCES risk_scores(id) ON DELETE SET NULL,
    alert_type VARCHAR(100) NOT NULL,
    alert_severity VARCHAR(20) NOT NULL
        CHECK (alert_severity IN ('info', 'low', 'medium', 'high', 'critical')),
    status VARCHAR(20) NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'investigating', 'resolved', 'false_positive', 'dismissed')),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    reason_codes TEXT[],
    risk_score_value NUMERIC(5,2),
    threshold_value NUMERIC(5,2),
    anomaly_details JSONB DEFAULT '{}',
    assigned_to INT REFERENCES users(id) ON DELETE SET NULL,
    resolved_by INT REFERENCES users(id) ON DELETE SET NULL,
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fraud_alerts_user_id ON fraud_alerts(user_id);
CREATE INDEX idx_fraud_alerts_transaction_id ON fraud_alerts(transaction_id);
CREATE INDEX idx_fraud_alerts_session_id ON fraud_alerts(session_id);
CREATE INDEX idx_fraud_alerts_risk_score_id ON fraud_alerts(risk_score_id);
CREATE INDEX idx_fraud_alerts_severity ON fraud_alerts(alert_severity);
CREATE INDEX idx_fraud_alerts_status ON fraud_alerts(status);
CREATE INDEX idx_fraud_alerts_type ON fraud_alerts(alert_type);
CREATE INDEX idx_fraud_alerts_created ON fraud_alerts(created_at DESC);
CREATE INDEX idx_fraud_alerts_assigned ON fraud_alerts(assigned_to) WHERE assigned_to IS NOT NULL;
CREATE INDEX idx_fraud_alerts_user_status ON fraud_alerts(user_id, status);

-- ============================================================================
-- 16. EXPLAINABILITY RESULTS
-- ============================================================================
CREATE TABLE explainability_results (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fraud_alert_id INT REFERENCES fraud_alerts(id) ON DELETE CASCADE,
    risk_score_id INT NOT NULL REFERENCES risk_scores(id) ON DELETE CASCADE,
    transaction_id INT REFERENCES transactions(id) ON DELETE SET NULL,
    session_id INT REFERENCES sessions(id) ON DELETE SET NULL,
    model_id INT REFERENCES ml_models(id) ON DELETE SET NULL,
    explanation_type VARCHAR(50) NOT NULL
        CHECK (explanation_type IN ('shap', 'lime', 'feature_importance', 'rule_based', 'counterfactual', 'anchor')),
    reason_codes TEXT[] NOT NULL,
    reason_descriptions JSONB DEFAULT '{}',
    top_features JSONB DEFAULT '[]',
    feature_contributions JSONB DEFAULT '{}',
    shap_values JSONB,
    decision_path JSONB,
    counterfactuals JSONB,
    confidence_score NUMERIC(5,2)
        CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100)),
    human_readable_summary TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_explainability_user_id ON explainability_results(user_id);
CREATE INDEX idx_explainability_fraud_alert ON explainability_results(fraud_alert_id);
CREATE INDEX idx_explainability_risk_score ON explainability_results(risk_score_id);
CREATE INDEX idx_explainability_transaction ON explainability_results(transaction_id);
CREATE INDEX idx_explainability_session ON explainability_results(session_id);
CREATE INDEX idx_explainability_model ON explainability_results(model_id);
CREATE INDEX idx_explainability_type ON explainability_results(explanation_type);
CREATE INDEX idx_explainability_created ON explainability_results(created_at DESC);
CREATE INDEX idx_explainability_gin ON explainability_results USING GIN (top_features jsonb);

-- ============================================================================
-- 17. MODEL DRIFT LOGS
-- ============================================================================
CREATE TABLE model_drift_logs (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    model_id INT NOT NULL REFERENCES ml_models(id) ON DELETE CASCADE,
    drift_type VARCHAR(50) NOT NULL
        CHECK (drift_type IN ('concept_drift', 'data_drift', 'model_decay', 'feature_drift', 'prediction_drift')),
    drift_score NUMERIC(10,6) NOT NULL,
    drift_severity VARCHAR(20) NOT NULL
        CHECK (drift_severity IN ('low', 'medium', 'high', 'critical')),
    previous_metrics JSONB DEFAULT '{}',
    current_metrics JSONB DEFAULT '{}',
    drifted_features TEXT[],
    feature_statistics JSONB DEFAULT '{}',
    sample_count INT
        CHECK (sample_count IS NULL OR sample_count > 0),
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    action_taken VARCHAR(255),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_model_drift_logs_model_id ON model_drift_logs(model_id);
CREATE INDEX idx_model_drift_logs_type ON model_drift_logs(drift_type);
CREATE INDEX idx_model_drift_logs_severity ON model_drift_logs(drift_severity);
CREATE INDEX idx_model_drift_logs_detected ON model_drift_logs(detected_at DESC);
CREATE INDEX idx_model_drift_logs_window ON model_drift_logs(window_start, window_end);

-- ============================================================================
-- 18. RETRAINING QUEUE
-- ============================================================================
CREATE TABLE retraining_queue (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    model_id INT REFERENCES ml_models(id) ON DELETE SET NULL,
    model_name VARCHAR(255) NOT NULL,
    priority INT NOT NULL DEFAULT 0
        CHECK (priority >= 0 AND priority <= 100),
    status VARCHAR(20) NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'in_progress', 'completed', 'failed', 'cancelled')),
    trigger_reason VARCHAR(255) NOT NULL,
    trigger_event_id INT REFERENCES model_drift_logs(id) ON DELETE SET NULL,
    training_config JSONB DEFAULT '{}',
    training_duration_ms INT
        CHECK (training_duration_ms IS NULL OR training_duration_ms >= 0),
    result_metrics JSONB,
    error_message TEXT,
    error_traceback TEXT,
    triggered_by INT REFERENCES users(id) ON DELETE SET NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_retraining_queue_model_id ON retraining_queue(model_id);
CREATE INDEX idx_retraining_queue_status ON retraining_queue(status);
CREATE INDEX idx_retraining_queue_priority ON retraining_queue(priority DESC, created_at ASC);
CREATE INDEX idx_retraining_queue_trigger ON retraining_queue(trigger_event_id);

-- ============================================================================
-- 19. MFA TOKENS
-- ============================================================================
CREATE TABLE mfa_tokens (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id INT REFERENCES sessions(id) ON DELETE CASCADE,
    token_type VARCHAR(20) NOT NULL
        CHECK (token_type IN ('totp', 'sms', 'email', 'push', 'backup_code')),
    token_code_hash VARCHAR(255) NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    is_valid BOOLEAN NOT NULL DEFAULT TRUE,
    attempts INT NOT NULL DEFAULT 0
        CHECK (attempts >= 0 AND attempts <= 5),
    max_attempts INT NOT NULL DEFAULT 5
        CHECK (max_attempts > 0),
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    verified_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mfa_tokens_user_id ON mfa_tokens(user_id);
CREATE INDEX idx_mfa_tokens_session_id ON mfa_tokens(session_id);
CREATE INDEX idx_mfa_tokens_type ON mfa_tokens(token_type);
CREATE INDEX idx_mfa_tokens_valid ON mfa_tokens(is_valid, expires_at) WHERE is_valid = TRUE;
CREATE INDEX idx_mfa_tokens_cleanup ON mfa_tokens(expires_at) WHERE is_valid = TRUE;

-- ============================================================================
-- 20. REFRESH TOKENS
-- ============================================================================
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    device_fingerprint_id INT REFERENCES device_fingerprints(id) ON DELETE SET NULL,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    replaced_by INT REFERENCES refresh_tokens(id) ON DELETE SET NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_active ON refresh_tokens(expires_at) WHERE is_revoked = FALSE AND is_used = FALSE;
CREATE INDEX idx_refresh_tokens_device ON refresh_tokens(device_fingerprint_id);

-- ============================================================================
-- 21. AUDIT LOGS
-- ============================================================================
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    session_id INT REFERENCES sessions(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INT,
    entity_uuid UUID,
    action_type VARCHAR(20) NOT NULL
        CHECK (action_type IN ('CREATE', 'READ', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'EXPORT', 'OTHER')),
    severity VARCHAR(20) NOT NULL
        CHECK (severity IN ('info', 'low', 'medium', 'high', 'critical')),
    status VARCHAR(20) NOT NULL
        CHECK (status IN ('success', 'failure', 'pending')),
    old_values JSONB,
    new_values JSONB,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(100),
    geo_location JSONB,
    failure_reason TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_session_id ON audit_logs(session_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_severity ON audit_logs(severity);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_user_action ON audit_logs(user_id, action);
CREATE INDEX idx_audit_logs_action_type ON audit_logs(action_type, created_at DESC);
CREATE INDEX idx_audit_logs_gin ON audit_logs USING GIN (changes jsonb);

-- ============================================================================
-- UPDATED_AT TRIGGERS
-- ============================================================================
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_device_fingerprints_updated_at
    BEFORE UPDATE ON device_fingerprints
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_accounts_updated_at
    BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_cards_updated_at
    BEFORE UPDATE ON cards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_beneficiaries_updated_at
    BEFORE UPDATE ON beneficiaries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_loans_updated_at
    BEFORE UPDATE ON loans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_loan_emi_schedule_updated_at
    BEFORE UPDATE ON loan_emi_schedule
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_behavioral_features_updated_at
    BEFORE UPDATE ON behavioral_features
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_behavioral_profiles_updated_at
    BEFORE UPDATE ON behavioral_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_ml_models_updated_at
    BEFORE UPDATE ON ml_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_risk_scores_updated_at
    BEFORE UPDATE ON risk_scores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_fraud_alerts_updated_at
    BEFORE UPDATE ON fraud_alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_explainability_results_updated_at
    BEFORE UPDATE ON explainability_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_model_drift_logs_updated_at
    BEFORE UPDATE ON model_drift_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_retraining_queue_updated_at
    BEFORE UPDATE ON retraining_queue
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_mfa_tokens_updated_at
    BEFORE UPDATE ON mfa_tokens
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_refresh_tokens_updated_at
    BEFORE UPDATE ON refresh_tokens
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SCHEMA VERSION
-- ============================================================================
INSERT INTO schema_migrations (version, description)
VALUES ('001', 'Initial schema: all 21 tables, indexes, triggers')
ON CONFLICT (version) DO NOTHING;

COMMIT;
