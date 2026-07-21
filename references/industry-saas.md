# SaaS 行业深度研究附录

适用范围：订阅制软件、云原生应用软件、平台型 B2B 软件、垂直 SaaS、消费订阅软件，以及以订阅收入为核心的混合软件公司。若公司同时有硬件、服务、广告、交易抽佣或云基础设施业务，先拆分收入和毛利，再只对订阅/软件部分使用本附录。

## 目录

1. 使用原则
2. 信息来源与公允机制
3. SaaS 价值驱动树
4. 核心 KPI 字典
5. 财务模型结构
6. 估值方法
7. 财报模式重点
8. 护城河与竞争判断
9. 红旗、反证与常见误判
10. 报告输出要求

## 1. 使用原则

- 先确定公司是否真是 SaaS：收入必须以可续约订阅、用量订阅或长期软件合约为主。一次性 license、咨询实施、硬件打包收入不能直接套 SaaS 倍数。
- 不要只看收入增速。SaaS 研究的核心是“增长质量”：留存、扩张、获客效率、毛利率、现金流、SBC 稀释和竞争强度共同决定价值。
- 区分企业级、SMB、开发者工具、垂直 SaaS、消费订阅和平台型 SaaS。不同客群的 churn、销售周期、毛利率、S&M 效率和估值中枢不同。
- 所有公司自定义 KPI 必须回到披露原文定义，不得把不同公司口径强行横比。
- 把 reported growth 拆成 organic growth、并购、汇率、价格、seat expansion、usage expansion 和 churn 的贡献。
- 对高估值 SaaS，估值章节优先用反向 DCF 说明现价隐含的 ARR、FCF margin、Rule of 40 和终局市场份额。

## 2. 信息来源与公允机制

### 来源优先级

1. **监管申报**：10-K/10-Q/20-F/S-1/F-1/年报。用于确认收入确认、RPO、deferred revenue、客户集中度、风险因素、SBC、并购和分部口径。
2. **公司财报材料**：earnings release、shareholder letter、investor presentation、supplemental metrics。用于获取 ARR、NRR、RPO、客户数、ACV、guidance 和管理层口径。
3. **电话会文字稿**：用于跟踪管理层对 demand、pipeline、seat expansion、AI monetization、pricing、churn、macro headwind 的措辞变化。
4. **同业公司披露**：用于建立 peer set 和 KPI 合理区间。优先选择相同客群、销售模式、产品类别和增长阶段的公司。
5. **第三方与卖方研究**：只能作为补充观点，不得替代一手披露。引用时标明日期和口径。

### 公允机制

- **定义优先**：每个 KPI 首次出现时写明公司定义。若公司没有披露定义，写“未获取到公司定义”，不要用行业习惯定义代替事实。
- **同业可比前先调口径**：横比 NRR、ARR、RPO、billings、FCF margin 前，说明口径差异和不可比项。
- **增长与质量并列**：任何“高速增长”结论必须同时给出留存、获客效率、毛利率、FCF 或 SBC 稀释的质量约束。
- **反证优先写入**：每个看多论点必须给出可推翻证据。例如“AI 驱动扩张”必须绑定 AI attach rate、ARPU、gross retention 或 usage 增长，而不是只引用管理层描述。
- **避免幸存者偏差**：选择可比公司时同时纳入优质、高增长、成熟和受压公司，不能只选高倍数同业。
- **区分周期与结构**：预算冻结、销售周期拉长、seat contraction 可能是宏观周期，也可能是产品竞争力下降。必须用续约、扩张、pipeline conversion 和客户 cohort 证据判断。

## 3. SaaS 价值驱动树

SaaS 内在价值可以拆成：

```text
企业价值 =
  可服务市场规模
  × 长期可获取份额
  × 定价能力 / ARPU
  × 留存与扩张质量
  × 稳态毛利率
  × 稳态销售与营销效率
  × 研发和管理费用杠杆
  × 税后 FCF 转换率
  ÷ 风险折现率
  − 稀释与资本配置损耗
```

报告中至少回答：

- 增长来自新客户、老客户扩张、价格、用量、模块 attach，还是并购？
- 增长是否需要持续高 S&M 投入才能维持？
- 客户留存是否足以证明产品是 workflow system of record，而非可替换工具？
- 毛利率和 FCF margin 是否已经接近成熟软件公司水平，还是仍被基础设施、支持、服务或 AI 推理成本压制？
- SBC 和股本稀释是否吞掉了自由现金流价值？

