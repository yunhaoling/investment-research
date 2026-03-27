# B2C_SOFTWARE_AGENT_TEMPLATE.md
# B2C 软件公司 · 投资研究仪表板 · Agent 操作手册 v1.0
# 适用文件：`[COMPANY]_moat_tracker.html`
# 使用方式：将所有 `[占位符]` 替换为目标公司对应内容后使用

---

## 【全局规则 0：数据时效性与校验总则】

> ⚠️ **每次运行前必读，优先级高于所有模块指令。**

### 0.1 当前日期感知

Agent 在启动时**必须**先确认今天的日期，并以此为基准判断数据时效：

```
步骤 1：记录运行日期
  TODAY = 当前系统日期（YYYY-MM-DD）

步骤 2：推断最新已披露财季
  上市公司通常在季末后 6–8 周发布财报。
  规则：
    - 若 TODAY 在季末后 < 6 周 → 最新可用数据仍为上上季度
    - 若 TODAY 在季末后 ≥ 6 周 → 最新可用数据为上季度
    - 若已确认财报发布 → 使用已发布季度

步骤 3：明确标注数据截止日期
  所有填入 HTML 的数据，须在数据来源 Tab 注明「截止 [YYYY-QX]」。
```

### 0.2 强制数据验证规则

以下验证在**每次数据采集后立即执行**，不可跳过：

| 验证项 | 规则 | 失败时处理 |
|--------|------|-----------|
| 计算指标复核 | 所有由 Agent 自行计算的比率，必须基于原始数字重新计算，误差 < 0.2ppt | 重新核对原文；标注 recast 可能性 |
| YoY 增速一致性 | 原文 YoY% 与 Agent 计算偏差 > 1ppt → 不可直接使用 | 回溯上年同期原始数字，注明差异原因 |
| 数据来源唯一性 | 同一指标若多来源矛盾（如 IR 页与 SEC 不一致） | 以 SEC EDGAR 原文为准，其余来源仅作参考 |
| 数据新鲜度检查 | 情绪类数据（App 评分、Reddit）须确认为**当前页面实时内容**，非缓存或第三方转载 | 直接 `web_fetch` 原始页面 |
| 未披露字段处理 | 任何未在官方文件中出现的指标 → HTML 填 `—（未披露）`，**严禁估算或推断** | — |

### 0.3 运行前快速核查清单

```
□ 已确认 TODAY 日期？
□ 已判断最新可用财季？
□ SEC EDGAR（或对应交易所）已存在该季报原文？
□ 运行环境支持 web_search 和 web_fetch？
□ 目标 HTML 文件路径确认？
```

---

## 一、概述与触发机制

### 这份文档是什么

本文档是供 AI Agent 执行的完整季度更新 SOP（标准操作流程）。
每次运行后，`[COMPANY]_moat_tracker.html` 应完整反映最新一个季度的所有数据。

**使用前配置**（在本文件顶部维护）：

```yaml
# ── 目标公司配置 ──────────────────────────────
company_name: "[公司全名]"              # 如：Duolingo / Spotify / Discord
company_ticker: "[TICKER]"              # 如：DUOL / SPOT
exchange: "[交易所]"                    # NYSE / NASDAQ / 港交所等
sec_cik: "[CIK 编号]"                  # 仅美股上市公司；其他交易所见 4.1 注
ir_url: "[IR 主页 URL]"
app_store_id: "[iOS App ID]"
google_play_id: "[包名，如 com.xxx]"
reddit_community: "[r/xxx]"             # 主要社区，无则留空
trustpilot_slug: "[域名，如 spotify.com]"
business_model: "[freemium / 纯订阅 / 广告+订阅 / 其他]"
key_engagement_metric: "[DAU/MAU / WAU / 会话时长 / 其他]"  # 该公司最核心的参与度指标
```

### 触发条件

| 触发类型 | 条件 | 执行范围 |
|----------|------|----------|
| **主要触发** | 季度财报发布（季末后约 6–8 周） | 全流程，MODULE 1–6 + HTML + QC |
| **次要触发 A** | 重大产品变更公告（新功能上线、定价调整、订阅模式变化） | MODULE 3 + MODULE 4 情绪相关区域 |
| **次要触发 B** | 股价单日波动超过 ±10% | MODULE 1 财务速览 + MODULE 2 信号更新 |
| **次要触发 C** | 主要社区（Reddit/App Store）出现大规模舆情事件 | MODULE 3 情绪采集 |
| **次要触发 D** | 竞争对手重大动态（新产品、定价战、收购） | MODULE 2 品牌/网络效应护城河 |

### 执行顺序与依赖关系

```
【前置】全局规则 0：确认日期 + 明确可用财季
    ↓
MODULE 1: 财务数据采集
    ↓  （输出：核心指标数值）
MODULE 2: 护城河信号判断
    ↓  （依赖 MODULE 1 数据）
MODULE 3: 情绪数据采集
    ↓  （独立执行，不依赖前两步）
MODULE 6: 估值分析
    ↓  （依赖 MODULE 1；需采集同行数据与历史倍数）
MODULE 4: HTML 文件更新
    ↓  （依赖 MODULE 1 + 2 + 3 + 6 全部完成）
MODULE 5: 质量检验与版本归档
```

---

## 二、MODULE 1：财务数据采集

**目标**：从官方披露渠道获取最新季度的所有核心财务和用户指标。

> ⚡ **时效提醒**：执行本模块前，先运行**全局规则 0.1** 确认目标财季，再开始采集。

### 1.1 定位最新季报

**美股上市公司（SEC 路径）**：

```
步骤 1：搜索最新股东信或季报
  web_search: "[COMPANY] shareholder letter [最新季度] site:sec.gov"
  或直接访问 IR 主页：[ir_url]

步骤 2：SEC EDGAR 直接检索
  8-K 归档：https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=[CIK]&type=8-K&count=10
  10-Q 归档：https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=[CIK]&type=10-Q&count=10
```

**非美股上市公司（港股/A股/欧洲等）**：

```
港股：https://www.hkexnews.hk/（搜索股票代码）
A股：http://www.cninfo.com.cn/（巨潮资讯）
其他：参考 [ir_url] 披露的报告页面
数据来源 Tab 中注明所用文件编号和发布日期
```

**备用方案**（主链接失效时）：

