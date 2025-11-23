#!/bin/bash
# TuneScore Docker Shell Script
# Opens a shell in a running container

SERVICE=${1:-backend}

echo "🎵 Opening shell in $SERVICE container"
echo "======================================="
echo ""

if [ "$SERVICE" = "backend" ]; then
    docker compose exec backend /bin/bash
elif [ "$SERVICE" = "frontend" ]; then
    docker compose exec frontend /bin/sh
elif [ "$SERVICE" = "postgres" ]; then
    docker compose exec postgres psql -U tunescore -d tunescore
else
    docker compose exec "$SERVICE" /bin/sh
fi

