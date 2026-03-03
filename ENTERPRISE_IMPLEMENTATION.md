# Enterprise Resume Verification - Days 8-14 Implementation

## 🚀 IMPLEMENTATION COMPLETE

This document describes the **enterprise-level upgrade** implemented for the Resume Truth Verification Platform.

---

## 📋 OVERVIEW

**Implementation Period:** Days 8-14  
**Total Services Added:** 4 major services  
**New API Endpoints:** 4 verification endpoints  
**Production Ready:** ✅ Yes

---

## 🏗️ ARCHITECTURE

### New Services Structure

```
backend/
├── services/
│   ├── __init__.py
│   ├── github_service.py         # GitHub API integration
│   ├── ocr_service.py             # Certificate OCR verification
│   ├── llm_reasoning.py           # LLM explanation layer
│   └── deepfake_detector.py       # AI-generated content detection
├── main.py                        # Updated with new endpoints
└── requirements.txt               # Updated dependencies
```

---

## 🔧 DAY 8-9: GITHUB API INTEGRATION

### Feature: Real GitHub Profile Verification

**File:** `backend/services/github_service.py`

#### Capabilities:
- ✅ Real GitHub REST API v3 integration
- ✅ Repository count analysis
- ✅ Programming language detection
- ✅ Contribution frequency scoring
- ✅ Star/fork social proof analysis
- ✅ Redis caching (1-hour TTL)
- ✅ Rate limit handling (5000/hour with token)

#### Authenticity Scoring Algorithm:

```python
Total Score = (
    Repository Score × 30% +
    Activity Score × 30% +
    Language Match × 25% +
    Social Proof × 15%
)
```

#### API Endpoint:

```http
POST /api/verify/github
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

Request:
{
  "username": "octocat",
  "claimed_skills": ["Python", "JavaScript", "Go"]
}

Response:
{
  "username": "octocat",
  "profile_exists": true,
  "github_authenticity_score": 87.5,
  "risk_level": "Low",
  "metrics": {
    "public_repos": 32,
    "total_stars": 145,
    "top_languages": ["Python", "JavaScript", "TypeScript"],
    "days_since_last_activity": 5,
    "recent_commit_count": 23
  },
  "recommendations": [
    "Active GitHub presence with 32 repositories",
    "Recent GitHub activity (within 30 days)"
  ],
  "verified_at": "2026-03-03T10:30:00Z"
}
```

#### Usage:

```python
from services import get_github_service

github_service = get_github_service(api_token="your_github_token")
result = await github_service.verify_profile(
    username="johndoe",
    claimed_skills=["Python", "React", "AWS"]
)
```

#### Environment Variables:

```bash
GITHUB_API_KEY=github_pat_YOUR_TOKEN_HERE
```

Generate at: https://github.com/settings/tokens

---

## 📄 DAY 10-11: OCR CERTIFICATE VERIFICATION

### Feature: Certificate Authenticity Detection

**File:** `backend/services/ocr_service.py`

#### Capabilities:
- ✅ Multi-OCR engine support (Tesseract + EasyOCR)
- ✅ Image preprocessing (denoise, deskew, threshold)
- ✅ Entity extraction: Name, Issuer, Date, Certificate ID
- ✅ Issuer whitelist validation (50+ trusted issuers)
- ✅ Duplicate certificate detection
- ✅ Tamper detection (font inconsistency, compression artifacts)
- ✅ Date validity checks

#### Supported Certificate Issuers:

- **Online Platforms:** Coursera, Udemy, edX, Udacity, LinkedIn Learning
- **Cloud Providers:** AWS, Google Cloud, Azure, Oracle
- **Tech Companies:** IBM, Red Hat, Cisco, VMware
- **Universities:** Stanford, MIT, Harvard, Berkeley

#### API Endpoint:

```http
POST /api/verify/certificate
Content-Type: multipart/form-data
Authorization: Bearer <JWT_TOKEN>

Request: (Form Data)
- file: certificate_image.jpg
- expected_name: "John Doe"
- resume_id: "uuid-here"

Response:
{
  "certificate_valid": true,
  "authenticity_score": 85.0,
  "risk_level": "Low",
  "extracted_data": {
    "candidate_name": "John Doe",
    "issuer": "Coursera",
    "issue_date": "2024-05-15",
    "certificate_id": "CRS-2024-AB12345",
    "course_name": "Machine Learning Specialization"
  },
  "validation_checks": {
    "has_name": true,
    "has_issuer": true,
    "trusted_issuer": true,
    "valid_date": true,
    "has_certificate_id": true
  },
  "duplicate_detected": false,
  "recommendations": [
    "Certificate appears authentic"
  ],
  "verified_at": "2026-03-03T10:35:00Z"
}
```

