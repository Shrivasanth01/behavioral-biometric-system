-- ============================================================================
-- Migration 002: Seed Data
-- Behavioral Biometric Banking Platform
-- ============================================================================
-- Inserts initial reference data: users, accounts, transactions,
-- behavioral profiles, and fraud alerts for development/testing.
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. ADMIN USERS (3)
-- ============================================================================
INSERT INTO users (email, password_hash, full_name, phone, role, is_active, last_login_at) VALUES
    ('admin@b3bank.io', '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5G8xYmMvKHzQ6qBm9vzX7YqS', 'Alice Chen', '+1-212-555-0101', 'admin', TRUE, NOW() - INTERVAL '2 hours'),
    ('admin@b3bank.io', '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5G8xYmMvKHzQ6qBm9vzX7YqS', 'Bob Martinez', '+1-312-555-0102', 'admin', TRUE, NOW() - INTERVAL '1 hour'),
    ('sysadmin@b3bank.io', '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5G8xYmMvKHzQ6qBm9vzX7YqS', 'Carol Washington', '+1-415-555-0103', 'admin', TRUE, NOW() - INTERVAL '30 minutes')
ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- 2. ANALYST USERS (5)
-- ============================================================================
INSERT INTO users (email, password_hash, full_name, phone, role, is_active, last_login_at) VALUES
    ('analyst1@b3bank.io', '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5G8xYmMvKHzQ6qBm9vzX7YqS', 'David Kim', '+1-510-555-0201', 'analyst', TRUE, NOW() - INTERVAL '3 hours'),
    ('analyst2@b3bank.io', '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5G8xYmMvKHzQ6qBm9vzX7YqS', 'Eva Johansson', '+1-617-555-0202', 'analyst', TRUE, NOW() - INTERVAL '4 hours'),
    ('analyst3@b3bank.io', '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5G8xYmMvKHzQ6qBm9vzX7YqS', 'Frank Okafor', '+1-206-555-0203', 'analyst', TRUE, NOW() - INTERVAL '5 hours'),
    ('analyst4@b3bank.io', '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5G8xYmMvKHzQ6qBm9vzX7YqS', 'Grace Patel', '+1-713-555-0204', 'analyst', TRUE, NOW() - INTERVAL '6 hours'),
    ('analyst5@b3bank.io', '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5G8xYmMvKHzQ6qBm9vzX7YqS', 'Henry Thompson', '+1-305-555-0205', 'analyst', TRUE, NOW() - INTERVAL '7 hours')
ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- 3. CUSTOMER USERS (50)
-- ============================================================================
INSERT INTO users (email, password_hash, full_name, phone, role, is_active, two_factor_enabled, last_login_at)
SELECT
    'customer' || n || '@b3bank.io',
    '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5G8xYmMvKHzQ6qBm9vzX7YqS',
    CASE (n % 10)
        WHEN 0 THEN 'James'
        WHEN 1 THEN 'Mary'
        WHEN 2 THEN 'Robert'
        WHEN 3 THEN 'Patricia'
        WHEN 4 THEN 'John'
        WHEN 5 THEN 'Jennifer'
        WHEN 6 THEN 'Michael'
        WHEN 7 THEN 'Linda'
        WHEN 8 THEN 'David'
        WHEN 9 THEN 'Elizabeth'
    END || ' ' || CASE (n % 10)
        WHEN 0 THEN 'Williams'
        WHEN 1 THEN 'Brown'
        WHEN 2 THEN 'Jones'
        WHEN 3 THEN 'Garcia'
        WHEN 4 THEN 'Miller'
        WHEN 5 THEN 'Davis'
        WHEN 6 THEN 'Rodriguez'
        WHEN 7 THEN 'Martinez'
        WHEN 8 THEN 'Hernandez'
        WHEN 9 THEN 'Lopez'
    END || ' ' || n,
    '+1-555-' || LPAD((n + 1000)::TEXT, 4, '0'),
    'customer',
    TRUE,
    CASE WHEN n % 5 = 0 THEN TRUE ELSE FALSE END,
    NOW() - (random() * INTERVAL '30 days')
FROM generate_series(1, 50) AS n
ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- 4. ACCOUNTS (one savings + one current per customer)
-- ============================================================================
DO $$
DECLARE
    cust RECORD;
    acct_num VARCHAR(20);
    acct_type VARCHAR(20);
    opening_balance NUMERIC(18,2);
BEGIN
    FOR cust IN SELECT id, LPAD((ROW_NUMBER() OVER (ORDER BY id))::TEXT, 6, '0') AS seq
                FROM users WHERE role = 'customer'
                ORDER BY id
    LOOP
        -- Savings account
        acct_num := 'SAV' || cust.seq || LPAD((100 + cust.seq::INT % 900)::TEXT, 3, '0');
        opening_balance := 500 + (random() * 50000)::NUMERIC(18,2);
        INSERT INTO accounts (user_id, account_number, account_type, currency, balance, available_balance)
        VALUES (cust.id, acct_num, 'savings', 'USD', opening_balance, opening_balance);

        -- Current account
        acct_num := 'CUR' || cust.seq || LPAD((200 + cust.seq::INT % 900)::TEXT, 3, '0');
        opening_balance := 1000 + (random() * 100000)::NUMERIC(18,2);
        INSERT INTO accounts (user_id, account_number, account_type, currency, balance, available_balance)
        VALUES (cust.id, acct_num, 'current', 'USD', opening_balance, opening_balance);
    END LOOP;
