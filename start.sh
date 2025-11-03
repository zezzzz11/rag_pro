#!/bin/bash

echo "Starting RAG Pro..."

# Start backend in background
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"
deactivate
cd ..

# Start frontend in background
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"
cd ..

# Save PIDs
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "✓ RAG Pro is running!"
echo "  - Backend: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo ""
echo "To stop, run: ./stop.sh"
