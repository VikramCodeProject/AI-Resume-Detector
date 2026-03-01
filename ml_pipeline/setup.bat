@echo off
REM Resume Authenticity Detection - Automated Setup Script for Windows
REM This script sets up the complete ML pipeline environment

echo ================================================================================
echo RESUME AUTHENTICITY DETECTION - AUTOMATED SETUP
echo ================================================================================
echo.

REM Check Python installation
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo.

REM Create virtual environment
echo [2/6] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo Virtual environment created successfully
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo [5/6] Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Download NLTK data
echo [6/6] Downloading NLTK data...
python -c "import nltk; nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('punkt', quiet=True); nltk.download('omw-1.4', quiet=True); print('NLTK data downloaded')"
echo.

REM Download spaCy model
echo [7/7] Downloading spaCy model...
python -m spacy download en_core_web_sm
echo.

REM Create necessary directories
echo Creating project directories...
if not exist data mkdir data
if not exist models mkdir models
if not exist artifacts mkdir artifacts
if not exist results mkdir results
echo Directories created
echo.

echo ================================================================================
echo SETUP COMPLETED SUCCESSFULLY!
echo ================================================================================
echo.
echo Next steps:
echo   1. Generate sample dataset:
echo      python generate_sample_dataset.py
echo.
echo   2. Run the ML pipeline:
echo      python main.py --dataset ./data/resume_dataset.csv
echo.
echo   3. View results in MLflow UI:
echo      mlflow ui
echo      Then open http://localhost:5000 in your browser
echo.
echo For more information, see README.md or QUICKSTART.md
echo ================================================================================
echo.

pause
