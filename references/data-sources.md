# 数据源操作手册

目录：
0. 工具可用性探测与降级路径（先读）
1. IBKR（价格与市场数据）
2. Morningstar（公允价值/护城河）
3. 财报与基本面（SEC EDGAR 优先；A股/港股见 markets-cn-hk.md）
4. 分析师评级与目标价
5. 新闻与催化剂
6. 数据对账规则
7. 财年口径陷阱
8. 市值计算

> 工具名说明：连接器工具在不同环境下前缀可能不同（形如 `mcp__<id>__search_contracts`），且部分环境要求先搜索/加载工具后才能调用。按**功能名**识别即可：`search_contracts`、`get_price_snapshot`、`get_price_history`。本手册用功能名指代。

---

## 0. 工具可用性探测与降级路径（先读）

采集开始前，先确认当前会话实际可用的工具（含需要加载后才可见的延迟工具）。**任何数据源缺失都不中断流程**：按下表降级，并在报告末尾"数据来源与时间戳清单"里如实标注降级原因与精度损失。

| 数据需求 | 首选 | 次选 | 兜底 | 降级时必须标注 |
|---|---|---|---|---|
| 实时/历史行情 | IBKR 连接器 | Morningstar 连接器或行情页 web_fetch | WebSearch 报价快照 | 来源、延迟级别、是否收盘价 |
| 公允价值/护城河/星级 | **Morningstar 专用连接器（若已接入）** | web_fetch Morningstar 个股页 | WebSearch 其分析文章/转引 | 转引需带原始发布日期；量化评级≠分析师公允价值 |
| 财报与分部数据 | 一手申报（EDGAR / 巨潮 / 披露易） | 财务数据聚合站交叉核对 | — | 聚合站口径以原始申报复核 |
| 分析师评级/目标价 | 聚合站（按市场选，见第 4 节与 markets-cn-hk.md） | WebSearch | — | 抓取日期与覆盖家数 |
| 文件输出（docx 等） | 对应技能 | 降级为 Markdown | — | 向用户说明格式降级 |

原则：工具调用连续失败（如参数校验类故障）重试不超过 2–3 次即降级，把时间留给分析而不是和接口搏斗；失败项计入来源清单（写"未获取到 + 原因"）。

---

## 1. IBKR（价格与市场数据）

### 1.1 解析合约（关键：挑对那一个）
调用 `search_contracts(query="<代码或公司名>", security_type="STK")`，返回多条候选。**一定要挑对**，否则后续价格全错。挑选规则：
- `symbol` 完全匹配、`description` 是目标公司、`country_code` 与上市地一致（美股 = `US`）、`exchange` 是主交易所（如 NASDAQ / NYSE）。
- 记下 `underlying_contract_id`（即 contract_id）与 `exchange`，供后续调用。

**真实坑位（以 MRVL 为例）**：搜索 "MRVL" 会同时返回——
- `MARVELL TECHNOLOGY INC` / NASDAQ / US ✅ 正确（contract_id 483492393）
- `MARVEL BIOSCIENCES CORP` / 加拿大 VENTURE ❌ 同名不同公司
- `MRVL1` / 墨西哥 MEXI、`MRVLUSD` / 瑞士 ❌ 海外重复挂牌
- `MVLL`(2X Long)、`MRVU`(Bull 2X)、`MRVY`(期权 ETP) ❌ 杠杆/衍生 ETF

取价务必用主挂牌的那条。

**非美股标的**（A股/港股/H股、A+H 双重上市）：合约挑选规则、Connect 通道代码、双边各解析一次等差异项见 `markets-cn-hk.md` 第 1 节；双重上市标的两地合约都要解析。

### 1.2 实时快照 `get_price_snapshot`
参数：`contract_id`、`exchange`（可用 `"SMART"` 取最优，或主交易所）、`market_data_names`（数组，只取需要的字段以提速）。常用字段：

| 字段 | 含义 |
|---|---|
| `last` | 最新成交价（同价时 price 可能为 null，只更新时间戳） |
| `change` | 较前收盘的绝对/百分比变动 |
| `prior-close` | 前收盘 |
| `open` / `high` / `low` | 当日开/高/低 |
| `volume` | 当日成交量 |
| `misc-statistics` | 13/26/52 周高低 + 52 周前开盘价（**52 周区间从这里取**） |
| `year-to-date-change` | 年初至今变动 |
| `dividend-yield` | 股息率（STK/CFD，保留 1 位小数） |
| `avg-90d-usd-volume` | 近 90 天平均美元成交额（流动性） |
| `cumulative-perf-1m/ytd/1y/3y/5y` | 区间累计涨幅 |

### 1.3 历史走势 `get_price_history`
参数：`contract_id`、`exchange`、`security_type="STK"`、`step`（如 `ONE_DAY`/`ONE_WEEK`/`ONE_MONTH`）、`outside_rth`（一般 false）、以及 **`period` 与 `step_count` 二选一**（不可同时传）。例：近一年周线用 `period="ONE_YEAR"`, `step="ONE_WEEK"`。可加 `include_corporate_actions=true` 看拆股/分红。