```
1. IR 主页搜索 "earnings" / "quarterly results" / "interim results"
2. web_search: "[COMPANY] Q[X] [YYYY] earnings press release"
3. 专业数据终端（如 Bloomberg/Wind）仅作数据校验，不作唯一来源
```

### 1.2 必须采集的通用字段

从财报摘要表格中提取以下字段（根据公司实际披露调整）：

```yaml
# ── 用户/参与度指标 ──────────────────────────
primary_engagement_metric: ~         # 该公司核心参与度指标（如 DAU/WAU/MAU）
  value: ~                           # 数值（单位与原文一致）
  yoy_pct: ~                         # 同比增速（%）
  qoq_change: ~                      # 环比变化（带正负号）

secondary_engagement_metric: ~       # 次级指标（如 MAU / 会话时长 / 内容消费量）
  value: ~
  yoy_pct: ~

paying_users: ~                      # 付费用户数（绝对值，如公司披露）
  value: ~
  yoy_pct: ~
  as_pct_of_total: ~                 # 付费渗透率（付费 ÷ MAU 或类似基数）

# ── 财务指标 ─────────────────────────────────
total_revenue_millions: ~
revenue_yoy_pct: ~
gross_margin_pct: ~                  # 毛利率
operating_income_millions: ~         # 经营利润（GAAP）
adj_ebitda_millions: ~               # 调整后 EBITDA（如披露）
adj_ebitda_margin_pct: ~
free_cash_flow_millions: ~           # 自由现金流（如披露）

# ── 收入结构（如有分拆） ─────────────────────
subscription_revenue_millions: ~     # 订阅收入
advertising_revenue_millions: ~      # 广告收入（如有）
other_revenue_millions: ~

# ── 计算字段（Agent 自行计算，必须校验） ──────
engagement_ratio: ~                  # 如 DAU/MAU，保留一位小数
arpu_monthly: ~                      # = 订阅收入 ÷ 付费用户数（月度化）
```

**⚠️ 数据验证规则**（采集后立即执行，参见全局规则 0.2）：

```
✓ adj_ebitda_margin = adj_ebitda ÷ revenue × 100，与原文偏差 < 0.2ppt
✓ 所有比率字段均由 Agent 基于原始数字计算，不引用第三方估算
✓ YoY 增速与 Agent 计算结果偏差 > 1ppt → 核查是否存在历史数据重述（recast）
✓ 付费渗透率 = 付费用户 ÷ 活跃用户基数（须与公司定义一致，在来源 Tab 注明口径）
```

### 1.3 采集管理层指引

在财报「Guidance / Outlook」部分提取：

```yaml
next_quarter_guidance:
  quarter: ~
  revenue_growth_yoy_pct: ~          # 收入增速指引
  adj_ebitda_margin_pct: ~           # 利润率指引
  other_kpi_note: ~                  # 其他 KPI 说明（如 DAU 增速、订阅增速等）

full_year_guidance:
  year: ~
  revenue_growth_range: ~
  adj_ebitda_margin_range: ~
  key_investment_areas: ~            # 管理层强调的主要投入方向（AI / 内容 / 扩张等）
```

**指引衍生指标估算规则**（如管理层仅给出增速而非绝对值）：

```
指引绝对值 = 上年同季度实际值 × (1 + 指引 YoY 增速)
⚠️ 不得用上季度末数据乘以增速；须明确注明为 Agent 推算，非官方数字
```

### 1.4 采集关键定性表述

阅读财报正文，摘录管理层对以下方面的表述（与护城河判断直接相关）：

```yaml
qualitative_notes:
  user_growth_driver: ~              # 用户/参与度增长的主要来源
  monetization_update: ~             # 货币化策略变化
  cost_structure_comment: ~          # 成本趋势（尤其是 AI/基础设施成本）
  product_highlight: ~               # 重点产品进展
  competitive_positioning: ~         # 竞争格局表述
  strategic_shift: ~                 # 新战略调整（无则填 None）
  guidance_rationale: ~              # 指引逻辑说明
```

**重点关注触发词**——出现以下词汇时完整记录原句：
`"headwind"` / `"friction"` / `"churn"` / `"prioritize"` / `"AI-first"` / `"we acknowledge"` /
`"accelerate"` / `"plateau"` / `"pricing power"` / `"retention"` / `"competitive pressure"`

---

## 三、MODULE 2：护城河信号判断

**目标**：基于 MODULE 1 数据，判断四条护城河的当季状态，与上季度对比。

> 📌 **通用说明**：以下四条护城河适用于大多数 B2C 软件，但**部分指标须根据公司商业模式调整**。
> 模板中的数值阈值为**参考基准**，使用前应基于该公司历史数据重新标定。

### 2.1 行为锁定护城河（Behavioral Lock-in）

**核心问题**：用户是否已形成使用习惯，换用竞品的摩擦成本是否足够高？

**核心指标**：`engagement_ratio`（如 DAU/MAU）+ 留存率（如有披露）

| 信号组合 | 判断 | 颜色 |
|----------|------|------|
| 参与度指标同比提升 + 付费渗透率维持或上升 | 强·持续加深 | green |
| 参与度指标持平 + 付费渗透率轻微波动 | 稳·维持中 | amber |
| 参与度指标连续两季下滑 或 付费渗透率明显下降 | 弱·出现松动 | red |

**辅助判断**：
- MAU/用户基数环比方向（止跌回升 = 获客恢复 / 继续下滑 = 获客受损）
- 管理层是否披露用户习惯相关数据（如连续使用天数、功能完成率）
- ARPU 趋势（上升 = 用户深度参与 / 下降须区分定价调整还是用户降级）

```yaml
moat_behavioral_lock:
  status: ~                          # 强化中 / 稳定 / 受损
  engagement_ratio_current: ~
  engagement_ratio_vs_last_q: ~      # 改善 / 持平 / 恶化
  paid_penetration_current: ~
  key_evidence: ~
  signal_color: ~                    # green / amber / red
```

### 2.2 数据飞轮护城河（Data / AI Flywheel）

**核心问题**：随着用户规模扩大，产品质量是否持续提升？AI/数据积累是否构成壁垒？

**核心指标**：毛利率趋势 + R&D 占收入比 + 技术基础设施投入效率

