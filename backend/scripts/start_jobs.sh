#!/bin/bash
# Start TuneScore background jobs with APScheduler

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

cd "$BACKEND_DIR"

# Activate virtual environment
source venv/bin/activate

# Load environment variables
export $(cat ../.env | grep -v '^#' | xargs)

# Start scheduler
echo "Starting TuneScore job scheduler..."
python3 jobs/scheduler.py

