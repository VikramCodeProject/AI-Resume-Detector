# PRODUCTION DEPLOYMENT CHECKLIST

**Goal:** Complete all items below to deploy Resume Verify to production.  
**Estimated Time:** 2-3 hours  
**Status:** Ready to begin ✓

---

## PHASE 1: Database & Infrastructure (30 min)

### PostgreSQL Setup
- [ ] **Create PostgreSQL database**
  - Option A: Local - `brew install postgresql` / `apt-get install postgresql`
  - Option B: AWS RDS - Create database instance (15-20 min)
  - Verify: `psql -U postgres -h localhost -c "SELECT version();"`

- [ ] **Create database and user**
  ```sql
  CREATE DATABASE resume_verify;
  CREATE USER resume_user WITH PASSWORD 'your-strong-password';
  GRANT ALL PRIVILEGES ON DATABASE resume_verify TO resume_user;
  ```

- [ ] **Run migrations**
  ```bash
  cd backend
  alembic upgrade head
  ```

- [ ] **Update .env.production with DATABASE_URL**
  ```
  DATABASE_URL=postgresql://resume_user:password@localhost:5432/resume_verify
  ```

### Redis Setup
- [ ] **Install/Setup Redis**
  - Option A: Local - `brew install redis` / `apt-get install redis-server`
  - Option B: AWS ElastiCache (Redis) - Create cluster
  - Option C: Docker - `docker run -d -p 6379:6379 redis`

- [ ] **Update .env.production with REDIS_URL**
  ```
  REDIS_URL=redis://localhost:6379/0
  ```

---

## PHASE 2: External APIs & Credentials (45 min)

### GitHub API Token
- [ ] **Create GitHub token**
  1. Go to https://github.com/settings/tokens
  2. Click "Generate new token (classic)"
  3. Select scopes: `read:user`, `repo`, `public_repo`
  4. Copy token (format: `ghp_xxxxxxxxxxxxxxxxxxxx`)

- [ ] **Add to .env.production**
  ```
  GITHUB_API_KEY=ghp_xxxxxxxxxxxxxxxxxxxx
  ```

- [ ] **Test GitHub token**
  ```bash
  curl -H "Authorization: token ghp_xxxxxxxxxxxxxxxxxxxx" \
    https://api.github.com/user
  # Should return user data
  ```

### AWS S3 Setup
- [ ] **Create S3 bucket**
  1. AWS Console > S3 > Create Bucket
  2. Name: `resume-verify-prod-[unique-id]`
  3. Region: us-east-1
  4. Block Public Access: ON
  5. Versioning: Enable
  6. Encryption: Enable (AES-256)

- [ ] **Create IAM user for S3 access**
  1. AWS IAM > Users > Create User
  2. Username: `resume-verify-app`
  3. Programmatic access: ON
  4. Inline policy with S3 permissions (see guide)
  5. Copy Access Key ID and Secret Key

- [ ] **Add to .env.production**
  ```
  AWS_S3_BUCKET=resume-verify-prod-[unique-id]
  AWS_REGION=us-east-1
  AWS_ACCESS_KEY_ID=AKIA...
  AWS_SECRET_ACCESS_KEY=...
  ```

- [ ] **Test S3 connection**
  ```python
  import boto3
  s3 = boto3.client('s3', aws_access_key_id='...', aws_secret_access_key='...')
  s3.head_bucket(Bucket='resume-verify-prod-...')
  # Should succeed silently
  ```

### SendGrid Email Service
- [ ] **Create SendGrid account**
  1. Go to https://sendgrid.com
  2. Sign up (free tier: 100 emails/day)
  3. Verify email address

- [ ] **Generate API key**
  1. Settings > API Keys > Create API Key
  2. Name: `Resume-Verify-App`
  3. Copy key (format: `SG.xxxxxxxxxxxxxxxxxxxx`)

- [ ] **Add to .env.production**
  ```
  SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxx
  SENDGRID_FROM_EMAIL=noreply@your-domain.com
  ```

- [ ] **Test SendGrid**
  ```python
  import sendgrid
  sg = sendgrid.SendGridAPIClient('SG.xxx...')
  # Should initialize without errors
  ```

### LinkedIn API
- [ ] **Decide on approach**
  - [ ] **Option A:** Manual verification (no API needed)
  - [ ] **Option B:** Third-party service (e.g., Clearbit)
  - [ ] **Option C:** Request LinkedIn official API access (2-4 week review)

- [ ] **Update .env.production**
  ```
  LINKEDIN_API_KEY=manual_verification_required
  # Or: CLEARBIT_API_KEY=... (if using Clearbit)
  ```

---

## PHASE 3: Security & Authentication (20 min)

