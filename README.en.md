# Equity Research Skill (v2)

Author: [@rollingSirius](https://x.com/rollingSirius)

中文文档：[README.md](README.md)

**Possibly the deepest AI equity-research skill.** It turns "analyze this stock" into an institutional-grade, nine-chapter research report that is fact-traceable, valuation-reproducible, and conclusion-auditable — built around an **expectations-investing spine** (what the market has priced in vs. your independent view).

## What v2 adds

| Capability | Design |
|---|---|
| Expectations spine | Reverse DCF + PVGO decomposition decode the price; an Expectations Gap table and a falsifiable variant view are mandatory — no variant view, no buy/sell call (insight gate) |
| Forensic accounting | Accruals quality, Beneish M-Score, DSO/deferred-revenue divergence, capitalization policy, governance signals → earnings-credibility grade A–D; C/D vetoes any buy action |
| Reproducible valuation | Reverse DCF, probability-weighted 3-scenario DCF, EPV (Graham–Greenwald), **EVA/residual income**, warranted-multiple comps, SOTP — all computed by `scripts/dcf.py` with JSON assumptions on file; optional **Monte Carlo** (fair-value distribution, P(loss)) |
| Outside view | Every key assumption is placed on historical base-rate distributions (`base-rates.md`); terminal value passes three anti-cheating checks |
| Red team & sizing | Mandatory pre-mortem before finalizing; expected value, upside/downside asymmetry, quarter-Kelly size reference |
| Deep earnings mode | Nine-chapter earnings review (expectations gap, GAAP/Non-GAAP, cash flow, call language, model bridge); auto-initiates coverage if no prior report exists |
| 16 industry appendices | SaaS, semis, banks, insurance, pharma, consumer, energy, utilities, internet platforms, payments/fintech, REITs, industrials, telecom, autos/EV, metals & mining, transport |
| Multi-market | US, HK, China A-shares, A/H dual listings, China ADR/VIE structural-risk pricing |

## Output

**The user receives exactly one file: the report, PDF by default.**

- If no format is specified, the skill delivers a **PDF** (rendered from the Markdown draft; CJK fonts and tables verified).
- Users may explicitly request `.md`, `.docx`, or `.xlsx` (a four-tab valuation workbook).
- The report opens with a verdict box + tearsheet + expectations-gap table; the valuation chapter includes a text football-field chart.
- Assumption JSON, script outputs, checker results, and financial CSVs are **internal working files** — kept for reproducibility and summarized in the report appendix, but not delivered unless the user asks.

## Install

Send the repo link to any skill-capable AI tool, or:

```bash
# Claude Code (personal)
git clone https://github.com/rollingSirius/equity-research-skill.git ~/.claude/skills/equity-research
```

Claude Desktop / Cowork: zip the repo and upload under **Settings → Capabilities → Skills**.

## Usage

```text
Research NVDA for me
Is Marvell a buy? (deliver as Word)
Deep-dive AAPL's latest earnings
Compare CATL's A-share vs H-share pricing
```

No format specified → PDF. Scripts are stdlib-only Python; run them in the agent's own sandbox.

## Disclaimer

Research reference only — **not investment advice**. Neither the author nor this skill is a licensed advisor; decisions and outcomes are the user's own. License: [MIT](LICENSE).
