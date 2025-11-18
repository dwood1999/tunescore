#!/bin/bash
# PostgreSQL restore script for TuneScore
# Restores database from a backup file

set -e

# Configuration
DB_NAME="tunescore"
DB_USER="dwood"
BACKUP_DIR="/home/dwood/tunescore/backups"
LOG_FILE="/home/dwood/tunescore/logs/restore.log"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null || echo "No backups found"
    echo ""
    echo "Available weekly backups:"
    ls -lh "$BACKUP_DIR"/weekly/*.sql.gz 2>/dev/null || echo "No weekly backups found"
    echo ""
    echo "Available monthly backups:"
    ls -lh "$BACKUP_DIR"/monthly/*.sql.gz 2>/dev/null || echo "No monthly backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    log "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

log "Starting restore from backup: $BACKUP_FILE"

# Confirm with user
read -p "This will DROP and recreate the database '$DB_NAME'. Are you sure? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    log "Restore cancelled by user"
    exit 0
fi

# Drop and recreate database
log "Dropping existing database..."
dropdb -U "$DB_USER" --if-exists "$DB_NAME"

log "Creating new database..."
createdb -U "$DB_USER" "$DB_NAME"

# Restore from backup
log "Restoring from backup..."
if gunzip -c "$BACKUP_FILE" | psql -U "$DB_USER" "$DB_NAME" > /dev/null 2>&1; then
    log "Restore completed successfully"
else
    log "ERROR: Restore failed!"
    exit 1
fi

# Run migrations to ensure schema is up to date
log "Running migrations..."
cd /home/dwood/tunescore/backend
if poetry run alembic upgrade head; then
    log "Migrations completed successfully"
else
    log "WARNING: Migrations failed. Database may be in inconsistent state."
fi

log "Restore process completed"

exit 0

