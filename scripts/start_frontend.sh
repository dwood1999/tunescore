#!/bin/bash
# Start the SvelteKit frontend

cd "$(dirname "$0")/../frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start Vite dev server
# --host 0.0.0.0 makes it accessible from outside
# --port 5128 specifies the port
npm run dev -- --host 0.0.0.0 --port 5128