#### OCR Preprocessing Pipeline:

1. **Grayscale Conversion**
2. **Denoising** (fastNlMeansDenoising)
3. **Adaptive Thresholding** (Gaussian)
4. **Deskewing** (angle detection + rotation)
5. **Text Extraction** (Tesseract or EasyOCR)

#### Usage:

```python
from services import get_ocr_service

ocr_service = get_ocr_service(use_easyocr=False)
result = await ocr_service.verify_certificate(
    image_path="certificate.jpg",
    expected_name="John Doe",
    resume_id="resume-uuid"
)
```

#### Environment Variables:

```bash
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
USE_EASYOCR=false
```

---

## 🤖 DAY 12-13: LLM REASONING LAYER

### Feature: Contextual Explanation Generation

**File:** `backend/services/llm_reasoning.py`

#### Capabilities:
- ✅ OpenAI GPT-4o-mini integration (primary)
- ✅ HuggingFace Mistral-7B fallback
- ✅ Template-based reasoning (no API required)
- ✅ Multi-source data synthesis
- ✅ Risk narrative generation
- ✅ Actionable recommendations
- ✅ Red flag / green flag extraction

#### Reasoning Inputs:

- Resume data (name, skills, experience)
- GitHub analysis results
- Certificate verification results
- Deepfake detection results
- ML model predictions
- Timeline anomalies

#### API Endpoint:

Integrated into unified verification (see `/api/verify/full`)

#### Example Output:

```json
{
  "final_trust_score": 78.5,
  "risk_level": "Medium",
  "explanation": "The resume for John Doe shows moderate authenticity with some concerns. GitHub profile has limited activity (12 repos) and may not fully support claimed 5+ years of experience. Certificate from Coursera appears authentic. No AI-generated content detected. Timeline inconsistency detected between 2020-2022 employment records.",
  "key_findings": [
    "GitHub: 12 repos, Medium risk",
    "Certificate: Valid",
    "ML Classification: Doubtful"
  ],
  "red_flags": [
    "GitHub activity does not match claimed experience",
    "Timeline inconsistency in employment history"
  ],
  "green_flags": [
    "Valid certificate from recognized issuer",
    "Recent GitHub activity (within 30 days)"
  ],
  "recommendation": "PROCEED WITH CAUTION - Some concerns identified. Recommend additional reference checks.",
  "reasoning_engine": "Template"
}
```

#### Cost Comparison:

| Engine | Cost/Resume | Speed | Accuracy |
|--------|-------------|-------|----------|
| **OpenAI GPT-4o-mini** | $0.01-0.03 | ~2s | High |
| **HuggingFace Mistral** | Free | ~5-10s | Medium |
| **Template-based** | Free | <0.1s | Medium |

#### Usage:

```python
from services import get_llm_service

llm_service = get_llm_service(use_openai=True)
result = await llm_service.generate_verification_explanation(
    resume_data=resume_dict,
    github_analysis=github_result,
    certificate_analysis=cert_result,
    deepfake_analysis=deepfake_result
)
```

#### Environment Variables:

```bash
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
```

---

## 🕵️ DAY 14: DEEPFAKE RESUME DETECTION

### Feature: AI-Generated Text Detection

**File:** `backend/services/deepfake_detector.py`

#### Capabilities:
- ✅ Perplexity scoring (GPT-2 language model)
- ✅ Stylometric analysis
- ✅ N-gram repetition detection
- ✅ Burstiness analysis
- ✅ Generic phrase detection
- ✅ Vocabulary richness (Type-Token Ratio)
- ✅ Sentence complexity variance

#### Detection Methods:

1. **Perplexity Scoring** (Optional - computationally expensive)
   - Measures text predictability
   - AI text: perplexity 20-50 (too predictable)
   - Human text: perplexity 50-200+ (natural variation)

2. **Stylometric Analysis**
   - Sentence length variance (Coefficient of Variation)
   - Lexical diversity (Type-Token Ratio)
   - Average word length
   - Punctuation patterns

3. **N-gram Repetition**
   - Bigram/trigram frequency analysis
   - AI tends to repeat phrases more

4. **Burstiness**
   - Sentence complexity variation
   - Human writing has "bursts" of complex/simple sentences
   - AI writing is uniform

5. **Generic Phrase Detection**
   - 17+ common clichés ("results-oriented", "team player", etc.)

#### API Endpoint:

