# Equity Research Skill

Author: [@rollingSirius](https://x.com/rollingSirius)

Chinese documentation: [README.zh-CN.md](README.zh-CN.md)

**It may be one of the deepest AI skills for equity research reports.**

This skill is not designed to produce a few generic paragraphs about a stock. It is designed to make an AI agent follow an institutional-style research process and produce a deep public-equity report with traceable facts, reproducible valuation, and an auditable conclusion.

The default report language is Chinese.

## Why It Exists

Most AI stock analysis stops at “company summary + recent news + vague valuation.” This skill deliberately goes deeper:

- **Two deep modes, not quick summaries**: the full-research mode produces a nine-chapter company report; the earnings mode produces a nine-chapter deep earnings analysis covering expectation quality, segment and KPI bridges, GAAP/non-GAAP reconciliation, cash flow, management signals, and valuation changes.
- **Reproducible valuation, not improvised price targets**: DCF, reverse DCF, probability-weighted scenario DCF, EPV / three-element analysis, and SOTP-style work run through `scripts/dcf.py`; key assumptions are saved as JSON.
- **Source discipline, not model memory**: key data must carry source and timestamp; conflicting data must be reconciled; missing data must be explicitly marked.
- **Buy-side decision framing**: the conclusion must answer, “If this were cash today, would I buy the stock? Why?”
- **Multi-market coverage**: U.S. stocks, Hong Kong stocks, China A-shares, and A/H dual-listed companies.
- **Earnings-first initiation**: no prior report or model is required. The skill builds at least a three-year and eight-quarter baseline and clearly separates initiation from continuing-coverage changes.

## What It Does

- **Five-step workflow**: confirm ticker and listing venue -> detect data tools and collect data in parallel -> reconcile sources and timestamps -> write a nine-chapter report -> run valuation cross-checks and deliver a file.
- **Nine-chapter report**: quick view, business details, competition and moat, management and governance, financial analysis, valuation, analyst consensus, news and catalysts, and investment conclusion.
- **Nine-chapter earnings mode**: verdict and snapshot, expectation gap, segment/KPI analysis, earnings quality, cash flow and capital allocation, guidance and call signals, competition and market reaction, model/valuation bridge, and thesis/action update.
- **Eight industry appendices**: SaaS, semiconductors, banks, insurance, pharma, consumer, energy, and utilities each receive dedicated KPIs, model drivers, valuation methods, and falsification tests.
- **Valuation discipline**: at least three methods, including reverse DCF, probability-weighted scenario DCF, EPV / three-element analysis, relative valuation, or SOTP.
- **Scripted calculations**: all DCF / EPV-style calculations must be run through `scripts/dcf.py`; assumptions are stored as JSON for auditability.
- **Research hygiene**: separate facts from judgment, timestamp key numbers, reconcile conflicting data, and clearly mark missing data as “not obtained.”

## Industry-Specific Depth

| Industry | Additional research focus |
|---|---|
| SaaS | ARR, NRR, RPO/cRPO, sales efficiency, Rule of 40, SBC, and reverse DCF. |
| Semiconductors | Product/end-market mix, units and ASP, inventory cycle, yield, capacity, roadmaps, and cycle-normalized valuation. |
| Banks | NIM, deposit beta, credit migration, provisions, CET1, liquidity, and P/TBV versus ROTCE. |
| Insurance | Underwriting, reserves, combined ratio, VNB/CSM, solvency, investments, and P/EV. |
| Pharma | Clinical evidence, probability of success, patient funnel, exclusivity, cash runway, and asset-level rNPV. |
| Consumer | Volume/price/mix, comparable sales, traffic, sell-through, inventory, brand share, and unit economics. |
| Energy | Production, reserves, decline, costs, differentials/hedges, maintenance capex, commodity sensitivity, and NAV. |
| Utilities | Rate base, allowed/earned ROE, rate cases, projects, financing dilution, and dividend coverage. |

The skill loads only the primary appendix and, when materially necessary, one secondary appendix for mixed businesses.

## Data Sources

IBKR, Morningstar, and any other single vendor are optional. The default evidence order is:

1. Regulatory filings, exchange disclosures, government/regulator databases, and original company documents.
2. Exchange or regulated market data, formal company materials, and official industry statistics.
3. Professional sources such as Bloomberg, FactSet, LSEG, S&P Capital IQ, Visible Alpha, Morningstar, Koyfin, and Quartr.
4. Public quote and financial aggregators for gaps and cross-checks.
5. Media, reposts, and search snippets as leads that should be traced to originals.

Connectors are access methods, not credibility guarantees. The skill selects the highest-quality sources available in the current environment and discloses delays, fallbacks, definitions, and conflicts.

## Best For

| Scenario | Fit | Notes |
|---|---|---|
| First-pass company deep dive | Strong | Builds a full business, financial, valuation, and thesis baseline. |
| Earnings review | Strong | Uses earnings mode to analyze expectation gaps, quality, guidance, call signals, and valuation impact. |
| Investment memo | Strong | Produces an auditable research file with sources and valuation assumptions. |
| Continuing coverage | Strong | Updates prior thesis, forecasts, fair value, and action checklist. |
| One-line price question | Weak | The skill prioritizes depth and source discipline over speed. |
| Intraday trading signal | Weak | This is not a quantitative trading or market-timing system. |

## Repository Structure

```text
equity-research-skill/
├── SKILL.md                        # Main skill file: trigger rules and workflow
├── references/
│   ├── report-template.md          # Nine-chapter report template and table skeletons
│   ├── earnings-mode.md            # Deep earnings workflow, coverage routing, model bridge, and nine-chapter template
│   ├── data-sources.md             # Source tiers, fallbacks, market data, filings, industry data, reconciliation
│   ├── valuation-methods.md        # Valuation methods, DCF/EPV/SOTP rules, conclusion calibration
│   └── markets-cn-hk.md            # China A-share, Hong Kong, and A/H dual-listing notes
├── industries/
│   ├── saas.md                     # SaaS and subscription software
│   ├── semiconductors.md           # Semiconductors
│   ├── banks.md                    # Banks
│   ├── insurance.md                # Insurance
│   ├── pharma.md                   # Pharmaceuticals and biotech
│   ├── consumer.md                 # Consumer
│   ├── energy.md                   # Energy
│   └── utilities.md                # Utilities
├── scripts/
│   ├── dcf.py                      # Valuation calculator: DCF, reverse DCF, sensitivity, scenario weighting, EPV
│   └── check_research_output.py    # Financial and valuation consistency checker
└── Example/
    └── EXAMPLE_NVDA.md             # NVIDIA sample output; not loaded during execution
```

[`Example/EXAMPLE_NVDA.md`](Example/EXAMPLE_NVDA.md) is only a sample report. Its data sources reflect that particular run and are not installation requirements.

## Installation

### Simplest Method

Copy this repository URL and send it to an AI tool that supports skills or agent instructions:

```text
https://github.com/rollingSirius/equity-research-skill
```

For example:

```text
Please install and use this skill:
https://github.com/rollingSirius/equity-research-skill
```

### Claude Code

```bash
# Personal installation, available across projects
git clone https://github.com/rollingSirius/equity-research-skill.git ~/.claude/skills/equity-research

# Project-level installation, shared with a repository
git clone https://github.com/rollingSirius/equity-research-skill.git .claude/skills/equity-research
```

### Claude Desktop / Cowork

Zip this repository, or download a release package, then upload it from **Settings → Capabilities → Skills**.

### Codex and Other Agents

The core skill is plain Markdown with reproducible calculation scripts. Any agent that can read files can use it; local Python is not an installation prerequisite:

1. Place the repository in a project directory, such as `skills/equity-research/`.
2. Add an instruction to your agent config: when the user asks to research or analyze a stock, first read and follow `skills/equity-research/SKILL.md`.
3. When calculations are needed, use the agent's hosted code runtime, an AI online environment, an online notebook, or local Python.

## Usage

Natural-language prompts are enough:

```text
Research NVDA for me
Analyze whether Marvell is worth buying
Is AMD overvalued?
帮我研究一下 AAPL
Deeply analyze AAPL's latest earnings
Review MSFT earnings and update the valuation
Compare the A-share and H-share valuation gap for CATL
Use the SaaS appendix to deeply analyze Salesforce / CRM
Use the semiconductor appendix to analyze TSMC's cycle position and valuation
Review JPMorgan's latest earnings using the bank appendix
```

Explicit invocation also works:

| Tool | Example |
|---|---|
| Claude Code | `/equity-research analyze NVDA`, or “Use the equity-research skill to analyze TSLA.” |
| Claude Desktop / Cowork | “Use the equity-research skill to tell me whether AAPL is worth buying.” |
| Codex CLI | “Read skills/equity-research/SKILL.md first, then analyze NVDA according to it.” |
| Other agents | “Read skills/equity-research/SKILL.md and strictly follow its workflow to research <ticker>.” |

## Dependencies

| Dependency | Required | Notes |
|---|---|---|
| Web search / webpage fetching | Recommended | Used for current filings, prices, industry data, analyst estimates, and news; offline runs require user-provided materials |
| Executable Python environment | Needed when running scripts | Agent-hosted runtimes, AI online environments, notebooks, or local Python all work; local installation is not required |
| IBKR or another market-data connector | Optional | One possible quote path; exchange pages, professional APIs, or public sources can be used instead |
| Morningstar or professional-data connector | Optional | Useful for external valuation anchors, consensus, and standardized data, but never required |
| DOCX skill | Optional | Only needed when the user asks for a Word report |

## Outputs

A full run usually produces:

- A Markdown deep research report.
- Key data sources with timestamps.
- At least three valuation cross-checks.
- DCF / EPV results generated by `scripts/dcf.py`.
- Auditable valuation assumptions in JSON.
- In earnings mode, a model and fair-value bridge.

## Design Philosophy

This skill is **depth first**. It intentionally favors source discipline, transparent assumptions, reproducible valuation, and accountable conclusions over speed. It is best suited for serious investment research, long-term coverage, and investment memos rather than one-line quotes or generic market commentary.

## Disclaimer

Reports generated by this skill are for research reference only and **do not constitute investment advice**. The author is not a licensed investment adviser. Users are responsible for their own investment decisions.

## License

[MIT](LICENSE)
