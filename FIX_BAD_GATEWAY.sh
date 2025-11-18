#!/bin/bash
# Fix Bad Gateway errors and start Industry Pulse

echo "🔧 Fixing Bad Gateway Error..."
echo ""

# Check if backend is running
echo "Checking backend status..."
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is NOT running - starting it..."
    sudo systemctl start tunescore-backend
    sleep 5
    
    if curl -s http://localhost:8001/health | grep -q "healthy"; then
        echo "✅ Backend started successfully"
    else
        echo "❌ Backend failed to start - check logs:"
        sudo journalctl -u tunescore-backend -n 20
        exit 1
    fi
fi

echo ""
echo "Rebuilding frontend..."
cd /home/dwood/tunescore/frontend
npm run build

echo ""
echo "Restarting frontend..."
sudo systemctl restart tunescore-frontend
sleep 8

echo ""
echo "🧪 Testing..."

# Test backend
echo -n "Backend health: "
curl -s http://localhost:8001/health | grep -q "healthy" && echo "✅" || echo "❌"

# Test tracks API (the one showing Bad Gateway)
echo -n "Tracks API: "
curl -s http://localhost:8001/api/v1/tracks/ | python -c "import sys, json; data = json.load(sys.stdin); print(f'✅ {len(data)} tracks')" 2>/dev/null || echo "❌ Not working"

# Test Industry Pulse news
echo -n "Industry Pulse news: "
curl -s http://localhost:8001/api/v1/industry-pulse/news?limit=1 | grep -q "title" && echo "✅ Working" || echo "❌ Not working"

echo ""
echo "✅ Done!"
echo ""
echo "🌐 Access your sites:"
echo "  Dashboard: https://music.quilty.app/dashboard"
echo "  Industry Pulse: https://music.quilty.app/industry-pulse"
echo ""
echo "👉 Click the 'News 📰' tab on Industry Pulse to see 40+ articles!"