| 指标 | 健康基准（参考，需按公司调整） | 警报线 |
|------|-------------------------------|--------|
| 毛利率 | 维持或逐步提升 | 连续两季大幅下滑且无战略解释 |
| R&D / Revenue | 随规模扩大呈下降趋势 | 收入增速放缓但 R&D 占比反弹 |
| ARPU YoY | ≥ 0%（维持或增长） | 连续负增长 |
| EBITDA margin | 随商业模式成熟逐步改善 | 非主动选择下持续恶化 |

**⚠️ 特殊规则**：若管理层**主动**压低毛利率以支撑战略性投入（如向免费用户开放 AI 功能、
扩张新市场），该下滑属于战略预期内。判断标准：实际值 vs 管理层指引偏差是否超过 1.5ppt。

```yaml
moat_data_flywheel:
  status: ~                          # 飞轮加速 / 正常运转 / 成本压制
  gross_margin_vs_guidance: ~        # 超预期 / 在轨 / 低于指引
  rd_efficiency_trend: ~             # 改善 / 持平 / 恶化
  ai_infra_cost_comment: ~           # 来自 MODULE 1.4 定性采集
  signal_color: ~
```

### 2.3 品牌资产护城河（Brand Moat）

**核心问题**：品牌是否能降低获客成本？用户是否因品牌认知主动选择该产品？

**核心判断矩阵**：

| S&M / Revenue 趋势 | 用户增速 | 判断 |
|--------------------|----------|------|
| 比率下降 | 维持或提升 | 品牌飞轮在转（green）|
| 比率持平或小幅上升 | 正增长 | 依赖付费获客，尚可接受（amber）|
| 比率大幅上升 | 增速下滑 | 品牌效率恶化（red）|
| 任何水平 | 用户绝对数下降 | 触发警报（red）|

**辅助信号**：
- App Store / Google Play 评分趋势（MODULE 3 提供）
- 社区口碑与自然传播证据（MODULE 3 提供）
- 管理层是否提及品牌活动及曝光数据

```yaml
moat_brand:
  sm_ratio_current: ~
  sm_ratio_trend: ~                  # 下降 / 持平 / 上升
  user_growth_vs_sm_scissors: ~      # 剪刀差扩大 / 持平 / 收窄
  organic_vs_paid_growth_comment: ~  # 来自 MODULE 1.4
  signal_color: ~
```

### 2.4 网络效应护城河（Network Effects）

**核心问题**：用户增加是否直接提升产品对其他用户的价值？

**适用性说明**：
- **强网络效应**：社交软件、通讯工具、UGC 平台（产品价值直接依赖其他用户）
- **弱网络效应**：独立学习/使用类应用（通过内容社区间接产生）
- **无网络效应**：纯工具类软件（诚实标注为 ★，不强行归入此护城河）

**观察信号（定性为主）**：
- 管理层是否披露社区功能参与率或社交功能数据
- 是否有「因为朋友/同事在用而留下」的获客案例或数据
- UGC 内容规模或社区活跃度是否持续增长

```yaml
moat_network_effect:
  applicability: ~                   # 强 / 弱 / 不适用（据商业模式判断）
  current_rating: ~                  # ★ / ★★ / ★★★
  rating_vs_last_quarter: ~          # 升级 / 维持 / 降级 / 无新数据
  community_signal: ~                # 正向 / 中性 / 负向 / 无
  signal_color: ~                    # green / amber / gray（不适用时）
```

### 2.5 护城河摘要（写入 HTML）

完成 2.1–2.4 后，写出本季度的一段护城河健康度摘要（≤ 80 字），用于更新 HTML「护城河信号」Tab 顶部说明文字。

---

## 四、MODULE 3：情绪数据采集

**目标**：采集三方平台用户情绪信号，与财务数据交叉验证。

> ⚡ **时效提醒**：所有情绪数据须通过 `web_fetch` 直接访问原始页面，
> 确保为**当前实时数据**，不得使用缓存、截图或第三方转载版本。

### 3.1 应用商店评分

```yaml
# iOS App Store
url: "https://apps.apple.com/us/app/[app-name]/id[app_store_id]"
采集字段:
  ios_rating: ~
  ios_rating_count: ~
  ios_top_complaints: ~             # 近期 1–2 星评论主要投诉类型

# Google Play
url: "https://play.google.com/store/apps/details?id=[google_play_id]&hl=en_US"
采集字段:
  android_rating: ~
  android_rating_count: ~
  android_top_complaints: ~

# Trustpilot（如有）
url: "https://www.trustpilot.com/review/[trustpilot_slug]"
采集字段:
  trustpilot_rating: ~
  trustpilot_review_count: ~
  trustpilot_complaint_type: ~
```

**投诉类型解读规则**：
- 投诉集中于「计费/退款/客服」→ 运营问题，**不触发**护城河警报，但在来源 Tab 标注
- 投诉转向「产品质量/核心功能变差/内容恶化」→ **触发**品牌护城河警报
- 投诉涉及「隐私/安全/数据泄露」→ 单独标注，视规模决定是否触发护城河警报

**评分变化阈值**（超过以下阈值须向情绪时间线新增事件）：
- iOS 或 Android 评分变化 ≥ 0.1 分
- Trustpilot 投诉主类型发生转变
- 任一平台评分跌破 4.0 分

### 3.2 社区情绪采样

```
# 主要社区（Reddit / Discord / 微博 / 小红书等，根据产品受众调整）

搜索 1: [reddit_community] 月度热帖
  URL: https://www.reddit.com/r/[community]/top/?t=month
  （或对应平台的热门内容页）

搜索 2: "[公司名]" 平台内 + 本季度核心关键词
  关键词示例：new feature / pricing change / [产品名] alternative / cancel subscription

搜索 3: "[公司名] alternative" 近3个月
  目标：判断用户流失意图强度
```

```yaml
community_overall_sentiment: ~      # 正面 / 分裂 / 负面
community_top_positive_themes: ~    # [主题1, 主题2]
community_top_negative_themes: ~    # [主题1, 主题2]
switch_intent_level: ~              # 低 / 中 / 高（「换产品」帖子频率）
notable_post_title: ~
notable_post_url: ~
```

### 3.3 搜索趋势

```
web_search: "google trends [公司名] vs [主要竞品1] vs [主要竞品2] 12 months"
目标 URL: https://trends.google.com/trends/explore?q=[公司],[竞品1],[竞品2]&date=today+12-m
```

