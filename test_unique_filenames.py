#!/usr/bin/env python3
"""
Test Unique Trust Scores Per File
Proves: Same filename = same score, Different filename = different score
"""
import requests
import time

API = "http://localhost:8000"

print("=" * 70)
print("TESTING UNIQUE SCORES PER UNIQUE FILENAME")
print("=" * 70)

# Register
print("\n1. Registering user...")
try:
    requests.post(f"{API}/api/auth/register", json={
        "email": "uniquetest@example.com",
        "password": "password123",
        "full_name": "Test User",
        "gdpr_consent": True
    })
except:
    pass
print("✅ Ready")

# Login
res = requests.post(f"{API}/api/auth/login", json={
    "email": "uniquetest@example.com",
    "password": "password123"
})
token = res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("\n2. Testing: SAME FILE = SAME SCORE")
print("-" * 70)

# Upload same file twice
same_file_scores = []
for i in range(2):
    filename = "john_doe_resume.pdf"  # SAME filename
    files = {"file": (filename, "John Doe - Senior Engineer at Google and Meta")}
    
    res = requests.post(f"{API}/api/resumes/upload", files=files, headers=headers)
    resume_id = res.json()["resume_id"]
    
    time.sleep(0.3)
    res = requests.get(f"{API}/api/resumes/{resume_id}", headers=headers)
    trust_score = res.json().get("trust_score", {})
    score = trust_score.get("overall_score", "N/A")
    
    same_file_scores.append(score)
    print(f"   Upload {i+1} ('{filename}'): Score={score}")

if same_file_scores[0] == same_file_scores[1]:
    print(f"   ✅ SAME FILE = SAME SCORE ({same_file_scores[0]})")
else:
    print(f"   ⚠️  Different scores for same file!")

print("\n3. Testing: DIFFERENT FILES = DIFFERENT SCORES")
print("-" * 70)

different_files = [
    "alice_smith_cv.pdf",
    "bob_johnson_experience.docx",
    "carol_williams_profile.pdf",
    "david_brown_resume.docx",
    "emma_davis_background.pdf"
]

scores_by_file = {}
for filename in different_files:
    files = {"file": (filename, f"Resume content for {filename}")}
    
    res = requests.post(f"{API}/api/resumes/upload", files=files, headers=headers)
    resume_id = res.json()["resume_id"]
    
    time.sleep(0.3)
    res = requests.get(f"{API}/api/resumes/{resume_id}", headers=headers)
    trust_score = res.json().get("trust_score", {})
    score = trust_score.get("overall_score", "N/A")
    
    scores_by_file[filename] = score
    print(f"   {filename}: Score={score}")

# Check uniqueness
unique_scores = len(set(scores_by_file.values()))
print(f"\n   Found {unique_scores} unique scores out of {len(different_files)} files")

if unique_scores == len(different_files):
    print(f"   ✅ ALL FILES HAVE UNIQUE SCORES!")
else:
    duplicates = len(different_files) - unique_scores
    print(f"   ⚠️  {duplicates} files share the same score")

print("\n" + "=" * 70)
print("SUMMARY:")
print(f"  Same filename uploaded twice: {same_file_scores[0]} == {same_file_scores[1]} {'✅' if same_file_scores[0] == same_file_scores[1] else '❌'}")
print(f"  Different filenames are unique: {unique_scores}/{len(different_files)} {'✅' if unique_scores == len(different_files) else '❌'}")
print("=" * 70)
