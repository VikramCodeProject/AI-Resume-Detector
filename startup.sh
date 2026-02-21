#!/bin/bash
# Resume Verification System - Linux/macOS Startup Script
# This script starts all services: Backend (FastAPI), Frontend (Vite)

echo "========================================"
echo "Resume Verification System - Startup"
echo "========================================"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python
if ! command_exists python3; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check for Node.js/npm
if ! command_exists npm; then
    echo "Error: Node.js/npm is not installed"
    exit 1
fi

# Check and create virtual environment
if [ ! -d "backend/venv" ]; then
    echo "Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo ""
fi

# Check and install frontend dependencies
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo ""
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file with default values..."
    cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resume_verify
REDIS_URL=redis://localhost:6379

# JWT Configuration
JWT_SECRET=your-secret-key-change-in-production-to-random-string
JWT_ALGORITHM=HS256

# External APIs
GITHUB_API_KEY=your-github-token-here
LINKEDIN_API_KEY=your-linkedin-token-here

# AWS S3
AWS_S3_BUCKET=resume-verify-prod
AWS_REGION=us-east-1

# Blockchain
ETH_RPC_URL=https://polygon-rpc.com
SMART_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000
PRIVATE_KEY=0x0000000000000000000000000000000000000000000000000000000000000000

# Environment
ENVIRONMENT=development
EOF
    echo ".env file created!"
    echo ""
fi

echo "Starting services..."
echo ""

# Start Backend
echo "Starting Backend (FastAPI on port 8000)..."
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ..
sleep 3

# Start Frontend
echo "Starting Frontend (Vite on port 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "Services are starting:"
echo "  - Backend: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - API Docs: http://localhost:8000/api/docs"
echo "========================================"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop services, run: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Wait for user interruption
wait
