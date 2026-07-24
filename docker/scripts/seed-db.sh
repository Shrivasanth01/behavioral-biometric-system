#!/bin/bash
set -e

echo "Seeding Behavioral Biometric System data..."

DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-bbs_user}"
DB_PASS="${DB_PASSWORD:-bbs_secure_password}"
DB_NAME="${DB_NAME:-bbs_platform}"

export PGPASSWORD="$DB_PASS"

PSQL_CMD="psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"

echo "Creating seed data for development/testing..."

# Insert sample users
$PSQL_CMD <<-EOSQL
    INSERT INTO auth.users (email, first_name, last_name, is_active, is_verified, created_at)
    VALUES
        ('admin@bbs-platform.com', 'Admin', 'User', true, true, NOW()),
        ('john.doe@example.com', 'John', 'Doe', true, true, NOW() - INTERVAL '30 days'),
        ('jane.smith@example.com', 'Jane', 'Smith', true, true, NOW() - INTERVAL '15 days'),
        ('bob.wilson@example.com', 'Bob', 'Wilson', true, true, NOW() - INTERVAL '7 days'),
        ('alice.johnson@example.com', 'Alice', 'Johnson', true, true, NOW() - INTERVAL '60 days'),
        ('fraud.test@example.com', 'Fraud', 'Test', true, true, NOW() - INTERVAL '1 day')
    ON CONFLICT (email) DO NOTHING;
EOSQL

# Insert biometric profiles
$PSQL_CMD <<-EOSQL
    INSERT INTO biometric.profiles (user_id, keystroke_pattern, mouse_pattern, touch_pattern, gait_pattern, voice_pattern, enrollment_status, enrollment_date)
    SELECT
        id,
        '{"dwell_time_mean": 85.5, "dwell_time_std": 12.3, "flight_time_mean": 145.2, "flight_time_std": 25.1, "key_press_duration_mean": 95.0, "key_press_duration_std": 15.0}'::jsonb,
        '{"velocity_mean": 450.0, "velocity_std": 120.0, "acceleration_mean": 3000.0, "acceleration_std": 800.0, "click_duration_mean": 120.0, "click_duration_std": 30.0, "scroll_pattern": {"avg_speed": 200, "direction_changes": 15}}'::jsonb,
        '{"swipe_velocity_mean": 500.0, "swipe_velocity_std": 150.0, "touch_pressure_mean": 0.45, "touch_pressure_std": 0.1, "hold_duration_mean": 200.0, "hold_duration_std": 50.0}'::jsonb,
        '{"stride_length_mean": 0.75, "stride_length_std": 0.1, "step_duration_mean": 0.5, "step_duration_std": 0.05, "acceleration_pattern": [1.2, 0.8, 1.1, 0.9]}'::jsonb,
        '{"pitch_mean": 120.0, "pitch_std": 15.0, "speech_rate_mean": 3.5, "speech_rate_std": 0.5, "tone_variance": 0.3}'::jsonb,
        'enrolled',
        NOW() - (random() * INTERVAL '60 days')
    FROM auth.users
    WHERE id NOT IN (SELECT user_id FROM biometric.profiles)
    LIMIT 6;
EOSQL

# Insert banking accounts
$PSQL_CMD <<-EOSQL
    INSERT INTO banking.accounts (user_id, account_number, account_type, currency, balance, available_balance, status, opened_date)
    SELECT
        u.id,
        'BBS' || LPAD(CAST(floor(random() * 99999999)::int AS text), 8, '0'),
        CASE floor(random() * 3)
            WHEN 0 THEN 'checking'
            WHEN 1 THEN 'savings'
            ELSE 'investment'
        END,
        'USD',
        round((random() * 100000)::numeric, 2),
        round((random() * 100000)::numeric, 2),
        'active',
        NOW() - (random() * INTERVAL '90 days')
    FROM auth.users u
    CROSS JOIN generate_series(1, 2)
    ON CONFLICT DO NOTHING;
EOSQL

# Insert sample transactions
$PSQL_CMD <<-EOSQL
    INSERT INTO banking.transactions (account_id, transaction_type, amount, currency, description, merchant_name, merchant_category, status, is_suspicious, created_at)
    SELECT
        a.id,
        CASE floor(random() * 4)
            WHEN 0 THEN 'debit'
            WHEN 1 THEN 'credit'
            WHEN 2 THEN 'transfer'
            ELSE 'payment'
        END,
        round((random() * 5000)::numeric, 2),
        'USD',
        CASE floor(random() * 5)
            WHEN 0 THEN 'Online purchase'
            WHEN 1 THEN 'ATM withdrawal'
            WHEN 2 THEN 'Wire transfer'
            WHEN 3 THEN 'Direct deposit'
            ELSE 'Bill payment'
        END,
        CASE floor(random() * 10)
            WHEN 0 THEN 'Amazon'
            WHEN 1 THEN 'Walmart'
            WHEN 2 THEN 'Starbucks'
            WHEN 3 THEN 'Uber'
            WHEN 4 THEN 'Netflix'
            WHEN 5 THEN 'Apple Store'
            WHEN 6 THEN 'Target'
            WHEN 7 THEN 'Costco'
            WHEN 8 THEN 'Shell Gas'
            ELSE 'Unknown Merchant'
        END,
        CASE floor(random() * 4)
            WHEN 0 THEN 'retail'
            WHEN 1 THEN 'food'
            WHEN 2 THEN 'transport'
            WHEN 3 THEN 'entertainment'
            ELSE 'other'
        END,
        'completed',
        random() < 0.05,
        NOW() - (random() * INTERVAL '30 days')
    FROM banking.accounts a
    CROSS JOIN generate_series(1, 50);
