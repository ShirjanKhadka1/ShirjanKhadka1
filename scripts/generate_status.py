#!/usr/bin/env python3
"""Round 3 status generator for the profile repo (ShirjanKhadka1).

The profile repo has no code of its own, so its counts come from the
owning repos' status.json files -- fetched, never typed:
- default: fetch each repo's status.json from raw.githubusercontent.com
  (main branch) -- the committed, generated artifact of that repo.
- --from-dir DIR: read status.json files from a local directory of
  per-repo status files instead (used to generate the Round 3 PR, where
  the owning status.json files live on their R3 branches, not main yet).
  After all R3 PRs merge, re-running with the default must reproduce
  the same numbers; if it does not, the profile numbers are stale.
Any repo whose status.json cannot be fetched/read is recorded as
TO VERIFY (null), never guessed. Writes status.json.
"""
import argparse
import json
import urllib.request
from datetime import date
from pathlib import Path

REPOS = {
    "finance-research-agents": ("agents", "runbooks"),
    "investment-analyst-toolkit": ("tests_total",),
    "financial-research-analyst-agent": ("tests_total",),
    "nepali-capital-market-research": ("tests_total",),
    "nepal-market-research": ("case_studies", "datasets"),
    "nepali-business-opportunities": ("sectors",),
    "equity-research-playbook": ("tests_total", "templates"),
}
RAW = "https://raw.githubusercontent.com/ShirjanKhadka1/{repo}/main/status.json"


def fetch(repo, from_dir):
    if from_dir:
        p = Path(from_dir) / f"{repo}.status.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        p2 = Path(from_dir) / repo / "status.json"
        if p2.exists():
            return json.loads(p2.read_text(encoding="utf-8"))
        return None
    try:
        with urllib.request.urlopen(RAW.format(repo=repo), timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--from-dir", default=None)
    args = ap.parse_args()
    root = Path(args.root)
    per_repo = {}
    for repo in REPOS:
        data = fetch(repo, args.from_dir)
        per_repo[repo] = data
    def get(repo, field):
        d = per_repo.get(repo)
        return d.get(field) if d else None
    agents = get("finance-research-agents", "agents")
    runbooks = get("finance-research-agents", "runbooks")
    # agents status.json lives at ops/status.json, not the repo root;
    # the fetch above looks for <repo>/status.json, so also try ops/ for it.
    if agents is None and not args.from_dir:
        try:
            with urllib.request.urlopen(
                    "https://raw.githubusercontent.com/ShirjanKhadka1/finance-research-agents/main/ops/status.json",
                    timeout=30) as r:
                d = json.loads(r.read().decode())
                agents, runbooks = d.get("agents"), d.get("runbooks")
                per_repo["finance-research-agents"] = d
        except Exception:
            pass
    toolkit = get("investment-analyst-toolkit", "tests_total")
    analyst = get("financial-research-analyst-agent", "tests_total")
    scanner = get("nepali-capital-market-research", "tests_total")
    playbook = get("equity-research-playbook", "tests_total")
    tests = [t for t in (toolkit, analyst, scanner, playbook) if t is not None]
    status = {
        "repo": "ShirjanKhadka1",
        "agents": agents,
        "runbooks": runbooks,
        "toolkit_tests": toolkit,
        "analyst_tests": analyst,
        "scanner_tests": scanner,
        "playbook_tests": playbook,
        "tests_total": sum(tests) if len(tests) == 4 else None,
        "tests_note": ("sum of the four owning repos' status.json tests_total; "
                       "null if any owning status.json was unfetchable (TO VERIFY)")
                       if len(tests) != 4 else
                       "sum of toolkit + analyst-agent + scanner + playbook tests_total, "
                       "each from that repo's generated status.json",
        "sectors": get("nepali-business-opportunities", "sectors"),
        "generated_by": "scripts/generate_status.py (Round 3: fetched owning repos' status.json)",
        "generated_at": date.today().isoformat(),
        "method": ("fetched from raw.githubusercontent.com main-branch status.json files"
                   if not args.from_dir else
                   f"read from local status files under {args.from_dir} (R3 branch artifacts); "
                   "re-run with the default after the R3 PRs merge to confirm"),
        "sources": {repo: ("fetched" if per_repo.get(repo) else "TO VERIFY: unfetchable")
                    for repo in REPOS},
    }
    (root / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
