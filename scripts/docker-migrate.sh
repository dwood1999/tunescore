#!/bin/bash
# TuneScore Docker Migration Script
# Runs database migrations in the backend container

set -e

echo "🗃️  Running database migrations"
echo "==============================="
echo ""

# Check if backend container is running
if ! docker compose ps backend | grep -q "Up"; then
    echo "❌ Backend container is not running. Start it with: ./scripts/docker-start.sh"
    exit 1
fi

# Run migrations
docker compose exec backend alembic upgrade head

echo ""
echo "✅ Migrations complete"