### JWT Secret Generation
- [ ] **Generate secure JWT_SECRET (32+ characters)**
  
  **Windows PowerShell:**
  ```powershell
  [System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32)) | Set-Clipboard
  ```
  
  **Linux/macOS:**
  ```bash
  openssl rand -base64 32
  ```
  
  **Python:**
  ```python
  import secrets
  print(secrets.token_urlsafe(32))
  ```

- [ ] **Add to .env.production**
  ```
  JWT_SECRET=JzQ4F7nP2kL9mQ6wXyZ1bV3cD5eF8gH0xKi8jN2...
  JWT_ALGORITHM=HS256
  JWT_EXPIRY_MINUTES=15
  REFRESH_TOKEN_EXPIRY_DAYS=30
  ```

- [ ] **Install Argon2 for password hashing**
  ```bash
  pip install argon2-cffi
  ```

- [ ] **Update backend authentication** (see production_config.py)
  - Replace plaintext password comparison with `password_hasher.hash_password()`
  - Update login endpoint to use `password_hasher.verify_password()`

- [ ] **Verify password hashing works**
  ```bash
  python test_security_implementations.py
  # Should show: 33/33 PASSED
  ```

---

## PHASE 4: Blockchain Smart Contract (30 min)

### Deploy to Polygon (Testnet First)

- [ ] **Setup Hardhat**
  ```bash
  cd blockchain
  npm install -g hardhat
  hardhat init
  ```

- [ ] **Create deploy script** (`scripts/deploy.js`)
  - See PRODUCTION_SETUP_GUIDE.md section 7 for template

- [ ] **Update hardhat.config.js**
  - Add Polygon testnet (Mumbai): `https://rpc-mumbai.maticvigil.com`
  - Add Polygon mainnet: `https://polygon-rpc.com`

- [ ] **Get private key from MetaMask**
  1. Open MetaMask > Account Details > Export Private Key
  2. Copy key (starts with `0x`)

- [ ] **Create .env (NOT .env.production!)**
  ```bash
  PRIVATE_KEY=0x1234567890abcdef...
  ```

- [ ] **Deploy to Mumbai Testnet (Free)**
  ```bash
  npx hardhat run scripts/deploy.js --network mumbai
  # Output: Contract deployed to: 0x1234...abcd
  ```

- [ ] **Verify contract on PolygonScan**
  1. Go to https://mumbai.polygonscan.com
  2. Search for contract address
  3. Verify source code for transparency

- [ ] **Get test POL tokens** (free from faucet)
  1. https://faucet.polygon.technology/
  2. Enter wallet address
  3. Request POL tokens

- [ ] **Deploy to Polygon Mainnet**
  ```bash
  npx hardhat run scripts/deploy.js --network polygon
  # Need small amount of POL (~$0.10 for gas)
  ```

- [ ] **Add to .env.production**
  ```
  ETH_RPC_URL=https://polygon-rpc.com
  SMART_CONTRACT_ADDRESS=0x1234567890abcdef...
  PRIVATE_KEY=0x9876543210fedcba...
  ```

---

## PHASE 5: Environment Configuration (10 min)

- [ ] **Create .env.production file**
  ```bash
  cp .env.production.template .env.production
  # Edit with all actual credentials
  ```

- [ ] **Populate all variables**
  - Database: ✓
  - Redis: ✓
  - GitHub API: ✓
  - AWS S3: ✓
  - SendGrid: ✓
  - JWT Secret: ✓
  - Blockchain: ✓

- [ ] **Set production flags**
  ```
  ENVIRONMENT=production
  DEBUG=false
  ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
  ```

- [ ] **Verify no credentials in git**
  ```bash
  echo ".env.production" >> .gitignore
  git rm --cached .env.production  # If already committed
  ```

---

## PHASE 6: Validation & Testing (20 min)

### Run Production Validator
- [ ] **Install validation script**
  ```bash
  # Already created: validate_production.py
  python validate_production.py
  ```

- [ ] **Fix any failures**
  - Check error messages in validator output
  - Verify credentials are correct
  - Test each service individually

### Run Security Test Suite
- [ ] **Execute comprehensive tests**
  ```bash
  python test_security_implementations.py
  # Expected: 33/33 PASSED
  ```

- [ ] **Verify no regressions**
  - All 5 security implementations active
  - Rate limiting working
  - Account lockout functional
  - JWT validation active

### Test Full Flow
- [ ] **User registration** → Email verification → Resume upload
- [ ] **ML pipeline** → GitHub verification → Trust score calculation
- [ ] **Blockchain** → Claim registered on-chain
- [ ] **Email** → Verification report sent

---

## PHASE 7: Deployment (30 min)

### Build Frontend
- [ ] **Build production React bundle**
  ```bash
  cd frontend
  npm install
  npm run build
  # Creates: dist/ folder with optimized assets
  ```

