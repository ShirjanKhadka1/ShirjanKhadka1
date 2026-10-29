#!/usr/bin/env python3
"""Preview screenshots via Playwright + the local Meta Chromium binary.

Renders docs/preview/preview.html (a faithful local rendering of the
README's images and layout) at 900px and 350px, dark and light.
This is a LOCAL preview: github.com cannot show the new profile until
the PR merges, so screenshots of github.com would show the OLD profile
and would be misleading. That substitution is recorded in DESIGN.md.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "preview")
os.makedirs(OUT, exist_ok=True)

HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0 auto;max-width:900px;padding:16px;font-family:Arial,Helvetica,sans-serif;background:#0d1117;color:#e6edf3}
body.light{background:#ffffff;color:#1f2328}
img{max-width:100%;height:auto;display:block;margin:12px auto}
table{width:100%;border-collapse:collapse}td{padding:6px;vertical-align:top}
h2{border-bottom:1px solid #30363d;padding-bottom:6px}
</style></head><body class="MODE"><h1>Shirjan Khadka — preview</h1>
<picture><source media="(prefers-color-scheme: light)" srcset="../../assets/hero-light.svg"><img src="../../assets/hero-dark.svg" alt="hero" width="1200" height="502"></picture>
<h2>Now Showing</h2><table><tr><td>POSTER1</td><td>POSTER2</td></tr></table>
<h2>By the numbers</h2>
<picture><source media="(prefers-color-scheme: light)" srcset="../../generated/numbers-light.svg"><img src="../../generated/numbers-dark.svg" alt="numbers" width="900" height="210"></picture>
<picture><source media="(prefers-color-scheme: light)" srcset="../../generated/skyline-light.svg"><img src="../../generated/skyline-dark.svg" alt="skyline" width="900" height="260"></picture>
<h2>Principles</h2>
<picture><source media="(prefers-color-scheme: light)" srcset="../../assets/principles-light.svg"><img src="../../assets/principles-dark.svg" alt="principles" width="900" height="310"></picture>
</body></html>"""


def main():
    from playwright.sync_api import sync_playwright
    for mode in ("dark", "light"):
        html = HTML.replace("MODE", mode)
        html = html.replace("POSTER1", '<img src="../../assets/posters/poster-1-dark.svg" alt="poster 1" width="430" height="187">')
        html = html.replace("POSTER2", '<img src="../../assets/posters/poster-2-dark.svg" alt="poster 2" width="430" height="187">')
        path = os.path.join(OUT, f"preview-{mode}.html")
        with open(path, "w") as f:
            f.write(html)
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path="/opt/meta-chromium/chrome",
                                        args=["--no-sandbox"])
            for width, label in ((900, "desktop"), (350, "mobile")):
                page = browser.new_page(viewport={"width": width, "height": 1200},
                                        color_scheme=mode)
                page.goto("file://" + path)
                page.wait_for_timeout(2500)
                out = os.path.join(OUT, f"{label}-{mode}.png")
                page.screenshot(path=out, full_page=True)
                print(out)
            browser.close()


if __name__ == "__main__":
    main()