### 1.4 注意
- 取到的是实时或延迟价，取决于用户的行情订阅；报告里标"截至 <时间>"。
- **不要下单**：本技能只做研究。即便 IBKR 连接器支持 `create_order_instruction`，也绝不替用户交易或建仓——下单由用户自行完成。

---

## 2. Morningstar（公允价值 / 护城河）

**取数优先级**：① 若会话已接入 Morningstar 专用连接器（MCP），优先用其工具直接取结构化字段；② 否则 `web_fetch` 个股页：`https://www.morningstar.com/stocks/<MIC>/<ticker>/quote`（NASDAQ 用 `xnas`、NYSE 用 `xnys`；港股 `xhkg`、上证 `xshg`、深证 `xshe`，如 `.../stocks/xnas/mrvl/quote`、`.../stocks/xhkg/00700/quote`）；③ 客户端渲染抓不到正文时，改用其分析文章页或 `WebSearch`。A股/港股覆盖稀疏与"量化评级≠分析师公允价值"的区分见 `markets-cn-hk.md` 第 3 节。

要取的字段：
- **Fair Value Estimate（公允价值）** —— 注意标注日期。
- **Star Rating（星级，1–5）**、**Economic Moat（无/窄/宽，None/Narrow/Wide）**、**Uncertainty Rating（低/中/高/很高）**、**Capital Allocation（资本配置评级）**。
- 分析师对增长/盈利的核心观点（用于第三、四章佐证）。

**真实坑位**：搜索快照常混入不同时点的公允价值（例如同一标的会同时看到 $424、$235、$130、$120 等不同数字，是不同发布日期的旧值）。**务必取带明确日期的最新一手数值**，并对账（见第 6 节）。

---

## 3. 财报与基本面（SEC EDGAR 优先）

> A股用巨潮资讯网、港股用披露易，及业绩预告/盈利警告等差异制度，见 `markets-cn-hk.md` 第 2 节。以下为美股路径。

- 一手来源：`https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=<ticker>&type=10-K`（及 10-Q、8-K）。年报 10-K、季报 10-Q、业绩公告 8-K（含新闻稿 EX-99.1）。
- 收入分部、地区、客户集中度：见 10-K 的 MD&A 与分部附注、风险因素（客户集中度常在此披露）。
- 五年趋势：用 10-K 的 Selected Financial Data 或连续年报；也可用财务数据站（stockanalysis.com、macrotrends）交叉核对，但**以原始申报为准**。
- 内部持股、激励、关联交易：看代理声明 **DEF 14A（Proxy Statement）**。
- 财报电话会：搜索 "<公司> Q<x> FY<y> earnings call transcript"（Motley Fool、Seeking Alpha、公司 IR 页）。

---

## 4. 分析师评级与目标价

用 `WebSearch` 聚合：MarketBeat、TipRanks、Visible Alpha、Benzinga、Koyfin 等常给出"买入/持有/卖出家数 + 目标价区间/中位数"。

- 取**评级分布**、**目标价高/低/中位**、**近期上调/下调及理由**。
- 标注抓取日期；不同站点家数口径略有差异，取覆盖广、日期新的，并在表里注明来源。

---

## 5. 新闻与催化剂

- `WebSearch` 近 1–3 个月："<公司> earnings"、"<公司> guidance"、"<公司> 新闻/合作/产品"。
- 催化剂时间表：下次财报日、产品/客户里程碑、行业事件（如大客户资本开支指引）、监管/诉讼节点、解禁/回购计划。
- 区分已发生事实与预期事件。

---

## 6. 数据对账规则

当多个来源冲突：
1. 优先**一手来源**（公司申报 > Morningstar/卖方 > 二手聚合站 > 无日期的博客片段）。
2. 优先**最新且有明确日期**的数值。
3. 在报告里**显式列出差异**与采信理由，不要静默取一个。
4. 价格类以 IBKR 为准并标时间；估值类（公允价值/目标价）标清发布方与日期。

---

## 7. 财年口径陷阱

很多公司财年 ≠ 自然年，季度标签容易误读：
- 例：Marvell 财年于 1 月底/2 月初结束，"Q1 FY2027" 实际对应 ~2026 年 5 月初结束的季度。
- **务必把财年/财季标签映射到自然日历**，再与价格、新闻时间对齐；报告中同时写出财季与对应自然时间，避免读者误解。
- A股法定 12-31 年结（无此陷阱）；港股无强制、3-31 年结常见（如联想），先查年结日。详见 `markets-cn-hk.md` 第 4 节。

---

## 8. 市值计算

IBKR 快照通常**不直接给流通股本/市值**。做法：
- 从最新 10-Q/10-K 封面或财务站取**摊薄/基本股本（shares outstanding）**。
- 市值 ≈ 现价 × 股本；企业价值 EV ≈ 市值 + 总有息负债 − 现金。
- 标注股本的来源与日期（股本随回购/增发变化）。
