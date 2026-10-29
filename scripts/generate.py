#!/usr/bin/env python3
"""Self-hosted profile asset generator (stdlib + Pillow for the portrait).

Reads scripts/stats.json (fetched by scripts/fetch_stats.py, or the
checked-in copy with its as_of date) and rebuilds every SVG under
assets/ and generated/. No third-party image service is used anywhere.
Display text is converted to vector paths with fontTools + DejaVu
(system fonts cannot be relied on inside an SVG loaded via <img>);
small body text uses a safe system-font stack.
"""
import base64
import io
import json
import os
import sys

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = TTFont(BOLD)
GLYPHS = FONT.getBestCmap()
UNITS = FONT["head"].unitsPerEm
SANS = "Arial, Helvetica, 'Segoe UI', sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', monospace"

DARK = dict(bg0="#070A12", bg1="#0B1020", panel="#121A2E", line="#2A3550",
            gold="#C9A227", gold2="#E6C35C", teal="#7FB5B0", ice="#A8C8E8",
            text="#E8ECF4", muted="#9AA7C2", grid="#1E2A44")
LIGHT = dict(bg0="#F5F2EA", bg1="#EDE9DC", panel="#FFFFFF", line="#D8D2C0",
             gold="#9A7B14", gold2="#C9A227", teal="#2F6F6A", ice="#3E6B94",
             text="#10182A", muted="#4A556E", grid="#DCD6C4",
             # Contrast fix 29 Oct 2026: gold2 (#C9A227) on cream was 2.16:1
             # (FAIL). Tagline uses deep bronze #7A5E00: 5.47:1 on #F5F2EA,
             # 5.04:1 on #EDE9DC (both PASS AA). Dark variant keeps gold2.
             tagline="#7A5E00", sweep_op="0.06", vig_edge="0.52",
             bar_op="0.65", bar_op2="0.9", ring="3")

MOTION_CSS = """<style>
@keyframes sweep{0%{transform:translateX(-30%)}100%{transform:translateX(130%)}}
@keyframes rise{0%{transform:scaleY(.55)}50%{transform:scaleY(1)}100%{transform:scaleY(.55)}}
@keyframes drift{0%{transform:translateY(0);opacity:0}20%{opacity:.8}100%{transform:translateY(-160px);opacity:0}}
@keyframes glow{0%,100%{opacity:.35}50%{opacity:.7}}
.sweep{animation:sweep 14s ease-in-out infinite}
.bar{transform-origin:bottom;animation:rise 9s ease-in-out infinite}
.particle{animation:drift 11s linear infinite}
.glow{animation:glow 7s ease-in-out infinite}
@media (prefers-reduced-motion: reduce){.sweep,.bar,.particle,.glow{animation:none!important}}
</style>"""


def text_path(text, size, x, y, anchor="start"):
    """Return SVG paths for text at (x, y) baseline, using DejaVu Bold.

    Glyph coordinates are y-up, so each glyph is flipped with a negative
    y-scale; the group itself carries the fill (replaced by callers).
    """
    scale = size / UNITS
    total = 0
    for ch in text:
        g = GLYPHS.get(ord(ch))
        total += (FONT["hmtx"][g][0] * scale) if g else size * 0.5
    cx = x - total / 2 if anchor == "middle" else (x - total if anchor == "end" else x)
    out = []
    for ch in text:
        g = GLYPHS.get(ord(ch))
        if g is None or ch == " ":
            cx += (FONT["hmtx"][g][0] * scale) if g else size * 0.5
            continue
        p = SVGPathPen(GLYPHS)
        FONT.getGlyphSet()[g].draw(p)
        out.append(f'<path d="{p.getCommands()}" transform="translate({cx:.1f} {y:.1f}) scale({scale:.5f} {-scale:.5f})"/>')
        cx += FONT["hmtx"][g][0] * scale
    return '<g fill="CURRENT">' + "".join(out) + "</g>"


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def grain(pal):
    return (f'<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" '
            f'numOctaves="2"/><feColorMatrix type="saturate" values="0"/></filter>'
            f'<rect width="100%" height="100%" filter="url(#grain)" opacity="0.05"/>')