END $$;

-- ============================================================================
-- 5. CARDS (one debit card per savings account)
-- ============================================================================
DO $$
DECLARE
    acct RECORD;
    card_num VARCHAR(16);
    masked VARCHAR(20);
    last4 VARCHAR(4);
    card_hash VARCHAR(255);
BEGIN
    FOR acct IN SELECT a.id AS account_id, a.user_id, u.full_name
                FROM accounts a
                JOIN users u ON u.id = a.user_id
                WHERE a.account_type = 'savings'
    LOOP
        card_num := '4532' || LPAD((FLOOR(RANDOM() * 1e12)::BIGINT)::TEXT, 12, '0');
        last4 := RIGHT(card_num, 4);
        masked := '4532-XXXX-XXXX-' || last4;
        card_hash := '$2b$12$' || encode(gen_random_bytes(22), 'base64');
        INSERT INTO cards (
            account_id, user_id, card_type, card_network, card_holder_name,
            masked_card_number, card_hash, last_four_digits, expiry_date,
            daily_limit, transaction_limit, monthly_limit
        ) VALUES (
            acct.account_id, acct.user_id, 'debit', 'visa', UPPER(acct.full_name),
            masked, card_hash, last4,
            (DATE '2027-12-01' + (RANDOM() * 365)::INT),
            5000.00, 2000.00, 25000.00
        );
    END LOOP;
END $$;

-- ============================================================================
-- 6. BENEFICIARIES (3 per customer)
-- ============================================================================
DO $$
DECLARE
    cust RECORD;
    beneficiary_names TEXT[] := ARRAY['Alice Johnson', 'Bob Smith', 'Carol White', 'Dan Brown', 'Eva Green', 'Frank Black', 'Grace Hall', 'Henry Lee', 'Iris Young', 'Jack Turner'];
BEGIN
    FOR cust IN SELECT id FROM users WHERE role = 'customer' ORDER BY id
    LOOP
        INSERT INTO beneficiaries (user_id, beneficiary_name, beneficiary_account, beneficiary_bank, nickname, relationship, max_limit)
        VALUES
            (cust.id, beneficiary_names[1 + (cust.id % 10)], 'ACC' || LPAD((10000 + cust.id * 3)::TEXT, 10, '0'), 'First National Bank', 'Primary Contact', 'Friend', 10000.00),
            (cust.id, beneficiary_names[1 + ((cust.id + 3) % 10)], 'ACC' || LPAD((10001 + cust.id * 3)::TEXT, 10, '0'), 'Global Trust Bank', 'Family', 'Brother', 25000.00),
            (cust.id, beneficiary_names[1 + ((cust.id + 7) % 10)], 'ACC' || LPAD((10002 + cust.id * 3)::TEXT, 10, '0'), 'City Credit Union', 'Utility', 'Other', 5000.00);
    END LOOP;
END $$;

-- ============================================================================
-- 7. SESSIONS (recent login sessions)
-- ============================================================================
INSERT INTO sessions (user_id, session_token, ip_address, user_agent, is_active, expires_at, last_activity_at)
SELECT
    id,
    encode(gen_random_bytes(48), 'hex'),
    (ARRAY['192.168.1.100'::INET, '10.0.0.50'::INET, '172.16.0.75'::INET])[1 + (id % 3)],
    CASE (id % 4)
        WHEN 0 THEN 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
        WHEN 1 THEN 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) Safari/17.0'
        WHEN 2 THEN 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) Mobile/15E148'
        WHEN 3 THEN 'Mozilla/5.0 (Linux; Android 14) Firefox/121.0'
    END,
    TRUE,
    NOW() + INTERVAL '24 hours',
    NOW() - (random() * INTERVAL '2 hours')
FROM users
WHERE role != 'admin'
LIMIT 60;

-- ============================================================================
-- 8. DEVICE FINGERPRINTS (one per session)
-- ============================================================================
INSERT INTO device_fingerprints (user_id, device_id, device_type, os, browser, screen_resolution, timezone, language, webgl_fingerprint, canvas_fingerprint, audio_fingerprint, ip_addresses)
SELECT
    s.user_id,
    'DEV-' || encode(gen_random_bytes(8), 'hex'),
    CASE (s.id % 3) WHEN 0 THEN 'desktop' WHEN 1 THEN 'mobile' ELSE 'tablet' END,
    CASE (s.id % 4) WHEN 0 THEN 'Windows 10' WHEN 1 THEN 'macOS 14' WHEN 2 THEN 'iOS 17' ELSE 'Android 14' END,
    CASE (s.id % 3) WHEN 0 THEN 'Chrome 120' WHEN 1 THEN 'Safari 17' ELSE 'Firefox 121' END,
    CASE (s.id % 4) WHEN 0 THEN '1920x1080' WHEN 1 THEN '2560x1440' WHEN 2 THEN '1440x900' ELSE '390x844' END,
    CASE (s.id % 5) WHEN 0 THEN 'America/New_York' WHEN 1 THEN 'America/Chicago' WHEN 2 THEN 'America/Denver' WHEN 3 THEN 'America/Los_Angeles' ELSE 'Europe/London' END,
    CASE (s.id % 3) WHEN 0 THEN 'en-US' WHEN 1 THEN 'en-GB' ELSE 'en' END,
    'wg-' || encode(gen_random_bytes(16), 'hex'),
    'cv-' || encode(gen_random_bytes(16), 'hex'),
    'af-' || encode(gen_random_bytes(16), 'hex'),
    ARRAY[s.ip_address]
