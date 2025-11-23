#!/bin/bash
# TuneScore Docker Backup Script
# Creates a backup of the PostgreSQL database

set -e

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/tunescore_backup_$TIMESTAMP.sql.gz"

echo "📦 Creating TuneScore database backup"
echo "======================================"
echo ""

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create backup
echo "Backing up to: $BACKUP_FILE"
docker compose exec -T postgres pg_dump -U tunescore tunescore | gzip > "$BACKUP_FILE"

# Verify backup was created
if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo ""
    echo "✅ Backup created successfully: $BACKUP_FILE ($SIZE)"
    
    # Keep only last 7 backups
    echo "🧹 Cleaning old backups (keeping last 7)..."
    cd "$BACKUP_DIR"
    ls -t tunescore_backup_*.sql.gz | tail -n +8 | xargs -r rm
    cd ..
else
    echo ""
    echo "❌ Backup failed"
    exit 1
fi

