# 🚀 Quick Start Guide - Enterprise Features

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env - Minimum required:
# GITHUB_API_KEY=your_token_here  (Get from https://github.com/settings/tokens)
```

### Step 3: Start Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Test API

Open browser: http://localhost:8000/api/docs

---

## 📝 API Testing Examples

### 1. GitHub Verification

```bash
curl -X POST "http://localhost:8000/api/verify/github" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "torvalds",
    "claimed_skills": ["C", "Linux", "Git"]
  }'
```

**Expected Response:**
```json
{
  "username": "torvalds",
  "github_authenticity_score": 95.2,
  "risk_level": "Low",
  "metrics": {
    "public_repos": 52,
    "total_stars": 158243,
    "top_languages": ["C", "Shell", "Makefile"]
  }
}
```

---

### 2. Upload & Verify Resume

```python
import requests

# Step 1: Upload resume
files = {'file': open('resume.pdf', 'rb')}
response = requests.post(
    'http://localhost:8000/api/resumes/upload',
    files=files
)
resume_id = response.json()['resume_id']

# Step 2: Full verification
response = requests.post(
    'http://localhost:8000/api/verify/full',
    json={
        'resume_id': resume_id,
        'github_username': 'johndoe',
        'claimed_skills': ['Python', 'React', 'AWS']
    }
)
print(response.json())
```

---

### 3. Certificate Verification

```bash
curl -X POST "http://localhost:8000/api/verify/certificate" \
  -F "file=@certificate.jpg" \
  -F "expected_name=John Doe"
```

---

### 4. Deepfake Detection

```bash
curl -X POST "http://localhost:8000/api/verify/deepfake" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "I am a results-oriented professional with excellent communication skills and a proven track record in dynamic team environments..."
  }'
```

---

## 🧪 Python Test Script

Save as `test_verification.py`:

```python
import asyncio
import requests

BASE_URL = "http://localhost:8000"

async def test_all_services():
    print("🧪 Testing Enterprise Verification Services\n")
    
    # 1. Health Check
    print("1️⃣ Health Check...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"   Status: {response.json()['status']}\n")
    
    # 2. GitHub Verification
    print("2️⃣ GitHub Verification...")
    response = requests.post(
        f"{BASE_URL}/api/verify/github",
        json={
            "username": "octocat",
            "claimed_skills": ["Ruby", "JavaScript"]
        }
    )
    result = response.json()
    print(f"   Score: {result.get('github_authenticity_score', 'N/A')}")
    print(f"   Risk: {result.get('risk_level', 'N/A')}\n")
    
    # 3. Deepfake Detection
    print("3️⃣ Deepfake Detection...")
    test_text = """
    I am a results-oriented professional with excellent communication skills.
    I have a proven track record in fast-paced environments.
    I am a team player with strong analytical skills.
    """
    response = requests.post(
        f"{BASE_URL}/api/verify/deepfake",
        json={"resume_text": test_text}
    )
    result = response.json()
    print(f"   AI Probability: {result.get('ai_generated_probability', 'N/A')}")
    print(f"   Deepfake Flag: {result.get('deepfake_flag', 'N/A')}\n")
    
    print("✅ All tests complete!")

if __name__ == "__main__":
    asyncio.run(test_all_services())
```

Run:
```bash
python test_verification.py
```

---

## 🔍 Service Status Check

```python
# Check which services are available
import os

print("Service Status:")
print(f"GitHub API: {'✅' if os.getenv('GITHUB_API_KEY') else '❌ (Set GITHUB_API_KEY)'}")
print(f"OpenAI LLM: {'✅' if os.getenv('OPENAI_API_KEY') else '⚠️ (Optional - using template mode)'}")
print(f"Tesseract OCR: {'✅' if os.path.exists('C:\\\\Program Files\\\\Tesseract-OCR\\\\tesseract.exe') else '⚠️ (Install Tesseract)'}")
```

---

## 📊 Expected Performance

| Operation | Time | Cost |
|-----------|------|------|
| GitHub Verification | 1-2s | Free |
| Certificate OCR | 2-3s | Free |
| Deepfake Detection | 1-2s | Free |
| LLM Reasoning (Template) | <0.1s | Free |
| LLM Reasoning (OpenAI) | 2-3s | $0.01-0.03 |
| **Full Verification** | **3-5s** | **Free** |

---

## 🐛 Quick Troubleshooting

### Problem: GitHub API rate limit

**Solution:**
```bash
# Add to .env
GITHUB_API_KEY=github_pat_YOUR_TOKEN_HERE
```

### Problem: spaCy model not found

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Problem: Tesseract not found

**Solution:**
```bash
# Windows: Download from
# https://github.com/UB-Mannheim/tesseract/wiki

# Linux:
sudo apt-get install tesseract-ocr

# Mac:
brew install tesseract
```

---

## 📚 Next Steps

1. ✅ Test all endpoints with Postman/Thunder Client
2. ✅ Review API docs at http://localhost:8000/api/docs
3. ✅ Check detailed documentation in `ENTERPRISE_IMPLEMENTATION.md`
4. ✅ Integrate with frontend dashboard
5. ✅ Set up production deployment

---

## 🎯 Key Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/verify/github` | POST | GitHub profile verification |
| `/api/verify/certificate` | POST | Certificate OCR validation |
| `/api/verify/deepfake` | POST | AI-generated text detection |
| `/api/verify/full` | POST | Complete verification (all services) |
| `/api/health` | GET | System health check |
| `/api/docs` | GET | Interactive API documentation |

---

**Ready to verify your first resume? Start with the `/api/docs` endpoint!**