FROM sessions s
WHERE s.is_active = TRUE;

-- Link device fingerprints to sessions
UPDATE sessions s
SET device_fingerprint_id = df.id
FROM device_fingerprints df
WHERE df.user_id = s.user_id
AND s.device_fingerprint_id IS NULL
AND s.id IN (
    SELECT MIN(s2.id) FROM sessions s2
    JOIN device_fingerprints df2 ON df2.user_id = s2.user_id
    GROUP BY s2.user_id
);

-- ============================================================================
-- 9. TRANSACTIONS (50 sample transactions across customers)
-- ============================================================================
DO $$
DECLARE
    acct RECORD;
    txn_types TEXT[] := ARRAY['transfer', 'payment', 'recharge', 'withdrawal', 'deposit'];
    txn_statuses TEXT[] := ARRAY['completed', 'completed', 'completed', 'completed', 'failed', 'pending'];
    counterparties TEXT[] := ARRAY['Amazon Payments', 'Walmart Inc', 'Netflix', 'Spotify AB', 'Uber Technologies', 'DoorDash Inc', 'Apple Store', 'Google Services', 'AT&T Wireless', 'Electric Company'];
    cat TEXT[] := ARRAY['shopping', 'utilities', 'entertainment', 'food', 'transport', 'subscription', 'healthcare', 'education'];
    v_amount NUMERIC(18,2);
    v_type TEXT;
    v_status TEXT;
    v_counterparty TEXT;
    v_cat TEXT;
    v_ref VARCHAR(50);
    v_acct_id INT;
    v_user_id INT;
BEGIN
    FOR i IN 1..50 LOOP
        SELECT a.id, a.user_id INTO v_acct_id, v_user_id
        FROM accounts a
        JOIN users u ON u.id = a.user_id
        WHERE u.role = 'customer'
        ORDER BY RANDOM()
        LIMIT 1;

        v_amount := (10 + RANDOM() * 5000)::NUMERIC(18,2);
        v_type := txn_types[1 + (RANDOM() * 4)::INT];
        v_status := txn_statuses[1 + (RANDOM() * 5)::INT];
        v_counterparty := counterparties[1 + (RANDOM() * 9)::INT];
        v_cat := cat[1 + (RANDOM() * 7)::INT];
        v_ref := 'B3B-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD((10000 + i)::TEXT, 6, '0');

        INSERT INTO transactions (
            account_id, user_id, transaction_type, amount, currency,
            reference_number, description, status, counterparty_name,
            counterparty_account, category, ip_address, processed_at
        ) VALUES (
            v_acct_id, v_user_id, v_type, v_amount, 'USD',
            v_ref, v_counterparty || ' - ' || v_cat || ' payment',
            v_status, v_counterparty,
            'CP' || LPAD((FLOOR(RANDOM() * 1e8)::BIGINT)::TEXT, 10, '0'),
            v_cat,
            (ARRAY['192.168.1.100'::INET, '10.0.0.50'::INET, '172.16.0.75'::INET])[1 + (i % 3)],
            CASE WHEN v_status = 'completed' THEN NOW() - (RANDOM() * INTERVAL '7 days') ELSE NULL END
        );

        -- Update balance for completed transactions
        IF v_status = 'completed' AND v_type != 'deposit' THEN
            UPDATE accounts
            SET balance = balance - v_amount,
                available_balance = available_balance - v_amount
            WHERE id = v_acct_id;
        ELSIF v_status = 'completed' AND v_type = 'deposit' THEN
            UPDATE accounts
            SET balance = balance + v_amount,
                available_balance = available_balance + v_amount
            WHERE id = v_acct_id;
        END IF;
    END LOOP;
END $$;

-- ============================================================================
-- 10. LOANS (10 sample loans)
-- ============================================================================
INSERT INTO loans (account_id, user_id, loan_type, loan_reference, principal_amount, interest_rate, tenure_months, emi_amount, outstanding_amount, status, disbursed_at, next_emi_date)
SELECT
    a.id,
    a.user_id,
    loan_types[1 + (RANDOM() * 4)::INT],
    'LN-' || TO_CHAR(NOW(), 'YYYY') || '-' || LPAD((100 + n)::TEXT, 6, '0'),
    principals[n],
    rates[n],
    tenures[n],
    principals[n] * (rates[n]/100/12 * POWER(1 + rates[n]/100/12, tenures[n])) / (POWER(1 + rates[n]/100/12, tenures[n]) - 1),
    principals[n] - (RANDOM() * principals[n] * 0.3)::NUMERIC(18,2),
    CASE WHEN n % 3 = 0 THEN 'defaulted' WHEN n % 5 = 0 THEN 'closed' ELSE 'active' END,
    NOW() - (tenures[n] * INTERVAL '15 days'),
    CASE WHEN n % 3 != 0 AND n % 5 != 0 THEN NOW() + INTERVAL '30 days' ELSE NULL END
