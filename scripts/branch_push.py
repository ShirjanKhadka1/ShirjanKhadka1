#!/usr/bin/env python3
"""Branch + file push for the profile redesign, via the custom.github
connection (surrogate exchange). Usage:
  branch_push.py create   -- create design/cinematic-profile from main HEAD
  branch_push.py push     -- upload every file in the workdir to the branch
  branch_push.py pr       -- try creating the PR once (may 403: record it)
  branch_push.py delete-old -- delete superseded main-branch assets
Workdir files map 1:1 to repo paths, EXCEPT .github/workflows/* which
is deliberately skipped here (token lacks workflow scope).
"""
import base64
import json
import os
import sys
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

REPO = "ShirjanKhadka1/ShirjanKhadka1"
BRANCH = "design/cinematic-profile"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".github"}


def call(method, path, body=None):
    url = f"https://api.github.com/repos/{REPO}{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if body is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(body).encode()
    add_surrogate_to_request(req, "custom.github", allowed_hosts=["api.github.com"])
    try:
        with urllib.request.build_opener().open(req, timeout=60) as resp:
            return resp.status, read_json_response(resp)
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode()
        except Exception:
            detail = ""
        return e.code, {"error": detail[:500]}


def main():
    cmd = sys.argv[1]
    if cmd == "create":
        _, main_ref = call("GET", "/git/ref/heads/main")
        sha = main_ref["object"]["sha"]
        print("main HEAD", sha)
        status, data = call("POST", "/git/refs",
                            {"ref": f"refs/heads/{BRANCH}", "sha": sha})
        print("create branch:", status, json.dumps(data)[:300])
    elif cmd == "push":
        count = 0
        for base, _, files in os.walk(ROOT):
            rel_base = os.path.relpath(base, ROOT)
            if rel_base.split(os.sep)[0] in SKIP_DIRS:
                continue
            for f in sorted(files):
                if f.startswith("."):
                    continue
                local = os.path.join(base, f)
                repo_path = os.path.relpath(local, ROOT).replace(os.sep, "/")
                with open(local, "rb") as fh:
                    content = base64.b64encode(fh.read()).decode()
                body = {"message": f"Profile redesign: {repo_path}",
                        "content": content, "branch": BRANCH}
                status, data = call("GET", f"/contents/{repo_path}?ref={BRANCH}")
                if status == 200:
                    body["sha"] = data["sha"]
                status, data = call("PUT", f"/contents/{repo_path}", body)
                print(repo_path, status, (data.get("commit") or {}).get("sha", "")[:7]
                      if isinstance(data, dict) else data)
                count += 1
        print("pushed files:", count)
    elif cmd == "delete-old":
        for repo_path in ("assets/banner.svg", "assets/profile-picture-circle.png",
                          "assets/profile-picture-full.jpg", "assets/profile-picture.jpg"):
            status, data = call("GET", f"/contents/{repo_path}?ref={BRANCH}")
            if status != 200:
                print(repo_path, "not on branch, skip")
                continue
            status, data = call("DELETE", f"/contents/{repo_path}",
                                {"message": f"Profile redesign: remove superseded {repo_path}",
                                 "sha": data["sha"], "branch": BRANCH})
            print("delete", repo_path, status)
    elif cmd == "pr":
        with open(os.path.join(ROOT, "PR-BODY.md")) as fh:
            body = fh.read()
        status, data = call("POST", "/pulls",
                            {"title": "Cinematic profile redesign (dark/light, self-hosted assets)",
                             "head": BRANCH, "base": "main", "body": body})
        print("create PR:", status, json.dumps(data)[:500])
    else:
        raise SystemExit("unknown command")


if __name__ == "__main__":
    main()
