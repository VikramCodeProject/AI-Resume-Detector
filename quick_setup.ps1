# Quick Setup Script for Enterprise Features
# PowerShell version

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  Enterprise Verification Setup" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Step 1: Install dependencies
Write-Host "Step 1: Installing dependencies..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Download spaCy model
Write-Host "`nStep 2: Downloading spaCy model..." -ForegroundColor Yellow
python -m spacy download en_core_web_sm

if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: spaCy model download failed - some features may be limited" -ForegroundColor Yellow
}

# Step 3: Run tests
Write-Host "`nStep 3: Running service tests..." -ForegroundColor Yellow
python test_services.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nWARNING: Some tests failed - review output above" -ForegroundColor Yellow
}

# Success message
Write-Host "`n============================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Green

Write-Host "To start the backend, run:" -ForegroundColor Cyan
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  uvicorn main:app --reload --port 8000`n" -ForegroundColor White

Write-Host "Then visit: " -NoNewline -ForegroundColor Cyan
Write-Host "http://localhost:8000/api/docs`n" -ForegroundColor Green

Read-Host "Press Enter to exit"
