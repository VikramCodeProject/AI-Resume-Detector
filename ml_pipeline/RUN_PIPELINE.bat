@echo off
REM Quick Run Script - Resume Authenticity Detection ML Pipeline
REM This script runs the complete pipeline with one click

echo.
echo ================================================================================
echo   RESUME AUTHENTICITY DETECTION - ONE-CLICK PIPELINE EXECUTION
echo ================================================================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to set up the environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Check if dataset exists, if not generate it
if not exist data\resume_dataset.csv (
    echo [2/4] Dataset not found. Generating sample dataset...
    python generate_sample_dataset.py
    if errorlevel 1 (
        echo ERROR: Failed to generate dataset
        pause
        exit /b 1
    )
) else (
    echo [2/4] Dataset found: data\resume_dataset.csv
)
echo.

REM Run the ML pipeline
echo [3/4] Running ML Pipeline...
echo This will take approximately 2-3 minutes...
echo.
python main.py --dataset ./data/resume_dataset.csv
if errorlevel 1 (
    echo.
    echo ERROR: Pipeline execution failed!
    echo Check the log file for details.
    pause
    exit /b 1
)
echo.

REM Success message
echo ================================================================================
echo   PIPELINE EXECUTION COMPLETED SUCCESSFULLY!
echo ================================================================================
echo.
echo Results have been saved to:
echo   - Models:    ./models/
echo   - Artifacts: ./artifacts/
echo   - Results:   ./results/
echo.
echo To view detailed results in MLflow UI:
echo   1. Run: mlflow ui
echo   2. Open: http://localhost:5000
echo.
echo [4/4] Opening results directory...
start explorer results
echo.

echo Press any key to view MLflow UI (or close to skip)...
pause > nul

echo Starting MLflow UI...
echo Opening http://localhost:5000 in your browser...
start http://localhost:5000
mlflow ui

REM Keep window open
pause