```yaml
trends_direction: ~                 # 上升 / 持平 / 下降
trends_vs_top_competitor: ~         # 领先 / 接近 / 落后
trends_notable_spike: ~             # 异常峰值及原因，或 None
```

### 3.4 专业评测与行业报告（可选）

```
web_search: "[公司名] review [季度] [年份] site:[行业媒体域名]"
```

若有新的独立分析报告，提取其主要结论，记录为定性注释，并在来源 Tab 注明链接。

---

## 五、MODULE 6：估值分析

**目标**：基于 MODULE 1 财务数据，通过 PE / PS / DCF 三种方法，输出 Bear / Base / Bull 三情景目标价，并与历史估值区间（纵向）及可比公司（横向）进行对比，形成综合估值判断。

> ⚡ **时效提醒**：股价、市值须采集运行当日数据（参见全局规则 0.1）。历史倍数至少覆盖过去 8 个季度。

### 估值方法选用逻辑

在执行各估值方法前，先根据公司阶段确定**方法权重**：

| 公司阶段 | PS 权重 | PE 权重 | DCF 权重 | 说明 |
|---------|---------|---------|---------|------|
| 高增速 + 尚未稳定盈利（增速 > 30%，EBITDA margin < 15%） | 50% | 0%（改用 EV/Revenue 替代） | 50% | PE 不适用，DCF 捕捉长期价值 |
| 增速放缓 + 进入盈利通道（增速 15–30%，margin 15–25%） | 35% | 30% | 35% | 三法均衡 |
| 成熟盈利期（增速 < 15%，margin > 25%） | 20% | 45% | 35% | PE 为主，现金流稳定 |
| FCF 长期为负 | 40% | 0% | 降至 10%，需说明 | DCF 可靠性低，PS 主导 |

> Agent 须根据目标公司当季数据判断所处阶段，并在 `valuation_summary.weighting_rationale` 中说明。

### 护城河评级 → 情景概率联动规则

MODULE 2 的护城河评级**直接影响** Bear/Bull 情景的概率分配：

| 护城河综合评级（4条平均） | Bear 概率参考 | Base 概率参考 | Bull 概率参考 |
|--------------------------|-------------|-------------|-------------|
| 全绿（3–4 条 green） | 15–20% | 55–60% | 20–30% |
| 混合（多数 amber） | 25–30% | 50–55% | 15–25% |
| 偏弱（1 条以上 red） | 35–45% | 45–50% | 10–20% |

> 此为**起点参考**，Agent 须结合宏观环境（利率趋势、行业竞争格局）和管理层指引置信度进行最终调整，并在 `scenario_probability.rationale` 中说明调整依据。

---

### 6.0 前置数据采集

在进入各估值方法前，先采集以下基础数据：

```
web_search: "[TICKER] stock price today"
web_search: "[TICKER] shares outstanding market cap"
web_search: "[TICKER] balance sheet cash net debt latest quarter"
```

```yaml
market_data:
  as_of_date: ~                      # TODAY（YYYY-MM-DD）
  stock_price: ~                     # 当前股价
  shares_outstanding_millions: ~
  market_cap_millions: ~             # = 股价 × 流通股数（Agent 自行计算并核验）
  enterprise_value_millions: ~       # EV = 市值 + 净负债（净现金为负）
  net_cash_millions: ~               # = 现金及等价物 − 有息负债（来自最新资产负债表）
  balance_sheet_date: ~              # 净现金数据对应的资产负债表日期

ttm_financials:                      # TTM = 最近四个完整财季合计
  revenue_millions: ~
  gross_profit_millions: ~
  adj_ebitda_millions: ~
  free_cash_flow_millions: ~         # 若未披露则填 —（未披露）

forward_financials:                  # 基于管理层全年指引（MODULE 1.3 中点）
  next_fy_revenue_millions: ~
  next_fy_adj_ebitda_millions: ~
  revenue_growth_consensus_pct: ~    # 分析师共识增速（web_search）
```

**前置数据验证**：
```
✓ market_cap = stock_price × shares_outstanding，误差 < 1%
✓ EV 计算须与资产负债表日期一致，注明日期
✓ TTM = 最近已披露连续四个季度之和，逐季核算，不得使用年报估算
```

---

### 6.1 纵向比较：历史估值区间

**目标**：建立公司自身的估值锚点，判断当前倍数处于历史哪个分位。

**采集方式**：

```
# 搜索历史倍数摘要
web_search: "[COMPANY] historical P/S P/E EV/Revenue multiple by quarter"

# 若无现成数据，则基于已有各季度财报数据手动推算：
# 对每个历史季度：季末市值（股价 × 流通股）÷ TTM Revenue = 当季 P/S
```

```yaml
historical_multiples:               # 建议采集最近 8 个季度，逐季填写
  - quarter: ~
    period_end_price: ~
    ps_ttm: ~
    ev_revenue_ttm: ~
    pe_ttm: ~                       # 亏损则填 N/A
    ev_ebitda_ttm: ~                # EBITDA 为负则填 N/A

  # Agent 自行计算统计摘要
history_summary:
  ps_ttm_min: ~
  ps_ttm_max: ~
  ps_ttm_median: ~
  ps_ttm_current_percentile: ~      # 当前倍数在历史中的分位（0–100）
  ev_revenue_min: ~
  ev_revenue_max: ~
  ev_revenue_median: ~
  ev_revenue_current_percentile: ~
  pe_ttm_median: ~                  # 若有足够盈利历史
  pe_ttm_current_percentile: ~
```

**分位数解读规则**：

| 当前倍数分位 | 解读 | HTML 颜色 |
|-------------|------|-----------|
| > 75% | 估值偏高，需强劲增长支撑 | red |
| 50–75% | 合理偏高，部分增长已定价 | amber |
| 25–50% | 合理区间，市场情绪中性 | green |
| < 25% | 估值偏低，关注催化剂缺失原因 | amber |

---

### 6.2 横向比较：可比公司估值对标

**目标**：了解市场对同类 B2C 软件的定价逻辑，判断溢价/折价是否有基本面支撑。

**可比公司选择原则**：① 商业模式相似；② 收入增速同量级（±15ppt）；③ 不超过 6 家。

```
web_search: "[竞品1] [竞品2] [竞品3] NTM P/S EV Revenue multiple [当前年份]"
web_search: "B2C software [细分赛道] valuation comps [当前年份]"
```