def hero(pal, portrait_b64, dark=True):
    W, H = 2400, 1004
    bars = []
    xs = [120, 260, 420, 600, 800, 1010, 1230, 1460, 1700, 1950, 2180]
    hs = [300, 430, 260, 520, 380, 610, 340, 470, 290, 560, 400]
    cols = [pal["teal"], pal["gold"], pal["ice"], pal["teal"], pal["gold2"]]
    for i, (x, h) in enumerate(zip(xs, hs)):
        col = cols[i % len(cols)]
        delay = (i % 5) * 1.3
        bars.append(
            f'<g class="bar" style="animation-delay:{delay}s">'
            f'<rect x="{x}" y="{H - 180 - h}" width="90" height="{h}" fill="{col}" opacity="{pal.get("bar_op", "0.55")}"/>'
            f'<rect x="{x + 30}" y="{H - 180 - h - 46}" width="30" height="46" fill="{col}" opacity="{pal.get("bar_op2", "0.8")}"/>'
            f'</g>')
    particles = "".join(
        f'<circle class="particle" style="animation-delay:{i * 1.7}s" cx="{200 + i * 210}" '
        f'cy="{H - 220}" r="5" fill="{pal["gold2"]}"/>' for i in range(10))
    name = text_path("SHIRJAN KHADKA", 132, 1475, 430, anchor="middle")
    name_shadow = name.replace('fill="CURRENT"', 'fill="#000000" opacity="0.55"')
    # layered depth: shadow offset, gold edge, face
    name_gold = name.replace('fill="CURRENT"', f'fill="{pal["gold"]}"')
    name_face = name.replace('fill="CURRENT"', f'fill="{pal["text"]}"')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Shirjan Khadka — Finance Research, Open Source, Kathmandu Nepal">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{pal["bg0"]}"/><stop offset="1" stop-color="{pal["bg1"]}"/></linearGradient>
<linearGradient id="sweepg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/><stop offset=".5" stop-color="#FFFFFF" stop-opacity="{pal["sweep_op"] if "sweep_op" in pal else ".12"}"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>
<radialGradient id="vig" cx=".5" cy=".45" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="{pal.get("vig_edge", ".45")}"/></radialGradient>
<clipPath id="portraitClip"><circle cx="300" cy="330" r="185"/></clipPath></defs>
{MOTION_CSS}
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<g stroke="{pal["grid"]}" stroke-width="1" opacity="0.6">
{''.join(f'<line x1="{x}" y1="{H - 180}" x2="{x - 160}" y2="{H}"/>' for x in range(0, W + 200, 200))}
{''.join(f'<line x1="0" y1="{H - 180 + i * 45}" x2="{W}" y2="{H - 180 + i * 45}"/>' for i in range(5))}
</g>
<g>{''.join(bars)}</g>
<g>{particles}</g>
<rect class="sweep" x="0" y="0" width="700" height="{H}" fill="url(#sweepg)"/>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
<g transform="translate(8 10)">{name_shadow}</g>
<g transform="translate(2 2)">{name_gold}</g>
{name_face}
<text x="1475" y="510" text-anchor="middle" font-family="{SANS}" font-size="44" letter-spacing="4" fill="{pal.get("tagline", pal["gold2"])}">FINANCE RESEARCH · OPEN SOURCE · KATHMANDU, NEPAL</text>
<text x="1475" y="580" text-anchor="middle" font-family="{SANS}" font-size="36" fill="{pal["muted"]}">Free tools. Open code. Honest research.</text>
<rect x="1175" y="630" width="600" height="4" fill="{pal["gold"]}"/>
<image href="data:image/jpeg;base64,{portrait_b64}" x="115" y="145" width="370" height="370" clip-path="url(#portraitClip)" preserveAspectRatio="xMidYMid slice"/>
<circle cx="300" cy="330" r="185" fill="none" stroke="{pal["gold"]}" stroke-width="{pal.get("ring", "5")}"/>
<circle cx="300" cy="330" r="196" fill="none" stroke="{pal["gold"]}" stroke-width="1.5" opacity="0.5"/>
{grain(pal)}
</svg>"""


def principles(pal):
    W, H = 1800, 620
    title = text_path("PRINCIPLES", 92, 900, 150, anchor="middle").replace(
        'fill="CURRENT"', f'fill="{pal["text"]}"')
    lines = [("01", "Sourced numbers", ("Source + period,", "same page as the number.")),
             ("02", "Honest downside", ("Every thesis states", "how it could be wrong.")),
             ("03", "Open code", ("Free tools anyone can", "run on their own machine."))]
    cols = ""
    for i, (n, t, (d1, d2)) in enumerate(lines):
        x = 120 + i * 560
        cols += (f'<rect x="{x}" y="210" width="500" height="300" rx="18" fill="{pal["panel"]}" '
                 f'stroke="{pal["line"]}" stroke-width="2"/>'
                 f'<text x="{x + 40}" y="290" font-family="{MONO}" font-size="34" fill="{pal["gold2"]}">{n}</text>'
                 f'<text x="{x + 40}" y="350" font-family="{SANS}" font-size="40" font-weight="bold" fill="{pal["text"]}">{esc(t)}</text>'
                 f'<text x="{x + 40}" y="410" font-family="{SANS}" font-size="26" fill="{pal["muted"]}">{esc(d1)}</text>'
                 f'<text x="{x + 40}" y="448" font-family="{SANS}" font-size="26" fill="{pal["muted"]}">{esc(d2)}</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Principles: sourced numbers, honest downside, open code">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{pal["bg0"]}"/><stop offset="1" stop-color="{pal["bg1"]}"/></linearGradient></defs>
{MOTION_CSS}
<rect width="{W}" height="{H}" fill="url(#bg)"/>{title}
<rect x="800" y="185" width="200" height="4" fill="{pal["gold"]}"/>""" + cols + "</svg>"