EOSQL

# Insert behavioral biometric sessions
$PSQL_CMD <<-EOSQL
    INSERT INTO biometric.sessions (user_id, device_id, session_type, keystroke_data, mouse_data, touch_data, gait_data, risk_score, is_anomalous, verdict, started_at, ended_at)
    SELECT
        u.id,
        'DEVICE-' || encode(gen_random_bytes(6), 'hex'),
        CASE floor(random() * 3)
            WHEN 0 THEN 'login'
            WHEN 1 THEN 'transaction'
            ELSE 'navigation'
        END,
        '{"key_press_events": [{"key": "a", "timestamp": 0.0, "duration": 95}, {"key": "b", "timestamp": 150.0, "duration": 85}], "typing_speed": 65.0, "error_rate": 0.02}'::jsonb,
        '{"move_events": [{"x": 100, "y": 200, "timestamp": 0.0}, {"x": 150, "y": 250, "timestamp": 100.0}], "click_events": [{"x": 100, "y": 200, "timestamp": 0.0, "button": "left"}], "scroll_events": [{"delta_y": 100, "timestamp": 500.0}]}'::jsonb,
        '{"swipe_events": [{"start_x": 0, "start_y": 0, "end_x": 200, "end_y": 300, "duration": 150}], "touch_points": [{"x": 50, "y": 75, "pressure": 0.5, "timestamp": 0.0}]}'::jsonb,
        '{"steps": [{"timestamp": 0.0, "acceleration_x": 1.2, "acceleration_y": 0.5, "acceleration_z": 9.8}], "stride_pattern": "normal"}'::jsonb,
        round((random() * 0.8)::numeric, 3),
        random() < 0.08,
        CASE
            WHEN random() < 0.08 THEN 'blocked'
            WHEN random() < 0.15 THEN 'flagged'
            ELSE 'approved'
        END,
        NOW() - (random() * INTERVAL '7 days'),
        NOW() - (random() * INTERVAL '7 days') + (random() * INTERVAL '30 minutes')
    FROM auth.users u
    CROSS JOIN generate_series(1, 20)
    ON CONFLICT DO NOTHING;
EOSQL

# Insert sample fraud alerts
$PSQL_CMD <<-EOSQL
    INSERT INTO fraud.alerts (user_id, transaction_id, alert_type, severity, risk_score, description, metadata, status, detected_at, resolved_at)
    SELECT
        u.id,
        t.id,
        CASE floor(random() * 6)
            WHEN 0 THEN 'unusual_location'
            WHEN 1 THEN 'velocity_check'
            WHEN 2 THEN 'device_mismatch'
            WHEN 3 THEN 'behavioral_anomaly'
            WHEN 4 THEN 'session_hijacking'
            ELSE 'impossible_travel'
        END,
        CASE floor(random() * 3)
            WHEN 0 THEN 'low'
            WHEN 1 THEN 'medium'
            ELSE 'high'
        END,
        round((random() * 0.9 + 0.1)::numeric, 3),
        CASE floor(random() * 4)
            WHEN 0 THEN 'Transaction from unusual location detected'
            WHEN 1 THEN 'Rapid transactions from multiple devices'
            WHEN 2 THEN 'Biometric profile mismatch detected'
            ELSE 'Atypical behavioral pattern detected'
        END,
        '{"source_ip": "192.168.' || floor(random() * 255)::int || '.' || floor(random() * 255)::int || '", "device_id": "DEVICE-' || encode(gen_random_bytes(6), 'hex') || '", "location": {"lat": ' || round((random() * 180 - 90)::numeric, 4) || ', "lng": ' || round((random() * 360 - 180)::numeric, 4) || '}, "user_agent": "Mozilla/5.0..."}'::jsonb,
        CASE floor(random() * 3)
            WHEN 0 THEN 'open'
            WHEN 1 THEN 'investigating'
            ELSE 'resolved'
        END,
        NOW() - (random() * INTERVAL '14 days'),
        CASE WHEN random() < 0.6 THEN NOW() - (random() * INTERVAL '7 days') ELSE NULL END
    FROM auth.users u
    CROSS JOIN banking.transactions t
    WHERE random() < 0.3
    LIMIT 30;
EOSQL

echo "Database seeding complete!"
echo ""
echo "Seed Summary:"
echo "  - Users: 6 (1 admin, 4 regular, 1 fraud test)"
echo "  - Biometric Profiles: 6"
echo "  - Bank Accounts: 12"
echo "  - Transactions: 600"
echo "  - Biometric Sessions: 120"
echo "  - Fraud Alerts: ~30"
echo ""
echo "Test credentials:"
echo "  Admin: admin@bbs-platform.com"
echo "  User:  john.doe@example.com"
echo "  Fraud: fraud.test@example.com"
echo ""
