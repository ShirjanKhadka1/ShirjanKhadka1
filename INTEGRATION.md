> **SUPERSEDED (Round 3) — do not use the numbers below as current.**
> The canonical programme map is
> [`finance-research-agents/ops/SYSTEM-MAP.md`](https://github.com/ShirjanKhadka1/finance-research-agents/blob/main/ops/SYSTEM-MAP.md),
> and current counts live in each repo's generated `status.json`
> (produced by `scripts/generate_status.py`, checked by `scripts/check_numbers.py`).
> This file is kept in place, unchanged except for this banner and for
> count claims replaced by pointers below, so its history is preserved.
> Any number still visible below is historical, not current.

# Integration — how all my repos work together

One system, not six separate projects. This file is the map. Every repo
also carries its own `INTEGRATION.md` with its own connections.

## The system in one diagram

```
                        ┌─────────────────────────┐
                        │   YOUR QUESTION         │
                        │  company / market /     │
                        │  business idea          │
                        └────────────┬────────────┘
                                     ▼
              ┌──────────────────────────────────────┐
              │  FINANCE RESEARCH AGENTS (think)     │
              │  agents, Markdown, free, local     │
              │  Researcher → Forensic → Financial → │
              │  Valuation → Reality Checker         │
              │  + World Market + Nepal Market       │
              └──────┬───────────────────────┬───────┘
                     ▼                       ▼
        ┌────────────────────┐   ┌────────────────────────┐
        │ TOOLKIT (calculate)│   │ PLAYBOOK (structure)   │
        │ ratios, DuPont,    │   │ initiation, earnings,  │
        │ DCF, multiples     │   │ forensic, valuation    │
        │ Python, 0 deps,    │   │ templates              │
        │ count in toolkit status.json │   │                        │
        └─────────┬──────────┘   └────────────┬───────────┘
                  └──────────────┬───────────┘
                                 ▼
              ┌──────────────────────────────────────┐
              │  DOMAIN REPOS (apply, with sources)  │
              │  • Nepal Market Research (companies) │
              │  • Nepali Capital Market Research    │
              │    (market structure)                │
              │  • Nepali Business Opportunities     │
              │    (sectors, scored by evidence)     │
              └──────────────────────────────────────┘
```

## Use it in your AI tool (free, local, no server)

The agents are Markdown files. Any tool that reads agent files can run them.
There is nothing to install on a server, and no account to create in this repo.

| Tool | How to add the agents |
|---|---|
| Claude Code | `./scripts/install.sh --tool claude-code` (copies to `~/.claude/agents/`) |
| GitHub Copilot | `./scripts/install.sh --tool copilot` (copies to `~/.github/agents/`) |
| Cursor / Gemini CLI / others | Copy the `.md` file from `agents/` into that tool's agent/agent-file folder, or paste it into a chat as a system prompt — the file is self-contained |

**No tool at all?** Open any agent `.md` file, read it, and follow its
workflow by hand. The workflow is the value, not the tool.

## Use the repos together — three worked paths

### Path 1: Research a company (most common)
1. Agent: Investment Researcher → thesis, business, industry.
2. Agent: Forensic Analyst → checklist, verdict.
3. Toolkit: ratios + DuPont on the statements (code, tested).
4. Agent: Financial Analyst → drivers, trends, cash vs profit.
5. Agent: Valuation Analyst → only if inputs allow, with sanity check.
6. Template: initiation-report.md → structure the answer.
7. Agent: Reality Checker → audit, fix, then share.

### Path 2: Understand a market (Nepal or world)
1. Agent: Nepali Capital Market Researcher (Nepal) or World Market
   Researcher (global) → structure/regime first.
2. Domain repo: capital-market guide or market review template.
3. Agent: Reality Checker → source audit.

### Path 3: Find a business opportunity in Nepal
1. Repo: Nepali Business Opportunities → scorecard + sector files.
2. Score all 8 sectors with cited evidence (evidence quality ≥ 3 to rank).
3. Top 2 sectors → 3 specific models each → score again with unit economics.
4. Highest scorer, with evidence attached, is the current best candidate.

## Why this serves millions (and what would break that)

- **Zero marginal cost:** Markdown + Python with zero dependencies. No
  server to scale, no API bill per user, no account system to maintain.
- **Forkable:** MIT licence. Anyone can copy, translate, teach, or adapt
  it without asking. Translation is the fastest way to reach more people:
  a translated agent file is a new agent file, same workflow.
- **Offline-capable:** once copied, the agents and templates work without
  the internet (except for fetching sources, which is the user's own research).
- **Trust-scaled:** the accuracy rules (sourced numbers, downside,
  unfinished labelled) are what make a tool shareable. A tool people
  cannot trust does not scale, however viral it looks.

**What would break it:** adding a paid API, a central server, or a login
wall; hard-coding numbers without sources; or claiming results the work
does not support. None of those are in this system, by design.

## Extend it without breaking it

1. One new agent = one new `.md` file, following the existing format
   (frontmatter + identity + mission + rules + workflow + deliverable +
   example prompt).
2. Add it to `agents.json` and to the roster table.
3. Add its `INTEGRATION.md` connections: which agent feeds it, which
   template it fills, which checker audits it.
4. Test: install script `--dry-run`, toolkit tests if code changed,
   Reality Checker pass on any new example.

## Repo-by-repo integration map

| Repo | Feeds into | Fed by | Its INTEGRATION.md |
|---|---|---|---|
| finance-research-agents | every other repo (thinking) | toolkit, playbook | `finance-research-agents/INTEGRATION.md` |
| investment-analyst-toolkit | agents' calculations | agents' inputs | `investment-analyst-toolkit/INTEGRATION.md` |
| equity-research-playbook | agents' deliverables | agents' workflows | `equity-research-playbook/INTEGRATION.md` |
| nepal-market-research | company studies | agents + toolkit | `nepal-market-research/INTEGRATION.md` |
| nepali-capital-market-research | market studies | agents | `nepali-capital-market-research/INTEGRATION.md` |
| nepali-business-opportunities | opportunity ranking | agents + scorecard | `nepali-business-opportunities/INTEGRATION.md` |
