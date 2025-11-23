#!/bin/bash
# TuneScore Docker Logs Script
# View logs from TuneScore Docker containers

SERVICE=${1:-}

if [ -z "$SERVICE" ]; then
    echo "🎵 TuneScore Docker Logs (All Services)"
    echo "========================================"
    echo ""
    docker compose logs -f --tail=100
else
    echo "🎵 TuneScore Docker Logs: $SERVICE"
    echo "========================================"
    echo ""
    docker compose logs -f --tail=100 "$SERVICE"
fi

