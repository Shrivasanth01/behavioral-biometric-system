#!/bin/bash
set -e

echo "=== Behavioral Biometric System Database Backup ==="
echo ""

BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-bbs_user}"
DB_PASS="${DB_PASSWORD:-bbs_secure_password}"
DB_NAMES="${DB_NAMES:-bbs_platform bbs_analytics bbs_audit}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BUCKET:-}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$TIMESTAMP"

export PGPASSWORD="$DB_PASS"

mkdir -p "$BACKUP_PATH"
mkdir -p "$BACKUP_DIR"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    find "$BACKUP_DIR" -maxdepth 1 -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \;
    log "Old backup cleanup complete"
}

backup_database() {
    local db_name="$1"
    local backup_file="$BACKUP_PATH/${db_name}.sql.gz"
    local checksum_file="${backup_file}.sha256"

    log "Starting backup of database: $db_name"

    pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$db_name" \
        --format=custom \
        --compress=9 \
        --verbose \
        --no-owner \
        --no-acl \
        --no-password \
        2>"$BACKUP_PATH/${db_name}_dump.log" \
        | gzip > "$backup_file"

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        local file_size=$(du -h "$backup_file" | cut -f1)
        sha256sum "$backup_file" > "$checksum_file"
        log "Backup of $db_name completed: $backup_file ($file_size)"

        # Verify backup integrity
        gunzip -t "$backup_file"
        log "Integrity check passed for $db_name"
    else
        log "ERROR: Backup of $db_name failed!"
        rm -f "$backup_file"
        return 1
    fi
}

upload_to_s3() {
    if [ -z "$S3_BUCKET" ]; then
        log "S3 bucket not configured, skipping cloud upload"
        return 0
    fi

    log "Uploading backups to S3: $S3_BUCKET"
    aws s3 sync "$BACKUP_PATH" "s3://$S3_BUCKET/backups/postgres/$TIMESTAMP/" \
        --storage-class STANDARD_IA \
        --only-show-errors

    if [ $? -eq 0 ]; then
        log "S3 upload completed successfully"
    else
        log "ERROR: S3 upload failed!"
        return 1
    fi
}

generate_report() {
    local report_file="$BACKUP_PATH/backup_report.txt"

    cat > "$report_file" <<- EOF
========================================
Database Backup Report
========================================
Timestamp: $TIMESTAMP
Date: $(date +'%Y-%m-%d %H:%M:%S')
Host: $DB_HOST:$DB_PORT
User: $DB_USER

Databases Backed Up:
$(for f in "$BACKUP_PATH"/*.sql.gz; do
    if [ -f "$f" ]; then
        db=$(basename "$f" .sql.gz)
        size=$(du -h "$f" | cut -f1)
        echo "  - $db ($size)"
    fi
done)

Total Size: $(du -sh "$BACKUP_PATH" | cut -f1)
========================================
EOF

    log "Backup report generated: $report_file"
}

# Main backup process
log "Starting database backup process"
log "Backup directory: $BACKUP_PATH"

for db in $DB_NAMES; do
    if ! backup_database "$db"; then
        log "ERROR: Critical backup failure on $db! Aborting."
        exit 1
    fi
done

generate_report
cleanup_old_backups
upload_to_s3

# Create latest symlink
rm -f "$BACKUP_DIR/latest"
ln -s "$BACKUP_PATH" "$BACKUP_DIR/latest"

log "=== Database backup completed successfully ==="
log "Backup location: $BACKUP_PATH"
echo ""

# Print summary
echo "Backup Summary:"
echo "  Databases: $DB_NAMES"
echo "  Location: $BACKUP_PATH"
echo "  Total Size: $(du -sh "$BACKUP_PATH" | cut -f1)"
echo "  Retention: $RETENTION_DAYS days"
echo ""
