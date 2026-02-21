"""
Simple test server to verify setup
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uuid
import os
import asyncio
from datetime import datetime

app = FastAPI(title="Resume Verification API", version="1.0.0")

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for demo purposes
RESUMES: Dict[str, Dict[str, Any]] = {}
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
async def root():
    return {"message": "API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/resumes/upload")
async def upload_resume(file: UploadFile = File(...)):
    # Basic validation (filename + extension)
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    resume_id = str(uuid.uuid4())
    filename = f"{resume_id}_{os.path.basename(file.filename)}"
    path = os.path.join(UPLOAD_DIR, filename)

    # Save file to disk
    with open(path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Create initial metadata
    RESUMES[resume_id] = {
        "resume_id": resume_id,
        "filename": file.filename,
        "status": "processing",
        "uploaded_at": datetime.utcnow().isoformat() + "Z",
        "trust_score": None,
        "claims": [],
        "predictions": [],
        "blockchain_hash": None,
    }

    # Simulate background processing
    asyncio.create_task(_simulate_processing(resume_id))

    return JSONResponse({
        "resume_id": resume_id,
        "status": "processing",
        "message": "File uploaded and queued for processing",
        "processing_job_id": resume_id,
    })


async def _simulate_processing(resume_id: str):
    # Simulate work (parsing, verification, ML)
    await asyncio.sleep(2)

    # Populate with dummy results
    RESUMES[resume_id]["status"] = "completed"
    RESUMES[resume_id]["trust_score"] = {
        "overall_score": 85.0,
        "verified_count": 3,
        "doubtful_count": 0,
        "fake_count": 0,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
    RESUMES[resume_id]["claims"] = [
        {"id": "c1", "claim_type": "skill", "claim_text": "Python", "confidence": 0.98},
        {"id": "c2", "claim_type": "education", "claim_text": "B.Sc. Computer Science", "confidence": 0.9},
    ]
    RESUMES[resume_id]["predictions"] = [
        {"claim_id": "c1", "prediction": "verified", "confidence": 0.95, "shap_explanation": "Top features: GitHub activity"},
        {"claim_id": "c2", "prediction": "verified", "confidence": 0.87, "shap_explanation": "Education matches public records"},
    ]
    RESUMES[resume_id]["blockchain_hash"] = "0xdeadbeef"


@app.get("/resumes/{resume_id}")
async def get_resume(resume_id: str):
    data = RESUMES.get(resume_id)
    if not data:
        raise HTTPException(status_code=404, detail="Resume not found")
    return data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
