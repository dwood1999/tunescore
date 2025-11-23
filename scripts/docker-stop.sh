#!/bin/bash
# TuneScore Docker Stop Script
# Stops all TuneScore Docker containers

set -e

echo "🛑 Stopping TuneScore (Docker)"
echo "=============================="
echo ""

docker compose down

echo ""
echo "✅ All TuneScore containers stopped."
echo ""
echo "To start again: ./scripts/docker-start.sh"
echo "To remove volumes: docker compose down -v"
echo ""

