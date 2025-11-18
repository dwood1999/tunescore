#!/bin/bash
# Stop all TuneScore development servers

echo "Stopping TuneScore development servers..."

# Kill backend
if pkill -f "uvicorn.*8001"; then
    echo "✅ Backend stopped"
else
    echo "⚠️  Backend was not running"
fi

# Kill frontend
if pkill -f "vite.*5128"; then
    echo "✅ Frontend stopped"
else
    echo "⚠️  Frontend was not running"
fi

echo ""
echo "All development servers stopped."

