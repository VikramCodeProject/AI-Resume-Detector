@echo off
REM Quick setup and test script for Windows
echo ============================================
echo Enterprise Verification Setup
echo ============================================
echo.

echo Step 1: Installing dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Downloading spaCy model...
python -m spacy download en_core_web_sm
if %errorlevel% neq 0 (
    echo WARNING: spaCy model download failed - some features may be limited
)

echo.
echo Step 3: Running service tests...
python test_services.py
if %errorlevel% neq 0 (
    echo WARNING: Some tests failed - review output above
)

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo To start the backend, run:
echo   cd backend
echo   uvicorn main:app --reload --port 8000
echo.
echo Then visit: http://localhost:8000/api/docs
echo.
pause
