# Equity Research Skill 个股投研报告技能

作者：[@rollingSirius](https://x.com/rollingSirius)

**可能是最深度的 AI 投研报告 Skill。**

这个 skill 的目标不是生成几段股票摘要，而是让 AI Agent 按接近机构投研的纪律完成一份**事实可追溯、估值可复算、结论可审计**的深度个股研究报告。

## 核心定位

多数 AI 股票分析会停在“公司简介 + 最近新闻 + 模糊估值”。这个 skill 刻意往更深处走：

- **深度研究，而非快餐摘要**：默认输出九章个股研报，覆盖业务、竞争、治理、财务、估值、卖方观点、新闻催化剂与最终动作。
- **可复算估值，而非随口目标价**：DCF、反向 DCF、三情景概率加权、EPV / 三要素法、SOTP 等估值必须由 `scripts/dcf.py` 执行，关键假设以 JSON 留档。
- **来源纪律，而非模型记忆**：关键数据必须标注来源与时间戳；冲突数据要对账；缺失数据必须写“未获取到”。
- **买方视角，而非漂亮文章**：结论按预注册标定规则映射，要求回答“如果今天这是一笔现金，我会买入它吗？为什么？”
- **多市场覆盖**：支持美股、港股、A 股与 A/H 双重上市对比。

## 它能做什么

- **五步工作流**：确认标的 → 探测可用数据源并并行采集（行情 / Morningstar / 财报与卖方观点，工具缺失自动降级并标注）→ 数据对账与时间戳 → 按九章模板撰写 → 估值交叉验证并交付文件。
- **九章报告结构**：一页速览、业务详情、竞争与护城河、管理层与治理、财务分析、多方法估值、分析师观点汇总、新闻与催化剂、投资结论。
- **估值纪律**：至少三种方法交叉验证，包括反向 DCF、三情景概率加权 DCF、三要素/EPV、相对估值或 SOTP。所有 DCF / EPV 计算由 `scripts/dcf.py` 执行，假设以 JSON 留档。
- **结论可复现**：估值标签与买卖动作按预注册标定规则映射产出，避免同一组数字生成不一致结论。
- **研究纪律**：事实与判断分离、每个关键数据标注来源与时间、冲突数据显式对账、缺失数据如实标注“未获取到”。

## 文件结构

```text
equity-research-skill/
├── SKILL.md                        # 技能主文件：触发条件 + 工作流程
├── references/
│   ├── report-template.md          # 九章报告模板与表格骨架
│   ├── data-sources.md             # 取数手册：工具探测、行情、Morningstar、申报文件、分析师数据
│   ├── valuation-methods.md        # 估值方法：DCF、反向 DCF、情景加权、EPV、SOTP 与结论标定
│   └── markets-cn-hk.md            # A股/港股/A+H 差异手册
├── scripts/
│   └── dcf.py                      # 估值计算器：DCF、反向 DCF、敏感性、概率加权、EPV
└── EXAMPLE_NVDA.md                 # 示例产出，仅供参考效果，不参与技能执行
```

> `EXAMPLE_NVDA.md` 只是给用户看最终产出长什么样的样例，不会被 `SKILL.md` 加载，也不影响技能执行。

## 安装

### Claude Code

```bash
# 个人级：所有项目可用
git clone https://github.com/rollingSirius/equity-research-skill.git ~/.claude/skills/equity-research

# 项目级：随仓库共享
git clone https://github.com/rollingSirius/equity-research-skill.git .claude/skills/equity-research
```

### Claude Desktop / Cowork

把本仓库打包为 zip，或下载 Release，在 **Settings → Capabilities → Skills** 中上传。

### Codex / 其他 Agent 工具

本技能是纯 Markdown 指令，加一个标准库 Python 估值脚本。任何能读取文件并运行 Python 的 Agent 都可以使用：

1. 把本仓库放进项目目录，例如 `skills/equity-research/`。
2. 在 Agent 配置中加入一句：当用户要求研究/分析某只股票时，先读取并遵循 `skills/equity-research/SKILL.md` 的完整流程。

## 使用

自然语言即可触发：

```text
帮我研究一下 NVDA
分析下 Marvell 值不值得买
Is AMD overvalued?
```

也可以显式指定技能：

| 工具 | 调用示例 |
|---|---|
| Claude Code | `/equity-research 分析 NVDA`，或“用 equity-research 技能研究 TSLA” |
| Claude Desktop / Cowork | “用 equity-research 技能帮我看看 AAPL 值不值得买” |
| Codex CLI | “先读 skills/equity-research/SKILL.md，再按它分析 NVDA” |
| 其他 Agent | “先读取 skills/equity-research/SKILL.md 并严格按其流程执行，然后研究 <股票>” |

## 依赖

| 依赖 | 必需性 | 说明 |
|---|---|---|
| 联网搜索 / 网页抓取 | 必需 | 获取 Morningstar、财报申报、分析师评级、新闻 |
| Python 3 | 必需 | 运行 `scripts/dcf.py`，仅使用标准库 |
| Interactive Brokers (IBKR) MCP | 可选 | 实时行情快照与历史走势；未连接时按降级表改用公开网络行情源 |
| Morningstar MCP | 可选 | 有则直取结构化字段，无则网页抓取 |
| docx 技能 | 可选 | 仅当需要输出 Word 版报告 |

## 设计取向

这个 skill 的设计取向是 **depth first**：宁可慢一点，也要尽量做到来源清楚、假设透明、估值可复算、结论可追责。它适合严肃投资研究、长线跟踪和投资备忘录，不适合只想要一句话报价或泛泛市场评论的场景。

## 免责声明

本技能产出的内容仅为研究参考，**不构成投资建议**。作者与本技能均非持牌投资顾问，投资决策及其后果由使用者自行承担。

## License

[MIT](LICENSE)
