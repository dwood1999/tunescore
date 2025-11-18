#!/bin/bash
# Restart TuneScore Backend without sudo

echo "Restarting TuneScore Backend (no sudo)..."
echo "=========================================="

cd /home/dwood/tunescore/backend

# Find and kill the backend process
echo "Stopping backend process..."
pkill -f "tunescore-backend.*uvicorn app.main:app --host 127.0.0.1 --port 8001" || true
sleep 3

# Verify it's stopped
if pgrep -f "tunescore-backend.*uvicorn app.main:app --host 127.0.0.1 --port 8001" > /dev/null; then
    echo "⚠️  Backend process still running, forcing kill..."
    pkill -9 -f "tunescore-backend.*uvicorn app.main:app --host 127.0.0.1 --port 8001" || true
    sleep 2
fi

# Load environment
source /home/dwood/tunescore/.env

# Start the backend
echo "Starting backend process..."
cd /home/dwood/tunescore/backend
/home/dwood/.cache/pypoetry/virtualenvs/tunescore-backend-0udhgdCI-py3.12/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001 > /home/dwood/tunescore/logs/backend.log 2>&1 &

sleep 5

# Check if it started
if pgrep -f "tunescore-backend.*uvicorn app.main:app --host 127.0.0.1 --port 8001" > /dev/null; then
    echo "✅ Backend process started"
    ps aux | grep "[u]vicorn app.main:app --host 127.0.0.1 --port 8001"
else
    echo "❌ Backend process failed to start"
    echo "Check logs: tail -20 /home/dwood/tunescore/logs/backend.log"
    exit 1
fi

# Test API
echo ""
echo "Testing API..."
echo "----------------"
sleep 2
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/v1/health)
if [ "$response" = "200" ]; then
    echo "✅ API is responding (HTTP $response)"
else
    echo "❌ API not responding (HTTP $response)"
fi

# Check logs for AI initialization
echo ""
echo "Checking AI initialization in logs..."
echo "--------------------------------------"
tail -30 /home/dwood/tunescore/logs/backend.log | grep -E "(Loaded environment|Section detector|AI|DeepSeek|Anthropic|OpenAI)" || echo "No AI logs found yet"

echo ""
echo "Restart complete!"

