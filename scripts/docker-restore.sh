#!/bin/bash
# TuneScore Docker Restore Script
# Restores a PostgreSQL database backup

set -e

BACKUP_FILE=${1:-}

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ No backup file specified"
    echo ""
    echo "Usage: $0 <backup_file>"
    echo ""
    echo "Available backups:"
    ls -lh backups/tunescore_backup_*.sql.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will replace the current database!"
echo "Backup file: $BACKUP_FILE"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Restore cancelled"
    exit 0
fi

echo ""
echo "📦 Restoring TuneScore database"
echo "================================"
echo ""

# Stop backend to prevent connections
echo "🛑 Stopping backend..."
docker compose stop backend

# Drop and recreate database
echo "🗑️  Dropping existing database..."
docker compose exec -T postgres psql -U tunescore -d postgres -c "DROP DATABASE IF EXISTS tunescore;"
docker compose exec -T postgres psql -U tunescore -d postgres -c "CREATE DATABASE tunescore;"

# Restore backup
echo "📥 Restoring backup..."
gunzip -c "$BACKUP_FILE" | docker compose exec -T postgres psql -U tunescore -d tunescore

# Restart backend
echo "🚀 Starting backend..."
docker compose start backend

echo ""
echo "✅ Database restored successfully"