- [ ] **Test production build locally**
  ```bash
  npm run preview  # Vite preview mode
  # Visit: http://localhost:5173
  ```

### Start Backend
- [ ] **Install production server** (Gunicorn)
  ```bash
  pip install gunicorn uvicorn
  ```

- [ ] **Start backend with production settings**
  ```bash
  gunicorn -w 4 -b 0.0.0.0:8000 --timeout 60 backend.main:app
  # -w 4: 4 worker processes
  # -b 0.0.0.0:8000: Bind to all interfaces on port 8000
  # --timeout 60: 60-second timeout for async tasks
  ```

### Deployment Options

**Option A: Self-Hosted (DigitalOcean/AWS EC2)**
- [ ] Rent server ($5-20/month)
- [ ] Install Docker and Docker Compose
- [ ] Deploy using docker-compose.yml
- [ ] Setup Nginx as reverse proxy
- [ ] Configure SSL/HTTPS with Let's Encrypt

**Option B: AWS Elastic Beanstalk (Easiest)**
- [ ] `eb init -p python-3.11 resume-verify`
- [ ] `eb create production`
- [ ] `eb deploy`

**Option C: Heroku**
- [ ] `heroku create resume-verify-prod`
- [ ] `git push heroku main`
- [ ] `heroku config:set $(cat .env.production)`

### Configure HTTPS/SSL
- [ ] **Get SSL certificate** (Let's Encrypt, AWS ACM, etc.)
- [ ] **Install certificate on web server** (Nginx, Apache, ALB)
- [ ] **Redirect HTTP → HTTPS**
- [ ] **Test SSL**: https://your-domain.com

### Post-Deployment
- [ ] **Monitor application logs**
  ```bash
  tail -f /var/log/app.log
  # Or: heroku logs --tail
  # Or: AWS CloudWatch logs
  ```

- [ ] **Monitor system resources**
  - CPU usage
  - Memory usage
  - Database connections
  - API response times

---

## PHASE 8: Launch & Monitoring (Ongoing)

- [ ] **Monitor health**
  ```bash
  curl -s https://your-domain.com/api/health
  # Should return: {"status": "ok"}
  ```

- [ ] **Check error rates**
  - Application errors: < 1%
  - Failed verification tasks: < 5%

- [ ] **Review analytics**
  - User registrations
  - Resume uploads
  - Average verification time

- [ ] **Backup strategy**
  - Database: Daily automated backup
  - S3 files: Versioning enabled
  - Smart contract: Immutable on-chain

- [ ] **Scaling plan**
  - Database: Add read replicas if needed
  - API: Add load balancer + multiple instances
  - Celery: Scale workers for async tasks

---

## Troubleshooting

### Common Issues

**Database Connection Error**
```
Error: could not translate host name "localhost" to address
Fix: Ensure PostgreSQL is running and DATABASE_URL is correct
```

**S3 Permission Denied**
```
Error: An error occurred (AccessDenied) when calling the PutObject operation
Fix: Verify IAM user policy includes s3:PutObject on your bucket
```

**GitHub API Rate Limit**
```
Error: API rate limit exceeded
Fix: Use authenticated requests with GITHUB_API_KEY
```

**Blockchain Gas too Low**
```
Error: transaction underpriced
Fix: Increase gas price in hardhat config or wait for lower network congestion
```

**Email Not Sending**
```
Error: 403 Forbidden
Fix: Verify SENDGRID_API_KEY is correct and from_email is verified
```

---

## Final Validation Checklist

Before marking deployment complete:

- [ ] All 8 phases above completed ✓
- [ ] `validate_production.py` shows all checks passed ✓
- [ ] `test_security_implementations.py` shows 33/33 passed ✓
- [ ] Database migrations running ✓
- [ ] All APIs tested and responding ✓
- [ ] Smart contract deployed and verified ✓
- [ ] SSL/HTTPS working ✓
- [ ] Email service operational ✓
- [ ] Monitoring and logging active ✓
- [ ] Backups configured ✓

---

## Post-Launch Checklist

**Week 1:**
- Monitor error rates and performance
- Respond to user issues promptly
- Review database growth
- Test disaster recovery procedures

**Month 1:**
- Analyze usage patterns
- Optimize slow queries
- Review security logs
- Plan scaling if needed

**Ongoing:**
- Keep dependencies updated
- Monitor blockchain gas costs
- Review vendor contracts (AWS, SendGrid, etc.)
- Plan feature improvements

---

**You're ready to deploy! 🚀**

For detailed instructions, see: `PRODUCTION_SETUP_GUIDE.md`  
For code implementation, see: `backend/production_config.py`  
For validation, run: `python validate_production.py`

Questions? Check the troubleshooting section or PRODUCTION_SETUP_GUIDE.md
