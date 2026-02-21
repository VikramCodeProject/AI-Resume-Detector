#!/usr/bin/env python3
"""
Test Dynamic Trust Scores
Upload multiple resumes and compare their trust scores
"""
import requests
import time

API = "http://localhost:8000"

print("=" * 60)
print("TESTING DYNAMIC TRUST SCORES")
print("=" * 60)

# Register user
print("\n1. Registering user...")
try:
    res = requests.post(f"{API}/api/auth/register", json={
        "email": "scoretest@example.com",
        "password": "password123",
        "full_name": "Test User",
        "gdpr_consent": True
    })
    print(f"✅ Registered")
except:
    print("⚠️  User may already exist")

# Login
print("\n2. Logging in...")
res = requests.post(f"{API}/api/auth/login", json={
    "email": "scoretest@example.com",
    "password": "password123"
})
token = res.json()["access_token"]
print(f"✅ Logged in")

headers = {"Authorization": f"Bearer {token}"}
scores = []

# Upload multiple resumes with different filenames
print("\n3. Uploading 5 different resumes...")
for i in range(1, 6):
    filename = f"resume_{i}.pdf"
    files = {"file": (filename, f"Sample content for resume {i}")}
    
    res = requests.post(f"{API}/api/resumes/upload", files=files, headers=headers)
    resume_id = res.json()["resume_id"]
    
    # Wait a moment then get trust score
    time.sleep(0.5)
    res = requests.get(f"{API}/api/resumes/{resume_id}", headers=headers)
    trust_score = res.json().get("trust_score", {})
    
    score = trust_score.get("overall_score", "N/A")
    verified = trust_score.get("verified_count", 0)
    doubtful = trust_score.get("doubtful_count", 0)
    fake = trust_score.get("fake_count", 0)
    
    scores.append(score)
    print(f"   Resume {i}: Score={score} | Verified={verified} | Doubtful={doubtful} | Fake={fake}")

print("\n" + "=" * 60)
print("RESULTS:")
print(f"Scores: {scores}")
print(f"Min: {min(scores) if isinstance(scores[0], (int, float)) else 'N/A'}")
print(f"Max: {max(scores) if isinstance(scores[0], (int, float)) else 'N/A'}")
print(f"Avg: {round(sum([s for s in scores if isinstance(s, (int, float))]) / len([s for s in scores if isinstance(s, (int, float))]), 1)}")

if len(set(scores)) > 1:
    print("\n✅ DYNAMIC SCORES WORKING!")
    print("   Each resume has a different trust score!")
else:
    print("\n⚠️  All scores were the same")

print("=" * 60)