FROM (
    SELECT a.id, a.user_id FROM accounts a WHERE a.account_type = 'savings' ORDER BY RANDOM() LIMIT 10
) a
CROSS JOIN LATERAL (
    SELECT
        (ARRAY['personal', 'home', 'auto', 'education', 'business'])[n] AS loan_types,
        (ARRAY[15000, 350000, 25000, 40000, 100000])[n] AS principals,
        (ARRAY[8.5, 6.75, 7.25, 9.0, 10.5])[n] AS rates,
        (ARRAY[36, 240, 60, 84, 120])[n] AS tenures
) params
CROSS JOIN (SELECT generate_series(1, 10) AS n) nums
WHERE nums.n = (
    SELECT COUNT(*) FROM accounts a2
    JOIN loans l2 ON l2.account_id = a2.id
    WHERE a2.id = a.id
) + 1
LIMIT 10;

-- ============================================================================
-- 11. BEHAVIORAL EVENTS (sample raw events)
-- ============================================================================
INSERT INTO behavioral_events (user_id, session_id, event_type, event_name, event_data, client_timestamp, action, coordinates, page_url)
SELECT
    s.user_id,
    s.id,
    CASE (e.n % 5)
        WHEN 0 THEN 'mouse'
        WHEN 1 THEN 'keyboard'
        WHEN 2 THEN 'navigation'
        WHEN 3 THEN 'touch'
        WHEN 4 THEN 'device'
    END,
    CASE (e.n % 5)
        WHEN 0 THEN 'mouse.move'
        WHEN 1 THEN 'keyboard.keydown'
        WHEN 2 THEN 'page.navigate'
        WHEN 3 THEN 'touch.swipe'
        WHEN 4 THEN 'window.resize'
    END,
    CASE (e.n % 5)
        WHEN 0 THEN jsonb_build_object('x', (RANDOM() * 1920)::INT, 'y', (RANDOM() * 1080)::INT, 'velocity', RANDOM() * 1000, 'acceleration', RANDOM() * 500, 'button', 0)
        WHEN 1 THEN jsonb_build_object('key', CHR(65 + (RANDOM() * 25)::INT), 'keyCode', 65 + (RANDOM() * 25)::INT, 'duration', (RANDOM() * 200)::INT, 'pressToPress', (RANDOM() * 500)::INT)
        WHEN 2 THEN jsonb_build_object('from', '/dashboard', 'to', '/accounts', 'timestamp', EXTRACT(EPOCH FROM NOW())::BIGINT)
        WHEN 3 THEN jsonb_build_object('startX', (RANDOM() * 390)::INT, 'startY', (RANDOM() * 844)::INT, 'endX', (RANDOM() * 390)::INT, 'endY', (RANDOM() * 844)::INT, 'duration', (RANDOM() * 1000)::INT)
        WHEN 4 THEN jsonb_build_object('width', 1920, 'height', 1080, 'orientation', 'landscape', 'pixelRatio', 2.0)
    END,
    NOW() - ((100 - e.n) * INTERVAL '1 minute'),
    CASE (e.n % 5)
        WHEN 0 THEN 'move'
        WHEN 1 THEN 'keydown'
        WHEN 2 THEN 'navigate'
        WHEN 3 THEN 'swipe'
        WHEN 4 THEN 'resize'
    END,
    CASE (e.n % 5)
        WHEN 0 THEN jsonb_build_object('x', (RANDOM() * 1920)::INT, 'y', (RANDOM() * 1080)::INT)
        WHEN 3 THEN jsonb_build_object('x', (RANDOM() * 390)::INT, 'y', (RANDOM() * 844)::INT)
        ELSE NULL
    END,
    CASE (e.n % 3)
        WHEN 0 THEN '/dashboard'
        WHEN 1 THEN '/accounts'
        WHEN 2 THEN '/transactions'
    END
FROM sessions s
CROSS JOIN generate_series(1, 20) AS e(n)
WHERE s.is_active = TRUE
ORDER BY s.id, e.n
LIMIT 500;

-- ============================================================================
-- 12. BEHAVIORAL FEATURES (extracted feature vectors)
-- ============================================================================
INSERT INTO behavioral_features (user_id, session_id, feature_version, feature_set, mouse_features, keystroke_features, navigation_features, temporal_features, combined_vector, feature_dimension, is_outlier)
SELECT
    s.user_id,
    s.id,
    '1.0',
    'full',
    jsonb_build_object(
        'avg_velocity', 100 + RANDOM() * 900,
        'avg_acceleration', 50 + RANDOM() * 450,
        'click_count', (RANDOM() * 50)::INT,
        'avg_click_duration', 50 + RANDOM() * 200,
        'movement_efficiency', RANDOM() * 100,
        'scroll_speed', RANDOM() * 500,
        'straightness_ratio', RANDOM(),
        'pause_frequency', (RANDOM() * 20)::INT
    ),
    jsonb_build_object(
        'avg_key_duration', 50 + RANDOM() * 150,
        'avg_press_to_press', 100 + RANDOM() * 400,
        'typing_speed', 30 + RANDOM() * 70,
        'error_rate', RANDOM() * 0.1,
        'backspace_frequency', RANDOM() * 0.2,
        'special_key_ratio', RANDOM() * 0.3,
        'key_latency_variance', RANDOM() * 100,
        'digraph_times', jsonb_build_object('th', 80 + RANDOM() * 40, 'he', 90 + RANDOM() * 50, 'in', 70 + RANDOM() * 30)
    ),
    jsonb_build_object(
        'pages_visited', (1 + RANDOM() * 10)::INT,
        'time_on_page', (10 + RANDOM() * 300)::INT,
        'navigation_depth', (1 + RANDOM() * 5)::INT,
        'back_forward_ratio', RANDOM() * 0.5,
        'form_interaction_count', (RANDOM() * 15)::INT,
        'copy_paste_events', (RANDOM() * 5)::INT
    ),
    jsonb_build_object(
        'session_duration', (60 + RANDOM() * 3600)::INT,
        'idle_time_ratio', RANDOM() * 0.4,
        'active_time_ratio', 0.6 + RANDOM() * 0.4,
        'hour_of_day', (8 + RANDOM() * 14)::INT,
        'day_of_week', (RANDOM() * 6)::INT,
        'inter_event_time_mean', 1000 + RANDOM() * 5000,
        'inter_event_time_variance', RANDOM() * 10000
    ),
    (SELECT jsonb_agg(RANDOM()) FROM generate_series(1, 32)),
    32,
    CASE WHEN RANDOM() < 0.05 THEN TRUE ELSE FALSE END
