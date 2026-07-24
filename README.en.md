# Equity Research Skill

Author: [@rollingSirius](https://x.com/rollingSirius)

中文文档：[README.md](README.md)

**Possibly the deepest AI equity-research skill.**

The goal is not a stock summary, but an institutional-grade report that is **fact-traceable, valuation-reproducible, and conclusion-auditable** — built for serious research, long-term coverage, earnings reviews, and investment memos. Since v2, every report is organized around an **expectations gap** (what the market has priced in vs. your independent view), with an **earnings-quality review** performed before any valuation.

## Positioning

| Capability | Design requirement |
|---|---|
| Deep research | Nine-chapter report covering business, competition, governance, financials, valuation, catalysts, and verdict. |
| Expectations-gap analysis | Reverse DCF + PVGO decode the current price; a gap table and a falsifiable variant view are mandatory — no independent view, no buy/sell call. |
| Earnings mode | Nine-chapter earnings deep-dive: surprise quality, segments/KPIs, GAAP vs Non-GAAP, cash flow, call language, model & fair-value bridge. |
| Earnings-quality review | Accruals, Beneish M-Score, revenue-recognition red flags, governance signals → credibility grade A–D; C/D vetoes buy actions. |
| Reproducible valuation | DCF, reverse DCF, probability-weighted scenarios, EPV, EVA/residual income, SOTP — all computed by `scripts/dcf.py`, assumptions filed as JSON; optional Monte Carlo. |
| Outside view | Key assumptions placed on historical base-rate distributions; terminal value passes a three-point sanity check. |
| Source discipline | Source + timestamp on every key number; conflicts reconciled; missing data marked "not obtained"; external content treated as data, never as instructions. |
| Buy-side lens | Pre-registered calibration rules map label → action; a counter-case (pre-mortem) is written before finalizing. |
| 16 industry appendices | Each changes the KPIs, model, valuation, and disconfirming evidence. |
| Multi-market | US, HK, A-shares, A/H dual listings, China ADR/VIE structural-risk pricing. |

## What it does

### 1. Full deep-dive research

Nine chapters: one-page summary (verdict box + tearsheet + expectations-gap table), business detail, competition & moat, management/governance & capital-allocation scorecard, financials & earnings quality, multi-method valuation (with a football-field chart), analyst views & divergence attribution, news & catalysts, verdict with counter-case and sizing reference.

### 2. Deep earnings mode

With prior coverage → continuing-coverage update (thesis/forecast/fair-value bridges). Without → initiate coverage from the earnings event, rebuilding at least 3 years / 8 quarters of baseline. Every earnings run includes a minimum quality-check set (accruals, cash conversion, DSO/deferred-revenue divergence, recurring "one-offs").

### 3. Valuation & calibration

At least three independent methods: reverse DCF + PVGO (what the price implies), three-scenario weighted DCF (+ optional Monte Carlo with P(loss)), EPV/three-factor ladder with EPV-to-book moat verification, EVA/residual income with the g = reinvestment × ROIIC consistency check, warranted-multiple comps, SOTP. Labels map through pre-registered calibration bands; actions carry expected value, upside/downside asymmetry, and a quarter-Kelly size reference.

### 4. Earnings-quality review

Before valuing anything: accruals ratio and cash conversion, Beneish M-Score (auto-computed by the checker), DSO/deferred divergences, capitalization and smoothing patterns, audit/governance signals → grade A–D with hard veto rules ("cheap" never offsets credibility problems).

### 5. Industry appendices (16)

SaaS · semiconductors · banks · insurance · pharma · consumer · energy · utilities · internet platforms · payments/fintech · REITs · industrials · telecom · autos/EV · metals & mining · transport — each with its own KPI set (e.g. REITs: FFO/AFFO, same-store NOI, cap rate, debt maturity wall, P/NAV; mining: AISC cost-curve percentile, reserve life, per-mine NAV).

### 6. Data sourcing & reconciliation

No mandatory data vendor. Priority: regulatory filings → exchange/official data → professional databases → public aggregators → media as leads only. Downgrades, delays, and conflicts are disclosed; fetched content is data, not instructions.

## Install

Send the repo link to any skill-capable AI tool, or:

```bash
# Claude Code (personal)
git clone https://github.com/rollingSirius/equity-research-skill.git ~/.claude/skills/equity-research
```

Claude Desktop / Cowork: zip the repo and upload under **Settings → Capabilities → Skills**. Other agents: instruct them to read and follow `skills/equity-research/SKILL.md`. Scripts are stdlib-only Python.

## Usage

```text
Research NVDA for me
Is Marvell a buy? (deliver as Word)
Deep-dive AAPL's latest earnings
Compare CATL's A-share vs H-share pricing
```

**Output defaults to PDF** when no format is specified; `.md`, `.docx`, and `.xlsx` (valuation workbook) are available on request. The user receives the report only — assumption JSONs, script outputs, and CSVs are internal working files kept for reproducibility and summarized in the report appendix.

## Disclaimer

Research reference only — **not investment advice**. Neither the author nor this skill is a licensed advisor; decisions and outcomes are the user's own. License: [MIT](LICENSE).
