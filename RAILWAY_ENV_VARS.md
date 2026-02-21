# Railway Environment Variables - Copy these to Railway Dashboard
# Settings → Variables

# Database (Railway will provide PostgreSQL)
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:5432/resume_verify

# Redis (Railway will provide Redis)
REDIS_URL=redis://default:PASSWORD@HOST:6379

# JWT Configuration
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Environment
ENVIRONMENT=production
DEBUG=false

# CORS
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# API Settings
MAX_UPLOAD_SIZE_MB=10
ALLOWED_FILE_TYPES=["pdf", "docx", "txt"]

# External APIs (Optional)
GITHUB_API_KEY=your-github-token
LINKEDIN_API_KEY=your-linkedin-token

# AWS S3 (for resume storage)
AWS_S3_BUCKET=resume-verify-prod
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Blockchain
ETH_RPC_URL=https://polygon-rpc.com
SMART_CONTRACT_ADDRESS=0x...
PRIVATE_KEY=0x...

# Email (Optional - for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com

# Application Name
APP_NAME=AI Resume Authenticity Detector
APP_VERSION=1.0.0
