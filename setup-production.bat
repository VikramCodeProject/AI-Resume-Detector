@echo off
REM Production Deployment Setup Script for Windows
REM Run this script to prepare your project for production deployment

echo ============================================
echo Resume Verification System
echo Production Deployment Setup
echo ============================================
echo.

REM Check if .env exists
if exist .env (
    echo [WARNING] .env file already exists
    set /p REPLY="Do you want to create a new production .env? (y/N): "
    if /i not "%REPLY%"=="y" (
        echo Keeping existing .env file
    ) else (
        copy /Y .env.production .env
        echo [OK] Created new .env from production template
    )
) else (
    copy /Y .env.production .env
    echo [OK] Created .env from production template
)

echo.
echo ============================================
echo Generating Secure Secrets
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Generating JWT secret...
    for /f "delims=" %%i in ('python -c "import secrets; print(secrets.token_hex(32))"') do set JWT_SECRET=%%i
    echo [OK] Generated JWT_SECRET: %JWT_SECRET:~0,16%...
    
    echo Generating SECRET_KEY...
    for /f "delims=" %%i in ('python -c "import secrets; print(secrets.token_hex(32))"') do set SECRET_KEY=%%i
    echo [OK] Generated SECRET_KEY: %SECRET_KEY:~0,16%...
    
    REM Update .env file with PowerShell
    powershell -Command "(Get-Content .env) -replace 'JWT_SECRET=.*', 'JWT_SECRET=%JWT_SECRET%' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'SECRET_KEY=.*', 'SECRET_KEY=%SECRET_KEY%' | Set-Content .env"
    
    echo [OK] Updated .env with secure secrets
) else (
    echo [ERROR] Python not found. Please manually generate secrets:
    echo   python -c "import secrets; print(secrets.token_hex(32))"
)

echo.
echo ============================================
echo Checklist - Manual Steps Required
echo ============================================
echo.
echo You still need to configure these in .env:
echo.
echo   1. DATABASE_URL - Your production database connection
echo   2. REDIS_URL - Your production Redis instance
echo   3. GITHUB_API_KEY - Get from: https://github.com/settings/tokens
echo   4. AWS_ACCESS_KEY_ID - Your AWS credentials
echo   5. AWS_SECRET_ACCESS_KEY - Your AWS secret
echo   6. AWS_S3_BUCKET - Your S3 bucket name
echo   7. ETH_RPC_URL - Blockchain RPC endpoint (Alchemy/Infura)
echo   8. SMART_CONTRACT_ADDRESS - Your deployed contract address
echo   9. PRIVATE_KEY - Blockchain wallet private key
echo   10. ALLOWED_ORIGINS - Your production domain(s)
echo.
echo Edit with: notepad .env
echo.

echo ============================================
echo Docker Images
echo ============================================
echo.
set /p REPLY="Build Docker images now? (y/N): "
if /i "%REPLY%"=="y" (
    echo Building images...
    docker-compose -f docker-compose.production.yml build
    if %errorlevel% equ 0 (
        echo [OK] Docker images built successfully
    ) else (
        echo [ERROR] Failed to build Docker images
    )
) else (
    echo Skipped. Build later with:
    echo   docker-compose -f docker-compose.production.yml build
)

echo.
echo ============================================
echo SSL/TLS Certificates
echo ============================================
echo.
echo For HTTPS, you need SSL certificates. Options:
echo.
echo   1. Let's Encrypt (Free, recommended):
echo      Use Certbot on your Linux server
echo.
echo   2. CloudFlare (Free, with CDN):
echo      Use CloudFlare as reverse proxy
echo.
echo   3. Purchase certificate:
echo      From SSL vendors (DigiCert, Comodo, etc.)
echo.

echo ============================================
echo Deployment Commands
echo ============================================
echo.
echo To deploy with Docker Compose:
echo   docker-compose -f docker-compose.production.yml up -d
echo.
echo To check status:
echo   docker-compose -f docker-compose.production.yml ps
echo.
echo To view logs:
echo   docker-compose -f docker-compose.production.yml logs -f
echo.
echo To stop:
echo   docker-compose -f docker-compose.production.yml down
echo.

echo ============================================
echo Next Steps
echo ============================================
echo.
echo 1. Edit .env with your production values
echo 2. Set up managed database (AWS RDS, DigitalOcean, etc.)
echo 3. Configure SSL/TLS certificates
echo 4. Deploy: docker-compose -f docker-compose.production.yml up -d
echo 5. Set up monitoring and backups
echo 6. Configure domain DNS
echo.
echo For detailed instructions, see:
echo   PRODUCTION_DEPLOYMENT.md
echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.

pause
