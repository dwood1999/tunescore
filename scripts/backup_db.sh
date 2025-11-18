#!/bin/bash
# PostgreSQL backup script for TuneScore
# Creates compressed backups with rotation (keeps last 7 daily, 4 weekly)

set -e

# Configuration
DB_NAME="tunescore"
DB_USER="dwood"
BACKUP_DIR="/home/dwood/tunescore/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/tunescore_backup_$TIMESTAMP.sql.gz"
LOG_FILE="/home/dwood/tunescore/logs/backup.log"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting backup of database: $DB_NAME"

# Perform backup
if pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "Backup completed successfully: $BACKUP_FILE (Size: $BACKUP_SIZE)"
else
    log "ERROR: Backup failed!"
    exit 1
fi

# Rotation: Keep last 7 daily backups
log "Rotating daily backups (keeping last 7)..."
cd "$BACKUP_DIR"
ls -t tunescore_backup_*.sql.gz | tail -n +8 | xargs -r rm -f
REMAINING=$(ls -1 tunescore_backup_*.sql.gz 2>/dev/null | wc -l)
log "Daily backups remaining: $REMAINING"

# Weekly backup (every Sunday)
if [ "$(date +%u)" -eq 7 ]; then
    WEEKLY_DIR="$BACKUP_DIR/weekly"
    mkdir -p "$WEEKLY_DIR"
    WEEKLY_FILE="$WEEKLY_DIR/tunescore_weekly_$(date +"%Y%m%d").sql.gz"
    
    log "Creating weekly backup: $WEEKLY_FILE"
    cp "$BACKUP_FILE" "$WEEKLY_FILE"
    
    # Keep last 4 weekly backups
    cd "$WEEKLY_DIR"
    ls -t tunescore_weekly_*.sql.gz | tail -n +5 | xargs -r rm -f
    WEEKLY_REMAINING=$(ls -1 tunescore_weekly_*.sql.gz 2>/dev/null | wc -l)
    log "Weekly backups remaining: $WEEKLY_REMAINING"
fi

# Monthly backup (first day of month)
if [ "$(date +%d)" -eq 01 ]; then
    MONTHLY_DIR="$BACKUP_DIR/monthly"
    mkdir -p "$MONTHLY_DIR"
    MONTHLY_FILE="$MONTHLY_DIR/tunescore_monthly_$(date +"%Y%m").sql.gz"
    
    log "Creating monthly backup: $MONTHLY_FILE"
    cp "$BACKUP_FILE" "$MONTHLY_FILE"
    
    # Keep last 12 monthly backups
    cd "$MONTHLY_DIR"
    ls -t tunescore_monthly_*.sql.gz | tail -n +13 | xargs -r rm -f
    MONTHLY_REMAINING=$(ls -1 tunescore_monthly_*.sql.gz 2>/dev/null | wc -l)
    log "Monthly backups remaining: $MONTHLY_REMAINING"
fi

# Display disk usage
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "Total backup directory size: $TOTAL_SIZE"

log "Backup process completed successfully"

exit 0