## 4. 核心 KPI 字典

| KPI | 计算/定义 | 研究用途 | 常见陷阱 |
|---|---|---|---|
| ARR | 年化经常性收入；以公司定义为准 | 订阅收入基准和 forward revenue 先行指标 | 有的公司用 ending ARR，有的用 run-rate revenue；并购 ARR 需剔除 |
| Revenue growth | reported / organic / constant currency | 顶线增长速度 | 并购、汇率、价格、一次性迁移收入会污染 |
| NRR / DBNRR | 期初客户群在期末的收入留存和扩张 | 老客户扩张与产品粘性 | 是否包含 churn、降级、价格、并购客户、超大客户扩张要查定义 |
| Gross retention | 剔除 expansion 后的收入留存 | 产品不可替代性 | 只披露 NRR 不披露 gross retention 时，可能用 upsell 掩盖 churn |
| Churn | 客户或收入流失率 | 需求韧性和竞争压力 | logo churn 与 revenue churn 含义不同 |
| RPO / cRPO | 剩余履约义务及 12 个月内可确认部分 | 已签合同和收入可见度 | 多年大单、合同期限变化、消费型合约会扭曲 |
| Billings | revenue + deferred revenue change | 订单/收款趋势 | 年付/月付变化、合同期限、预付款会影响 |
| Customer count | 付费客户数，常分 ACV 档 | 客户获取和上行空间 | 低价值客户增长不等于高质量 ARR |
| ACV / ARPA | 年合同价值 / 每账户收入 | 客户质量与上行空间 | 企业客户 mix 变化会推高但降低客户数增速 |
| Net new ARR | 新增 ARR | 增长动能 | 季节性强，需看 4Q rolling |
| CAC payback | 获客成本回收月数 | S&M 效率 | 用 gross margin-adjusted ARR 更保守 |
| Magic number | 净新增 ARR × 4 × gross margin / 上季 S&M | 销售效率 | 对季节性、企业大单和价格调整敏感 |
| Rule of 40 | 收入增长率 + FCF margin 或 operating margin | 增长和利润平衡 | 口径必须统一，不要混用 non-GAAP operating margin 和 unlevered FCF |
| Gross margin | gross profit / revenue | 软件经济性 | Professional services、hosting、AI inference cost 会压低 |
| S&M / Revenue | 销售营销费用率 | 增长投入强度 | 高增长阶段高费用率不一定坏，需结合新增 ARR |
| R&D / Revenue | 研发费用率 | 产品再投资 | 资本化软件、SBC 和平台迁移要单列 |
| SBC / Revenue | 股权激励 / revenue | 股东稀释 | Non-GAAP 利润常排除 SBC，但估值不能忽略 |
| FCF margin | FCF / revenue | 现金生成能力 | 年付预收款、裁员、capex、租赁和收款周期会扰动 |

必须优先披露的 8 个指标：ARR 或订阅收入、revenue growth、NRR 或 gross retention、RPO/cRPO、gross margin、S&M efficiency、FCF margin、SBC/revenue。

## 5. 财务模型结构

### 收入模型

按可得数据从高到低选择驱动：

1. `ARR beginning + new ARR + expansion ARR - churned ARR = ARR ending`
2. `客户数 × ARPA`
3. `seat 数 × price per seat × attach rate`
4. `usage volume × price per unit`
5. 披露不足时用订阅收入与服务收入分开预测，不得只做总收入 CAGR。

最低预测要求：

- 至少 3 年历史、8 个季度历史；首次覆盖财报模式同样适用。
- 未来 5 年显性预测，收入增速逐年向成熟水平衰减。
- 单列订阅收入、专业服务/实施收入、硬件或其他非订阅收入。
- 单列 organic growth 与并购影响；若无法拆分，写“未获取到拆分”，并降低结论置信度。

### 成本与利润率模型