```yaml
peer_companies:
  - name: ~
    ticker: ~
    business_model: ~               # freemium / 纯订阅 / 广告+订阅
    revenue_growth_yoy_pct: ~       # 最近 TTM
    gross_margin_pct: ~
    rule_of_40_score: ~             # = 收入增速% + FCF Margin%（或 EBITDA Margin%）
    ps_ntm: ~
    ev_revenue_ntm: ~
    pe_ntm: ~                       # 亏损填 N/A
    ev_ebitda_ntm: ~
    profitability_status: ~         # 盈利 / 亏损 / 盈亏平衡

peer_summary:
  median_ps_ntm: ~
  median_ev_revenue_ntm: ~
  median_pe_ntm: ~
  median_rule_of_40: ~
  target_ps_premium_vs_median_pct: ~   # 目标公司 PS 相对同行中位数溢价（%）
  premium_justification: ~             # 增速溢价 / 护城河溢价 / 折价 / 合理
```

**Rule of 40 溢价框架**：

| Rule of 40 得分 | 同行溢价参考 | 结合护城河（MODULE 2）调整 |
|----------------|-------------|--------------------------|
| ≥ 60 | 可接受 20–30% 溢价 | 护城河强 → 溢价上限取高端 |
| 40–60 | 0–15% 溢价区间 | 护城河中性 → 贴近中位数 |
| < 40 | 折价 10–20% | 护城河弱 → 折价下限取低端 |

---

### 6.3 PS 估值法

**适用场景**：高增速、尚未稳定盈利，或利润率波动较大的 B2C 软件公司。

**三情景 NTM Revenue 与 PS 倍数假设原则**：

| 情景 | 收入增速来源 | PS 倍数来源 |
|------|------------|------------|
| Bear | 指引下限 × 0.85；或历史最低增速 | 历史 PS 25 分位；或同行最低可比 |
| Base | 指引中点；或分析师共识 | 历史 PS 中位数；或同行中位数 |
| Bull | 指引上限 × 1.10；或近两年最高增速 | 历史 PS 75 分位；或同行顶部四分位 |

```yaml
ps_valuation:
  bear:
    ntm_revenue_millions: ~
    revenue_growth_assumption_pct: ~
    ps_multiple: ~
    implied_market_cap_millions: ~   # = ntm_revenue × ps_multiple
    implied_price: ~                 # = implied_market_cap ÷ shares_outstanding
    upside_downside_pct: ~
    multiple_source: ~               # 说明倍数选取依据

  base:
    ntm_revenue_millions: ~
    revenue_growth_assumption_pct: ~
    ps_multiple: ~
    implied_market_cap_millions: ~
    implied_price: ~
    upside_downside_pct: ~
    multiple_source: ~

  bull:
    ntm_revenue_millions: ~
    revenue_growth_assumption_pct: ~
    ps_multiple: ~
    implied_market_cap_millions: ~
    implied_price: ~
    upside_downside_pct: ~
    multiple_source: ~
```

---

### 6.4 PE 估值法

**适用场景**：Non-GAAP EPS 或 GAAP EPS 持续为正的公司。
**不适用时**：在 HTML 中标注「PE 法暂不适用 — [原因]」，改用 EV/EBITDA 替代。

**EPS 来源**：优先使用管理层 EPS 指引；若无则用 EBITDA 指引推算（需注明口径与税率假设）。

```yaml
pe_valuation:
  eps_basis: ~                       # Non-GAAP EPS / GAAP EPS / EV/EBITDA（替代）
  applicability: ~                   # 适用 / 暂不适用（注明原因）

  bear:
    ntm_eps: ~
    eps_assumption_note: ~           # 假设说明
    pe_multiple: ~                   # 历史 PE 25 分位 或 同行低端
    implied_price: ~
    upside_downside_pct: ~

  base:
    ntm_eps: ~
    eps_assumption_note: ~
    pe_multiple: ~
    implied_price: ~
    upside_downside_pct: ~

  bull:
    ntm_eps: ~
    eps_assumption_note: ~
    pe_multiple: ~
    implied_price: ~
    upside_downside_pct: ~
```

---

### 6.5 DCF 估值法

**说明**：DCF 对假设高度敏感，结果作为「内在价值参考范围」，不得作为唯一定价依据。
三情景主要通过**收入/FCF 增速**和 **WACC** 的差异来体现。

#### 6.5.1 WACC 估算

```
web_search: "10 year US treasury yield today"            # 无风险利率
web_search: "[COMPANY] [TICKER] beta 5 year monthly"    # β 系数
# 股权风险溢价（ERP）参考 Damodaran 当年更新值：通常 4.5–5.5%
```

```yaml
wacc_inputs:
  risk_free_rate_pct: ~             # 当日 10 年期国债收益率
  equity_risk_premium_pct: ~        # 4.5–5.5%（注明来源年份）
  beta: ~                           # 来源：Yahoo Finance / SEC 10-K
  cost_of_equity_pct: ~             # = Rf + β × ERP
  debt_weight_pct: ~                # 若几乎无有息负债则 ≈ 0
  wacc_base_pct: ~
  wacc_bear_pct: ~                  # Base + 1.5ppt
  wacc_bull_pct: ~                  # Base − 1.0ppt
```

#### 6.5.2 五年显式期预测 + 终值