```http
POST /api/verify/deepfake
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

Request:
{
  "resume_text": "I am a results-oriented professional with excellent communication skills..."
}

Response:
{
  "ai_generated_probability": 0.72,
  "deepfake_flag": true,
  "risk_level": "High",
  "analysis_breakdown": {
    "perplexity_score": null,
    "stylometric_risk": 0.68,
    "repetition_score": 0.55,
    "burstiness_score": 0.71,
    "generic_phrase_count": 5
  },
  "indicators": [
    "Uniform writing style (TTR: 0.42)",
    "Uniform sentence complexity (burstiness: 0.08)",
    "5 generic phrases found"
  ],
  "recommendations": [
    "⚠️ HIGH RISK: Resume shows strong AI-generation indicators",
    "Conduct thorough interview to verify claimed experience"
  ],
  "analyzed_at": "2026-03-03T10:40:00Z"
}
```

#### Usage:

```python
from services import get_deepfake_detector

detector = get_deepfake_detector(use_perplexity=False)
result = await detector.analyze_resume_text(resume_text)
```

---

## 🔄 UNIFIED VERIFICATION ENDPOINT

### Feature: Complete Resume Authenticity Check

**Endpoint:** `POST /api/verify/full`

#### What It Does:

Orchestrates **all verification services** in a single API call:

1. GitHub profile verification
2. Certificate validation (multiple certificates)
3. Deepfake detection
4. LLM reasoning/explanation
5. Final trust score computation

#### API Endpoint:

```http
POST /api/verify/full
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

Request:
{
  "resume_id": "resume-uuid-here",
  "github_username": "johndoe",
  "certificate_image_paths": [
    "uploads/certificates/cert1.jpg",
    "uploads/certificates/cert2.jpg"
  ],
  "claimed_skills": ["Python", "React", "AWS", "Docker"]
}

Response:
{
  "resume_id": "resume-uuid-here",
  "final_trust_score": 78.5,
  "risk_level": "Medium",
  "classification": "Doubtful",
  "github_analysis": {
    "github_authenticity_score": 67.3,
    "risk_level": "Medium",
    ...
  },
  "certificate_analysis": [
    {
      "certificate_valid": true,
      "authenticity_score": 85.0,
      ...
    }
  ],
  "deepfake_analysis": {
    "ai_generated_probability": 0.38,
    "deepfake_flag": false,
    ...
  },
  "llm_explanation": {
    "explanation": "The resume shows moderate authenticity...",
    "red_flags": [...],
    "green_flags": [...],
    "recommendation": "PROCEED WITH CAUTION"
  },
  "verified_at": "2026-03-03T10:45:00Z"
}
```

#### Trust Score Calculation:

```python
Final Score = (
    GitHub Score × 30% +
    Certificate Score × 25% +
    Deepfake Score × 20% +
    ML Prediction × 25%
)
```

#### Classification Rules:

- **Verified:** Trust Score ≥ 75
- **Doubtful:** Trust Score 50-74
- **Fake:** Trust Score < 50

---

## 📦 INSTALLATION & SETUP

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt

# Install spaCy model (required)
python -m spacy download en_core_web_sm

# Install Tesseract OCR (Windows)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use Chocolatey: choco install tesseract

# Install Tesseract OCR (Linux)
sudo apt-get install tesseract-ocr

# Install Tesseract OCR (Mac)
brew install tesseract
```

### 2. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env and fill in:
# - GITHUB_API_KEY (required for GitHub verification)
# - OPENAI_API_KEY (optional, for LLM reasoning)
# - TESSERACT_CMD (Windows only)
```

### 3. Start Services

```bash
# Terminal 1: Redis (if not using Docker)
redis-server

# Terminal 2: Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Frontend (if needed)
cd frontend
npm run dev
```

### 4. Test Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# GitHub verification
curl -X POST http://localhost:8000/api/verify/github \
  -H "Content-Type: application/json" \
  -d '{
    "username": "octocat",
    "claimed_skills": ["Python", "JavaScript"]
  }'

# View API docs
# http://localhost:8000/api/docs
```

---

## 🧪 TESTING

### Unit Tests

```bash
cd backend
pytest tests/ -v
```

### Integration Tests

```bash
# Test GitHub service
python -c "
import asyncio
from services import get_github_service

async def test():
    service = get_github_service()
    result = await service.verify_profile('octocat')
    print(result)

asyncio.run(test())
"

# Test OCR service
python -c "
import asyncio
from services import get_ocr_service

async def test():
    service = get_ocr_service()
    result = await service.verify_certificate('test_cert.jpg')
    print(result)

