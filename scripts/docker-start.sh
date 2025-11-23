#!/bin/bash
# TuneScore Docker Start Script
# Starts all TuneScore services in Docker containers

set -e

echo "🎵 Starting TuneScore (Docker)"
echo "=============================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ No .env file found. Run ./scripts/docker-setup.sh first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker compose down 2>/dev/null || true

# Pull latest base images
echo "📥 Pulling latest base images..."
docker compose pull

# Build containers
echo "🔨 Building containers..."
docker compose build --no-cache

# Start containers
echo "🚀 Starting containers..."
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
docker compose ps

# Run database migrations
echo "🗃️  Running database migrations..."
docker compose exec -T backend alembic upgrade head || echo "⚠️  No migrations to run or migration failed"

echo ""
echo "✅ TuneScore is running!"
echo ""
echo "Services:"
echo "  - Backend API: http://localhost:8001"
echo "  - Frontend: http://localhost:5128"
echo "  - PostgreSQL: localhost:5433"
echo "  - Redis: localhost:6380"
echo ""
echo "View logs: ./scripts/docker-logs.sh"
echo "Stop services: ./scripts/docker-stop.sh"
echo ""

