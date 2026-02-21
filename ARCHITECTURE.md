# Resume Truth Verification System - System Architecture

## 1. System Overview

**Vision:** Production-grade AI platform that verifies resume claims using multi-source verification, machine learning, and blockchain immutability.

**Core Flow:**
```
User Upload → Resume Parsing → Claim Extraction → Multi-Source Verification 
→ Feature Engineering → ML Classification → SHAP Explanation 
→ Trust Score Generation → Blockchain Storage → Report Generation
```

---

## 2. Tech Stack Rationale

### Frontend
- **React.js 18+** - Modern component architecture, SSR-ready
- **TypeScript** - Type safety, better IDE support
- **Redux Toolkit** - State management at scale
- **Material-UI (MUI)** - Enterprise UI components
- **Chart.js / D3.js** - Trust score visualization
- **Axios** - HTTP client with interceptors
- **Web3.js** - Blockchain interaction from frontend

### Backend
- **FastAPI** - High-performance async Python API (>15k req/sec)
- **PostgreSQL** - Relational data, ACID transactions, JSONB for flexible claims
- **Celery + Redis** - Async task queue for long-running ML jobs
- **SQLAlchemy ORM** - Database abstraction layer
- **Pydantic** - Data validation and serialization
- **JWT** - Secure API authentication

### ML/NLP Pipeline
- **SpaCy** - NER, POS tagging (fast, production-ready)
- **Transformers (HuggingFace)** - BERT/RoBERTa for semantic understanding
- **PyPDF2 + python-docx** - Resume parsing
- **Scikit-learn** - Feature engineering, ML models
- **XGBoost** - Gradient boosting classifier
- **SHAP** - Model explainability
- **Tesseract OCR** - Certificate verification
- **OpenCV** - Image processing for certificate analysis

### Blockchain
- **Solidity** - Smart contracts on Ethereum/Polygon
- **Web3.py** - Python blockchain interaction
- **ethers.js** - JavaScript blockchain interaction
- **Hardhat** - Smart contract development framework

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Local orchestration
- **AWS S3/GCS** - Resume storage (encrypted)
- **JWT + OAuth2** - Authentication
- **AES-256** - Data encryption at rest

---

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                        │
│  Upload | Dashboard | Reports | Blockchain Verification   │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API (HTTPS)
┌────────────────────▼────────────────────────────────────────┐
│               FASTAPI BACKEND (Python)                      │
├──────────────────────────────────────────────────────────────┤
│ ┌─────────────┬──────────────┬─────────────┬──────────────┐ │
│ │ Auth Layer  │ Upload Mgmt  │ Verification│ Blockchain  │ │
│ │ (JWT/OAuth) │ (Resume S3)  │ Orchestration│ Interface  │ │
│ └─────────────┴──────────────┴─────────────┴──────────────┘ │
│              ▼                                ▼               │
│ ┌──────────────────────────┐    ┌─────────────────────────┐ │
│ │    ML/NLP Pipeline       │    │   Verification Engines  │ │
│ │  • Resume Parser         │    │  • GitHub Analyzer      │ │
│ │  • Claim Extractor       │    │  • LinkedIn Matcher     │ │
│ │  • Feature Engineer      │    │  • Certificate Detector │ │
│ │  • ML Classifier         │    │  • Timeline Validator   │ │
│ │  • SHAP Explainer        │    │  • Skill Assessor       │ │
│ └──────────────────────────┘    └─────────────────────────┘ │
│                                          ▼                    │
│                         ┌────────────────────────────────┐   │
│                         │  Task Queue (Celery + Redis)   │   │
│                         └────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌─────────────┐ ┌──────────────┐ ┌──────────────┐
   │ PostgreSQL  │ │ File Storage │ │  Blockchain  │
   │ (Claims,    │ │ (S3/GCS)     │ │ (Ethereum/   │
   │ Users)      │ │              │ │  Polygon)    │
   └─────────────┘ └──────────────┘ └──────────────┘
