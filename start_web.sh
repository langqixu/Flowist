#!/bin/bash

echo "🎨 Starting Flowist Web Frontend..."
echo ""
echo "Frontend will start at: http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop"
echo "================================"
echo ""

cd "$(dirname "$0")/admin-frontend"
npm run dev
