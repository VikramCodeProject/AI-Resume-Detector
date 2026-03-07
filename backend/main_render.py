"""Render-safe backend entrypoint.

Behavior:
- BACKEND_MODE=full: try to load full app from main.py
- Otherwise (default): load minimal app from main_minimal.py
- If full load fails, automatically fall back to minimal app
"""

import logging
import os
from datetime import datetime, timezone

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mode = os.getenv("BACKEND_MODE", "minimal").strip().lower()
active_mode = "minimal"
fallback_used = False
fallback_reason = ""

if mode == "full":
    try:
        from main import app as full_app

        app = full_app
        active_mode = "full"
        logger.info("Loaded FULL backend app (BACKEND_MODE=full)")
    except Exception as exc:
        from main_minimal import app as minimal_app

        app = minimal_app
        active_mode = "minimal"
        fallback_used = True
        fallback_reason = str(exc)
        logger.exception("Full app failed to load. Falling back to minimal app. Error: %s", exc)
else:
    from main_minimal import app as minimal_app

    app = minimal_app
    active_mode = "minimal"
    logger.info("Loaded MINIMAL backend app (BACKEND_MODE=%s)", mode)


if isinstance(app, FastAPI):
    @app.get("/api/mode")
    def get_runtime_mode():
        return {
            "configured_mode": mode,
            "active_mode": active_mode,
            "fallback_used": fallback_used,
            "fallback_reason": fallback_reason,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
