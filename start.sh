#!/bin/bash

echo "🚀 Starting AI Agent UI Service..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js not found, please install Node.js first"
    exit 1
fi


# Enter frontend directory
cd frontend

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 First run, installing frontend dependencies..."
    npm install
fi

echo "🎨 Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 2

# Return to project root directory
cd ..
cd backend

echo "🤖 Starting backend service..."
uv run agent_service.py &
BACKEND_PID=$!

echo ""
echo "✅ Services started!"
echo ""
echo "Frontend address: http://localhost:3000"
echo "Backend address: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop services"

# Catch exit signal, cleanup processes
trap "echo ''; echo '🛑 Stopping services...'; kill $FRONTEND_PID $BACKEND_PID; exit" INT TERM

# Wait for processes
wait

