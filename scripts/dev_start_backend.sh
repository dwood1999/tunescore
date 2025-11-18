#!/bin/bash
# Start TuneScore backend in development mode

cd "$(dirname "$0")/../backend"

# Activate Poetry environment
source $(poetry env info --path)/bin/activate

# Start Uvicorn with auto-reload
echo "Starting TuneScore backend on http://127.0.0.1:8002"
echo "API docs: http://127.0.0.1:8002/api/v1/docs"
echo "Press Ctrl+C to stop"
echo ""

poetry run uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8002 \
    --reload \
    --reload-dir app

