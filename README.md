# 个股投研报告 Skill

作者：[@rollingSirius](https://x.com/rollingSirius)

英文文档：[README.en.md](README.en.md)

**可能是最深度的 AI 投研报告 Skill。**

这个 skill 的目标不是生成几段股票摘要，而是让 AI 工具按接近机构投研的纪律完成一份**事实可追溯、估值可复算、结论可审计**的深度个股研究报告。它面向严肃投资研究、长线跟踪、财报复盘、投资备忘录和估值校准，不追求最快给出一句话结论。

## 核心定位

多数 AI 股票分析会停在“公司简介 + 最近新闻 + 模糊估值”。这个 skill 刻意往更深处走：

| 能力 | 设计要求 |
|---|---|
| 深度研究 | 完整研究模式输出九章个股研报，覆盖业务、竞争、治理、财务、估值、催化剂与投资结论。 |
| 财报模式 | 财报模式不是摘要，而是九章财报深度分析，覆盖预期差质量、分部与 KPI、GAAP/Non-GAAP、现金流、电话会、模型与估值变动。 |
| 可复算估值 | DCF、反向 DCF、三情景概率加权、EPV / 三要素法、SOTP 等估值必须由 `scripts/dcf.py` 执行，关键假设以 JSON 留档。 |
| 一致性检查 | 成稿前用 `scripts/check_research_output.py` 检查估值标签、情景概率、EPV 参数、利润率、FCF、EPS 与现金流勾稽。 |
| 来源纪律 | 关键数据必须标注来源与时间戳；冲突数据要对账；缺失数据必须写“未获取到”。 |
| 买方视角 | 结论按预注册标定规则映射，要求回答“如果今天这是一笔现金，我会买入它吗？为什么？” |
| 多市场覆盖 | 支持美股、港股、A 股与 A/H 双重上市对比。 |
| 财报首次覆盖 | 没有旧研报或旧模型也能直接使用财报模式；skill 会补建至少 3 年、8 个季度的历史基线。 |

## 它能做什么

### 1. 完整个股深度研究

适合第一次系统研究一家公司，或需要重新建立投资框架的场景。默认输出九章报告：

1. 一页速览
2. 公司与业务详情
3. 竞争格局与护城河
4. 管理层与治理
5. 财务分析
6. 多方法估值
7. 分析师观点汇总
8. 新闻、风险与催化剂
9. 投资结论

### 2. 深度财报模式

适合公司刚发布季报、年报、业绩指引或电话会纪要后，判断“这份财报到底改变了什么”。财报模式会区分两种情况：

| 覆盖状态 | skill 的处理方式 |
|---|---|
| 已有历史报告或模型 | 做持续覆盖更新，重点分析财报相对旧论点、旧预测、旧估值的变化。 |
| 没有历史报告或模型 | 做“财报切入的首次覆盖”，先补建历史基线，再分析本次财报质量与估值含义。 |

财报模式默认输出九章：

1. 结论与快照
2. 预期差与质量
3. 收入、分部与 KPI
4. 利润率、费用与盈利质量
5. 现金流、资产负债表与资本配置
6. 指引、电话会与管理层信号
7. 竞争、行业与市场反应
8. 模型、估值与公允价值变动桥
9. 投资论点更新与行动清单

### 3. 估值与结论校准

这个 skill 不允许只给一个“看起来合理”的目标价。它要求至少三种估值方法交叉验证，并把假设、计算过程和结论映射留档：

- 反向 DCF：当前股价隐含了什么收入增速、利润率或资本回报。
- 三情景 DCF：乐观、中性、悲观情景及概率加权公允价值。
- EPV / 三要素法：对成熟企业或周期企业做盈利能力与再投资质量校验。
- 相对估值：用同业倍数检查市场定价是否一致。
- SOTP：适合多业务、多资产或分部差异极大的公司。

## 安装

### 最简单方法

直接复制这个仓库链接，发送给支持 skill 或 agent 指令的 AI 工具：

```text
https://github.com/rollingSirius/equity-research-skill
```

可以这样说：

```text
请安装并使用这个 skill：
https://github.com/rollingSirius/equity-research-skill
```

### Claude Code

```bash
# 个人级：所有项目可用
git clone https://github.com/rollingSirius/equity-research-skill.git ~/.claude/skills/equity-research

# 项目级：随仓库共享
git clone https://github.com/rollingSirius/equity-research-skill.git .claude/skills/equity-research
```

### Claude Desktop / Cowork

把本仓库打包为 zip，或下载 Release，在 **Settings -> Capabilities -> Skills** 中上传。

### Codex / 其他 Agent 工具

本技能是纯 Markdown 指令，加一个标准库 Python 估值脚本。任何能读取文件并运行 Python 的 Agent 都可以使用：

1. 把本仓库放进项目目录，例如 `skills/equity-research/`。
2. 在 Agent 配置中加入一句：当用户要求研究/分析某只股票时，先读取并遵循 `skills/equity-research/SKILL.md` 的完整流程。

## 使用

自然语言即可触发：

```text
帮我研究一下 NVDA
分析下 Marvell 值不值得买
深度分析一下 AAPL 最新财报
根据 MSFT 财报更新估值和投资结论
腾讯最新业绩怎么看？按财报模式做深度分析
帮我比较宁德时代 A 股和港股定价差异
```

也可以显式指定技能：

| 工具 | 调用示例 |
|---|---|
| Claude Code | `/equity-research 分析 NVDA`，或“用 equity-research 技能研究 TSLA”。 |
| Claude Desktop / Cowork | “用 equity-research 技能帮我看看 AAPL 值不值得买”。 |
| Codex CLI | “先读 skills/equity-research/SKILL.md，再按它分析 NVDA”。 |
| 其他 Agent | “先读取 skills/equity-research/SKILL.md 并严格按其流程执行，然后研究 <股票>”。 |

## 适合什么场景

| 场景 | 是否适合 | 说明 |
|---|---|---|
| 首次研究一家公司 | 适合 | 建立业务、财务、估值和投资结论的完整底稿。 |
| 财报发布后复盘 | 适合 | 用财报模式拆解预期差、质量、指引、电话会和估值变化。 |
| 投资备忘录 | 适合 | 适合形成可审计、可复盘的研究结论。 |
| 长线跟踪 | 适合 | 可以基于旧报告持续更新论点、预测和公允价值。 |
| 一句话问股价涨跌 | 不适合 | 这个 skill 会优先保证深度和来源纪律。 |
| 高频交易信号 | 不适合 | 它不是量化交易或盘中交易系统。 |

## 输出物

一次完整执行通常会生成：

- 一份 Markdown 深度报告。
- 一组关键数据来源与时间戳。
- 至少三种估值方法的交叉验证。
- `scripts/dcf.py` 生成的 DCF / EPV 计算结果。
- `scripts/check_research_output.py` 生成的财务/估值一致性检查结果。
- 可复查的估值假设 JSON。
- 财报模式下的模型与公允价值变动桥。

## 一致性检查脚本

成稿前可以单独运行：

```bash
python3 scripts/check_research_output.py \
  --report outputs/公司_代码_报告.md \
  --assumptions outputs/公司_代码_valuation_assumptions.json \
  --financials outputs/公司_代码_financials.csv
```

其中 `--financials` 可选；有历史或预测财务表时建议提供。脚本会按严重程度输出 `P0` 到 `P3`：`P0/P1` 应修正或在报告中显式解释，`P2` 是质量风险，`P3` 是轻提示。可用 `--demo` 自检脚本是否可运行。

## 文件结构

```text
equity-research-skill/
├── SKILL.md                        # 技能主文件：触发条件 + 工作流程
├── references/
│   ├── report-template.md          # 九章报告模板与表格骨架
│   ├── earnings-mode.md            # 深度财报模式：覆盖分流、财报分析协议、模型变动桥与九章模板
│   ├── data-sources.md             # 取数手册：工具探测、行情、Morningstar、申报文件、分析师数据
│   ├── valuation-methods.md        # 估值方法：DCF、反向 DCF、情景加权、EPV、SOTP 与结论标定
│   └── markets-cn-hk.md            # A股/港股/A+H 差异手册
├── scripts/
│   ├── dcf.py                      # 估值计算器：DCF、反向 DCF、敏感性、概率加权、EPV
│   └── check_research_output.py    # 财务/估值一致性检查器
└── EXAMPLE_NVDA.md                 # 示例产出，仅供参考效果，不参与技能执行
```

`EXAMPLE_NVDA.md` 只是给用户看最终产出长什么样的样例，不会被 `SKILL.md` 加载，也不影响技能执行。

## 依赖

| 依赖 | 必需性 | 说明 |
|---|---|---|
| 联网搜索 / 网页抓取 | 必需 | 获取行情、公司公告、监管申报、分析师评级和新闻。 |
| Python 3 | 必需 | 运行 `scripts/dcf.py` 和 `scripts/check_research_output.py`，仅使用标准库。 |
| Interactive Brokers (IBKR) MCP | 可选 | 实时行情快照与历史走势；未连接时按降级表改用公开网络行情源。 |
| Morningstar MCP | 可选 | 有则直取结构化字段，无则网页抓取。 |
| docx 技能 | 可选 | 仅当需要输出 Word 版报告。 |

## 继续加深的方向

如果要把它做得更深，可以优先考虑这些方向：

1. **行业专用附录**：为 SaaS、半导体、银行、保险、医药、消费、能源、公用事业分别做专用 KPI、估值方法和风险清单。
2. **模型文件输出**：除 Markdown 报告外，生成可编辑的 Excel / CSV 三表模型，并保留收入分部、成本、费用、资本开支、营运资本和股本假设。
3. **一致性检查脚本增强**：继续扩展更多行业特定勾稽项，例如银行资本充足率、保险内含价值、SaaS 留存率与半导体库存周期。
4. **历史覆盖数据库**：把每次报告的结论、假设、公允价值、评级和关键分歧点结构化存档，方便做持续覆盖。
5. **同业可比公司库**：按行业维护默认 peer set，并让 skill 解释为什么选择或剔除某些可比公司。
6. **电话会语义追踪**：对管理层措辞、风险提示、订单/需求/库存语言做跨季度变化表。
7. **反证章节**：强制加入“我可能错在哪里”，列出能推翻投资结论的关键证据和触发阈值。

## 设计取向

这个 skill 的设计取向是 **depth first**：宁可慢一点，也要尽量做到来源清楚、假设透明、估值可复算、结论可追责。它适合严肃投资研究、长线跟踪和投资备忘录，不适合只想要一句话报价或泛泛市场评论的场景。

## 免责声明

本技能产出的内容仅为研究参考，**不构成投资建议**。作者与本技能均非持牌投资顾问，投资决策及其后果由使用者自行承担。

## 许可证

[MIT](LICENSE)
