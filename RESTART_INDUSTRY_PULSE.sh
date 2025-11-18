#!/bin/bash
# Quick script to restart Industry Pulse services
# Run with: sudo bash RESTART_INDUSTRY_PULSE.sh

echo "🔄 Restarting Industry Pulse Services..."
echo ""

# Stop services
echo "Stopping frontend..."
systemctl stop tunescore-frontend
pkill -f "vite preview" 2>/dev/null || true
sleep 2

# Start services
echo "Starting frontend..."
systemctl start tunescore-frontend
sleep 8

# Check status
echo ""
echo "📊 Service Status:"
systemctl status tunescore-frontend --no-pager | head -15

echo ""
echo "🧪 Testing..."

# Test backend
echo -n "Backend API: "
curl -s http://localhost:8001/api/v1/industry-pulse/news?limit=1 | grep -q "title" && echo "✅ Working" || echo "❌ Not responding"

# Test frontend
echo -n "Frontend page: "
curl -s http://localhost:5128/industry-pulse | grep -q "Industry Pulse" && echo "✅ Loading" || echo "❌ Not loading"

# Test news display
echo -n "News articles: "
NEWS_COUNT=$(curl -s http://localhost:5128/industry-pulse | grep -o "Taylor Swift" | wc -l)
if [ "$NEWS_COUNT" -gt 0 ]; then
    echo "✅ Displaying ($NEWS_COUNT mentions)"
else
    echo "⏳ Check in browser at http://localhost:5128/industry-pulse"
fi

echo ""
echo "✅ Done! Visit: http://localhost:5128/industry-pulse"