```yaml
dcf_projections:
  base_year_fcf_millions: ~         # TTM FCF（来自 6.0）
  terminal_growth_rate_base_pct: ~  # 通常 2–3%（≤ 长期 GDP 增速）

  bear:
    fcf_growth_y1_pct: ~
    fcf_growth_y2_pct: ~
    fcf_growth_y3_pct: ~
    fcf_growth_y4_pct: ~
    fcf_growth_y5_pct: ~
    wacc_pct: ~                     # wacc_bear
    terminal_growth_pct: ~          # Base − 0.5ppt
    pv_explicit_millions: ~         # PV of Y1–Y5 FCF（Agent 逐年折现后求和）
    terminal_value_pv_millions: ~   # TV = FCF_Y5×(1+g)÷(WACC−g)，再折现至今
    enterprise_value_millions: ~
    equity_value_millions: ~        # = EV + net_cash
    implied_price: ~
    upside_downside_pct: ~

  base:
    fcf_growth_y1_pct: ~
    fcf_growth_y2_pct: ~
    fcf_growth_y3_pct: ~
    fcf_growth_y4_pct: ~
    fcf_growth_y5_pct: ~
    wacc_pct: ~
    terminal_growth_pct: ~
    pv_explicit_millions: ~
    terminal_value_pv_millions: ~
    enterprise_value_millions: ~
    equity_value_millions: ~
    implied_price: ~
    upside_downside_pct: ~

  bull:
    fcf_growth_y1_pct: ~
    fcf_growth_y2_pct: ~
    fcf_growth_y3_pct: ~
    fcf_growth_y4_pct: ~
    fcf_growth_y5_pct: ~
    wacc_pct: ~                     # wacc_bull
    terminal_growth_pct: ~
    pv_explicit_millions: ~
    terminal_value_pv_millions: ~
    enterprise_value_millions: ~
    equity_value_millions: ~
    implied_price: ~
    upside_downside_pct: ~

  # 敏感性分析（对 Base 情景）
  sensitivity:
    wacc_plus_1ppt_price: ~
    wacc_minus_1ppt_price: ~
    tgr_plus_0_5ppt_price: ~        # 终值增速 + 0.5ppt
    tgr_minus_0_5ppt_price: ~
    y1_y3_growth_plus_5ppt_price: ~
    y1_y3_growth_minus_5ppt_price: ~
```

---

### 6.6 三方法综合汇总与结论

```yaml
valuation_summary:
  as_of_date: ~
  current_price: ~

  # 三方法目标价矩阵
  method_results:
    ps:   { bear: ~, base: ~, bull: ~ }
    pe:   { bear: ~, base: ~, bull: ~ }   # N/A 若不适用
    dcf:  { bear: ~, base: ~, bull: ~ }

  # 综合目标价（加权平均，权重由 Agent 根据适用性分配，三者之和 = 100%）
  weighting:
    ps_weight_pct: ~
    pe_weight_pct: ~
    dcf_weight_pct: ~
    weighting_rationale: ~          # 说明权重分配逻辑（≤ 60 字）

  composite:
    bear_price: ~
    base_price: ~
    bull_price: ~

  # 情景概率（基于宏观环境 + 护城河评级，三者之和 = 100%）
  scenario_probability:
    bear_pct: ~
    base_pct: ~
    bull_pct: ~
    rationale: ~                    # 概率分配依据（≤ 80 字）

  # 期望值目标价
  expected_price: ~                 # = Σ(情景价格 × 概率)
  expected_upside_downside_pct: ~

  # 估值定性结论
  verdict: ~                        # 明显高估 / 略高估 / 合理 / 略低估 / 明显低估
  current_vs_history_percentile: ~  # 综合 PS/EV 历史分位描述
  current_vs_peers: ~               # 溢价 / 折价 X% vs 同行中位数
  key_bear_trigger: ~               # Bear 情景主要触发条件（≤ 60 字）
  key_bull_catalyst: ~              # Bull 情景主要催化剂（≤ 60 字）
  investment_summary: ~             # 综合估值判断，≤ 100 字
```

---

### 6.7 MODULE 6 数据验证清单

```
前置数据
□ market_cap 自行计算，误差 < 1%？
□ TTM 财务数据为四季度实际求和？
□ EV = 市值 + 净负债，资产负债表日期已记录？

纵向比较
□ 历史倍数覆盖 ≥ 8 个季度？
□ 历史分位数计算基于实际历史数据？

横向比较
□ 可比公司 ≤ 6 家，来源标注？
□ Rule of 40 计算口径一致（FCF Margin 或 EBITDA Margin，注明）？

PS / PE 估值
□ implied_market_cap = ntm_revenue × ps_multiple（逐情景核验）？
□ implied_price = implied_market_cap ÷ shares_outstanding？
□ PE 不适用情况已明确标注原因？

DCF
□ 终值分母 WACC − g > 0（否则终值无意义）？
□ 每年 FCF 折现：FCF_t ÷ (1+WACC)^t，逐年计算？
□ Bear WACC > Base WACC > Bull WACC？
□ 敏感性分析 6 个数值全部计算？

汇总
□ 加权权重之和 = 100%？
□ 情景概率之和 = 100%？
□ expected_price 计算无误？
```

---

## 六、MODULE 4：HTML 文件更新

**目标文件**：`[COMPANY]_moat_tracker.html`
**原则**：所有更新使用 `str_replace` 精确定位替换，不盲目追加内容。修改前必须 `view` 确认当前内容，避免覆盖有效历史数据。

### 4.1 「用户与财务」Tab

**新增季度卡片**（在 `.q-grid` 末尾插入）：

```html
<div class="q-card" onclick="selQ([N])" id="qc[N]">
  <div class="q-quarter">[Q# YYYY]</div>
  <div class="q-primary-metric">[主要参与度指标值]</div>
  <div class="q-yoy [badge]">↑ +[X]% YoY</div>
</div>
```

**徽章颜色规则**（根据公司历史增速区间设定，以下为通用参考）：
- `badge-up`：增速高于历史均值
- `badge-warn`：增速低于历史均值但为正增长
- `badge-danger`：增速为负或极低

**更新数据表格**：每行末尾追加新列，保持与卡片数量一致。

**同步更新 `selQ()` 函数**中的循环范围：`for (let i = 0; i < [N+1]; i++)`

### 4.2 「护城河信号」Tab

更新四个 `moat-card` 的 `.moat-body` 文字和 `.moat-dot` 颜色类（`dot-green` / `dot-amber` / `dot-red`）。

规则：保留历史关键数据点，新季度数据插入在最前；护城河★评级仅在真正升降时更新。

若新季度触发警报，新增或更新 `.alert` 框：

```html
<div class="alert [amber/red]">
  <strong>[⚠/🔴] [标题，10字以内]</strong><br>
  [说明，聚焦护城河含义，≤ 80字]
</div>
```

### 4.3 「指引」Tab

- 将上一季度的「指引」列更新为实际值（去掉指引样式）
- 新增下一季度的指引列（使用 `guide-col` 和虚线样式）
- 更新底部 `.prose` 战略解读文字

### 4.4 「观察清单」Tab（动态更新）

