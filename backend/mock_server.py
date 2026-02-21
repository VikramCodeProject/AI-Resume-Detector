from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid

app = FastAPI(title="ResumeVerify Mock Server", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/resumes/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Accepts a file upload and returns a mock resume id."""
    rid = f"mock-{uuid.uuid4()}"
    # read a small chunk (do not store)
    await file.read(1024)
    return JSONResponse({
        "resume_id": rid,
        "status": "processing",
        "message": "Mock upload accepted",
        "processing_job_id": f"job-{uuid.uuid4()}"
    })


@app.get("/api/resumes/{resume_id}")
async def get_resume(resume_id: str):
    """Return a simulated completed result for any resume id."""
    return JSONResponse({
        "resume_id": resume_id,
        "filename": "mock_resume.pdf",
        "status": "completed",
        "uploaded_at": datetime.utcnow().isoformat(),
        "trust_score": {"overall_score": 82.0, "verified_count": 5, "doubtful_count": 1, "fake_count": 0, "generated_at": datetime.utcnow().isoformat()},
        "claims": []
    })
