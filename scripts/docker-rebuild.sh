#!/bin/bash
# TuneScore Docker Rebuild Script
# Rebuilds and restarts specific or all services

set -e

SERVICE=${1:-}

if [ -z "$SERVICE" ]; then
    echo "🔨 Rebuilding all TuneScore services"
    echo "====================================="
    echo ""
    docker compose down
    docker compose build --no-cache
    docker compose up -d
    echo ""
    echo "✅ All services rebuilt and restarted"
else
    echo "🔨 Rebuilding $SERVICE"
    echo "======================"
    echo ""
    docker compose stop "$SERVICE"
    docker compose build --no-cache "$SERVICE"
    docker compose up -d "$SERVICE"
    echo ""
    echo "✅ $SERVICE rebuilt and restarted"
fi

echo ""
docker compose ps

