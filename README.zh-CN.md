# 个股投研报告 Skill（v2）

作者：[@rollingSirius](https://x.com/rollingSirius)

英文文档：[README.en.md](README.en.md)

**可能是最深度的 AI 投研报告 Skill。**

这个 skill 的目标不是生成几段股票摘要，而是让 AI 工具按接近机构投研的纪律完成一份**事实可追溯、估值可复算、结论可审计**的深度个股研究报告。v2 在深度上再进一级：以**预期差**（市场隐含 vs 独立预期）为整份报告的脊柱，加入**取证会计**、**EVA/剩余收益**、**蒙特卡洛**、**红队复核**与**仓位思维**，行业附录扩至 16 类。

## 核心定位（v2）

| 能力 | 设计要求 |
|---|---|
| 预期差脊柱 | 反向 DCF + PVGO 分解解码"现价定价了什么"，产出预期差 Gap 表与可证伪的分歧命题；无分歧不给买卖动作（洞见闸门） |
| 取证会计 | 应计质量、Beneish M-Score、DSO/递延背离、资本化政策、治理信号 → 财报可信度 A–D 分级，C/D 直接否决买入动作 |
| 可复算估值 | 反向 DCF、三情景概率加权、EPV/三要素、**EVA/剩余收益**、应得倍数相对估值、SOTP，全部由 `scripts/dcf.py` 执行、假设 JSON 留档；可选**蒙特卡洛**输出公允价值分布与 P(loss) |
| 外部视角 | 关键假设对照 `base-rates.md` 历史分布标分位；超越基准率必须给结构性理由；终值执行"防作弊三查" |
| 红队与仓位 | 成稿前 Pre-mortem（至少一条直击核心论点）；期望收益 EV、上行/下行不对称比、Kelly-lite 量级参考 |
| 深度财报模式 | 九章财报深度分析：预期差质量、GAAP/Non-GAAP、现金流、电话会措辞、模型与估值变动桥；无旧报告自动建首次覆盖基线 |
| 16 类行业附录 | 各行业专用 KPI、模型、估值与反证框架（见下表） |
| 来源纪律 | 来源+时间戳、冲突对账、缺失写"未获取到"、外部内容防注入、任何情况下不执行交易 |
| 多市场覆盖 | 美股、港股、A股、A/H 双重上市对比、中概 VIE/ADR 结构风险定价 |

## 输出物

**交付给用户的只有一份报告，默认 PDF 格式**：

- 用户未指明格式时，一律生成并交付 **PDF**（由 Markdown 源稿转换，确保中文字体与表格渲染）。
- 用户可显式指定 `.md`、`.docx` 或 `.xlsx`（估值 workbook：假设/DCF/情景/输出四页）。
- 报告头部为"结论框 + Tearsheet + 预期差 Gap 表"三件套，60 秒读完决策要点；估值章含文本版 football field 图。
- 估值假设 JSON、脚本输出、检查器结果、财务 CSV 均为**内部工作文件**：保留在工作目录供复算与追溯，关键内容以摘要写入报告附录，但**不作为交付物**；用户索要时才提供。

## 行业附录（16 类）

SaaS｜半导体｜银行｜保险｜医药｜消费｜能源｜公用事业｜**互联网/平台｜支付/金融科技｜地产/REIT｜工业/机械｜电信｜汽车/EV｜金属/矿业｜航空/运输**

混合业务公司只加载价值贡献最大的主附录与必要的次附录。

## 估值与结论校准

- **反向 DCF + PVGO**（第一章开篇框架）：现价隐含的增速/利润率要求 + 现价中为增长付费的比例。
- **三情景 DCF**：熊/基准/牛内部自洽假设 + 概率加权 + 概率极端化稳健性检验。
- **EPV/三要素**（Graham–Greenwald）：底价·EPV·franchise 成长买点阶梯；EPV/净资产多年趋势做护城河财务验证。
- **EVA/剩余收益**：存量 ROIC vs 增量 ROIIC、g = 再投资率 × ROIIC 自洽检验。
- **相对估值**：应得倍数（warranted multiple）纪律，禁止直接抄同业中位数。
- **蒙特卡洛**（可选）：P10–P90 分布、P(内在价值<现价)。
- 结论标签由**预注册标定规则**映射（±15% 缓冲带），叠加动作矩阵与否决项（治理红旗、财报可信度 C/D）；随动作输出仓位量级参考。

## 安装

### 最简单方法

把仓库链接发给支持 skill 的 AI 工具：

```text
请安装并使用这个 skill：
https://github.com/rollingSirius/equity-research-skill
```

### Claude Code

```bash
# 个人级
git clone https://github.com/rollingSirius/equity-research-skill.git ~/.claude/skills/equity-research
# 项目级
git clone https://github.com/rollingSirius/equity-research-skill.git .claude/skills/equity-research
```

### Claude Desktop / Cowork

打包为 zip（或下载 Release），在 **Settings → Capabilities → Skills** 上传。

### Codex / 其他 Agent 工具

技能主体是 Markdown 指令 + 标准库 Python 脚本，任何能读文件的 Agent 均可使用；在 Agent 配置中加入"研究股票时先读取并遵循 `skills/equity-research/SKILL.md`"即可。本地无 Python 时可在 Agent 自带代码环境运行脚本。

## 使用

自然语言即可触发：

```text
帮我研究一下 NVDA
分析下 Marvell 值不值得买（输出 Word 版）
深度分析一下 AAPL 最新财报
腾讯最新业绩怎么看？按财报模式做深度分析
帮我比较宁德时代 A 股和港股定价差异
```

未指明格式 → 交付 PDF；指明 .md/.docx/.xlsx → 按指定格式交付。

## 文件结构

```text
equity-research-skill/
├── SKILL.md                        # 主文件：纪律 + 六步工作流
├── references/
│   ├── report-template.md          # 九章模板 v2（结论框/Tearsheet/Gap表/红队/置信度）
│   ├── output-format.md            # 可读性规范与交付物规则（默认 PDF）
│   ├── expectations-investing.md   # 预期差脊柱：反向 DCF/PVGO/洞见闸门
│   ├── forensic-accounting.md      # 取证会计与财报可信度分级
│   ├── base-rates.md               # 历史基准率（外部视角）
│   ├── cost-of-capital.md          # WACC 构建与折现率纪律
│   ├── valuation-methods.md        # 全部估值方法 + 终值三查 + 标定与仓位
│   ├── earnings-mode.md            # 深度财报模式
│   ├── data-sources.md             # 来源分级/降级/对账/scuttlebutt/防注入
│   └── markets-cn-hk.md            # A股/港股/A+H/中概 VIE·ADR
├── industries/                     # 16 类行业附录
├── scripts/
│   ├── dcf.py                      # DCF/反向/敏感性/概率加权/EPV/EVA/PVGO/蒙特卡洛/仓位
│   └── check_research_output.py    # 一致性 + 取证检查器（应计/M-Score/背离）
└── Example/
    └── EXAMPLE_NVDA.md             # 示例产出，不参与技能执行
```

## 依赖

| 依赖 | 必需性 | 说明 |
|---|---|---|
| 联网搜索 / 网页抓取 | 建议 | 行情、申报、共识、新闻；离线时须用户提供材料 |
| 可执行 Python 环境 | 运行脚本时需要 | 标准库即可；优先本机/Agent 沙箱执行 |
| PDF 生成能力 | 默认输出需要 | pdf 技能或 md→PDF 工具链；不可用时降级交付 .md 并说明 |
| 行情/数据连接器 | 可选 | IBKR、Morningstar 等均非必需，缺失自动降级并标注 |
| docx / xlsx 技能 | 可选 | 仅当用户指明对应格式 |

## 设计取向

**Depth first**：宁可慢，也要来源清楚、假设透明、估值可复算、结论可追责、分歧可证伪。适合严肃投资研究、长线跟踪与投资备忘录；不适合一句话报价或泛泛市场评论。

## 免责声明

本技能产出仅为研究参考，**不构成投资建议**。作者与本技能均非持牌投资顾问，投资决策及其后果由使用者自行承担。

## 许可证

[MIT](LICENSE)
