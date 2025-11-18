#!/bin/bash
# Restart TuneScore Backend

echo "Restarting TuneScore Backend..."
echo "================================="

cd /home/dwood/tunescore/backend

# Stop the backend service with sudo
echo "Stopping backend service..."
sudo systemctl stop tunescore-backend.service

sleep 2

# Start the backend service with sudo
echo "Starting backend service..."
sudo systemctl start tunescore-backend.service

sleep 5

# Check status
echo ""
echo "Service Status:"
echo "----------------"
sudo systemctl status tunescore-backend.service --no-pager -l | head -20

# Test API
echo ""
echo "Testing API..."
echo "----------------"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/v1/health)
if [ "$response" = "200" ]; then
    echo "✅ API is responding (HTTP $response)"
else
    echo "❌ API not responding (HTTP $response)"
fi

# Check AI capabilities
echo ""
echo "Checking AI capabilities..."
echo "----------------------------"
sudo journalctl -u tunescore-backend.service --since "30 seconds ago" | grep -E "(Section detector|AI|DeepSeek|Anthropic|OpenAI)" | tail -5 || echo "No AI initialization logs found"

echo ""
echo "Restart complete!"

