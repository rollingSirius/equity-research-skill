# Equity Research Skill

Author: [@rollingSirius](https://x.com/rollingSirius)

Chinese documentation: [README.zh-CN.md](README.zh-CN.md)

**It may be one of the deepest AI skills for equity research reports.**

This skill is not designed to produce a few generic paragraphs about a stock. It is designed to make an AI agent follow an institutional-style research process and produce a deep public-equity report with traceable facts, reproducible valuation, and an auditable conclusion.

The default report language is Chinese.

## Why It Exists

Most AI stock analysis stops at “company summary + recent news + vague valuation.” This skill deliberately goes deeper:

- **Two deep modes, not quick summaries**: the full-research mode produces a nine-chapter company report; the earnings mode produces a nine-chapter deep earnings analysis covering expectation quality, segment and KPI bridges, GAAP/non-GAAP reconciliation, cash flow, management signals, and valuation changes.
- **Reproducible valuation, not improvised price targets**: DCF, reverse DCF, probability-weighted scenario DCF, EPV / three-element analysis, and SOTP-style work must run through `scripts/dcf.py`; key assumptions are saved as JSON.
- **Source discipline, not model memory**: key data must carry source and timestamp; conflicting data must be reconciled; missing data must be explicitly marked.
- **Buy-side decision framing**: the conclusion must answer, “If this were cash today, would I buy the stock? Why?”
- **Multi-market coverage**: U.S. stocks, Hong Kong stocks, China A-shares, and A/H dual-listed companies.
- **Earnings-first initiation**: no prior report or model is required. The skill builds at least a three-year and eight-quarter baseline and clearly separates initiation from continuing-coverage changes.

## What It Does

- **Five-step workflow**: confirm ticker and listing venue -> detect data tools and collect data in parallel -> reconcile sources and timestamps -> write a nine-chapter report -> run valuation cross-checks and deliver a file.
- **Nine-chapter report**: quick view, business details, competition and moat, management and governance, financial analysis, valuation, analyst consensus, news and catalysts, and investment conclusion.
- **Nine-chapter earnings mode**: verdict and snapshot, expectation gap, segment/KPI analysis, earnings quality, cash flow and capital allocation, guidance and call signals, competition and market reaction, model/valuation bridge, and thesis/action update.
- **SaaS industry appendix**: for SaaS, subscription-software, and cloud-software companies, the skill adds ARR, NRR, RPO/cRPO, Rule of 40, sales efficiency, SBC, FCF, and reverse-DCF implied-requirement analysis.
- **Valuation discipline**: at least three methods, including reverse DCF, probability-weighted scenario DCF, EPV / three-element analysis, relative valuation, or SOTP.
- **Scripted calculations**: all DCF / EPV-style calculations must be run through `scripts/dcf.py`; assumptions are stored as JSON for auditability.
- **Consistency checks**: `scripts/check_research_output.py` checks valuation labels, scenario probabilities, EPV parameters, margins, FCF, EPS, and cash-flow roll-forward math.
- **Research hygiene**: separate facts from judgment, timestamp key numbers, reconcile conflicting data, and clearly mark missing data as “not obtained.”

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
│   ├── data-sources.md             # Data-source playbook: tools, price data, Morningstar, filings, analysts
│   ├── valuation-methods.md        # Valuation methods, DCF/EPV/SOTP rules, conclusion calibration
│   ├── markets-cn-hk.md            # China A-share, Hong Kong, and A/H dual-listing notes
│   └── industry-saas.md            # SaaS industry deep-research appendix
├── scripts/
│   ├── dcf.py                      # Valuation calculator: DCF, reverse DCF, sensitivity, scenario weighting, EPV
│   └── check_research_output.py    # Financial and valuation consistency checker
└── EXAMPLE_NVDA.md                 # Example output only; not loaded during skill execution
```

`EXAMPLE_NVDA.md` is only a sample report for readers. It is not part of the execution path.

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

This skill is plain Markdown plus a standard-library Python script. Any agent that can read files and run Python can use it:

1. Place the repository in a project directory, such as `skills/equity-research/`.
2. Add an instruction to your agent config: when the user asks to research or analyze a stock, first read and follow `skills/equity-research/SKILL.md`.

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
| Web search / webpage fetching | Yes | Used for filings, Morningstar pages, analyst ratings, and news |
| Python 3 | Yes | Required for `scripts/dcf.py` and `scripts/check_research_output.py`; both use only the standard library |
| Interactive Brokers MCP | Optional | Preferred for real-time quotes and price history; falls back to public web data when unavailable |
| Morningstar MCP | Optional | Preferred for structured fair value, moat, uncertainty, and capital allocation fields |
| DOCX skill | Optional | Only needed when the user asks for a Word report |

## Outputs

A full run usually produces:

- A Markdown deep research report.
- Key data sources with timestamps.
- At least three valuation cross-checks.
- DCF / EPV results generated by `scripts/dcf.py`.
- Financial and valuation consistency checks generated by `scripts/check_research_output.py`.
- Auditable valuation assumptions in JSON.
- In earnings mode, a model and fair-value bridge.

## Consistency Checker

Before final delivery, the checker can be run directly:

```bash
python3 scripts/check_research_output.py \
  --report outputs/company_ticker_report.md \
  --assumptions outputs/company_ticker_valuation_assumptions.json \
  --financials outputs/company_ticker_financials.csv
```

`--financials` is optional, but recommended when historical or forecast financial tables exist. The script reports `P0` to `P3` findings: `P0/P1` should be fixed or explicitly explained in the report, `P2` marks quality risks, and `P3` is a light warning. Use `--demo` to verify the script itself.

## Design Philosophy

This skill is **depth first**. It intentionally favors source discipline, transparent assumptions, reproducible valuation, and accountable conclusions over speed. It is best suited for serious investment research, long-term coverage, and investment memos rather than one-line quotes or generic market commentary.

## Disclaimer

Reports generated by this skill are for research reference only and **do not constitute investment advice**. The author is not a licensed investment adviser. Users are responsible for their own investment decisions.

## License

[MIT](LICENSE)
