#!/usr/bin/env bash
set -euo pipefail

# Health monitoring script for DemocratIA services
# Usage: ./scripts/monitor.sh
# Checks all Docker services and logs results with timestamps

LOG_FILE="${LOG_FILE:-/tmp/democratia-monitor.log}"

SERVICES=(
    "backend|http://localhost:8000/api/health|Backend API"
    "frontend|http://localhost:3000|Frontend"
    "nginx|http://localhost:80|Nginx Proxy"
)

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${POSTGRES_USER:-democratia}"
DB_NAME="${POSTGRES_DB:-democratia}"

timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

log() {
    local msg="[$(timestamp)] $1"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

check_http() {
    local name="$1"
    local url="$2"
    local label="$3"

    local status
    status=$(curl -sf -o /dev/null -w "%{http_code}" --connect-timeout 5 "$url" 2>/dev/null || echo "000")

    if [ "$status" = "200" ]; then
        log "OK   $label ($name) - HTTP $status"
        return 0
    else
        log "FAIL $label ($name) - HTTP $status"
        return 1
    fi
}

check_postgres() {
    if command -v pg_isready &>/dev/null; then
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -q 2>/dev/null; then
            log "OK   PostgreSQL - accepting connections"
            return 0
        else
            log "FAIL PostgreSQL - not responding"
            return 1
        fi
    else
        # Fallback: check if port is open
        if nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
            log "OK   PostgreSQL - port $DB_PORT open"
            return 0
        else
            log "FAIL PostgreSQL - port $DB_PORT closed"
            return 1
        fi
    fi
}

check_docker_containers() {
    if ! command -v docker &>/dev/null; then
        log "WARN Docker not available - skipping container checks"
        return 0
    fi

    local containers
    containers=$(docker compose ps --format json 2>/dev/null || echo "")

    if [ -z "$containers" ]; then
        log "WARN No Docker Compose containers found"
        return 0
    fi

    docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null | while read -r line; do
        log "     $line"
    done
}

main() {
    log "========================================="
    log "DemocratIA Health Check"
    log "========================================="

    local total=0
    local passed=0
    local failed=0

    # Check HTTP services
    for service_entry in "${SERVICES[@]}"; do
        IFS='|' read -r name url label <<< "$service_entry"
        total=$((total + 1))
        if check_http "$name" "$url" "$label"; then
            passed=$((passed + 1))
        else
            failed=$((failed + 1))
        fi
    done

    # Check PostgreSQL
    total=$((total + 1))
    if check_postgres; then
        passed=$((passed + 1))
    else
        failed=$((failed + 1))
    fi

    # Docker container status
    log "-----------------------------------------"
    log "Docker containers:"
    check_docker_containers

    # Summary
    log "-----------------------------------------"
    log "Summary: $passed/$total services healthy ($failed failed)"
    log "========================================="

    if [ "$failed" -gt 0 ]; then
        exit 1
    fi
}

main "$@"