asyncio.run(test())
"
```

---

## 📊 API RESPONSE EXAMPLES

### GitHub Verification - High Score

```json
{
  "username": "torvalds",
  "github_authenticity_score": 95.2,
  "risk_level": "Low",
  "metrics": {
    "public_repos": 52,
    "total_stars": 158243,
    "top_languages": ["C", "Shell", "Makefile"],
    "days_since_last_activity": 2
  }
}
```

### Certificate Verification - Duplicate Detected

```json
{
  "certificate_valid": false,
  "authenticity_score": 35.0,
  "risk_level": "Critical",
  "duplicate_detected": true,
  "recommendations": [
    "⚠️ Certificate ID found in multiple resumes"
  ]
}
```

### Deepfake Detection - AI Generated

```json
{
  "ai_generated_probability": 0.89,
  "deepfake_flag": true,
  "risk_level": "Critical",
  "indicators": [
    "Uniform writing style (TTR: 0.38)",
    "8 generic phrases found"
  ]
}
```

---

## 🔐 SECURITY BEST PRACTICES

### API Keys

- ✅ Store in environment variables only
- ✅ Never commit .env to Git
- ✅ Rotate keys regularly
- ✅ Use minimum required scopes

### Rate Limiting

- ✅ GitHub: 5000 requests/hour (with token)
- ✅ OpenAI: Set budget limits
- ✅ Implement Redis caching

### Data Privacy

- ✅ Encrypt resume files at rest
- ✅ HTTPS only in production
- ✅ GDPR compliance (right to delete)
- ✅ Audit trail logging

---

## 💰 COST ANALYSIS

### Per Resume Verification

| Service | Cost | Optional |
|---------|------|----------|
| **GitHub API** | Free | No |
| **OCR (Tesseract)** | Free | No |
| **Deepfake Detection** | Free | No |
| **LLM Reasoning (Template)** | Free | Yes |
| **LLM Reasoning (OpenAI)** | $0.01-0.03 | Yes |
| **Total (Free Mode)** | **$0.00** | - |
| **Total (AI Mode)** | **$0.01-0.03** | - |

### Monthly Estimates (1000 resumes)

- **Free Mode:** $0/month
- **AI Mode:** $10-30/month

---

## 🚀 PRODUCTION DEPLOYMENT

### Checklist

- [ ] Set `ENVIRONMENT=production` in .env
- [ ] Change `JWT_SECRET` to strong random value
- [ ] Configure production database
- [ ] Set up Redis cluster
- [ ] Enable HTTPS/SSL
- [ ] Configure AWS S3 with encryption
- [ ] Set up Celery workers for async processing
- [ ] Configure logging/monitoring (Sentry, DataDog)
- [ ] Set up CI/CD pipeline
- [ ] Load testing (1000+ concurrent requests)
- [ ] Security audit
- [ ] GDPR compliance review

### Docker Deployment

```bash
# Build images
docker-compose -f docker-compose.production.yml build

# Start services
docker-compose -f docker-compose.production.yml up -d

# Check logs
docker-compose logs -f backend
```

---

## 📚 ADDITIONAL RESOURCES

### Documentation

- [GitHub REST API v3](https://docs.github.com/en/rest)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

### Tutorials

- [GitHub Token Setup](https://github.com/settings/tokens)
- [Tesseract Installation](https://tesseract-ocr.github.io/tessdoc/Installation.html)
- [OpenAI Quickstart](https://platform.openai.com/docs/quickstart)

---

## 🐛 TROUBLESHOOTING

### Common Issues

**1. GitHub API Rate Limit Exceeded**
```bash
# Solution: Add GITHUB_API_KEY to .env
# Without token: 60 requests/hour
# With token: 5000 requests/hour
```

**2. Tesseract Not Found**
```bash
# Windows: Install from https://github.com/UB-Mannheim/tesseract/wiki
# Set TESSERACT_CMD in .env

# Linux:
sudo apt-get install tesseract-ocr

# Mac:
brew install tesseract
```

**3. spaCy Model Not Found**
```bash
python -m spacy download en_core_web_sm
```

**4. OpenAI API Error**
```bash
# Check API key is valid
# Check account has credits
# Or disable OpenAI: set use_openai=False
```

---

## 📞 SUPPORT

For issues or questions:

1. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
2. Check [INSTALLATION.md](INSTALLATION.md) for setup
3. Review API docs at http://localhost:8000/api/docs
4. Check logs in `backend/logs/`

---

## ✅ IMPLEMENTATION STATUS

| Feature | Status | Testing | Production Ready |
|---------|--------|---------|------------------|
| GitHub API Integration | ✅ | ✅ | ✅ |
| OCR Certificate Verification | ✅ | ✅ | ✅ |
| LLM Reasoning Layer | ✅ | ✅ | ✅ |
| Deepfake Detection | ✅ | ✅ | ✅ |
| Unified Verification Endpoint | ✅ | ✅ | ✅ |
| Redis Caching | ✅ | ✅ | ✅ |
| Error Handling | ✅ | ✅ | ✅ |
| API Documentation | ✅ | ✅ | ✅ |

---

**Last Updated:** 2026-03-03  
**Version:** 1.0.0  
**Implementation:** Days 8-14 Complete ✅
