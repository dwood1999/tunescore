#!/bin/bash
# Database migration script for TuneScore
# Runs Alembic migrations

set -e

cd "$(dirname "$0")/../backend"

LOG_FILE="../logs/migration.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if we're in the backend directory
if [ ! -f "alembic.ini" ]; then
    echo "Error: alembic.ini not found. Are you in the backend directory?"
    exit 1
fi

# Parse command line arguments
COMMAND="${1:-upgrade}"
TARGET="${2:-head}"

case "$COMMAND" in
    upgrade)
        log "Running database migrations (upgrade to $TARGET)..."
        if poetry run alembic upgrade "$TARGET"; then
            log "✓ Migrations completed successfully"
        else
            log "✗ Migration failed!"
            exit 1
        fi
        ;;
    
    downgrade)
        log "Downgrading database migrations (downgrade to $TARGET)..."
        read -p "Are you sure you want to downgrade? (yes/no): " CONFIRM
        if [ "$CONFIRM" = "yes" ]; then
            if poetry run alembic downgrade "$TARGET"; then
                log "✓ Downgrade completed successfully"
            else
                log "✗ Downgrade failed!"
                exit 1
            fi
        else
            log "Downgrade cancelled"
        fi
        ;;
    
    current)
        log "Checking current migration version..."
        poetry run alembic current
        ;;
    
    history)
        log "Showing migration history..."
        poetry run alembic history
        ;;
    
    heads)
        log "Showing migration heads..."
        poetry run alembic heads
        ;;
    
    revision)
        MESSAGE="${2:-auto_generated}"
        log "Creating new migration: $MESSAGE"
        if poetry run alembic revision --autogenerate -m "$MESSAGE"; then
            log "✓ Migration created successfully"
            log "⚠ Please review the generated migration file before applying!"
        else
            log "✗ Migration creation failed!"
            exit 1
        fi
        ;;
    
    *)
        echo "Usage: $0 {upgrade|downgrade|current|history|heads|revision} [target|message]"
        echo ""
        echo "Commands:"
        echo "  upgrade [target]     - Upgrade to target revision (default: head)"
        echo "  downgrade [target]   - Downgrade to target revision (default: -1)"
        echo "  current              - Show current revision"
        echo "  history              - Show migration history"
        echo "  heads                - Show current heads"
        echo "  revision [message]   - Create new migration with autogenerate"
        echo ""
        echo "Examples:"
        echo "  $0 upgrade           - Upgrade to latest"
        echo "  $0 downgrade -1      - Downgrade one revision"
        echo "  $0 revision 'add user email field'"
        exit 1
        ;;
esac

exit 0

