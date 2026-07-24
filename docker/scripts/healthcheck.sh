#!/bin/bash
set -e

echo "=== Behavioral Biometric System Health Check ==="
echo ""

TIMESTAMP=$(date +'%Y-%m-%d %H:%M:%S')
COMPOSE_PROJECT="${COMPOSE_PROJECT:-bbs}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"
PAGERDUTY_KEY="${PAGERDUTY_KEY:-}"
CHECK_TIMEOUT="${CHECK_TIMEOUT:-10}"
LOG_FILE="${LOG_FILE:-/var/log/bbs-healthcheck.log}"
REPORT_FILE="${REPORT_FILE:-/tmp/bbs-health-report.json}"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

send_slack_notification() {
    if [ -z "$SLACK_WEBHOOK" ]; then
        return 0
    fi

    local status="$1"
    local message="$2"

    curl -s -X POST -H "Content-Type: application/json" \
        -d "{\"text\": \"*Health Check: $status*\\n$message\\nTimestamp: $TIMESTAMP\"}" \
        "$SLACK_WEBHOOK" > /dev/null 2>&1 || true
}

send_pagerduty_alert() {
    if [ -z "$PAGERDUTY_KEY" ]; then
        return 0
    fi

    local summary="$1"
    local severity="$2"

    curl -s -X POST -H "Content-Type: application/json" \
        -d "{
            \"routing_key\": \"$PAGERDUTY_KEY\",
            \"event_action\": \"trigger\",
            \"dedup_key\": \"healthcheck-$TIMESTAMP\",
            \"payload\": {
                \"summary\": \"$summary\",
                \"source\": \"healthcheck.sh\",
                \"severity\": \"$severity\",
                \"timestamp\": \"$TIMESTAMP\"
            }
        }" \
        "https://events.pagerduty.com/v2/enqueue" > /dev/null 2>&1 || true
}

check_http_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"

    log "  Checking $name... ($url)"

    local start_time=$(date +%s%N)
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$CHECK_TIMEOUT" "$url" 2>/dev/null || echo "000")
    local end_time=$(date +%s%N)
    local duration_ms=$(( (end_time - start_time) / 1000000 ))

    if [ "$http_status" = "$expected_status" ]; then
        log "  ✓ $name: UP (HTTP $http_status, ${duration_ms}ms)"
        return 0
    else
        log "  ✗ $name: DOWN (HTTP $http_status, expected $expected_status, ${duration_ms}ms)"
        return 1
    fi
}

check_postgres() {
    local host="${POSTGRES_HOST:-postgres}"
    local port="${POSTGRES_PORT:-5432}"
    local user="${POSTGRES_USER:-bbs_user}"
    local db="${POSTGRES_DB:-bbs_platform}"

    log "  Checking PostgreSQL... ($host:$port)"

    if PGPASSWORD="${POSTGRES_PASSWORD:-bbs_secure_password}" pg_isready -h "$host" -p "$port" -U "$user" -d "$db" -t "$CHECK_TIMEOUT" > /dev/null 2>&1; then
        log "  ✓ PostgreSQL: UP"

        # Check connection count
        local conn_count=$(PGPASSWORD="${POSTGRES_PASSWORD:-bbs_secure_password}" psql -h "$host" -p "$port" -U "$user" -d "$db" -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | tr -d ' ')
        log "  Active connections: $conn_count"
        return 0
    else
        log "  ✗ PostgreSQL: DOWN"
        return 1
    fi
}

check_redis() {
    local host="${REDIS_HOST:-redis}"
    local port="${REDIS_PORT:-6379}"
    local password="${REDIS_PASSWORD:-bbs_redis_pass}"

    log "  Checking Redis... ($host:$port)"

    if redis-cli -h "$host" -p "$port" -a "$password" --no-auth-warning ping 2>/dev/null | grep -q "PONG"; then
        log "  ✓ Redis: UP"

        local memory=$(redis-cli -h "$host" -p "$port" -a "$password" --no-auth-warning info memory 2>/dev/null | grep "used_memory_human" | cut -d: -f2)
        log "  Memory usage: $memory"
        return 0
    else
        log "  ✗ Redis: DOWN"
        return 1
    fi
}

check_docker_container() {
    local container="$1"

    log "  Checking container: $container"

    local status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "not_found")
    local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no_healthcheck")

    if [ "$status" = "running" ]; then
        if [ "$health" = "healthy" ] || [ "$health" = "no_healthcheck" ]; then
            log "  ✓ Container $container: $status (health: $health)"
            return 0
        else
            log "  ⚠ Container $container: $status (health: $health)"
            return 1
        fi
    else
        log "  ✗ Container $container: $status"
        return 1
    fi
}