FROM sessions s
WHERE s.is_active = TRUE
LIMIT 50;

-- ============================================================================
-- 13. BEHAVIORAL PROFILES (one per customer)
-- ============================================================================
INSERT INTO behavioral_profiles (user_id, profile_version, status, confidence_score, total_events_analyzed, total_sessions_analyzed, mouse_pattern, keystroke_pattern, navigation_pattern, temporal_pattern, behavioral_biometrics, baseline_deviation, last_calculated_at)
SELECT
    u.id,
    '1.0',
    CASE
        WHEN u.id % 10 = 0 THEN 'stale'
        WHEN u.id % 15 = 0 THEN 'learning'
        ELSE 'active'
    END,
    50 + RANDOM() * 45,
    100 + (RANDOM() * 9000)::INT,
    5 + (RANDOM() * 45)::INT,
    jsonb_build_object(
        'mean_speed', 200 + RANDOM() * 800,
        'speed_std', 50 + RANDOM() * 200,
        'mean_acceleration', 100 + RANDOM() * 400,
        'click_pattern', jsonb_build_object('single_click_ratio', 0.7 + RANDOM() * 0.2, 'double_click_ratio', RANDOM() * 0.15),
        'scroll_pattern', jsonb_build_object('avg_scroll_depth', 500 + RANDOM() * 1500, 'scroll_variance', RANDOM() * 500)
    ),
    jsonb_build_object(
        'mean_key_duration', 80 + RANDOM() * 120,
        'duration_std', 20 + RANDOM() * 60,
        'mean_press_to_press', 200 + RANDOM() * 300,
        'typing_profile', jsonb_build_object('wpm', 40 + RANDOM() * 40, 'error_rate', RANDOM() * 0.08),
        'digraph_profile', jsonb_build_object('th', 80 + RANDOM() * 40, 'he', 85 + RANDOM() * 45, 'in', 75 + RANDOM() * 35)
    ),
    jsonb_build_object(
        'common_paths', jsonb_build_array('/dashboard/accounts', '/accounts/transactions', '/transfer'),
        'avg_session_pages', 3 + RANDOM() * 7,
        'navigation_speed', 100 + RANDOM() * 900
    ),
    jsonb_build_object(
        'active_hours', jsonb_build_object('peak_start', 9, 'peak_end', 17),
        'weekday_activity', 0.7 + RANDOM() * 0.3,
        'weekend_activity', RANDOM() * 0.5,
        'session_length_mean', 300 + RANDOM() * 1500
    ),
    jsonb_build_object(
        'overall_confidence', 60 + RANDOM() * 35,
        'pattern_consistency', 50 + RANDOM() * 45,
        'entropy_score', RANDOM() * 10,
        'uniqueness_score', RANDOM() * 100
    ),
    RANDOM() * 5,
    NOW() - (RANDOM() * INTERVAL '7 days')
FROM users u
WHERE u.role = 'customer';

