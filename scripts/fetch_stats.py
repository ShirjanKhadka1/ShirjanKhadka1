#!/usr/bin/env python3
"""Fetch public repo stats via the GitHub REST API and write stats.json.

Uses GITHUB_TOKEN when set (the profile-refresh workflow provides it);
otherwise unauthenticated public reads. Commit counts come from the
Link header's last page on /commits?per_page=1. Test counts are NOT
typed here: they are read from each owning repo's live generated
status.json on main (raw.githubusercontent.com); the agents pack keeps
its status at ops/status.json, which also supplies the agents and
runbooks counts. On any fetch failure the previous stats.json is kept
untouched (last-known-good rule).
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
# Owning repos' generated status.json files: the live test counts,
# fetched, never typed. (Previously this script hardcoded TESTS =
# {toolkit: 129, scanner: 57, analyst: 46} with no playbook entry, so
# even a successful fetch published stale totals -- 232 instead of
# the true 413 on 7 Nov 2026.)
STATUS_JSON = {
    "investment-analyst-toolkit":
        "https://raw.githubusercontent.com/ShirjanKhadka1/investment-analyst-toolkit/main/status.json",
    "nepali-capital-market-research":
        "https://raw.githubusercontent.com/ShirjanKhadka1/nepali-capital-market-research/main/status.json",
    "financial-research-analyst-agent":
        "https://raw.githubusercontent.com/ShirjanKhadka1/financial-research-analyst-agent/main/status.json",
    "equity-research-playbook":
        "https://raw.githubusercontent.com/ShirjanKhadka1/equity-research-playbook/main/status.json",
}
AGENTS_STATUS_JSON = ("https://raw.githubusercontent.com/ShirjanKhadka1/"
                      "finance-research-agents/main/ops/status.json")


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "profile-refresh"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.headers, json.loads(resp.read() or b"{}")


def get_json(url):
    _, data = get(url)
    return data


def main():
    import datetime
    # Agents/runbooks come from the agents pack's generated status.
    agents_status = get_json(AGENTS_STATUS_JSON)
    agents = agents_status.get("agents")
    runbooks = agents_status.get("runbooks")
    if agents is None or runbooks is None:
        raise ValueError("agents ops/status.json has no agents/runbooks counts")
    # Test counts come from each owning repo's live status.json.
    tests_by_repo = {}
    for repo, url in STATUS_JSON.items():
        data = get_json(url)
        total = data.get("tests_total")
        if total is None:
            raise ValueError(f"{repo} status.json has no tests_total")
        tests_by_repo[repo] = total
    out = {"as_of": datetime.date.today().isoformat(),
           "source": "GitHub REST API (commit counts) + owning repos' live status.json on main (test counts, raw.githubusercontent.com)",
           "repos": [], "totals": {},
           "ci_note": ("Test counts read from each owning repo's live status.json "
                       "(no hardcoded counts); agents/runbooks from "
                       "finance-research-agents ops/status.json. Commit counts "
                       "from the GitHub REST API.")}
    total_commits = total_tests = 0
    for repo in REPOS:
        headers, _ = get(f"https://api.github.com/repos/{OWNER}/{repo}/commits?per_page=1")
        link = headers.get("Link", "")
        m = re.search(r'page=(\d+)>; rel="last"', link)
        commits = int(m.group(1)) if m else 1
        tests = tests_by_repo.get(repo)
        out["repos"].append({"name": repo, "short": SHORT[repo], "commits": commits,
                             "tests": tests})
        total_commits += commits
        total_tests += tests or 0
    out["totals"] = {"finance_repos": len(REPOS), "programme_repos_incl_profile": 8,
                     "commits_finance_repos": total_commits, "tests_total": total_tests,
                     "agents": agents, "runbooks": runbooks}
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
