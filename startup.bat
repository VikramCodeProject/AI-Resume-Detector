@echo off
REM Resume Verification System - Windows Startup Script
REM This script starts all services: Backend (FastAPI), Frontend (Vite), and supporting services

setlocal enabledelayedexpansion

echo ========================================
echo Resume Verification System - Startup
echo ========================================
echo.

REM Check if node_modules and venv exist
if not exist "frontend\node_modules\" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
    echo.
)

if not exist "backend\venv\" (
    echo Creating Python virtual environment...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..
    echo.
)

REM Check for .env file
if not exist ".env" (
    echo Creating .env file with default values...
    (
        echo # Database Configuration
        echo DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resume_verify
        echo REDIS_URL=redis://localhost:6379
        echo.
        echo # JWT Configuration
        echo JWT_SECRET=your-secret-key-change-in-production-to-random-string
        echo JWT_ALGORITHM=HS256
        echo.
        echo # External APIs
        echo GITHUB_API_KEY=your-github-token-here
        echo LINKEDIN_API_KEY=your-linkedin-token-here
        echo.
        echo # AWS S3
        echo AWS_S3_BUCKET=resume-verify-prod
        echo AWS_REGION=us-east-1
        echo.
        echo # Blockchain
        echo ETH_RPC_URL=https://polygon-rpc.com
        echo SMART_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000
        echo PRIVATE_KEY=0x0000000000000000000000000000000000000000000000000000000000000000
        echo.
        echo # Environment
        echo ENVIRONMENT=development
    ) > .env
    echo .env file created!
    echo.
)

echo Starting services...
echo.

REM Start Backend
echo Starting Backend (FastAPI on port 8000)...
cd backend
call venv\Scripts\activate.bat
start "Resume Verify - Backend" cmd /k "uvicorn main:app --reload --host 127.0.0.1 --port 8000"
cd ..
timeout /t 3 >nul

REM Start Frontend
echo Starting Frontend (Vite on port 3000)...
cd frontend
start "Resume Verify - Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo Services are starting:
echo  - Backend: http://localhost:8000
echo  - Frontend: http://localhost:3000
echo  - API Docs: http://localhost:8000/api/docs
echo ========================================
echo.
echo Press any key to view more instructions...
pause

echo.
echo Additional Services (Optional):
echo To start additional services, run these commands in new terminals:
echo.
echo For PostgreSQL (requires Docker):
echo   docker run --name resume-verify-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=resume_verify -p 5432:5432 postgres:15-alpine
echo.
echo For Redis (requires Docker):
echo   docker run --name resume-verify-redis -p 6379:6379 redis:7-alpine
echo.
echo For Celery Worker:
echo   cd backend ^& celery -A tasks worker --loglevel=info
echo.

pause
