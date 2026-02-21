# Copilot Instructions for UsMiniProject

Resume Truth Verification System: Production-grade AI platform verifying resume claims using multi-source verification, ML classification, explainable AI, and blockchain immutability.

## Project Overview

**Architecture:** Full-stack AI platform (React + FastAPI + ML/NLP + Blockchain)
**Core Workflow:** Resume Upload → Parsing → Claim Extraction → Multi-source Verification → ML Classification → SHAP Explanation → Trust Score → Blockchain Storage → Report Generation

**Tech Stack:**
- **Frontend:** React 18+ (TypeScript), Material UI v5, Redux, Web3.js
- **Backend:** FastAPI (async), PostgreSQL, Celery + Redis (async tasks)
- **ML/NLP:** SpaCy, Transformers, XGBoost, SHAP, Scikit-learn
- **Blockchain:** Solidity (Ethereum/Polygon), Web3.py, Hardhat
- **Infrastructure:** Docker, AWS S3, JWT/OAuth2, AES-256 encryption

---

## Development Environment Setup

### Prerequisites & Installation

```bash
# Python environment (3.10+)
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm  # Required NLP model

# Install frontend dependencies
cd ../frontend
npm install

# Start services
docker-compose up -d  # PostgreSQL, Redis
```

### Environment Configuration

Create `.env` in root:
```
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/resume_verify

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=your-secret-key-change-production
JWT_ALGORITHM=HS256

# External APIs
GITHUB_API_KEY=your-github-token
LINKEDIN_API_KEY=your-linkedin-token

# AWS S3
AWS_S3_BUCKET=resume-verify-prod
AWS_REGION=us-east-1

# Blockchain (Polygon)
ETH_RPC_URL=https://polygon-rpc.com
SMART_CONTRACT_ADDRESS=0x...
PRIVATE_KEY=0x...

# Environment
ENVIRONMENT=development
```

### Run Services

```bash
# Backend (Terminal 1)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
cd frontend
npm run dev  # Vite dev server on :3000

# Worker (Terminal 3 - processes async ML jobs)
celery -A tasks worker --loglevel=info

# Redis + PostgreSQL (one-time)
docker-compose up -d
```

---

## Architecture & Key Components

### High-Level Data Flow

```
User Upload (React)
  ↓
FastAPI Handler (auth, S3 storage)
  ↓
Celery Task Queue (async processing)
  ↓
├→ ResumeParser (PyPDF2/python-docx) → Raw text
├→ ClaimExtractor (SpaCy + Transformers) → Structured claims
├→ VerificationEngines (parallel):
│   ├→ GitHubAnalyzer (GitHub API)
│   ├→ LinkedInMatcher (LinkedIn public data)
│   ├→ CertificateDetector (Tesseract OCR + CV)
│   ├→ TimelineValidator (date parsing)
│   └→ SkillAssessor (dynamic MCQ)
├→ FeatureEngineer (numeric vectors)
├→ MLClassifier (XGBoost) → {verified|doubtful|fake}
├→ SHAPExplainer (model interpretability)
└→ TrustScoreCalculator (weighted scoring)
  ↓
BlockchainService (Web3.py) → Smart contract
  ↓
PostgreSQL (claims, results, user data)
  ↓
Report Generation + Dashboard (React)
```

### File Organization & Responsibilities

```
backend/
  main.py                    # FastAPI app, routes, middleware, auth
  requirements.txt          # Python dependencies

ml_engine/
  pipeline.py               # Core classes: ResumeParser, ClaimExtractor, FeatureEngineer, MLClassifier
  verification_engines.py   # GitHubAnalyzer, LinkedInMatcher, CertificateDetector, etc.

blockchain/
  blockchain_service.py     # Web3.py integration, contract interaction
  ResumeVerificationRegistry.sol  # Solidity smart contract

frontend/
  App.tsx                   # React main component, upload + dashboard

tests/                      # Unit & integration tests

docs/                       # Markdown guides (API, smart contract, etc.)

ARCHITECTURE.md             # Detailed system design document
INSTALLATION_GUIDE.md       # Setup instructions
DEVELOPMENT_ROADMAP.md      # Phased implementation plan
```

---

## Critical Patterns & Conventions

### Backend (FastAPI)

**Authentication Pattern:**
```python
# JWT tokens from Settings class
# Routes use: Depends(verify_jwt_token) -> get current user
# Refresh tokens stored in Redis
```

**Async Task Pattern:**
```python
# Long-running ML jobs sent to Celery
# Route returns job_id immediately
# Frontend polls /api/resume/{id}/status
# Celery workers process in parallel
```

