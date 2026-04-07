from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = PROJECT_ROOT / "backend"
UTCNOW_PATTERN = re.compile(r"\bdatetime\.utcnow\s*\(")


def test_backend_has_no_datetime_utcnow_calls():
    offenders = []

    for py_file in BACKEND_PATH.rglob("*.py"):
        try:
            text = py_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            if UTCNOW_PATTERN.search(line):
                relative_path = py_file.relative_to(PROJECT_ROOT).as_posix()
                offenders.append(f"{relative_path}:{line_number}: {line.strip()}")

    assert not offenders, "datetime.utcnow() is deprecated. Use utc_now()/utc_now_iso() from backend/utils/time_utils.py.\n" + "\n".join(offenders)