-- ============================================================================
-- 14. ML MODELS (sample models)
-- ============================================================================
INSERT INTO ml_models (model_name, model_version, model_type, algorithm, model_data, model_metadata, performance_metrics, is_active, is_production, trained_by, trained_at, deployed_at)
VALUES
    ('behavioral-anomaly-detector', '1.0.0', 'anomaly_detection', 'IsolationForest',
     E'\\x0123456789ABCDEF',
     jsonb_build_object('n_estimators', 200, 'max_samples', 'auto', 'contamination', 0.05, 'feature_count', 32),
     jsonb_build_object('precision', 0.92, 'recall', 0.88, 'f1_score', 0.90, 'auc_roc', 0.96, 'false_positive_rate', 0.03),
     TRUE, TRUE, (SELECT id FROM users WHERE role = 'admin' LIMIT 1), NOW() - INTERVAL '14 days', NOW() - INTERVAL '7 days'),
    ('keystroke-classifier', '2.1.0', 'classification', 'XGBoost',
     E'\\x0123456789ABCDEF',
     jsonb_build_object('max_depth', 6, 'learning_rate', 0.1, 'n_estimators', 150, 'subsample', 0.8),
     jsonb_build_object('accuracy', 0.94, 'precision', 0.93, 'recall', 0.91, 'f1_score', 0.92, 'auc_roc', 0.97),
     TRUE, TRUE, (SELECT id FROM users WHERE role = 'admin' LIMIT 1), NOW() - INTERVAL '10 days', NOW() - INTERVAL '5 days'),
    ('mouse-dynamics-regressor', '1.2.0', 'regression', 'RandomForest',
     E'\\x0123456789ABCDEF',
     jsonb_build_object('n_estimators', 300, 'max_depth', 12, 'min_samples_split', 5, 'n_jobs', -1),
     jsonb_build_object('r2_score', 0.87, 'mae', 0.12, 'rmse', 0.18, 'explained_variance', 0.88),
     TRUE, FALSE, (SELECT id FROM users WHERE role = 'admin' LIMIT 1), NOW() - INTERVAL '8 days', NULL),
    ('session-risk-scorer', '1.0.0', 'classification', 'GradientBoosting',
     E'\\x0123456789ABCDEF',
     jsonb_build_object('n_estimators', 250, 'learning_rate', 0.05, 'max_depth', 5, 'subsample', 0.7),
     jsonb_build_object('accuracy', 0.91, 'precision', 0.89, 'recall', 0.86, 'f1_score', 0.87, 'auc_roc', 0.95),
     TRUE, TRUE, (SELECT id FROM users WHERE role = 'admin' LIMIT 1), NOW() - INTERVAL '20 days', NOW() - INTERVAL '15 days'),
    ('deep-behavioral-encoder', '0.9.0', 'feature_extractor', 'AutoEncoder',
     E'\\x0123456789ABCDEF',
     jsonb_build_object('encoding_dim', 64, 'hidden_layers', ARRAY[128, 64, 32], 'activation', 'relu', 'dropout', 0.2, 'epochs', 100),
     jsonb_build_object('reconstruction_error', 0.023, 'validation_loss', 0.031, 'test_loss', 0.035),
     FALSE, FALSE, (SELECT id FROM users WHERE role = 'analyst' LIMIT 1), NOW() - INTERVAL '5 days', NULL);

-- ============================================================================
-- 15. RISK SCORES (sample scores)
-- ============================================================================
INSERT INTO risk_scores (user_id, transaction_id, session_id, model_id, score_type, risk_score, risk_level, confidence, feature_contributions, model_version, execution_time_ms)
SELECT
    t.user_id,
    t.id,
    t.session_id,
    (SELECT id FROM ml_models WHERE is_production = TRUE ORDER BY RANDOM() LIMIT 1),
    CASE t.transaction_type
        WHEN 'transfer' THEN 'transfer'
        WHEN 'payment' THEN 'transaction'
        ELSE 'transaction'
    END,
    (RANDOM() * 100)::NUMERIC(5,2),
    CASE
        WHEN RANDOM() < 0.4 THEN 'very_low'
        WHEN RANDOM() < 0.7 THEN 'low'
        WHEN RANDOM() < 0.85 THEN 'medium'
        WHEN RANDOM() < 0.95 THEN 'high'
        ELSE 'critical'
    END,
    (60 + RANDOM() * 35)::NUMERIC(5,2),
    jsonb_build_object(
        'amount_score', RANDOM() * 30,
        'velocity_score', RANDOM() * 25,
        'device_score', RANDOM() * 20,
        'location_score', RANDOM() * 15,
        'behavioral_score', RANDOM() * 10
    ),
    '1.0.0',
    (10 + RANDOM() * 200)::INT
FROM transactions t
WHERE t.status = 'completed'
LIMIT 30;

-- ============================================================================
-- 16. FRAUD ALERTS (sample alerts)
-- ============================================================================
INSERT INTO fraud_alerts (user_id, transaction_id, session_id, risk_score_id, alert_type, alert_severity, status, title, description, reason_codes, risk_score_value, threshold_value, anomaly_details, assigned_to)
SELECT
    rs.user_id,
    rs.transaction_id,
    rs.session_id,
    rs.id,
    CASE
        WHEN rs.risk_level IN ('critical', 'high') THEN 'high_risk_transaction'
        ELSE 'behavioral_anomaly'
    END,
    CASE rs.risk_level
        WHEN 'critical' THEN 'critical'
        WHEN 'high' THEN 'high'
        WHEN 'medium' THEN 'medium'
        ELSE 'low'
    END,
    CASE
        WHEN RANDOM() < 0.3 THEN 'open'
        WHEN RANDOM() < 0.5 THEN 'investigating'
        WHEN RANDOM() < 0.7 THEN 'resolved'
        WHEN RANDOM() < 0.85 THEN 'false_positive'
        ELSE 'dismissed'
    END,
    CASE rs.risk_level
        WHEN 'critical' THEN 'CRITICAL: Suspicious transaction pattern detected'
        WHEN 'high' THEN 'High-risk transaction flagged for review'
        WHEN 'medium' THEN 'Unusual behavioral pattern detected'
        ELSE 'Minor anomaly - informational alert'
    END,
    'Transaction #' || rs.transaction_id || ' scored ' || rs.risk_score || ' (' || rs.risk_level || '). ' ||
    'Primary contributors: amount deviation, unusual location. Recommended action: verify with customer.',
    CASE rs.risk_level
        WHEN 'critical' THEN ARRAY['RC-001', 'RC-003', 'RC-007', 'RC-012']
        WHEN 'high' THEN ARRAY['RC-001', 'RC-007', 'RC-012']
        WHEN 'medium' THEN ARRAY['RC-005', 'RC-012']
        ELSE ARRAY['RC-012']
    END,
    rs.risk_score,
    CASE rs.risk_level
        WHEN 'critical' THEN 80.00
        WHEN 'high' THEN 65.00
        WHEN 'medium' THEN 45.00
        ELSE 25.00
    END,
    jsonb_build_object(
        'amount_anomaly', RANDOM() > 0.5,
        'location_mismatch', RANDOM() > 0.6,
        'device_change', RANDOM() > 0.7,
        'speed_anomaly', RANDOM() > 0.5,
        'new_beneficiary', RANDOM() > 0.8,
        'off_hours_transaction', RANDOM() > 0.7
    ),
    CASE WHEN RANDOM() < 0.4 THEN (SELECT id FROM users WHERE role = 'analyst' ORDER BY RANDOM() LIMIT 1) ELSE NULL END
