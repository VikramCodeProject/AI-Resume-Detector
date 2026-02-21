# Resume Truth Verification System - Complete Setup Guide

## 🚀 Quick Start - 5 Minutes

### Windows
```bash
# Open Command Prompt and run:
startup.bat
```

### Linux / macOS
```bash
chmod +x startup.sh
./startup.sh
```

This will:
1. Create Python virtual environment and install dependencies
2. Install Node.js dependencies for frontend
3. Create `.env` file with defaults
4. Start Backend (FastAPI) on http://localhost:8000
5. Start Frontend (React) on http://localhost:3000

---

## 📋 Prerequisites

- **Python** 3.10+ ([Download](https://www.python.org/downloads/))
- **Node.js** 18+ ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- **Docker** (Optional, for PostgreSQL/Redis)

---

## 🛠️ Manual Setup

### Step 1: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate venv  
# Windows:
venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Backend will be available at:** http://localhost:8000

**API Documentation:** http://localhost:8000/api/docs

### Step 2: Frontend Setup

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Frontend will be available at:** http://localhost:3000

### Step 3: Optional - Database Services

If you want full features with database persistence:

```bash
# Using Docker Compose (requires Docker)
docker-compose up -d
```

This starts:
- PostgreSQL at localhost:5432
- Redis at localhost:6379

---

## 📁 Project Structure

```
UsMiniProject/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── tasks.py             # Celery async tasks
│   ├── database.py          # Database configuration
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile           # Docker image for backend
│   └── uploads/             # Uploaded resumes directory
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React component
│   │   └── main.tsx         # React entry point
│   ├── package.json         # Node.js dependencies
│   ├── vite.config.ts       # Vite configuration
│   └── index.html           # HTML template
│
├── ml_engine/
│   ├── pipeline.py          # NLP/ML processing pipeline
│   └── verification_engines.py  # Multi-source verification
│
├── blockchain/
│   ├── blockchain_service.py  # Web3 integration
│   └── ResumeVerificationRegistry.sol  # Smart contract
│
└── docker-compose.yml       # Docker services configuration
```

---

## 🔧 Configuration

### Environment Variables

Edit `.env` file to configure:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resume_verify
REDIS_URL=redis://localhost:6379

# API Keys
GITHUB_API_KEY=your_token_here
JWT_SECRET=your_secret_here

# Blockchain
ETH_RPC_URL=https://polygon-rpc.com

# Environment
ENVIRONMENT=development
```

---

## 🧪 Testing the System

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-02-19T10:30:00.000000",
  "environment": "development",
  "version": "1.0.0"
}
```

### 2. Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123",
    "full_name": "Test User",
    "gdpr_consent": true
  }'
```

### 3. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

### 4. Upload Resume
Use the frontend at http://localhost:3000 or:

```bash
curl -X POST http://localhost:8000/api/resumes/upload \
  -F "file=@your_resume.pdf"
```

---

## 📱 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login (returns JWT tokens)

### Resumes
- `POST /api/resumes/upload` - Upload resume for processing
- `GET /api/resumes` - List user's resumes
- `GET /api/resumes/{resume_id}` - Get resume details
- `GET /api/resumes/{resume_id}/trust-score` - Get trust score

### Verification
- `POST /api/verify/github/{username}` - Verify GitHub profile

### Dashboard
- `GET /api/dashboard/stats` - System statistics
- `GET /api/health` - Health check

---

## 🐳 Docker Deployment

### Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Windows - kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS - kill process on port 8000
lsof -i :8000
kill -9 <PID>
```

### Python venv Issues
```bash
# Delete and recreate venv
rm -rf backend/venv

cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Frontend Build Issues
```bash
# Clear cache and reinstall
rm -rf frontend/node_modules
rm frontend/package-lock.json
cd frontend
npm install
```

### Database Connection Error
Make sure PostgreSQL is running:
```bash
# Using Docker
docker run --name resume-verify-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=resume_verify \
  -p 5432:5432 \
  postgres:15-alpine
```

---

## 📚 API Documentation

Navigate to http://localhost:8000/api/docs for interactive API documentation (Swagger UI).

---

## 🚀 Production Deployment

### Requirements
- Change JWT_SECRET to a strong random value
- Set ENVIRONMENT=production
- Use actual database (not SQLite)
- Configure real API keys (GitHub, AWS, etc.)
- Set up proper SSL/TLS certificates
- Use a production WSGI server (Gunicorn)
- Configure CORS properly for your domain

### Deployment Example (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 backend.main:app
```

---

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Celery Documentation](https://docs.celeryproject.io/)

---

## 📝 License

This project is licensed under MIT License.

---

## ❓ Support

For issues or questions:
1. Check the [ARCHITECTURE.md](ARCHITECTURE.md) for system design details
2. Check the [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) for upcoming features
3. Review error logs in the terminal output

---

**Last Updated:** February 19, 2024  
**Version:** 1.0.0