```

---

## 4. Database Schema

### PostgreSQL Core Tables

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    gdpr_consent BOOLEAN
);

-- Resumes table
CREATE TABLE resumes (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    filename VARCHAR(255),
    original_file_path VARCHAR(512),
    raw_text TEXT,
    parsed_json JSONB,
    uploaded_at TIMESTAMP,
    status ENUM('uploaded', 'processing', 'completed', 'failed')
);

-- Extracted claims
CREATE TABLE claims (
    id UUID PRIMARY KEY,
    resume_id UUID REFERENCES resumes(id),
    claim_type VARCHAR(50), -- skill, education, experience, etc.
    claim_text TEXT,
    extracted_at TIMESTAMP
);

-- Verification results
CREATE TABLE verifications (
    id UUID PRIMARY KEY,
    claim_id UUID REFERENCES claims(id),
    verification_source VARCHAR(100), -- github, linkedin, certificate, etc.
    score FLOAT (0-1),
    evidence JSONB,
    verified_at TIMESTAMP
);

-- ML predictions
CREATE TABLE ml_predictions (
    id UUID PRIMARY KEY,
    claim_id UUID REFERENCES claims(id),
    prediction VARCHAR(50), -- verified, doubtful, fake
    confidence FLOAT,
    shap_explanation TEXT,
    created_at TIMESTAMP
);

-- Blockchain records
CREATE TABLE blockchain_records (
    id UUID PRIMARY KEY,
    resume_id UUID REFERENCES resumes(id),
    transaction_hash VARCHAR(255),
    contract_address VARCHAR(255),
    timestamp TIMESTAMP,
    claims_hash VARCHAR(255),
    network VARCHAR(50) -- ethereum, polygon
);

-- Trust scores
CREATE TABLE trust_scores (
    id UUID PRIMARY KEY,
    resume_id UUID REFERENCES resumes(id),
    overall_score FLOAT (0-100),
    verified_count INT,
    doubtful_count INT,
    fake_count INT,
    generated_at TIMESTAMP
);
```

---

## 5. API Endpoint Structure

```
POST   /api/auth/register              - User registration
POST   /api/auth/login                 - Login
POST   /api/auth/refresh               - Refresh JWT token

POST   /api/resumes/upload             - Upload resume (multipart)
GET    /api/resumes/<id>               - Get resume details
GET    /api/resumes/<id>/claims        - Get extracted claims
GET    /api/resumes/<id>/verifications - Get verification results
GET    /api/resumes/<id>/trust-score   - Get trust score
GET    /api/resumes/<id>/report        - Download verification report

POST   /api/verify/github/<username>   - Verify GitHub profile
POST   /api/verify/linkedin/<url>      - Verify LinkedIn
POST   /api/verify/certificate         - Verify certificate image
POST   /api/verify/timeline            - Check timeline consistency

POST   /api/blockchain/store-claim     - Store claim on blockchain
GET    /api/blockchain/verify-claim    - Verify claim authenticity

GET    /api/dashboard/stats            - Overall system statistics
GET    /api/dashboard/recent-resumes   - Recent uploads
```

---

## 6. ML Pipeline Architecture

### Stage 1: Resume Parsing
- Input: PDF/DOCX file
- Output: Structured JSON (text, sections, formatting)
- Tools: PyPDF2, python-docx, textract

### Stage 2: Claim Extraction
- Input: Parsed resume text
- Output: Structured claims with type and confidence
- Process:
  - NER with SpaCy (entities)
  - Semantic parsing with Transformers
  - Regex patterns for specific formats
  - Rule-based extraction for structured sections

### Stage 3: Feature Engineering
```python
Features extracted per claim:
- source_document_quality (grammar score)
- claim_specificity (length, detail level)
- language_confidence (spell check, linguistic analysis)
- entity_recognition_score (NER confidence)
- temporal_consistency (timeline analysis)
- duplicate_claim_count (claim appears N times)
```

### Stage 4: Verification Integration
```python
verification_features = {
    'github_activity_score': (0-1),        # Languages, commits, public repos
    'github_recency_score': (0-1),         # Recent activity
    'linkedin_match_score': (0-1),         # Company/timeline match
    'certificate_authenticity': (0-1),     # OCR + template matching
    'timeline_violation_penalty': (0-1),   # Overlaps, impossible dates
    'skill_test_score': (0-1),             # MCQ/coding test results
}
```

### Stage 5: ML Classification
```python
Model: XGBoost Classifier
Input: 20-30 engineered features
Output: [verified, doubtful, fake] with confidence scores
Training: Labeled dataset of 10k+ resumes

Weighted Scoring:
trust_score = (
    verified_claims * 100 +
    doubtful_claims * 50 +
    fake_claims * 0
) / total_claims
```

### Stage 6: Explainability
```python
Use SHAP TreeExplainer:
- Show top 5 contributing features
- Explain why claim classified as fake
- Example: "Python marked fake because:
  - GitHub shows 0 Python repos (-40)
  - Claimed 5 years experience, hired 1 year ago (-30)"
```

---

## 7. Blockchain Integration

### Smart Contract Structure (Solidity)

