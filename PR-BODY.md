# PR: Cinematic profile redesign — ShirjanKhadka1

## What this does
Redesigns the special profile README into a professional, cinematic,
modern-aesthetic profile: deep-navy + gold (continuing the current look),
letterbox hero with an isometric financial skyline, duotone portrait
(used once, in the hero only), movie-poster project cards for all 7
public finance repos plus the public NEPSE tools site, capabilities,
real-number stats, principles card, and credits. Dark + light variants
via `<picture>` + `prefers-color-scheme`. All graphics are generated
locally in this repo — the vercel/shields third-party stat cards are
removed entirely.

## Verification table (`make verify`, 29 Oct 2026, local run)
| Gate | Result |
|---|---|
| SVG budgets (each < 400 KB; hero < 3 MB; total < 6 MB) | PASS — hero 62 KB each, total assets ≈ 372 KB |
| No `<script>` in any SVG | PASS |
| No external references in any SVG (namespace excluded) | PASS |
| Every `<img>` has alt text | PASS (12 imgs) |
| Every `<img>` has width + height | PASS |
| No email address printed in README | PASS |
| No third-party stat services | PASS |
| No hype phrases / no experience-resume sections | PASS |
| Disclaimer present | PASS |
| All links return 200 | PASS — except LinkedIn, which returns 999 to curl (bot protection); the URL is the owner's verified profile URL |
| Screenshots 900px + 350px, dark + light | PASS — local preview page via Meta Chromium (see note below) |
| Reduced-motion respected | PASS — CSS keyframes cancelled by `prefers-reduced-motion` query |
| Spell-check | PASS — careful manual pass (aspell is not installed in this environment, so no automated spell-check ran; copy was proofread) |
| Contrast WCAG AA | PASS — navy/off-white ≈ 13.5:1; cream/navy ≈ 15:1 |

Screenshot note: screenshots are of a local preview page, not
github.com — github.com cannot show the new profile until this PR
merges, so a github.com screenshot would show the OLD profile and be
misleading. Two screenshot-round defects were found and fixed before
this PR: hero name/tagline colliding with the portrait, and principles
descriptions overflowing their cards.

## Honest CI note (please read before merging)
The README does NOT label any repo "Live" on CI grounds, because the
latest CI picture is mixed (29 Oct 2026): the toolkit's Tests matrix
jobs pass on ubuntu/macOS/Windows, but its quality (ruff) job fails on
`tests/test_phase9_ensemble.py` (RUF015). That fix belongs in the
toolkit repo, not in this profile repo. The scanner and analyst-agent
latest Tests runs also show failure; job-level detail was not yet
confirmed when this PR was built, so no green claim is made for them
either. CodeQL runs for the code repos completed successfully on
28 Oct 2026. Test counts quoted (129 / 57 / 46 = 232) were verified
locally on 28 Oct 2026.

## Could not be done within GitHub's limits (closest alternative)
- True-3D hero (Three.js/Blender WebP): not built — the SVG hero meets
  the brief within budget; recorded in DESIGN.md, not hidden.
- Hover effects: impossible in README — high-contrast clickable cards
  with a gold rule instead.
- Webfonts in SVG images: impossible — display text converted to
  vector paths; small text uses system stacks.
- Full contribution-calendar "snake": cannot be sourced cleanly with
  the available token scope — honestly labelled activity skyline from
  real per-repo commit counts instead.
- Market-pulse SVG: omitted — no fresh, validated NEPSE data pipeline
  exists for this repo; inventing NEPSE data would break the honesty rule.

## Email note
No email address is printed in the README. A public email attracts
spam; contact stays in the profile sidebar only, at the owner's choice.

## Recommendations (settings, NOT changed by this PR)
- Bio: "Finance Research · Open Source · Kathmandu, Nepal"
- Location: Kathmandu, Nepal. Website: https://shirjankhadka.com.np
- Pins, in value order: finance-research-agents,
  investment-analyst-toolkit, nepali-capital-market-research,
  financial-research-analyst-agent, nepal-market-research,
  equity-research-playbook (nepali-business-opportunities rotates in
  if a pin slot frees up).
- Repo descriptions/topics/social previews: align to DESIGN.md palette
  (navy + gold); no new badges or achievements invented.
- CITATION/Sponsors links: only if the owner wants them — not added here.

## Files in this PR
README.md, DESIGN.md, PR-BODY.md (this file), Makefile,
scripts/{generate,fetch_stats,portrait,verify,screenshot}.py,
scripts/stats.json, assets/{hero,principles,portrait,posters},
generated/{skyline,numbers}, docs/preview/*.png.
NOT included: `.github/workflows/profile-refresh.yml` — the token used
for API uploads lacks workflow scope, so that single file must be added
via the browser (see DESIGN.md). Old `assets/banner.svg` and old
profile-picture files are deleted as superseded.
