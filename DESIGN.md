# DESIGN.md — Cinematic profile, ShirjanKhadka1

## Identity
Finance Research · Open Source · Kathmandu, Nepal.
Principles: Free tools. Open code. Honest research.
Voice: confident, precise, understated. No hype, no buzzword soup,
no "guaranteed returns". This profile is not a resume: no experience
or job-history sections, by the owner's standing rule.

## Palette
| Role | Dark | Light |
|---|---|---|
| Background | #070A12 → #0B1020 | #F5F2EA → #EDE9DC |
| Gold accent | #C9A227 / #E6C35C | #9A7B14 / #C9A227 |
| Secondary | teal #7FB5B0, ice-blue #A8C8E8 | teal #2F6F6A, ice-blue #3E6B94 |
| Text | #E8ECF4 (on navy: contrast ≈ 13.5:1, AA) | #10182A (on cream: contrast ≈ 15:1, AA) |
| Muted | #9AA7C2 | #4A556E |

Dark and light variants are served with `<picture>` +
`prefers-color-scheme`. Continuity: the previous deep-navy + gold look
is kept and evolved, not replaced.

## Type
Headings: display text converted to vector paths (fontTools + DejaVu
Sans Bold, a geometric grotesque-adjacent face) so the hero and poster
titles render identically inside SVG-as-image, where webfonts cannot
load. Body/small text: safe system stacks
(`Arial, Helvetica, 'Segoe UI', sans-serif` and a mono stack for data).

## Motion rules
Hero: slow light sweep (14s), rising bars (9s, staggered), drifting
particles (11s), all CSS keyframes inside the SVG so they animate when
loaded via `<img>`. Every animation is cancelled by
`@media (prefers-reduced-motion: reduce)`. No autoplay video, no JS.

## Assets and budgets (measured 29 Oct 2026)
| Asset | Size |
|---|---|
| hero-dark.svg / hero-light.svg | 51 KB each (portrait embedded as data URI) |
| principles-dark/light.svg | 5 KB each |
| posters/poster-N-dark/light.svg (16) | 8–10 KB each |
| portrait.jpg (640px, soft warm-grey duotone, contrast-fix) | 27 KB |
| generated/skyline-*.svg | 3.5 KB each |
| generated/numbers-*.svg | 1.7 KB each |
| **Total assets** | **≈ 267 KB** (budget: < 6 MB; hero < 3 MB; each SVG < 400 KB) |

## Contrast fix (29 Oct 2026, branch design/hero-contrast-fix)

Owner's live screenshots showed the LIGHT hero as unmanaged: the gold
tagline was unreadable on cream, and the portrait circle clashed with
the soft skyline. Dark hero was acceptable and is unchanged except for
the shared portrait re-treatment. Layout, wording, skyline, and palette
family are unchanged.

- Portrait (scripts/portrait.py; generate.py embeds the new
  file into both heroes): gentle contrast compression before duotone
  (old duotone luminance p5=10, p95=243, stdev 79; new warm-grey duotone
  p5=69, p95=188, stdev 42 — blacks lifted, whites capped, still
  photographic), muted warm-grey duotone instead of navy-black/white
  (no pure black, no pure white, no saturated gold in the skin),
  feathered circular edge (~4px blur), thinner light ring (5px → 3px,
  muted #9A7B14; dark ring unchanged at 5px gold).
- Light tagline: #C9A227 on #F5F2EA was 2.16:1 (FAIL AA) and 1.99:1 on
  #EDE9DC. New deep bronze #7A5E00: 5.47:1 on #F5F2EA, 5.04:1 on
  #EDE9DC (both PASS AA). Gold is kept only for the thin rule/accents.
  Other light-hero text already passed and is unchanged: name #10182A
  15.83:1, subtitle #4A556E 6.67:1. Dark tagline #E6C35C on navy
  11.61:1 (unchanged, PASS).
- Light background: white sweep 0.12 → 0.06 opacity, vignette edge
  0.45 → 0.52, bar opacity 0.55/0.80 → 0.65/0.90, so the skyline reads
  without turning the hero dark.
- Verification (this branch): scripts/verify.py ALL GATES PASS;
  screenshots re-rendered desktop + mobile, dark + light, via
  Playwright + Meta Chromium (docs/preview/). Known remaining limit:
  at 350px the 2.39:1 letterbox scales small — inherent to the
  letterbox format, pre-existing, not introduced by this fix.
- GitHub's own profile chrome (sidebar avatar/bio/email/achievements,
  Pinned section, contribution graph/activity) is NOT controlled by
  the README and cannot be removed by a README change. This fix
  changes only what the README controls: the hero images and portrait.

## How to regenerate
```sh
python3 scripts/fetch_stats.py   # updates scripts/stats.json (keeps last-known-good on failure)
python3 scripts/generate.py      # rebuilds assets/ + generated/ from stats.json
make verify                      # gates below; screenshots land in docs/preview/
```
The GitHub Action `.github/workflows/profile-refresh.yml` runs the same
steps daily (02:30 UTC) and on manual dispatch, committing to the branch
it runs on. If a fetch fails, the previous assets stay and keep their
as_of date — never a status CI does not support.

## What was NOT done (GitHub limits, closest alternative)
- True-3D hero (Three.js/Blender animated WebP): NOT built. The SVG hero
  already meets the cinematic brief within budget, and a 3D render would
  have added weight and a render pipeline for marginal visual gain.
  SVG stays the hero; this decision is recorded, not hidden.
- Hover effects on poster cards: impossible in README (no CSS/JS).
  Alternative: high-contrast cards with a gold rule and clear link
  affordance, wrapped in `<a>`.
- Webfonts inside SVG images: impossible. Alternative: outlined display
  text (paths) + system stacks for small text.
- Contribution "snake" from a full calendar: the full calendar cannot
  be sourced cleanly with the available token scope. Alternative: an
  honestly labelled activity skyline from real per-repo commit counts.
- Market-pulse SVG from shirjankhadka.com.np data: OMITTED. No fresh,
  validated NEPSE data pipeline exists for this repo, and inventing
  NEPSE data would break the honesty rule.
- Third-party stat cards (vercel/shields): REMOVED. All badges and
  numbers are now generated locally from the GitHub API.
- Email in the README: NOT printed (spam risk; see PR body). Contact
  stays in the profile sidebar, owner's choice.

## Appendix — verification table (29 Oct 2026, local run)
See PR-BODY.md for the full table. Summary: budgets PASS, no-script /
no-external-reference grep PASS, alt text PASS, img dimensions PASS,
link checks PASS except where noted (LinkedIn 999 = bot-block, URL
verified), screenshots PASS (local preview page via Meta Chromium,
re-rendered for the contrast fix: desktop + mobile, dark + light).
Contrast-fix gates: light tagline 5.47:1/5.04:1 PASS AA (was 2.16:1
FAIL); portrait softened (see Contrast fix section); dark hero
unchanged in layout and verified visually. CI-status honesty: see
README status table; the toolkit ruff failure is real and is NOT
hidden.
