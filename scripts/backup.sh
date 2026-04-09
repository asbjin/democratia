#!/usr/bin/env bash
set -euo pipefail

# PostgreSQL backup script for DemocratIA
# Usage: ./scripts/backup.sh
# Creates a timestamped compressed backup and removes backups older than 7 days

BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS=7

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${POSTGRES_USER:-democratia}"
DB_NAME="${POSTGRES_DB:-democratia}"

TIMESTAMP=$(date "+%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/democratia_${TIMESTAMP}.sql.gz"

timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

log() {
    echo "[$(timestamp)] $1"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

log "=== DemocratIA PostgreSQL Backup ==="
log "Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
log "Target: $BACKUP_FILE"

# Perform backup
if command -v docker &>/dev/null && docker compose ps db --status running 2>/dev/null | grep -q running; then
    # Backup via Docker container
    log "Using Docker pg_dump..."
    docker compose exec -T db pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"
elif command -v pg_dump &>/dev/null; then
    # Backup via local pg_dump
    log "Using local pg_dump..."
    PGPASSWORD="${POSTGRES_PASSWORD:-democratia_secret}" pg_dump \
        -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"
else
    log "ERROR: Neither Docker nor pg_dump available"
    exit 1
fi

# Verify backup
if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "Backup created: $BACKUP_FILE ($SIZE)"
else
    log "ERROR: Backup file not created"
    exit 1
fi

# Remove old backups
log "Cleaning backups older than ${RETENTION_DAYS} days..."
DELETED=$(find "$BACKUP_DIR" -name "democratia_*.sql.gz" -mtime +${RETENTION_DAYS} -delete -print | wc -l)
log "Deleted $DELETED old backup(s)"

# List current backups
log "Current backups:"
ls -lh "$BACKUP_DIR"/democratia_*.sql.gz 2>/dev/null | while read -r line; do
    log "  $line"
done

log "=== Backup complete ==="
