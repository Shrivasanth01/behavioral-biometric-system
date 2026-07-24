#!/bin/bash
set -e

echo "Initializing Behavioral Biometric System databases..."

# Create multiple databases if POSTGRES_MULTIPLE_DATABASES is set
if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Creating additional databases: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo "$POSTGRES_MULTIPLE_DATABASES" | tr ',' ' '); do
        echo "  Creating database: $db"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
            CREATE DATABASE "$db"
                WITH OWNER = "$POSTGRES_USER"
                ENCODING = 'UTF8'
                LC_COLLATE = 'en_US.utf8'
                LC_CTYPE = 'en_US.utf8'
                CONNECTION LIMIT = -1;
EOSQL
        echo "  Database $db created successfully"
    done
    echo "All additional databases created"
fi

# Create extensions
echo "Creating database extensions..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
    CREATE EXTENSION IF NOT EXISTS "btree_gin";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    SELECT * FROM pg_extension;
EOSQL

# Create schemas
echo "Creating database schemas..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "bbs_platform" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS auth;
    CREATE SCHEMA IF NOT EXISTS biometric;
    CREATE SCHEMA IF NOT EXISTS banking;
    CREATE SCHEMA IF NOT EXISTS fraud;
    CREATE SCHEMA IF NOT EXISTS audit;
    CREATE SCHEMA IF NOT EXISTS analytics;
    GRANT ALL ON SCHEMA auth, biometric, banking, fraud, audit, analytics TO "$POSTGRES_USER";
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "bbs_analytics" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS metrics;
    CREATE SCHEMA IF NOT EXISTS reports;
    CREATE SCHEMA IF NOT EXISTS ml_training;
    GRANT ALL ON SCHEMA metrics, reports, ml_training TO "$POSTGRES_USER";
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "bbs_audit" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS audit_log;
    CREATE SCHEMA IF NOT EXISTS compliance;
    GRANT ALL ON SCHEMA audit_log, compliance TO "$POSTGRES_USER";
EOSQL

# Set up performance tuning
echo "Configuring performance parameters..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    ALTER SYSTEM SET max_connections = '200';
    ALTER SYSTEM SET shared_buffers = '256MB';
    ALTER SYSTEM SET effective_cache_size = '768MB';
    ALTER SYSTEM SET maintenance_work_mem = '64MB';
    ALTER SYSTEM SET checkpoint_completion_target = '0.9';
    ALTER SYSTEM SET wal_buffers = '16MB';
    ALTER SYSTEM SET default_statistics_target = '100';
    ALTER SYSTEM SET random_page_cost = '1.1';
    ALTER SYSTEM SET effective_io_concurrency = '200';
    ALTER SYSTEM SET work_mem = '6553kB';
    ALTER SYSTEM SET min_wal_size = '1GB';
    ALTER SYSTEM SET max_wal_size = '4GB';
    ALTER SYSTEM SET max_worker_processes = '8';
    ALTER SYSTEM SET max_parallel_workers_per_gather = '4';
    ALTER SYSTEM SET max_parallel_workers = '8';
    ALTER SYSTEM SET max_parallel_maintenance_workers = '4';
EOSQL

echo "Database initialization complete!"