**Settings Pattern:**
```python
# Use Settings() from environment vars
# @lru_cache() decorator for singleton
# Never hardcode credentials
```

**Database Pattern:**
```python
# Use SQLAlchemy ORM (models.py)
# All queries via async SQLSession
# JSONB columns for flexible claim storage
```

### ML/NLP Pipeline (ml_engine/)

**Data Classes:**
- `ExtractedClaim`: claim_type, claim_text, confidence, entities
- `FeatureVector`: 12+ numeric features for ML model input

**Processing Chain:**
1. `ResumeParser.parse()` → raw text
2. `ClaimExtractor.extract()` → List[ExtractedClaim]
3. `VerificationEngines.verify()` (parallel) → numeric scores
4. `FeatureEngineer.build_features()` → FeatureVector[]
5. `MLClassifier.predict()` → {verified|doubtful|fake}
6. `SHAPExplainer.explain()` → human-readable reasoning

**Model Training:**
- Train on 5000+ labeled resume/claim pairs
- Feature importance via SHAP
- Threshold tuning via F1-score optimization

### Blockchain Integration

**Smart Contract Pattern:**
- `registerVerifiedClaim(claimHash, trustScore, timestamp)`
- Immutable storage prevents resume tampering post-verification
- Event emission for audit trail

**Web3 Pattern:**
```python
# use Web3(Web3.HTTPProvider(ETH_RPC_URL))
# sign transactions with private key
# wait for transaction receipt before returning
```

### Frontend (React + TypeScript)

**Component Pattern:**
- Functional components with hooks
- Material UI theming for consistency
- Axios with auth header interceptor
- Redux for verification state

**API Integration:**
```typescript
// Axios interceptor adds JWT to all requests
// Error handler redirects to login on 401
// FormData for file uploads (multipart/form-data)
```

---

## Common Workflows

### Adding a New Verification Engine

1. Create class in `ml_engine/verification_engines.py` extending `BaseVerifier`
2. Implement `verify(claim: ExtractedClaim) -> float` (returns score 0.0-1.0)
3. Add to `VerificationEngineOrchestrator.parallel_verify()` 
4. Add corresponding feature column in `FeatureEngineer`
5. Retrain ML model with new feature

### Adding a New ML Classifier

1. Train model on existing feature data
2. Save model pickle in `backend/models/`
3. Update `MLClassifier.load_model()` to use new model
4. Validate on holdout test set (report F1, precision, recall)
5. A/B test before production rollout

### Blockchain Transaction Flow

1. Claim verification complete → feature vector → ML prediction
2. Hash prediction + timestamp: `sha256(claim_id + score + timestamp)`
3. Call `blockchain_service.register_claim(hash, score)`
4. Wait for transaction receipt
5. Store tx_hash in PostgreSQL for audit trail
6. Return blockchain_hash to frontend for wallet display

### Database Migrations

1. Update SQLAlchemy models in `backend/models.py`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Review generated migration file
4. Apply: `alembic upgrade head`
5. Rollback if needed: `alembic downgrade -1`

---

## Data Models & Key Entities

**Resume:**
- resume_id (UUID)
- user_id (FK to User)
- filename, upload_timestamp
- s3_key (encrypted file location)
- status (uploaded|processing|completed|failed)
- raw_text (parsed content)

**Claim:**
- claim_id (UUID)
- resume_id (FK)
- claim_type (skill|education|experience|certification|project)
- claim_text, confidence
- entities (JSONB for metadata)

**Verification:**
- verification_id (UUID)
- claim_id (FK)
- github_score, linkedin_score, certificate_score, etc.
- ml_prediction (verified|doubtful|fake)
- trust_score (0-100), confidence
- blockchain_hash, blockchain_tx_id
- explanation (SHAP reasoning)

**User:**
- user_id (UUID)
- email, password_hash
- gdpr_consent, data_deletion_requested
- created_at, last_login

---

## External Dependencies & Integrations

**GitHub API (`verification_engines.py`):**
- Analyze user's repositories, commits, languages
- Score Python/JavaScript/etc. skill claims
- Rate limit: 5000 req/hour (use token auth)

**LinkedIn (`verification_engines.py`):**
- Match resume education & company history
- Verify job timeline consistency
- Uses public scraping (no official API in free tier)

**OCR & Certificate Detection (`verification_engines.py`):**
- Tesseract: extract text from certificate images
- OpenCV: detect tampering (font mismatch, logo corruption)
- Requires `pytesseract` + local Tesseract binary