def poster(pal, title, value, tags, status):
    W, H = 760, 330
    t = text_path(title, 44, 40, 92).replace('fill="CURRENT"', f'fill="{pal["text"]}"')
    pills = ""
    x = 40
    for tag in tags:
        w = 18 + len(tag) * 13
        pills += (f'<rect x="{x}" y="240" width="{w}" height="38" rx="19" fill="{pal["panel"]}" '
                  f'stroke="{pal["line"]}"/><text x="{x + 14}" y="266" font-family="{MONO}" '
                  f'font-size="21" fill="{pal["muted"]}">{esc(tag)}</text>')
        x += w + 14
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)} — {esc(value)}">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{pal["bg0"]}"/><stop offset="1" stop-color="{pal["bg1"]}"/></linearGradient></defs>
<rect width="{W}" height="{H}" rx="20" fill="url(#bg)" stroke="{pal["line"]}" stroke-width="2"/>
<rect x="16" y="16" width="{W - 32}" height="{H - 32}" rx="14" fill="#FFFFFF" opacity="0.04"/>
<rect x="40" y="118" width="120" height="5" fill="{pal["gold"]}"/>""" + t + f"""
<text x="40" y="180" font-family="{SANS}" font-size="27" fill="{pal["muted"]}">{esc(value)}</text>
{pills}
<text x="40" y="305" font-family="{MONO}" font-size="20" fill="{pal["gold2"]}">{esc(status)}</text>
</svg>"""


def skyline(pal, stats):
    # Honest activity skyline: commits per finance repo, fetched via API.
    repos = stats["repos"]
    W, H = 1800, 520
    maxc = max(r["commits"] for r in repos) or 1
    bars = ""
    bw = 110
    gap = (W - 160 - bw * len(repos)) // max(len(repos) - 1, 1)
    for i, r in enumerate(repos):
        x = 80 + i * (bw + gap)
        h = int(250 * r["commits"] / maxc)
        bars += (f'<rect x="{x}" y="{H - 110 - h}" width="{bw}" height="{h}" fill="{pal["teal"] if i % 2 == 0 else pal["gold"]}" opacity="0.75"/>'
                 f'<text x="{x + bw // 2}" y="{H - 120 - h}" text-anchor="middle" font-family="{MONO}" font-size="28" fill="{pal["text"]}">{r["commits"]}</text>'
                 f'<text x="{x + bw // 2}" y="{H - 70}" text-anchor="middle" font-family="{MONO}" font-size="20" fill="{pal["muted"]}">{esc(r["short"])}</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Activity skyline: commits per finance repository, as of {stats['as_of']}">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{pal["bg0"]}"/><stop offset="1" stop-color="{pal["bg1"]}"/></linearGradient></defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<text x="80" y="70" font-family="{SANS}" font-size="38" font-weight="bold" fill="{pal["text"]}">Activity skyline — commits per repository</text>
<text x="80" y="115" font-family="{SANS}" font-size="26" fill="{pal["muted"]}">Fetched from the GitHub API, as of {stats['as_of']}. Not a contribution calendar.</text>
{bars}</svg>"""