```solidity
contract ResumeVerificationRegistry {
    struct VerifiedClaim {
        bytes32 claimHash;
        address verifier;
        uint256 timestamp;
        uint8 trustScore;
        bool isValid;
    }

    mapping(bytes32 => VerifiedClaim) public claims;
    mapping(address => bytes32[]) public userClaims;

    event ClaimRegistered(bytes32 claimHash, uint256 timestamp);
    
    function registerClaim(bytes32 _claimHash, uint8 _trustScore) public {
        require(_trustScore >= 0 && _trustScore <= 100, "Invalid score");
        
        VerifiedClaim memory newClaim = VerifiedClaim({
            claimHash: _claimHash,
            verifier: msg.sender,
            timestamp: block.timestamp,
            trustScore: _trustScore,
            isValid: true
        });
        
        claims[_claimHash] = newClaim;
        userClaims[msg.sender].push(_claimHash);
        emit ClaimRegistered(_claimHash, block.timestamp);
    }
}
```

### Backend Integration (Web3.py)

```python
from web3 import Web3

class BlockchainService:
    def __init__(self, contract_address, abi, private_key):
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('ETH_RPC_URL')))
        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)
        self.account = self.w3.eth.account.from_key(private_key)
    
    def store_verified_claim(self, claim_hash: str, trust_score: int) -> str:
        """Store verified claim on blockchain"""
        tx = self.contract.functions.registerClaim(
            bytes.fromhex(claim_hash),
            trust_score
        ).build_transaction({
            'from': self.account.address,
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
        })
        
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()
```

---

## 8. Security Architecture

### Authentication & Authorization
- JWT with 15-minute expiry
- Refresh tokens stored in secure HTTP-only cookies
- OAuth2 for social login (GitHub, LinkedIn)
- Role-based access control (RBAC)

### Data Encryption
- AES-256 for sensitive data at rest
- TLS 1.3 for data in transit
- Encrypted file storage on S3/GCS
- PII hashing (email, phone)

### API Security
- Rate limiting (100 req/min per IP)
- CORS properly configured
- CSRF protection
- SQL injection prevention (parameterized queries)
- XSS protection

### Compliance
- GDPR-compliant consent forms
- User right to delete (right to be forgotten)
- Data retention policies
- Audit logging for all operations

---

## 9. Deployment Architecture

### Containerization
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]

# Frontend Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
```

### Docker Compose (Local Development)
```yaml
version: '3.9'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://postgres@postgres/resume_verify
      REDIS_URL: redis://redis:6379
  
  celery:
    build: ./backend
    command: celery -A tasks worker --loglevel=info
    depends_on:
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
```

### Production Deployment (AWS/GCP)
- Kubernetes cluster with auto-scaling
- CloudSQL for PostgreSQL
- Cloud Storage for resume files
- Load balancer with TLS termination
- CloudArmor for DDoS protection
- VPC with private networking

---

## 10. Monitoring & Observability

```python
# Logging
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Metrics (Prometheus)
from prometheus_client import Counter, Histogram

resume_upload_counter = Counter('resume_uploads_total', 'Total resumes uploaded')
verification_time_histogram = Histogram('verification_time_seconds', 'Verification time')

# Tracing (OpenTelemetry)
from opentelemetry import trace
tracer = trace.get_tracer(__name__)
```

---

## 11. Testing Strategy

### Unit Tests (pytest)
- Test claim extraction accuracy
- Feature engineering correctness
- ML model predictions
- API endpoints
- Database operations

### Integration Tests
- End-to-end resume verification flow
- Blockchain transaction success
- External API integrations (GitHub, LinkedIn)
- Data consistency checks

### Load Testing
- 1000 concurrent uploads
- Verification latency under load
- Blockchain transaction throughput

---

## 12. Scalability Considerations

- **Horizontal Scaling**: Stateless API servers behind load balancer
- **Async Processing**: Celery for long-running ML tasks
- **Caching**: Redis for API responses and feature caches
- **Database**: Connection pooling, read replicas for analytics
- **File Storage**: S3 with CloudFront CDN
- **Blockchain**: Use Polygon (lower gas fees) for production

---

## 13. Data Flow Example: Resume Verification

```
1. User uploads resume.pdf
2. Backend receives multipart upload
3. File stored on S3 (encrypted)
4. Resume parsing task added to Celery queue
5. Worker processes: PDF → text extraction → NER → claim extraction
6. Claims stored in PostgreSQL
7. Parallel verification tasks created:
   - GitHub analysis job
   - LinkedIn matching job
   - Certificate detection job
   - Timeline validation job
8. ML features engineered from verification results
9. XGBoost model predicts claim validity
10. SHAP explainer generates human-readable explanations
11. Trust score calculated
12. Verified claim hash stored on blockchain
13. Report generated and user notified
14. Results cached in Redis for fast retrieval
```

This architecture ensures scalability, security, maintainability, and production-readiness.