check_disk_space() {
    local path="${1:-/}"
    local threshold="${2:-90}"

    local usage=$(df -h "$path" | awk 'NR==2 {print $5}' | sed 's/%//')

    if [ "$usage" -lt "$threshold" ]; then
        log "  ✓ Disk $path: ${usage}% used (threshold: ${threshold}%)"
        return 0
    else
        log "  ✗ Disk $path: ${usage}% used (threshold: ${threshold}%)"
        return 1
    fi
}

check_cpu_load() {
    local threshold="${1:-80}"

    local load=$(awk '{u=$2+$4; i=$5; print u/(u+i)*100}' <(cat /proc/stat | head -1))
    local load_int=${load%.*}

    if [ "$load_int" -lt "$threshold" ]; then
        log "  ✓ CPU Load: ${load}%"
        return 0
    else
        log "  ✗ CPU Load: ${load}% (threshold: ${threshold}%)"
        return 1
    fi
}

check_memory() {
    local threshold="${1:-90}"

    local total=$(free -m | awk '/Mem:/ {print $2}')
    local used=$(free -m | awk '/Mem:/ {print $3}')
    local usage=$(( (used * 100) / total ))

    if [ "$usage" -lt "$threshold" ]; then
        log "  ✓ Memory: ${used}MB/${total}MB (${usage}%)"
        return 0
    else
        log "  ✗ Memory: ${used}MB/${total}MB (${usage}%) (threshold: ${threshold}%)"
        return 1
    fi
}

# =========================================
# Main health check execution
# =========================================

OVERALL_STATUS="PASS"
FAILURES=0
WARNINGS=0
RESULTS=""

log "Starting health check..."
log ""

# Section: Container Status
log "--- Container Health ---"
for container in "bbs-postgres" "bbs-redis" "bbs-backend" "bbs-celery-worker" "bbs-celery-beat" "bbs-frontend" "bbs-security-dashboard" "bbs-ml-service" "bbs-nginx" "bbs-prometheus" "bbs-grafana"; do
    if ! check_docker_container "$container"; then
        FAILURES=$((FAILURES + 1))
        RESULTS="$RESULTS\n  ✗ $container: DOWN"
    else
        RESULTS="$RESULTS\n  ✓ $container: UP"
    fi
done

log ""
log "--- Service Endpoints ---"

if ! check_http_endpoint "Backend API" "http://backend:8000/api/v1/health"; then
    FAILURES=$((FAILURES + 1))
fi

if ! check_http_endpoint "Frontend" "http://frontend:3000/api/health"; then
    FAILURES=$((FAILURES + 1))
fi

if ! check_http_endpoint "Security Dashboard" "http://security-dashboard:3001/api/health"; then
    FAILURES=$((FAILURES + 1))
fi

if ! check_http_endpoint "ML Service" "http://ml-service:8001/health"; then
    FAILURES=$((FAILURES + 1))
fi

log ""
log "--- Database Health ---"
check_postgres || FAILURES=$((FAILURES + 1))
check_redis || FAILURES=$((FAILURES + 1))

log ""
log "--- System Resources ---"
check_disk_space "/" 90 || WARNINGS=$((WARNINGS + 1))
check_cpu_load 80 || WARNINGS=$((WARNINGS + 1))
check_memory 90 || WARNINGS=$((WARNINGS + 1))

# Generate report
cat > "$REPORT_FILE" <<- EOF
{
    "timestamp": "$TIMESTAMP",
    "status": "$OVERALL_STATUS",
    "failures": $FAILURES,
    "warnings": $WARNINGS,
    "results": "$RESULTS"
}
EOF

log ""
log "=== Health Check Complete ==="
log "Failures: $FAILURES"
log "Warnings: $WARNINGS"
log "Report: $REPORT_FILE"
echo ""

if [ "$FAILURES" -gt 0 ]; then
    OVERALL_STATUS="FAIL"
    log "OVERALL STATUS: FAIL ($FAILURES failures)"
    send_slack_notification "FAIL" "Health check failed with $FAILURES failures and $WARNINGS warnings"
    send_pagerduty_alert "BBS Health Check Failed: $FAILURES failures" "critical"
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    OVERALL_STATUS="WARNING"
    log "OVERALL STATUS: WARNING ($WARNINGS warnings)"
    send_slack_notification "WARNING" "Health check passed with $WARNINGS warnings"
    exit 0
else
    OVERALL_STATUS="PASS"
    log "OVERALL STATUS: PASS"
    exit 0
fi