财报发布后：
1. 已达标指标 → 更新 priority badge 为绿色「✓ 已验证」
2. 未达标指标 → 在 `.wl-interp` 末尾追加实际结果行
3. 季度标题和财报预计日期更新为下一季度
4. 按最新护城河判断（MODULE 2 输出）重写观察指标列表

### 4.5 「应用评分」Tab

更新每个 `platform-card` 的评分数值、评分数量和更新日期（必须注明数据采集日期，非财报日期）。

### 4.6 「情绪时间线」Tab

**评分历史快照**：在末行前插入新行
颜色规则：≥ 4.5 → green / 4.0–4.4 → amber / < 4.0 → red

**情绪事件**（满足任一条件时添加）：
- 评分变化 ≥ 0.1 分
- 社区出现大规模情绪波动
- 重大产品变更引发明显用户反应
- 与护城河假设直接相关的用户反馈变化

新事件插入位置：`.snt-timeline` 中最后一个 `.tl-item` 之前。

**社区热词标签**：替换整组 `<span>` 标签（绿 = 正面 / 红 = 负面 / 橙 = 争议）。

### 4.6b 「估值分析」Tab

本 Tab 包含三个区块，每季度完整刷新：

**区块 1：三情景目标价矩阵**

```html
<div class="val-scenario-grid">
  <!-- 每行对应 PS / PE / DCF / 综合，每列对应 Bear / Base / Bull -->
  <div class="val-row val-composite">
    <div class="val-method">综合目标价</div>
    <div class="val-bear val-highlight">[综合 Bear 价] ([±X%])</div>
    <div class="val-base val-highlight">[综合 Base 价] ([±X%])</div>
    <div class="val-bull val-highlight">[综合 Bull 价] ([±X%])</div>
  </div>
</div>
<div class="val-expected">
  当前价格：[price] | 期望目标价：[expected_price]（[±X%]）| 判断：[verdict]
</div>
```

**区块 2：历史估值走势（纵向，≥ 8 季度）**

每季度一个柱，标注历史中位数线和当前分位；分位 > 75% 标红，< 25% 标绿。

**区块 3：同行估值对比表（横向）**

列：公司 / 收入增速 / 毛利率 / Rule of 40 / NTM P/S / NTM PE；目标公司行高亮。
表格下方补充：vs 同行中位数溢价/折价 %，以及 Rule of 40 对比说明。

**颜色规则**：
- Bear 列 → 红色调；Base 列 → 中性蓝；Bull 列 → 绿色调
- `verdict` 「高估」→ `dot-red`；「合理」→ `dot-amber`；「低估」→ `dot-green`
- 历史分位 > 75% → `hist-high`（红色警示）；< 25% → `hist-low`（绿色提示）

### 4.7 「数据来源」Tab

- 新增本季度财报链接行（含文件编号、发布日期、数据截止日期）
- 新增估值分析数据行：股价来源、可比公司来源、历史倍数来源（注明采集日期）
- 在校验记录中记录本次更新中发现的任何数据修正或口径变化
- 情绪数据来源注明采集日期（`web_fetch` 执行日期）

### 4.8 通用更新

```
□ footer 版本号递增（v[X] → v[X+1]）
□ footer 日期更新为今日
□ notice 框（如有）在财报发布后移除或更新
□ 指引列在实际值发布后取消「指引」样式
□ 确认 HTML 无语法错误，所有 Tab 切换正常
```

---

## 七、MODULE 5：质量检验与版本归档

### 5.1 数据一致性自检

```
财务数据
□ 所有比率字段均由 Agent 自行计算并核验，与原文偏差 < 0.2ppt？
□ YoY 增速与计算结果一致（差异 > 1ppt 须注明原因）？
□ 指引推算值是否基于上年同期而非上季度末？
□ 指引列是否有「指引」样式标注（虚线/橙色）？
□ 数据截止日期是否与最新可用财季一致（全局规则 0.1）？

护城河判断
□ 四条护城河信号颜色与数据逻辑一致？
□ 观察清单中已验证指标全部标注？
□ 新季度观察清单基于最新指引重写？
□ 网络效应护城河适用性判断是否合理？

情绪数据
□ 评分数据来自直接 web_fetch（非缓存）？
□ 采集日期已记录在来源 Tab？
□ Trustpilot 低分已注明投诉类型？
□ 新增情绪事件标注了数据来源？

估值分析
□ market_cap 自行计算，误差 < 1%？
□ TTM 财务数据为四季度实际求和？
□ 历史倍数覆盖 ≥ 8 个季度，分位数计算正确？
□ 可比公司倍数来源已在来源 Tab 标注？
□ PS implied_price = implied_market_cap ÷ shares_outstanding？
□ DCF 终值分母 WACC − g > 0？
□ DCF 敏感性分析 6 个数值全部计算？
□ 加权权重之和 = 100%，情景概率之和 = 100%？
□ expected_price 计算正确（Σ 价格 × 概率）？

页面完整性
□ 所有 Tab 可正常切换（switchTab 函数未被破坏）？
□ 估值 Tab 三区块均已更新（情景矩阵 / 历史走势 / 同行对比）？
□ selQ() 循环范围与 q-card 数量一致？
□ footer 版本号已递增？
□ 无遗留占位符（如 `~` 或空字段）？
```

### 5.2 边界情况处理

| 情况 | 处理方式 |
|------|----------|
| 某项数据未披露 | HTML 填 `—（未披露）`，**严禁估算** |
| 管理层重述历史数据（recast） | 在来源 Tab 校验记录中记录，更新所有受影响历史行；标注重述原因 |
| 主要数据源无法访问 | 用 `web_search` 找 IR 页面或交易所公告备用；来源 Tab 注明备用来源 |
| 评分平台显示整数（精度不足） | 来源 Tab 标注「精确度有限，显示为四舍五入值」 |
| 关键指标环比/同比为负 | HTML 用 `danger` 色标注；同步在护城河信号中体现 |
| 公司变更指标定义或口径 | 在来源 Tab 详细记录口径变化，历史数据追加注释，不强行与旧数据对比 |
| 情绪数据无法访问（地区限制） | 改用 web_search 获取近期摘录，来源 Tab 注明「间接采集」 |
| FCF 为负（DCF 无法直接使用） | 改用 EBITDA × (1 − 资本化率) 估算 FCF，来源 Tab 注明口径；或将 DCF 权重降至 10% 并以 PS/PE 为主 |
| 可比公司全部亏损（PE 无参考） | PE 法不适用，权重归零；EV/Revenue 替代 EV/EBITDA |
| 历史数据不足 8 季度（新上市）| 注明「历史数据不足，分位数参考价值有限」；以行业横向对比为主要锚点 |
| 管理层未提供收入指引 | Base 场景使用分析师共识（标注来源）；若无共识则用历史增速均值并加注不确定性说明 |

