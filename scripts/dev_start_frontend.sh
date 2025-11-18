#!/bin/bash
# Start TuneScore frontend in development mode

cd "$(dirname "$0")/../frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start Vite dev server
echo "Starting TuneScore frontend on http://localhost:5128"
echo "Press Ctrl+C to stop"
echo ""

npm run dev

