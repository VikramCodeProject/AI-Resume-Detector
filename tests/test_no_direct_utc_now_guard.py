from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = PROJECT_ROOT / "backend"
TIME_UTILS_PATH = (BACKEND_PATH / "utils" / "time_utils.py").resolve()
DIRECT_UTC_NOW_PATTERN = re.compile(r"\bdatetime\.now\s*\(\s*UTC\s*\)")


def test_backend_uses_time_helpers_instead_of_direct_datetime_now_utc():
    offenders = []

    for py_file in BACKEND_PATH.rglob("*.py"):
        resolved = py_file.resolve()
        if resolved == TIME_UTILS_PATH:
            continue

        try:
            text = py_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            if DIRECT_UTC_NOW_PATTERN.search(line):
                relative_path = py_file.relative_to(PROJECT_ROOT).as_posix()
                offenders.append(f"{relative_path}:{line_number}: {line.strip()}")

    assert not offenders, (
        "Use utc_now()/utc_now_iso() from backend/utils/time_utils.py instead of direct datetime.now(UTC).\n"
        + "\n".join(offenders)
    )
