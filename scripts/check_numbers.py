#!/usr/bin/env python3
"""Round 3 number check: fail if any checked file carries a count that
disagrees with status.json.

Usage: python3 scripts/check_numbers.py [--root REPO_ROOT]
Exit 0 only when every checked prose count matches status.json, every
cheap file count re-counted from disk matches status.json, and (where
the repo has a test suite) the suite recorded in status.json is green
(tests_passed == tests_total) -- because the prose claims "passing".

How historical numbers are handled: a match is skipped ONLY when an
exact allowlisted substring (which includes the historical number
itself) appears next to the match. Changing a historical number breaks
its allowlist entry, so the check fails instead of silently passing.
Historical lines are therefore preserved, not laundered.

This checker does not re-run the test suite; in CI the workflow runs
scripts/generate_status.py first, so status.json is fresh when this
check runs. Locally, run the generator first, then this check.
"""
import argparse
import json
import re
from pathlib import Path

# ---- per-repo spec (Round 3) ----
STATUS_FIELDS = ["repo", "agents", "runbooks", "tests_total", "sectors", "generated_by", "generated_at"]
PROSE_FILES = ["README.md"]
PATTERNS = [
    (r"(\d+) agents", "agents", "agent count"),
    (r"(\d+) runbooks", "runbooks", "runbook count"),
    (r"(\d+) sectors", "sectors", "sector count"),
    (r"Investment Analyst Toolkit \| (\d+)/(\d+)", "toolkit_tests", "toolkit status-table tests"),
    (r"Nepali Capital Market Research \(scanner\) \| (\d+)/(\d+)", "scanner_tests", "scanner status-table tests"),
    (r"Financial Research Analyst Agent \| (\d+)/(\d+)", "analyst_tests", "analyst status-table tests"),
    (r"Equity Research Playbook \| (\d+)/(\d+)", "playbook_tests", "playbook status-table tests"),
    (r"Toolkit poster: (\d+) tests", "toolkit_tests", "toolkit poster tests"),
    (r"scanner, (\d+) tests", "scanner_tests", "scanner poster tests"),
    (r"Analyst Agent poster: (\d+) tests", "analyst_tests", "analyst poster tests"),
]
ALLOWLIST = []
FILE_COUNTS = []
REQUIRE_GREEN = False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    root = Path(ap.parse_args().root)
    status_path = root / "status.json"
    errors = []
    if not status_path.exists():
        print(f"FAIL: {status_path} missing; run the generate_status.py script first")
        return 1
    status = json.loads(status_path.read_text(encoding="utf-8"))
    for field in STATUS_FIELDS:
        if field not in status:
            errors.append(f"status.json missing field: {field}")
    for glob, field, desc in FILE_COUNTS:
        found = len([p for p in root.glob(glob) if p.is_file()])
        want = status.get(field)
        if want is not None and found != want:
            errors.append(f"file count {desc}: disk={found} status.json {field}={want}")
    if REQUIRE_GREEN and status.get("tests_passed") is not None:
        if status["tests_passed"] != status.get("tests_total"):
            errors.append(
                f"suite not green in status.json: "
                f"{status['tests_passed']}/{status.get('tests_total')}")
    for rel in PROSE_FILES:
        path = root / rel
        if not path.exists():
            errors.append(f"checked file missing: {rel}")
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for regex, field, desc in PATTERNS:
                for m in re.finditer(regex, line):
                    window = line[max(0, m.start() - 30):m.end() + 30]
                    if any(a in window for a in ALLOWLIST):
                        continue
                    want = status.get(field)
                    if want is None:
                        continue  # field TO VERIFY: nothing to check against
                    try:
                        got = int(m.group(1))
                        if m.re.groups >= 2 and m.group(2) is not None:
                            got2 = int(m.group(2))
                            if got2 != want:
                                errors.append(
                                    f"{rel}:{lineno}: {desc} says {got}/{got2}, "
                                    f"status.json {field}={want}: {line.strip()[:140]}")
                                continue
                    except (IndexError, ValueError):
                        continue
                    if got != want:
                        errors.append(
                            f"{rel}:{lineno}: {desc} says {got}, "
                            f"status.json {field}={want}: {line.strip()[:140]}")
    per_repo = ["toolkit_tests", "scanner_tests", "analyst_tests", "playbook_tests"]
    if all(status.get(f) is not None for f in per_repo) and status.get("tests_total") is not None:
        if sum(status[f] for f in per_repo) != status["tests_total"]:
            errors.append(
                f"status.json tests_total={status['tests_total']} != sum of per-repo tests "
                f"{sum(status[f] for f in per_repo)}")
    if errors:
        print("FAIL: number check found disagreements:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS: all checked numbers agree with status.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
