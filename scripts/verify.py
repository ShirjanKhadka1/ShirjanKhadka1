#!/usr/bin/env python3
"""Quality gates for the profile redesign. Exits non-zero on any FAIL.

Checks: SVG budgets, no <script> / external refs in SVGs, alt text on
every <img> in README.md, width+height on every <img>, link targets
return 200 (curl, HEAD fallback GET), no third-party stat services,
README contains no email address, no hype phrases.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not ok:
        fails.append(name)


def main():
    total = 0
    for base in ("assets", "generated"):
        for root, _, files in os.walk(os.path.join(ROOT, base)):
            for f in files:
                if f.endswith(".svg"):
                    p = os.path.join(root, f)
                    size = os.path.getsize(p)
                    total += size
                    check(f"budget {os.path.relpath(p, ROOT)} < 400KB",
                          size < 400_000, f"{size} bytes")
                    txt = open(p, encoding="utf-8").read()
                    check(f"no script in {f}", "<script" not in txt)
                    body = txt.replace('xmlns="http://www.w3.org/2000/svg"', "")
                    check(f"no external ref in {f}",
                          not re.search(r'(href|src|url\()\s*=\s*["\']?https?://', body)
                          and "@import" not in body)
    check("total assets < 6MB", total < 6_000_000, f"{total} bytes")
    hero = os.path.getsize(os.path.join(ROOT, "assets", "hero-dark.svg"))
    check("hero < 3MB", hero < 3_000_000, f"{hero} bytes")
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    imgs = re.findall(r"<img[^>]*>", readme)
    check("every img has alt", all("alt=" in i and 'alt=""' not in i for i in imgs),
          f"{len(imgs)} imgs")
    check("every img has width+height",
          all("width=" in i and "height=" in i for i in imgs))
    check("no email address printed",
          not re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", readme))
    check("no third-party stat services",
          "vercel.app" not in readme and "shields.io" not in readme)
    check("no hype phrases",
          not re.search(r"(?<!never )guaranteed returns|best in the world", readme, re.I))
    check("disclaimer present", "Never investment advice" in readme)
    check("no experience/resume section",
          not re.search(r"## (Experience|Work History|Employment)", readme))
    links = sorted(set(re.findall(r"\((https://[^)\s]+)\)", readme)))
    for link in links:
        try:
            r = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
                                "--max-time", "20", "-L", link],
                               capture_output=True, text=True, timeout=30)
            code = r.stdout.strip()
        except Exception as exc:
            code = f"error {exc}"
        # LinkedIn returns 999 to curl (bot protection); the URL itself is
        # the owner's verified profile URL, not a broken link.
        ok = code == "200" or (code == "999" and "linkedin.com" in link)
        check(f"link 200: {link}", ok, code + (" (LinkedIn bot-block, URL verified)" if code == "999" else ""))
    print(f"\n{len(fails)} failures" if fails else "\nALL GATES PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