- Gross margin：订阅毛利率和服务毛利率分开。若 AI 推理、云托管、支付通道或第三方数据成本显著，单独讨论稳态压力。
- S&M：用销售效率驱动，不要机械按收入比例下降。企业级 SaaS 需考虑销售周期和 quota capacity。
- R&D：高增长公司不能过早假设成熟利润率。若平台重构或 AI 产品投入期，研发杠杆应更慢释放。
- G&A：可随规模下降，但上市公司合规成本、并购整合、国际化会设下限。
- SBC：同时进入 diluted shares 和真实经济成本讨论；Non-GAAP margin 不能替代 FCF。
- FCF：从经营现金流、capex、capitalized software、租赁和 deferred revenue 变化解释，不只贴一个 margin。

### 稳态假设边界

- 成熟优质 SaaS 可拥有高毛利率和高 FCF margin，但必须由 retention、pricing power、低 churn 和费用杠杆支持。
- 若 NRR 下降、gross retention 低、CAC payback 拉长，不能同时给高增速、高稳态 margin 和低折现率。
- 若 SBC/revenue 长期高且回购只抵消稀释，应下调权益价值或显性增加股本稀释。

## 6. 估值方法

### 必做

1. **反向 DCF**：由现价倒推需要的稳态 ARR/revenue、FCF margin、增长年限和终局市场份额。用于回答“市场已经 price in 了什么”。
2. **三情景 DCF**：bear/base/bull 分别设置收入增速、FCF margin、稀释率和终值；概率和为 1，并做不利概率压力测试。
3. **相对估值**：EV/Revenue、EV/ARR、EV/FCF 或 P/FCF。高增长亏损期可用 EV/Revenue，但必须用 Rule of 40 和增长质量校正。

### 可选

- **SOTP**：平台公司、多个产品线差异大、或同时有云市场、数据、广告、支付、专业服务时使用。
- **EPV**：成熟盈利型 SaaS 可用，但早期亏损、高 SBC、高再投资公司不适合作为主估值。若使用 EPV，常态化盈利必须扣除真实 SBC 或通过稀释体现。
- **Unit economics 估值**：披露足够时，用 LTV/CAC、gross retention、CAC payback 交叉验证长期 FCF margin。

### Peer set 规则

选择 5-10 家可比公司，并标注选择理由：

- 产品类别：CRM、ERP、security、observability、data、collaboration、vertical SaaS 等。
- 客群：enterprise、mid-market、SMB、developer、consumer。
- 销售模式：sales-led、PLG、channel-led、marketplace-led。
- 增长阶段：高增长亏损、Rule of 40 平衡、成熟现金牛、转型受压。
- 地理与汇率：美国、欧洲、中国、全球化收入占比。

剔除项必须说明：若某公司看似同业但商业模式、毛利结构、客户群或增长阶段明显不同，不应强行放入同一倍数表。

## 7. 财报模式重点

财报模式必须回答“这份财报改变了什么”，而不是只列 beat/miss。

| 模块 | 必看问题 |
|---|---|
| 预期差 | 收入、ARR、billings、cRPO、operating margin、FCF 相对一致预期和公司指引差在哪里？ |
| 增长质量 | beat 来自新客户、扩张、价格、用量、提前确认、并购还是汇率？ |
| 留存 | NRR/gross retention/churn 是否改善？若未披露，管理层语言有无变化？ |
| RPO/cRPO | 新签与续约是否支持未来 12 个月收入？合同期限变化是否扭曲？ |
| 销售效率 | S&M 投入与 net new ARR 是否匹配？CAC payback 是改善还是牺牲增长换利润？ |
| 利润率 | 毛利率、S&M、R&D、G&A、SBC 和 FCF margin 哪项驱动利润变化？ |
| 指引 | revenue、operating margin、FCF、RPO 或 ARR 指引是否改变长期模型？ |
| 电话会 | demand、pipeline、budget scrutiny、AI monetization、pricing、seat expansion、churn 的措辞是否变强或变弱？ |
| 估值桥 | 新财报如何改变未来收入路径、稳态 FCF margin、稀释率、WACC 或情景概率？ |

财报后价格反应要扣除市场和同业表现：若公司上涨 8%，但 SaaS peer basket 同日上涨 5%，公司特异反应约为 +3%。

## 8. 护城河与竞争判断

SaaS 护城河不能只写“切换成本高”。至少从以下维度打分：

