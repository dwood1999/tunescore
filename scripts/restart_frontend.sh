#!/bin/bash
# Restart TuneScore Frontend

cd /home/dwood/tunescore/frontend

# Kill any existing vite processes
pkill -f "vite preview" || true
sleep 2

# Rebuild
npm run build

# Start with systemd
sudo systemctl start tunescore-frontend

sleep 5

# Check status
sudo systemctl status tunescore-frontend --no-pager

echo ""
echo "Testing Industry Pulse page..."
curl -s http://localhost:5128/industry-pulse | grep -q "Industry Pulse" && echo "✅ Page loads" || echo "❌ Page not loading"
curl -s http://localhost:5128/api/v1/industry-pulse/news?limit=1 | grep -q "title" && echo "✅ API proxy works" || echo "❌ API proxy not working"