FROM risk_scores rs
WHERE rs.risk_level IN ('medium', 'high', 'critical')
LIMIT 15;

-- ============================================================================
-- 17. EXPLAINABILITY RESULTS (for fraud alerts)
-- ============================================================================
INSERT INTO explainability_results (user_id, fraud_alert_id, risk_score_id, transaction_id, session_id, model_id, explanation_type, reason_codes, reason_descriptions, top_features, feature_contributions, human_readable_summary)
SELECT
    fa.user_id,
    fa.id,
    fa.risk_score_id,
    fa.transaction_id,
    fa.session_id,
    rs.model_id,
    CASE (fa.id % 4)
        WHEN 0 THEN 'shap'
        WHEN 1 THEN 'lime'
        WHEN 2 THEN 'feature_importance'
        WHEN 3 THEN 'rule_based'
    END,
    fa.reason_codes,
    jsonb_build_object(
        'RC-001', 'Transaction amount significantly exceeds user baseline',
        'RC-003', 'Geographic location mismatch with user profile',
        'RC-005', 'New device detected for this user',
        'RC-007', 'Transaction velocity exceeds threshold',
        'RC-012', 'Time of day outside normal user pattern'
    ),
    jsonb_build_array(
        jsonb_build_object('feature', 'amount', 'importance', 0.35, 'value', 2500.00, 'baseline', 150.00),
        jsonb_build_object('feature', 'location', 'importance', 0.25, 'value', 'foreign', 'baseline', 'domestic'),
        jsonb_build_object('feature', 'velocity', 'importance', 0.20, 'value', 5, 'baseline', 1),
        jsonb_build_object('feature', 'device_age', 'importance', 0.12, 'value', 'new', 'baseline', 'known'),
        jsonb_build_object('feature', 'hour_of_day', 'importance', 0.08, 'value', 3, 'baseline', 14)
    ),
    jsonb_build_object(
        'amount', 0.35,
        'location', 0.25,
        'velocity', 0.20,
        'device_age', 0.12,
        'hour_of_day', 0.08
    ),
    'This transaction was flagged because the amount ($2,500.00) is 16.7x higher than the user''s typical spending (baseline: $150.00), ' ||
    'originating from a foreign location while the user''s profile shows only domestic transactions, and the device was first seen in this session.'
FROM fraud_alerts fa
JOIN risk_scores rs ON rs.id = fa.risk_score_id
WHERE fa.status NOT IN ('dismissed')
LIMIT 10;

-- ============================================================================
-- 18. MODEL DRIFT LOGS (sample drift events)
-- ============================================================================
INSERT INTO model_drift_logs (model_id, drift_type, drift_score, drift_severity, previous_metrics, current_metrics, drifted_features, sample_count, window_start, window_end, detected_at, action_taken)
SELECT
    m.id,
    drift_types[1 + (RANDOM() * 4)::INT],
    (RANDOM() * 100)::NUMERIC(10,6),
    severities[1 + (RANDOM() * 3)::INT],
    jsonb_build_object('f1_score', 0.90 + RANDOM() * 0.05, 'precision', 0.91 + RANDOM() * 0.04, 'recall', 0.88 + RANDOM() * 0.05),
    jsonb_build_object('f1_score', 0.75 + RANDOM() * 0.15, 'precision', 0.78 + RANDOM() * 0.12, 'recall', 0.72 + RANDOM() * 0.18),
    ARRAY['amount_mean', 'keystroke_duration', 'mouse_velocity', 'login_hour'],
    500 + (RANDOM() * 4500)::INT,
    NOW() - INTERVAL '14 days',
    NOW() - INTERVAL '7 days',
    NOW() - (RANDOM() * INTERVAL '3 days'),
    CASE WHEN RANDOM() < 0.5 THEN 'Retraining queued automatically' ELSE 'Alert sent to ML team' END
FROM ml_models m
CROSS JOIN (
    SELECT ARRAY['concept_drift', 'data_drift', 'model_decay', 'feature_drift', 'prediction_drift'] AS drift_types,
           ARRAY['low', 'medium', 'high', 'critical'] AS severities
) params
WHERE m.is_active = TRUE
LIMIT 8;

