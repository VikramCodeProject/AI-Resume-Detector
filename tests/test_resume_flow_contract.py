from pathlib import Path
import sys
from uuid import uuid4

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = PROJECT_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from main import app  # noqa: E402


def _register_and_login(client: TestClient):
    email = f"resume-flow-{uuid4().hex}@example.com"
    password = "Password123!"

    register_payload = {
        "email": email,
        "password": password,
        "full_name": "Resume Flow User",
        "gdpr_consent": True,
        "role": "candidate",
    }
    register_response = client.post("/api/auth/register", json=register_payload)
    assert register_response.status_code in (200, 201)

    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def test_resume_upload_detail_and_trust_score_contracts():
    client = TestClient(app, base_url="http://127.0.0.1")
    access_token = _register_and_login(client)
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    upload_response = client.post(
        "/api/resumes/upload",
        headers=auth_headers,
        files={"file": ("sample_resume.pdf", b"%PDF-1.4\nFake resume bytes", "application/pdf")},
    )

    assert upload_response.status_code == 200
    upload_body = upload_response.json()
    assert "resume_id" in upload_body

    resume_id = upload_body["resume_id"]

    detail_response = client.get(f"/api/resumes/{resume_id}", headers=auth_headers)
    assert detail_response.status_code == 200
    detail_body = detail_response.json()
    assert detail_body["resume_id"] == resume_id
    assert detail_body["filename"] == "sample_resume.pdf"

    trust_response = client.get(f"/api/resumes/{resume_id}/trust-score", headers=auth_headers)
    assert trust_response.status_code == 200
    trust_body = trust_response.json()
    assert "overall_score" in trust_body
    assert "verified_count" in trust_body
    assert "doubtful_count" in trust_body
    assert "fake_count" in trust_body