def numbers(pal, stats):
    W, H = 1800, 420
    cells = [("7", "public finance repos"), ("232", "tests passing, locally verified"),
             ("187", "commits across those repos"), ("Python", "dominant language")]
    out = ""
    for i, (v, label) in enumerate(cells):
        x = 120 + i * 430
        out += (f'<text x="{x}" y="170" font-family="{SANS}" font-size="84" font-weight="bold" fill="{pal["gold2"]}">{v}</text>'
                f'<text x="{x}" y="230" font-family="{SANS}" font-size="30" fill="{pal["muted"]}">{label}</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="By the numbers: 7 public finance repos, 232 tests passing, 187 commits">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{pal["bg0"]}"/><stop offset="1" stop-color="{pal["bg1"]}"/></linearGradient></defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>{out}
<text x="120" y="330" font-family="{SANS}" font-size="26" fill="{pal["muted"]}">Test counts verified locally 28 Oct 2026 (toolkit 129, scanner 57, analyst-agent 46). CI status as of {stats['as_of']} in the README table.</text>
</svg>"""


POSTERS = [
    ("Finance Research Agents", "Research teams that check their own work.",
     ["Markdown", "18 agents"], "18 agents · 10 runbooks"),
    ("Investment Analyst Toolkit", "Ratios to Monte Carlo, tested and reproducible.",
     ["Python", "zero-dep"], "129 tests · CI matrix runs pass; quality gate: see note"),
    ("Equity Research Playbook", "Initiation, earnings, forensic and valuation templates.",
     ["Markdown", "templates"], "Templates · falsifier checklists"),
    ("Nepali Capital Market Research", "NEPSE structure plus a CSV-only scanner.",
     ["Python", "NEPSE"], "57 scanner tests"),
    ("Nepal Market Research", "Sourced NEPSE case studies, honestly labelled.",
     ["Research", "BNT"], "BNT study: inputs only, not a valuation"),
    ("Nepali Business Opportunities", "Opportunity scorecard, ranked only by evidence.",
     ["Research", "8 sectors"], "Sectors alphabetical, not ranked"),
    ("Financial Research Analyst Agent", "Technicals, Piotroski, valuation, debate and Risk Veto.",
     ["Python", "pipeline"], "46 tests"),
    ("NEPSE Tools — Nepse Decode", "Public NEPSE tools on the portfolio site.",
     ["Web", "NEPSE"], "External site · portfolio link"),
]


def main():
    with open(os.path.join(ROOT, "scripts", "stats.json")) as f:
        stats = json.load(f)
    assets = os.path.join(ROOT, "assets")
    gen = os.path.join(ROOT, "generated")
    os.makedirs(assets, exist_ok=True)
    os.makedirs(os.path.join(assets, "posters"), exist_ok=True)
    os.makedirs(gen, exist_ok=True)
    with open(os.path.join(assets, "portrait.jpg"), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    for name, pal, dark in (("hero-dark", DARK, True), ("hero-light", LIGHT, False)):
        with open(os.path.join(assets, f"{name}.svg"), "w") as f:
            f.write(hero(pal, b64, dark))
    for name, pal in (("principles-dark", DARK), ("principles-light", LIGHT)):
        with open(os.path.join(assets, f"{name}.svg"), "w") as f:
            f.write(principles(pal))
    for i, (title, value, tags, status) in enumerate(POSTERS):
        for variant, pal in (("dark", DARK), ("light", LIGHT)):
            with open(os.path.join(assets, "posters", f"poster-{i + 1}-{variant}.svg"), "w") as f:
                f.write(poster(pal, title, value, tags, status))
    for name, pal in (("skyline-dark", DARK), ("skyline-light", LIGHT)):
        with open(os.path.join(gen, f"{name}.svg"), "w") as f:
            f.write(skyline(pal, stats))
    for name, pal in (("numbers-dark", DARK), ("numbers-light", LIGHT)):
        with open(os.path.join(gen, f"{name}.svg"), "w") as f:
            f.write(numbers(pal, stats))
    print("generated: hero x2, principles x2, posters x16, skyline x2, numbers x2")


if __name__ == "__main__":
    main()
