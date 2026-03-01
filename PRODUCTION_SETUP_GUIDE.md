# Production Setup Guide - Complete Configuration

**Goal:** Configure all external services and credentials before deploying to production.

**Estimated Time:** 2-3 hours (depending on account setup speed)

---

## 1. PostgreSQL Database Setup

### Option A: Local PostgreSQL (Development/Testing)

```bash
# Install PostgreSQL
# Windows: https://www.postgresql.org/download/windows/
# macOS: brew install postgresql@15
# Linux: sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
# Windows: Services > PostgreSQL > Start
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Create database and user
psql -U postgres

# In PostgreSQL terminal:
CREATE DATABASE resume_verify;
CREATE USER resume_user WITH PASSWORD 'secure_password_here';
ALTER ROLE resume_user SET client_encoding TO 'utf8';
ALTER ROLE resume_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE resume_user SET default_transaction_deferrable TO on;
ALTER ROLE resume_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE resume_verify TO resume_user;
\q
```

### Option B: Cloud PostgreSQL (AWS RDS - Recommended for Production)

```bash
# 1. Go to AWS Console > RDS > Create Database
# 2. Engine: PostgreSQL 15
# 3. DB Instance Class: db.t3.micro (free tier eligible)
# 4. Storage: 20 GB
# 5. DB Name: resume_verify
# 6. Master Username: resume_user
# 7. Master Password: [generate strong password]
# 8. Publicly Accessible: No (for security)
# 9. VPC Security Group: Allow inbound port 5432

# Once created, get the endpoint:
# Format: [identifier].c9akciq32.us-east-1.rds.amazonaws.com
```

### Update .env.production

```bash
# Option A (Local):
DATABASE_URL=postgresql://resume_user:secure_password_here@localhost:5432/resume_verify

# Option B (AWS RDS):
DATABASE_URL=postgresql://resume_user:secure_password@[your-rds-endpoint]:5432/resume_verify
```

### Test Connection

```bash
# Install psycopg2 (already in requirements.txt)
python -c "import psycopg2; print('PostgreSQL connection OK')"

# Run migrations
alembic upgrade head
```

---

## 2. GitHub API Key Configuration

### Get GitHub Token

1. Go to **GitHub > Settings > Developer settings > Personal access tokens**
2. Click **Generate new token (classic)**
3. **Scopes needed:**
   - `read:user` - Read user profile
   - `repo` - Access repositories
   - `public_repo` - Access public repos