| 维度 | 强证据 | 弱证据/反证 |
|---|---|---|
| Workflow depth | 成为核心业务流程系统，停用会影响收入、合规或生产 | 只是 dashboard、插件或可替代工具 |
| Data moat | 客户数据、历史工作流、模型反馈形成累积优势 | 数据可轻易导出，竞品迁移成本低 |
| Ecosystem | API、marketplace、partner、developer 形成生态 | 生态收入弱，集成只是销售话术 |
| Multi-product expansion | 多模块 attach 推高 NRR 和 ARPA | 只靠单一爆款，cross-sell 证据不足 |
| Scale efficiency | S&M 效率随规模改善，gross retention 稳定 | 增长完全靠销售堆出来 |
| Pricing power | 多年提价后 churn 仍低，NRR 稳定 | 提价导致降级、seat contraction 或 logo churn |
| AI defensibility | AI 功能提升留存、ARPU、效率或数据壁垒 | AI 只是功能平权，压低价格或提高推理成本 |

定性护城河必须与财务证据交叉：若声称“强护城河”，但 gross retention 低、NRR 下降、CAC payback 拉长、SBC 高企，必须解释矛盾。

## 9. 红旗、反证与常见误判

### 红旗

- NRR 连续下降且公司停止披露或改口径。
- ARR 与 revenue 增速背离，且无法用合同期限、并购或汇率解释。
- RPO 增长靠合同期限拉长，而 cRPO 或 billings 走弱。
- 服务收入占比上升、订阅毛利率下降，说明软件化程度可能低于叙事。
- S&M 效率恶化但管理层仍维持长期高增长。
- Non-GAAP 利润好看，但 SBC/revenue 高、股本持续稀释。
- FCF 改善主要来自收款周期、裁员或 capex 延后，而不是经营杠杆。
- “AI 产品”只提升叙事，没有 attach rate、ARPU、retention 或 gross margin 证据。
- 并购贡献增长但 organic growth 未披露或明显放缓。
- 大客户集中、政府/单一行业预算暴露高，却使用普通 SaaS 倍数。

### 反证清单

每份 SaaS 报告至少列出 3 个能推翻主结论的证据阈值：

- NRR 低于某阈值或连续 N 个季度下降。
- cRPO / billings 增速跌破 revenue growth。
- CAC payback 拉长到超过合理区间。
- FCF margin 改善但 SBC/revenue 不降。
- AI/新产品未转化为 ARPU、attach rate 或 retention。
- 主要 peer 的价格战或产品替代导致 win rate 下降。

### 常见误判

- 把 EV/Revenue 低当便宜，但忽略低留存、低毛利或低增长质量。
- 把 Rule of 40 达标当充分条件，但忽略增长放缓后利润率还能否继续提升。
- 把 NRR 高当永续扩张，但忽略超大客户早期扩张不可持续。
- 把 deferred revenue 增长当 demand 强，忽略账期和预付款变化。
- 把裁员后的 margin 改善当经营杠杆，忽略产品和销售投入不足。

## 10. 报告输出要求

SaaS 公司报告除主模板外，必须增加以下表格或段落：

### SaaS KPI 表

| 指标 | 最新值 | 同比/环比 | 过去 8 季趋势 | 同业位置 | 来源与口径 |
|---|---:|---:|---|---|---|
| ARR / 订阅收入 | | | | | |
| Revenue growth | | | | | |
| NRR / gross retention | | | | | |
| RPO / cRPO | | | | | |
| Gross margin | | | | | |
| S&M efficiency / CAC payback | | | | | |
| Rule of 40 | | | | | |
| FCF margin | | | | | |
| SBC / revenue | | | | | |

### 估值假设表

| 假设 | Bear | Base | Bull | 依据 |
|---|---:|---:|---:|---|
| 5 年收入 CAGR | | | | |
| 稳态 FCF margin | | | | |
| 年化股本稀释 | | | | |
| 终局 EV/FCF 或退出倍数 | | | | |
| 情景概率 | | | | |

### 必写结论句

- “我的判断：这家公司当前估值最依赖的不是本季度收入，而是未来 N 年能否维持 X% 左右的增长并把 FCF margin 提升到 Y%。”
- “若 NRR / cRPO / CAC payback / SBC 中的任一核心指标触发以下阈值，我会下调长期假设：……”
- “当前股价隐含的 ARR、FCF margin 和终局份额是……；我认为这个隐含要求合理/激进/保守，原因是……”
