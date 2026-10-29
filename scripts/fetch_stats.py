#!/usr/bin/env python3
"""Fetch public repo stats via the GitHub REST API and write stats.json.

Uses GITHUB_TOKEN when set (the profile-refresh workflow provides it);
otherwise unauthenticated public reads. Commit counts come from the
Link header's last page on /commits?per_page=1. On any fetch failure
the previous stats.json is kept untouched (last-known-good rule).
"""
import json
import os
import re
import sys
import urllib.request

OWNER = "ShirjanKhadka1"
REPOS = ["finance-research-agents", "investment-analyst-toolkit",
         "equity-research-playbook", "nepali-capital-market-research",
         "nepal-market-research", "nepali-business-opportunities",
         "financial-research-analyst-agent"]
SHORT = {"finance-research-agents": "agents", "investment-analyst-toolkit": "toolkit",
         "equity-research-playbook": "playbook", "nepali-capital-market-research": "scanner",
         "nepal-market-research": "nepal-mkt", "nepali-business-opportunities": "biz-opp",
         "financial-research-analyst-agent": "analyst"}
TESTS = {"investment-analyst-toolkit": 129, "nepali-capital-market-research": 57,
         "financial-research-analyst-agent": 46}


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "profile-refresh"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.headers, json.loads(resp.read() or b"{}")


def main():
    import datetime
    out = {"as_of": datetime.date.today().isoformat(),
           "source": "GitHub REST API, public repositories",
           "repos": [], "totals": {}, "ci_note": ""}
    total_commits = total_tests = 0
    for repo in REPOS:
        headers, _ = get(f"https://api.github.com/repos/{OWNER}/{repo}/commits?per_page=1")
        link = headers.get("Link", "")
        m = re.search(r'page=(\d+)>; rel="last"', link)
        commits = int(m.group(1)) if m else 1
        tests = TESTS.get(repo)
        out["repos"].append({"name": repo, "short": SHORT[repo], "commits": commits,
                             "tests": tests})
        total_commits += commits
        total_tests += tests or 0
    out["totals"] = {"finance_repos": len(REPOS), "programme_repos_incl_profile": 8,
                     "commits_finance_repos": total_commits, "tests_total": total_tests}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out["totals"]))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # keep last-known-good on failure
        print(f"fetch failed, keeping previous stats.json: {exc}", file=sys.stderr)
        sys.exit(0)