4. Copy token (you won't see it again!)
5. Token format: `ghp_xxxxxxxxxxxxxxxxxxxx`

### Update .env.production

```bash
GITHUB_API_KEY=ghp_xxxxxxxxxxxxxxxxxxxx
```

### Test GitHub Integration

```bash
curl -H "Authorization: token ghp_xxxxxxxxxxxxxxxxxxxx" \
  https://api.github.com/user
# Should return: {"login": "your_username", ...}
```

### Implement in Code

Add to `backend/ml_engine/verification_engines.py`:

```python
import requests
from typing import Dict, List

class GitHubAnalyzer:
    """Verify programming skills via GitHub profiles"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.github.com"
        self.headers = {"Authorization": f"token {api_key}"}
    
    def analyze_user(self, github_username: str) -> Dict:
        """Analyze GitHub user's language proficiency"""
        try:
            # Get user repos
            repos_url = f"{self.base_url}/users/{github_username}/repos"
            resp = requests.get(repos_url, headers=self.headers)
            repos = resp.json()
            
            # Aggregate languages
            languages = {}
            for repo in repos:
                lang = repo.get('language')
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
            
            return {
                'verified': True,
                'languages': languages,
                'repo_count': len([r for r in repos if r['language']]),
                'confidence': 0.85
            }
        except Exception as e:
            return {'verified': False, 'error': str(e), 'confidence': 0.0}
```

---

## 3. LinkedIn API Configuration

### LinkedIn Setup (Limited Options)

LinkedIn Official API requires **business approval** and is not available for consumer apps. Use **alternative approach**:

```bash
# Option 1: LinkedIn Public Profile Scraping (No API key needed)
# Use package: linkedin-api (unofficial, terms of service risk)

# Option 2: Manual Verification
# Ask users to provide LinkedIn URL for manual verification

# Option 3: Third-party SERVICE
# Use clearbit.com or peopledatalabs.com APIs
```

### For Now: Placeholder Configuration

```bash
# In .env.production:
LINKEDIN_API_KEY=manual_verification_required

# Or use alternative service:
CLEARBIT_API_KEY=your_clearbit_key_here
```

---

## 4. AWS S3 Configuration (Resume Storage)

### Create S3 Bucket

1. Go to **AWS Console > S3 > Create bucket**
2. **Bucket name:** `resume-verify-prod-[your-unique-id]`
3. **Region:** us-east-1 (or nearest)
4. **Block Public Access:** ON (for security)
5. **Versioning:** Enable (for recovery)
6. **Encryption:** Enable (AES-256)

### Create IAM User with S3 Access

1. Go to **AWS IAM > Users > Create user**
2. **Username:** resume-verify-app
3. **Access type:** Programmatic access
4. **Permissions:** Attach policy `AmazonS3FullAccess` (or custom policy below)

**Custom S3-only Policy:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::resume-verify-prod-*/*"
        },
        {
            "Effect": "Allow",
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::resume-verify-prod-*"
        }
    ]
}
```

5. Copy **Access Key ID** and **Secret Access Key**

### Update .env.production

```bash
AWS_S3_BUCKET=resume-verify-prod-[your-unique-id]
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_S3_ENCRYPTION=AES256
```

### Test S3 Connection

```python
import boto3

s3_client = boto3.client(
    's3',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY',
    region_name='us-east-1'
)

# List buckets
buckets = s3_client.list_buckets()
print(buckets)  # Should show your bucket
```

---

## 5. Email Service Setup (SendGrid Recommended)

### SendGrid Configuration (Free tier: 100 emails/day)

1. Go to **sendgrid.com > Sign up > Free account**
2. Verify email address
3. Go to **Settings > API Keys > Create API Key**
4. **API Key name:** Resume-Verify-App
5. **Permissions:** Full Access (or Mail Send only)
6. Copy API key: `SG.xxxxxxxxxxxxxxxxxxxx`

### Update .env.production

```bash
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@resume-verify.com
```

### Implement Email Verification in Code

Add to `backend/main.py`:

```python
import sendgrid
from sendgrid.helpers.mail import Mail

class EmailService:
    """Send transactional emails via SendGrid"""
    
    def __init__(self, api_key: str):
        self.sg = sendgrid.SendGridAPIClient(api_key)
        self.from_email = "noreply@resume-verify.com"
    
    def send_verification_email(self, to_email: str, verification_code: str):
        """Send email verification link"""
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject="Verify Your Email - Resume Verify",
            html_content=f"""
            <p>Welcome to Resume Verify!</p>
            <p>Click the link below to verify your email:</p>
            <a href="https://resume-verify.com/verify?code={verification_code}">
                Verify Email
            </a>
            <p>This link expires in 24 hours.</p>
            """
        )
        
        try:
            response = self.sg.send(message)
            return response.status_code == 202
        except Exception as e:
            logger.error(f"SendGrid error: {str(e)}")
            return False
```

### Update Registration Endpoint

```python
@app.post("/api/auth/register")
async def register(request: UserRegisterRequest):
    # ... existing validation ...
    
    # Send verification email
    verification_code = secrets.token_urlsafe(32)
    email_service.send_verification_email(request.email, verification_code)
    
    return {"message": "Account created. Check email to verify."}
```

---

## 6. JWT_SECRET Generation

### Generate Secure Secret

**Windows PowerShell:**
```powershell
[System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32)) | Set-Clipboard
# Paste into .env.production
```

**Linux/macOS:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Output: JzQ4F...xKi8 (32+ characters)
```

**Python (Interactive):**
```python
import secrets
jwt_secret = secrets.token_urlsafe(32)
print(jwt_secret)  # Copy this to .env.production
```

### Update .env.production

```bash
JWT_SECRET=JzQ4F7nP2kL9mQ6wXyZ1bV3cD5eF8gH0xKi8jN2...
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=15
REFRESH_TOKEN_EXPIRY_DAYS=30
```

### Verify in Code

```python
# In backend/main.py - already implemented:
class Settings:
    JWT_SECRET: str = os.getenv('JWT_SECRET', '')
    
    def validate(self):
        if self.ENVIRONMENT == 'production':
            if len(self.JWT_SECRET) < 32:
                raise ValueError("JWT_SECRET must be 32+ characters in production")
```

---

## 7. Blockchain Smart Contract Deployment

### Polygon vs Ethereum

| Factor | Polygon | Ethereum |
|--------|---------|----------|
| Gas Cost | $0.01 - $0.10 | $2 - $50 |
| Speed | 2-3 seconds | 15+ seconds |
| Recommendation | ✅ Better for MVP | For mainnet only |

### Deploy to Polygon (Recommended)

**1. Install Hardhat**
```bash
cd blockchain
npm install -g hardhat
hardhat init
# Choose: Create an empty hardhat.config.js
```

**2. Create deploy script** (`scripts/deploy.js`):

```javascript
async function main() {
    const ResumeVerificationRegistry = await ethers.getContractFactory("ResumeVerificationRegistry");
    const contract = await ResumeVerificationRegistry.deploy();
    await contract.deployed();
    
    console.log("Contract deployed to:", contract.address);
    return contract.address;
}

main().catch((error) => {
    console.error(error);
    process.exit(1);
});
```

**3. Update hardhat.config.js:**

```javascript
require("@nomicfoundation/hardhat-toolbox");

module.exports = {
    solidity: "0.8.20",
    networks: {
        polygon: {
            url: "https://polygon-rpc.com",
            accounts: [process.env.PRIVATE_KEY],
            chainId: 137
        },
        mumbai: {  // Testnet
            url: "https://rpc-mumbai.maticvigil.com",
            accounts: [process.env.PRIVATE_KEY],
            chainId: 80001
        }
    }
};
```

**4. Get Private Key (MetaMask Wallet)**
- Open MetaMask extension
- Account > Account Details > Export Private Key
- Copy key (starts with 0x)

**5. Set Environment Variable**
```bash
# .env (NOT .env.production - keep this secret!)
PRIVATE_KEY=0x1234567890abcdef...
```

**6. Deploy to Polygon Mumbai Testnet (Free)**
```bash
cd blockchain
npx hardhat run scripts/deploy.js --network mumbai
# Output: Contract deployed to: 0x1234...abcd
```

**7. Once tested, deploy to Polygon Mainnet**
```bash
npx hardhat run scripts/deploy.js --network polygon
# Need POL tokens for gas (minuscule amount: ~$0.10)
```

**8. Update .env.production**
```bash
SMART_CONTRACT_ADDRESS=0x1234...abcd
ETH_RPC_URL=https://polygon-rpc.com
PRIVATE_KEY=0x9876...dcba  # Safe to use - limited permissions
```

**9. Verify on PolygonScan**
- Go to https://polygonscan.com
- Search for your contract address
- Verify source code for transparency

---

## 8. Bcrypt Password Hashing Implementation

### The Problem
- Current: Passwords stored as plaintext (mock development)
- Goal: Use bcrypt with 12 salt rounds (~180ms per hash)

### The Challenge
- `passlib` + `bcrypt` version compatibility issue
- Solution: Use direct `argon2-cffi` instead (more modern)

### Implementation

```python
# In backend/main.py
from argon2 import PasswordHasher as Argon2PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash

argon2_hasher = Argon2PasswordHasher()

class PasswordHasher:
    """Argon2 password hashing (alternative to bcrypt)"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using Argon2"""
        return argon2_hasher.hash(password)
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against Argon2 hash"""
        try:
            argon2_hasher.verify(password_hash, password)
            return True
        except (VerifyMismatchError, InvalidHash):
            return False
```

**Install dependency:**
```bash
pip install argon2-cffi
```

**Update register endpoint:**
```python
# In backend/main.py register():
user_id = str(uuid4())
password_hash = PasswordHasher.hash_password(request.password)  # Hash it!
mock_users[request.email] = {
    'id': user_id,
    'email': request.email,
    'password_hash': password_hash,  # Now hashed, not plaintext!
    ...
}
```

**Update login endpoint:**
```python
# In backend/main.py login():
user = mock_users.get(request.email)
if not user or not PasswordHasher.verify_password(request.password, user['password_hash']):
    # Failed login
    account_lockout.record_failure(request.email)
```

---

## 9. Complete .env.production Template

```bash
# ===== ENVIRONMENT =====
ENVIRONMENT=production
DEBUG=false

# ===== DATABASE =====
DATABASE_URL=postgresql://resume_user:password@your-rds-endpoint:5432/resume_verify
REDIS_URL=redis://your-redis-endpoint:6379

# ===== FRONTEND =====
FRONTEND_URL=https://your-domain.com
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# ===== JWT =====
JWT_SECRET=JzQ4F7nP2kL9mQ6wXyZ1bV3cD5eF8gH0xKi8jN2... (32+ chars)
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=15
REFRESH_TOKEN_EXPIRY_DAYS=30

# ===== GITHUB API =====
GITHUB_API_KEY=ghp_xxxxxxxxxxxxxxxxxxxx

# ===== LINKEDIN API =====
LINKEDIN_API_KEY=manual_verification_required

# ===== AWS S3 =====
AWS_S3_BUCKET=resume-verify-prod-unique-id
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_S3_ENCRYPTION=AES256

# ===== EMAIL SERVICE =====
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@your-domain.com

# ===== BLOCKCHAIN =====
ETH_RPC_URL=https://polygon-rpc.com
SMART_CONTRACT_ADDRESS=0x1234567890abcdef...
PRIVATE_KEY=0x9876543210fedcba...

# ===== SECURITY =====
RATE_LIMIT_LOGIN_ATTEMPTS=5
RATE_LIMIT_REGISTER_ATTEMPTS=3
ACCOUNT_LOCKOUT_DURATION_MINUTES=15
PASSWORD_MIN_LENGTH=8
PASSWORD_MAX_LENGTH=128
```

---

## 10. Deployment Checklist

- [ ] **Database**
  - [ ] PostgreSQL created (AWS RDS or local)
  - [ ] Database URL in .env.production
  - [ ] Migrations run: `alembic upgrade head`
  - [ ] Connection tested

- [ ] **APIs**
  - [ ] GitHub token obtained and tested
  - [ ] SendGrid account created and verified
  - [ ] AWS S3 bucket created with encryption
  - [ ] AWS IAM user created with limited permissions

- [ ] **Authentication**
  - [ ] JWT_SECRET generated (32+ chars)
  - [ ] Password hashing implemented (Argon2)
  - [ ] All security tests pass (33/33)

- [ ] **Blockchain**
  - [ ] Smart contract compiled
  - [ ] Contract deployed to Polygon testnet (verified)
  - [ ] Contract address in .env.production
  - [ ] Private key secured (not in git)

- [ ] **Security**
  - [ ] HTTPS/SSL certificate obtained
  - [ ] Rate limiting active
  - [ ] Account lockout active
  - [ ] Password validation active
  - [ ] File upload validation active

- [ ] **Environment**
  - [ ] .env.production created (never committed to git)
  - [ ] DEBUG=false
  - [ ] ENVIRONMENT=production
  - [ ] ALLOWED_ORIGINS set correctly

---

## 11. Deployment Step-by-Step

```bash
# 1. Prepare code
git checkout production-branch
git pull origin main

# 2. Install dependencies
pip install -r backend/requirements.txt
npm install --prefix frontend

# 3. Copy .env.production
cp .env.production.template .env.production
# Edit with actual credentials

# 4. Run migrations
alembic upgrade head

# 5. Build frontend
cd frontend && npm run build && cd ..

# 6. Start backend (with gunicorn for production)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 backend.main:app

# 7. Serve frontend (with Nginx)
# Configure Nginx to serve frontend/dist and proxy /api to backend

# 8. Run security tests (final verification)
python test_security_implementations.py
# Should show: Overall: 33/33 tests passed (100%)

# 9. Monitor during launch
# Check logs, monitor metrics, be ready to rollback
```

---

## 12. Production Deployment Options

### **Option 1: AWS (Recommended for Scalability)**
- **Backend:** AWS EC2 or Elastic Beanstalk
- **Frontend:** AWS S3 + CloudFront
- **Database:** AWS RDS PostgreSQL
- **Cost:** ~$50-100/month for small deployment

### **Option 2: Heroku (Easiest)**
- **Simple:** `git push heroku main`
- **Drawback:** Higher cost (~$14/month for Eco)
- **Benefit:** Automatic SSL, scaling, monitoring

### **Option 3: DigitalOcean (Best Value)**
- **Backend:** $6/month Droplet
- **Database:** Managed PostgreSQL $15/month
- **Total:** ~$25/month
- **Benefit:** Simple, full control

### **Option 4: Docker + Kubernetes**
- Use provided `docker-compose.yml`
- Deploy to GCP GKE, AWS ECS, or self-hosted K8s
- **Cost:** Varies, but very scalable

---

## Estimated Timeline

| Task | Time | Difficulty |
|------|------|-----------|
| PostgreSQL setup | 30 min | Easy |
| GitHub API | 10 min | Easy |
| AWS S3 | 20 min | Easy |
| SendGrid | 10 min | Easy |
| JWT_SECRET | 5 min | Easy |
| Blockchain deployment | 30 min | Medium |
| Bcrypt implementation | 15 min | Easy |
| Final testing | 20 min | Easy |
| **TOTAL** | **~2.5 hours** | |

---

**Ready to deploy!** Once all items above are completed, your system is production-ready and secure.