### 5.3 版本归档

在本文档「附录 D：版本历史」追加：

```
| v[X.X] | [YYYY-MM-DD] | [Q# YYYY] 财报更新 · [本次主要变化简述] |
```

---

## 附录 A：通用数据源索引

> **使用说明**：以下为各类数据源的通用 URL 模式，部分需替换 `[占位符]`。
> 请在目标公司配置完成后，将完整 URL 填入「财务数据源」表格。

### 财务数据源（一级，优先使用）

| 类型 | URL 模式 | 说明 |
|------|----------|------|
| SEC EDGAR（8-K） | `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=[CIK]&type=8-K&count=10` | 美股季度财报 |
| SEC EDGAR（10-Q） | `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=[CIK]&type=10-Q&count=10` | 美股季报详情 |
| 港交所披露 | `https://www.hkexnews.hk/` | 港股披露文件 |
| 巨潮资讯（A股） | `http://www.cninfo.com.cn/` | A股定期报告 |
| IR 主页 | `[ir_url]` | 各公司 IR 页面 |

### 估值数据源

| 类型 | URL 模式 / 来源 | 说明 |
|------|----------------|------|
| 当前股价 / 市值 | `web_search: "[TICKER] stock price today"` | 运行当日实时采集 |
| 流通股数 | `web_search: "[TICKER] shares outstanding"` | 季报或 IR 页面 |
| 历史股价 | `web_search: "[TICKER] historical price [季度末日期]"` | 各季末收盘价，用于计算历史倍数 |
| 分析师共识 | `web_search: "[TICKER] revenue consensus estimate [年份]"` | 仅作参考，需标注来源 |
| 同行倍数 | `web_search: "[竞品] NTM P/S valuation [当前年份]"` | 每季度采集并注明日期 |
| 无风险利率 | `web_search: "10 year treasury yield today"` | DCF WACC 输入，运行当日 |
| Beta | Yahoo Finance / SEC 10-K Beta section | 5 年月度 Beta |
| ERP（股权风险溢价） | `https://pages.stern.nyu.edu/~adamodar/` | Damodaran 年度更新值 |

### 情绪数据源（通用）

| 平台 | URL 模式 | 频率 |
|------|----------|------|
| App Store | `https://apps.apple.com/us/app/[app-name]/id[app_store_id]` | 每季度 |
| Google Play | `https://play.google.com/store/apps/details?id=[google_play_id]` | 每季度 |
| Trustpilot | `https://www.trustpilot.com/review/[trustpilot_slug]` | 每季度 |
| Reddit 月度热帖 | `https://www.reddit.com/r/[community]/top/?t=month` | 每月 |
| Google Trends | `https://trends.google.com/trends/explore?q=[公司],[竞品]&date=today+12-m` | 每季度 |
| Sensor Tower（可选） | `https://app.sensortower.com/overview/[google_play_id]?country=US` | 每季度 |

---

## 附录 B：护城河信号 → HTML 颜色映射（通用规则）

| 护城河 | 核心指标 | green 条件 | amber 条件 | red 条件 |
|--------|----------|------------|------------|----------|
| 行为锁定 | 参与度指标（DAU/MAU 等）+ 付费渗透率 | 指标同比提升 + 渗透率稳定 | 指标持平 + 轻微波动 | 连续两季下滑 或 渗透率明显下降 |
| 数据飞轮 | 毛利率 + R&D 效率 | 毛利率改善 + R&D 占比下降 | 符合战略指引内的压力 | 超出指引范围的大幅恶化 |
| 品牌资产 | S&M/Rev 比率 + 用户增速 | 比率降 + 增速稳 | 比率略升 + 增速正 | 比率大升 + 增速仍降 |
| 网络效应 | 社区/社交功能信号 | 明确社区化证据出现 | 无新信号 | 社区热度消退 或 不适用 |

---

## 附录 C：HTML 结构索引（str_replace 定位参考）

> 以下为通用 HTML 结构命名建议，实际使用时须与目标 HTML 文件的真实 class/id 对应。

```
季度卡片区域       → id="qc0" 至 id="qcN"
数据表格           → class="data-table" 内的 class="data-row"
主要指标柱状图     → id="overview" 内的 class="bar-section"
护城河卡片         → id="moat" 内的 class="moat-card"
护城河警报框       → class="alert amber" 或 class="alert red"
指引表格           → id="outlook" 内的 class="detail"
观察清单           → id="watchlist" 内的 class="wl-block"
评分卡片           → id="sent_ratings" 内的 class="platform-card"
情绪时间线         → id="sent_timeline" 内的 class="snt-timeline"
评分历史快照       → id="sent_timeline" 内的评分快照 grid 区域
社区热词           → id="sent_timeline" 内的 flex 热词 span 区域
估值情景矩阵       → id="valuation" 内的 class="val-scenario-grid"
估值期望目标价     → id="valuation" 内的 class="val-expected"
历史倍数走势图     → id="valuation" 内的 class="val-history-chart"
同行对比表         → id="valuation" 内的 class="val-peer-table"
同行溢折价说明     → id="valuation" 内的 class="val-peer-note"
来源表格           → id="sources" 内的 class="src-table"
数据校验记录       → id="sources" 内的 class="verify-grid"
页面版本号         → footer 内 class="footer-note"（右侧）
```

---

## 附录 D：版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-03 | 初始版本，从多邻国专用模板通用化。新增全局规则 0（数据时效与验证总则），覆盖 MODULE 1–5 完整流程 |
| v1.1 | 2026-03 | 新增 MODULE 6 估值分析（PE / PS / DCF 三法 + Bear/Base/Bull 三情景 + 纵向历史分位 + 横向同行对比）；同步更新执行流程、MODULE 4 估值 Tab、MODULE 5 检查清单、附录 A/C |

---

*使用前请完成「一、概述」中的公司配置项*
*适用范围：B2C 订阅制 / Freemium 软件公司季度分析*
*最后更新：2026 年 3 月*