**Blockchain (`blockchain_service.py`):**
- Polygon (cheaper than Ethereum)
- Smart contract stores claim hashes
- Requires ETH for gas fees (small amounts)

**AWS S3 (credentials in `.env`):**
- Encrypted resume file storage
- Server-side encryption with AES-256
- Presigned URLs for secure downloads

---

## Common Pitfalls & Best Practices

### Performance
- **NLP bottleneck:** Use spaCy (fast) not BERT for every claim; only use BERT for ambiguous cases
- **Celery workers:** Scale horizontally; 1 worker per CPU core
- **Database:** Add indexes on resume_id, user_id, claim_type; use connection pooling
- **Blockchain:** Batch claim writes; don't write every single prediction

### Security
- **Never log credentials:** Use `Settings` with env vars only
- **JWT expiry:** Short access tokens (15 min) + long refresh tokens (30 days)
- **Resume privacy:** Encrypt S3 files; use HTTPS only; GDPR right-to-delete
- **Contract audit:** Have smart contract reviewed before mainnet deployment

### Testing
- **Unit tests:** Mock external APIs (GitHub, LinkedIn, blockchain)
- **Integration tests:** Use PostgreSQL test database; run against real Celery
- **ML evaluation:** Always test on holdout set; report precision/recall/F1
- **Load test:** Simulate 100+ concurrent uploads; monitor Celery queue depth

### Common Mistakes
- **Not handling file upload timeouts** → Resume parsing takes >30s → HTTP 504
  - *Fix:* Return job_id immediately; client polls /status endpoint
- **Hardcoding API keys in code** → Credentials leaked in Git history
  - *Fix:* Use `.env` file + `Settings` class, add `.env` to `.gitignore`
- **Running verification engines sequentially** → 5 engines × 10s each = 50s latency
  - *Fix:* Use `asyncio.gather()` or Celery subtasks for parallel execution
- **Not validating resume parsing output** → Garbage in = garbage out
  - *Fix:* Check text extraction quality; fallback to OCR if needed

---

## Useful Commands

```bash
# Backend Development
uvicorn main:app --reload                    # Hot reload
uvicorn main:app --host 0.0.0.0 --port 8000 # Expose externally

# Celery
celery -A tasks worker --loglevel=info       # Start worker
celery -A tasks purge                        # Clear queue
celery -A tasks inspect active               # View running tasks

# Database
alembic upgrade head                         # Apply migrations
alembic revision --autogenerate -m "msg"     # Generate migration
psql -U postgres -h localhost -d resume_verify # Connect to DB

# Frontend
npm run dev                                  # Vite dev server
npm run build                                # Production build
npm run preview                              # Test production build

# Docker
docker-compose up -d                         # Start services
docker-compose down                          # Stop services
docker logs container_name                   # View container logs

# Testing
pytest tests/                                # Run unit tests
pytest tests/ -v --cov                       # With coverage report
python -m pytest --asyncio-mode=auto         # For async tests

# ML Model Training
python ml_engine/train_classifier.py         # Train XGBoost model
python ml_engine/evaluate_model.py           # Get accuracy/F1 metrics

# Blockchain
npx hardhat compile                          # Compile smart contracts
npx hardhat test                             # Run contract tests
npx hardhat deploy --network polygon         # Deploy to Polygon
```

---

## Key Patterns Exemplified

| Pattern | File | Example |
|---------|------|---------|
| Async ML processing | `backend/main.py` | `/api/verify` route returns job_id, Celery processes in background |
| NER + claim extraction | `ml_engine/pipeline.py` | `ClaimExtractor` uses spaCy entity recognition |
| Parallel verification | `ml_engine/verification_engines.py` | GitHubAnalyzer, LinkedInMatcher run in parallel via Celery |
| ML explainability | `ml_engine/pipeline.py` | `SHAPExplainer` generates human-readable feature importance |
| Blockchain immutability | `blockchain/blockchain_service.py` | `registerVerifiedClaim()` stores hash permanently on-chain |
| JWT authentication | `backend/main.py` | `verify_jwt_token()` dependency for protected routes |
| React state management | `frontend/App.tsx` | Axios + Redux for verification status polling |

---

**Last Updated:** 2026-02-02

**Key Contacts & Resources:**
- ARCHITECTURE.md — Full system design with diagrams
- DEVELOPMENT_ROADMAP.md — Phased implementation timeline
- INSTALLATION_GUIDE.md — Step-by-step setup
- IEEE research paper format available in `research/` folder
