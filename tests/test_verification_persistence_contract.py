from pathlib import Path
import sys
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = PROJECT_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from main import app  # noqa: E402


def test_verify_full_direct_mode_persists_verification_entries():
    client = TestClient(app, base_url="http://127.0.0.1")

    import api.routes as routes_module

    routes_module._verification_results_fallback.clear()

    original_verify_full = routes_module.verify_full
    mock_verify_full = MagicMock()
    mock_verify_full.delay = MagicMock(side_effect=RuntimeError("celery-down"))
    routes_module.verify_full = mock_verify_full

    github_result = {
        "username": "octocat",
        "github_authenticity_score": 83.0,
        "risk_level": "Low",
    }

    certificate_result = {
        "authenticity_score": 76.5,
        "is_authentic": True,
    }

    with patch("api.routes.get_github_service") as mock_github_get, patch("api.routes.get_ocr_service") as mock_ocr_get:
        mock_github = mock_github_get.return_value
        mock_github.verify_profile = AsyncMock(return_value=github_result)

        mock_ocr = mock_ocr_get.return_value
        mock_ocr.verify_certificate = AsyncMock(return_value=certificate_result)

        response = client.post(
            "/api/verify/full",
            json={
                "resume_id": "resume-persist-001",
                "github_username": "octocat",
                "certificate_image_paths": ["cert-a.png"],
                "claimed_skills": ["python"],
                "resume_text": "test resume text",
            },
        )

    routes_module.verify_full = original_verify_full

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    persisted = routes_module._verification_results_fallback.get("resume-persist-001", [])
    assert len(persisted) >= 2
    assert any(entry.get("source") == "github" for entry in persisted)
    assert any(entry.get("source") == "aggregate" for entry in persisted)