-- ============================================================================
-- 19. RETRAINING QUEUE (sample queue items)
-- ============================================================================
INSERT INTO retraining_queue (model_id, model_name, priority, status, trigger_reason, trigger_event_id, triggered_by, started_at, completed_at, result_metrics)
SELECT
    mdl.id,
    mdl.model_name,
    (RANDOM() * 100)::INT,
    statuses[1 + (RANDOM() * 4)::INT],
    reasons[1 + (RANDOM() * 4)::INT],
    drift.id,
    (SELECT id FROM users WHERE role = 'admin' LIMIT 1),
    CASE WHEN statuses[1 + (RANDOM() * 4)::INT] IN ('in_progress', 'completed', 'failed') THEN NOW() - INTERVAL '2 days' ELSE NULL END,
    CASE WHEN statuses[1 + (RANDOM() * 4)::INT] = 'completed' THEN NOW() - INTERVAL '1 day' ELSE NULL END,
    CASE WHEN statuses[1 + (RANDOM() * 4)::INT] = 'completed'
         THEN jsonb_build_object('new_f1', 0.91 + RANDOM() * 0.05, 'improvement', '+' || (RANDOM() * 0.05)::NUMERIC(4,3)::TEXT)
         ELSE NULL
    END
FROM ml_models mdl
JOIN LATERAL (
    SELECT id FROM model_drift_logs WHERE model_id = mdl.id ORDER BY RANDOM() LIMIT 1
) drift ON TRUE
CROSS JOIN (
    SELECT ARRAY['queued', 'queued', 'in_progress', 'completed', 'failed'] AS statuses,
           ARRAY['Model drift detected', 'Scheduled retraining', 'Performance degradation', 'New data available', 'Manual trigger'] AS reasons
) params
LIMIT 5;

-- ============================================================================
-- 20. MFA TOKENS (sample tokens)
-- ============================================================================
INSERT INTO mfa_tokens (user_id, session_id, token_type, token_code_hash, is_used, is_valid, attempts, expires_at, used_at, verified_at)
SELECT
    s.user_id,
    s.id,
    CASE (s.id % 5)
        WHEN 0 THEN 'totp'
        WHEN 1 THEN 'sms'
        WHEN 2 THEN 'email'
        WHEN 3 THEN 'push'
        WHEN 4 THEN 'backup_code'
    END,
    '$2b$12$' || encode(gen_random_bytes(22), 'base64'),
    CASE WHEN RANDOM() < 0.6 THEN TRUE ELSE FALSE END,
    CASE WHEN RANDOM() < 0.8 THEN TRUE ELSE FALSE END,
    (RANDOM() * 3)::INT,
    NOW() + (RANDOM() * INTERVAL '10 minutes'),
    CASE WHEN RANDOM() < 0.5 THEN NOW() - (RANDOM() * INTERVAL '5 minutes') ELSE NULL END,
    CASE WHEN RANDOM() < 0.5 THEN NOW() - (RANDOM() * INTERVAL '5 minutes') ELSE NULL END
FROM sessions s
WHERE s.is_active = TRUE
LIMIT 20;

-- ============================================================================
-- 21. REFRESH TOKENS (sample tokens)
-- ============================================================================
INSERT INTO refresh_tokens (user_id, token_hash, is_revoked, is_used, device_fingerprint_id, ip_address, user_agent, expires_at)
SELECT
    s.user_id,
    encode(gen_random_bytes(32), 'hex'),
    FALSE,
    FALSE,
    s.device_fingerprint_id,
    s.ip_address,
    s.user_agent,
    NOW() + INTERVAL '30 days'
FROM sessions s
WHERE s.is_active = TRUE
LIMIT 40;

-- ============================================================================
-- 22. AUDIT LOGS (sample audit entries)
-- ============================================================================
INSERT INTO audit_logs (user_id, session_id, action, entity_type, entity_id, action_type, severity, status, ip_address, user_agent, changes, request_id)
SELECT
    u.id,
    s.id,
    actions[1 + (RANDOM() * 7)::INT],
    entities[1 + (RANDOM() * 7)::INT],
    (RANDOM() * 1000)::INT,
    action_types[1 + (RANDOM() * 7)::INT],
    severities[1 + (RANDOM() * 4)::INT],
    statuses[1 + (RANDOM() * 2)::INT],
    s.ip_address,
    s.user_agent,
    jsonb_build_object('field', 'status', 'old', 'pending', 'new', 'completed'),
    'req-' || encode(gen_random_bytes(6), 'hex')
FROM users u
JOIN sessions s ON s.user_id = u.id
CROSS JOIN (
    SELECT
        ARRAY['user.login', 'user.logout', 'transaction.create', 'account.view', 'profile.update', 'transfer.initiate', 'alert.acknowledge', 'card.freeze'] AS actions,
        ARRAY['User', 'Session', 'Transaction', 'Account', 'Profile', 'Beneficiary', 'Card', 'Alert'] AS entities,
        ARRAY['LOGIN', 'LOGOUT', 'CREATE', 'READ', 'UPDATE', 'DELETE', 'EXPORT', 'OTHER'] AS action_types,
        ARRAY['info', 'low', 'medium', 'high', 'critical'] AS severities,
        ARRAY['success', 'failure', 'pending'] AS statuses
) params
WHERE u.role = 'customer'
LIMIT 100;

-- ============================================================================
-- Record migration
-- ============================================================================
INSERT INTO schema_migrations (version, description)
VALUES ('002', 'Seed data: 58 users, 100 accounts, 50 transactions, profiles, alerts')
ON CONFLICT (version) DO NOTHING;

COMMIT;
