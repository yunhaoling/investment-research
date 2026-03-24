# DUOLINGO_AGENT_TEMPLATE.md
# 多邻国 DUOL · 投资研究仪表板 · Agent 操作手册 v2.0
# 适用文件：duolingo_moat_tracker.html

---

## 一、概述与触发机制

### 这份文档是什么

本文档是供 AI Agent 执行的完整季度更新 SOP（标准操作流程）。
每次运行后，`duolingo_moat_tracker.html` 应完整反映最新一个季度的所有数据。

Agent 需要具备的能力：`web_search`、`web_fetch`、文件读写（`str_replace` 或等效工具）。

### 触发条件

| 触发类型 | 条件 | 执行范围 |
|----------|------|----------|
| **主要触发** | Duolingo 季度财报发布（季末后约 6–8 周） | 全流程，MODULE 1–5 |
| **次要触发 A** | 重大产品变更公告（新功能上线、定价调整） | MODULE 3 + MODULE 4 情绪相关区域 |
| **次要触发 B** | 股价单日波动超过 ±10% | MODULE 1 财务速览 + MODULE 2 信号更新 |
| **次要触发 C** | Reddit r/duolingo 出现大规模舆情事件 | MODULE 3 情绪采集 |

### 执行顺序与依赖关系

```
MODULE 1: 财务数据采集
    ↓  （输出：核心指标数值）
MODULE 2: 护城河信号判断
    ↓  （依赖 MODULE 1 数据）
MODULE 3: 情绪数据采集
    ↓  （独立执行，不依赖前两步）
MODULE 4: HTML 文件更新
    ↓  （依赖 MODULE 1 + 2 + 3 全部完成）
MODULE 5: 质量检验与版本归档
```

---

## 二、MODULE 1：财务数据采集

**目标**：从 SEC EDGAR 获取最新季度的所有核心财务和用户指标。

### 1.1 定位最新季报

**步骤 1**：搜索最新股东信

```
web_search: "Duolingo shareholder letter [最新季度] site:sec.gov"
```

或直接访问 IR 页面获取最新链接：
`https://investors.duolingo.com`

**步骤 2**：SEC 文件 URL 规律

```
Q1: .../q1fy[YY]duolingo[月-日]share.htm
Q2: .../q2fy[YY]duolingo[月-日]share.htm
Q3: .../q3fy[YY]duolingo[月-日]share.htm
Q4: .../q4fy[YY]duolingo[月-日]shar.htm
```

EDGAR 归档入口（找最新 8-K）：
`https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001562088&type=8-K&count=10`

### 1.2 必须采集的字段

从股东信「Summary of Financial and Key Operating Metrics」表格提取：

```yaml
# 用户指标（直接引用原文数字）
dau_millions: ~          # 日活用户（百万）
dau_yoy_pct: ~           # 同比增速（%）
mau_millions: ~          # 月活用户（百万）
mau_qoq_change: ~        # 环比变化（百万，带正负号）
paid_subscribers_millions: ~
paid_yoy_pct: ~

# 财务指标（直接引用原文数字）
total_bookings_millions: ~
bookings_yoy_pct: ~
revenue_millions: ~
revenue_yoy_pct: ~
gross_margin_pct: ~
adj_ebitda_millions: ~
adj_ebitda_margin_pct: ~

# 计算字段（Agent 自行计算，必须核验）
dau_mau_ratio: ~         # = DAU ÷ MAU × 100，保留一位小数
```

**数据验证规则**（采集后立即核算）：

```
✓ adj_ebitda_margin = adj_ebitda ÷ revenue × 100，与原文偏差 < 0.2ppt
✓ dau_mau_ratio 自行计算，不引用第三方估算
✓ YoY 增速与计算结果偏差 > 1ppt → 重新核对原文，可能有 recast
```

### 1.3 采集管理层指引

在股东信「Guidance」部分提取：

```yaml
next_q_guidance:
  quarter: ~
  bookings_growth_yoy_pct: ~
  revenue_growth_yoy_pct: ~
  adj_ebitda_margin_pct: ~
  gross_margin_note: ~       # 如有特殊说明（如 AI 成本影响）

fy_guidance:
  year: ~
  bookings_growth_range: ~
  revenue_growth_range: ~
  adj_ebitda_margin: ~
  dau_growth_expectation: ~  # 如披露
```

**指引 DAU 估算规则**（如管理层给出 YoY 增速而非绝对值）：

```
指引 DAU = 上年同季度实际 DAU × (1 + 指引 YoY 增速)
不得用上季度末 DAU 乘以增速
```

### 1.4 采集关键定性表述

阅读股东信正文，摘录管理层对以下方面的表述：

```yaml
qualitative_notes:
  user_growth_driver: ~       # DAU 增长主要来源
  ai_cost_comment: ~          # GenAI 成本趋势
  product_highlight: ~        # 重点产品进展
  strategic_shift: ~          # 新战略调整（如无则 None）
  guidance_rationale: ~       # 指引逻辑说明
```

**重点关注触发词**——出现以下词汇时完整记录原句：
`"friction"` / `"headwind"` / `"prioritize"` / `"AI-first"` / `"we acknowledge"` / `"accelerate"`

---

## 三、MODULE 2：护城河信号判断

**目标**：基于 MODULE 1 数据，判断四条护城河的当季状态，与上季度对比。

### 2.1 行为锁定护城河

**核心指标**：DAU/MAU ratio

| 数值区间 | 判断 | 颜色 |
|----------|------|------|
| ≥ 40% 且环比上升 | 强·持续加深 | green |
| 37%–40% 或持平 | 稳·维持中 | amber |
| < 37% 或连续两季环比下滑 | 弱·出现松动 | red |

**辅助判断**：
- MAU 环比方向（止跌回升 = 拉新恢复 / 继续下滑 = 获客受损）
- 管理层是否披露 streak 相关数据
- 付费转化率 = 付费用户 ÷ MAU，是否维持 ≥ 8.5%

**输出**：
```yaml
moat_behavioral_lock:
  status: ~                  # 强化中 / 稳定 / 受损
  key_evidence: ~
  signal_color: ~            # green / amber / red
  vs_last_quarter: ~         # 改善 / 持平 / 恶化
```

### 2.2 数据飞轮护城河

**核心指标**：毛利率 + R&D 占收入比 + Sub ARPU 增速

| 指标 | 健康基准 | 警报线 |
|------|----------|--------|
| 毛利率 | ≥ 72% | < 70% 连续两季 |
| R&D / Revenue (GAAP) | ≤ 32%，持续下降趋势 | 反弹超过 35% |
| Sub ARPU YoY | ≥ +5% | 负增长 |
| EBITDA margin | ≥ 25%（战略期允许主动压低） | < 20% 且非主动选择 |

**2026 年特殊规则**：管理层主动将毛利率压低至约 69–71%（向免费用户开放 AI），
此期间毛利率下滑属于战略预期内。若实际低于指引超过 1.5ppt，才标记红色。

**输出**：
```yaml
moat_data_flywheel:
  status: ~                          # 飞轮加速 / 正常运转 / 成本压制
  gross_margin_vs_guidance: ~        # 超预期 / 在轨 / 低于指引
  ai_cost_trend: ~                   # 改善 / 持平 / 恶化
  signal_color: ~
```

### 2.3 品牌资产护城河

**核心判断矩阵**：

| 信号组合 | 判断 |
|----------|------|
| S&M 比率下降 + DAU 增速维持 | 品牌飞轮在转（green） |
| S&M 比率上升 + DAU 增速回升 | 依赖付费获客（amber） |
| S&M 比率上升 + DAU 仍下滑 | 双重恶化（red） |

**辅助信号**：
- 管理层是否提及病毒式营销活动及曝光数据
- App Store 评分是否维持 ≥ 4.5（MODULE 3 提供）
- 社区 UGC 情绪（MODULE 3 提供）

**输出**：
```yaml
moat_brand:
  sm_ratio_trend: ~          # 下降 / 持平 / 上升
  dau_vs_sm_scissors: ~      # 剪刀差扩大 / 持平 / 收窄
  signal_color: ~
```

### 2.4 网络效应护城河

**当前基准**：★★（弱），处于早期演进阶段。

**观察信号（定性为主）**：
- 管理层是否披露 Chess PvP 参与率或社区赛事数据
- 是否有「因为朋友在用 Chess 而留下」的用户表述
- Friend Streak 渗透率是否继续上升

**输出**：
```yaml
moat_network_effect:
  rating_change: ~           # 升级 ★★→★★★ / 维持 ★★ / 无新数据
  chess_community_signal: ~  # 正向 / 中性 / 无
  signal_color: ~            # green / amber / gray
```

### 2.5 护城河摘要（写入 HTML）

完成 2.1–2.4 后，写出本季度的一段护城河健康度摘要（≤ 80 字），用于更新 HTML「护城河信号」Tab 顶部说明文字。

---

## 四、MODULE 3：情绪数据采集

**目标**：采集三方平台用户情绪信号，与财务数据交叉验证。

### 3.1 应用商店评分

```
# App Store
web_fetch: https://apps.apple.com/us/app/duolingo-language-lessons/id570060128
采集: ios_rating, ios_rating_count

# Google Play
web_fetch: https://play.google.com/store/apps/details?id=com.duolingo&hl=en_US
采集: android_rating, android_rating_count, android_top_recent_complaint

# Trustpilot
web_fetch: https://www.trustpilot.com/review/duolingo.com
采集: trustpilot_rating, trustpilot_review_count, trustpilot_complaint_type
```

**Trustpilot 解读规则**：
- 投诉类型为「计费/退款/客服」→ 不触发护城河警报，标注说明
- 投诉类型转向「产品质量/内容变差」→ 触发品牌护城河警报

**评分变化阈值**（超过以下阈值须向情绪时间线新增事件）：
- iOS 或 Android 变化 ≥ 0.1 分
- Trustpilot 投诉主类型发生转变

### 3.2 Reddit 情绪采样

按顺序执行：
```
搜索 1: reddit.com/r/duolingo 月度热帖
  URL: https://www.reddit.com/r/duolingo/top/?t=month

搜索 2: "duolingo" site:reddit.com [本季度核心关键词]
  关键词示例：AI free / energy system / MAU / chess / leaving duolingo

搜索 3: "duolingo alternative" site:reddit.com 最近3个月
```

**输出字段**：
```yaml
reddit_overall_sentiment: ~   # 正面 / 分裂 / 负面
reddit_top_positive: ~        # [主题1, 主题2]
reddit_top_negative: ~        # [主题1, 主题2]
reddit_switch_intent: ~       # 低 / 中 / 高（「换 App」帖子频率）
reddit_notable_post_title: ~
reddit_notable_post_url: ~
```

### 3.3 Google Trends

```
web_search: google trends duolingo vs babbel vs chatgpt language learning 12 months
目标 URL: https://trends.google.com/trends/explore?q=duolingo,babbel,chatgpt+language&date=today+12-m
```

**输出字段**：
```yaml
trends_direction: ~                   # 上升 / 持平 / 下降
trends_vs_chatgpt_language: ~         # 领先 / 接近 / 落后
trends_notable_spike: ~               # 异常峰值及原因，或 None
```

### 3.4 Class Central（可选）

```
web_search: "Duolingo [季度] [年份] site:classcentral.com"
```

如有新报告，提取其独立分析结论，记录为定性注释。

---

## 五、MODULE 4：HTML 文件更新

**目标文件**：`duolingo_moat_tracker.html`
**原则**：所有更新使用 `str_replace` 精确定位替换，不盲目追加内容。

### 4.1 「用户与财务」Tab

**新增季度卡片**（在 `.q-grid` 末尾插入）：

```html
<div class="q-card" onclick="selQ([N])" id="qc[N]">
  <div class="q-quarter">[Q# YYYY]</div>
  <div class="q-dau">[DAU]M</div>
  <div class="q-yoy [badge]">↑ +[X]% DAU YoY</div>
</div>
```

徽章规则：`badge-up`（≥30%）/ `badge-warn`（15–29%）/ `badge-danger`（<15%）

**更新数据表格**：每一行末尾追加新列，保持与卡片数量一致。

**更新柱状图 bar 宽度换算**（DAU 增速）：

| 增速 | width |
|------|-------|
| 50% | 83% |
| 40% | 67% |
| 30% | 50% |
| 20% | 33% |
| 10% | 17% |

**同步更新 selQ() 函数**中的循环范围：`for (let i = 0; i < [N+1]; i++)`

### 4.2 「护城河信号」Tab

更新四个 `moat-card` 的 `.moat-body` 文字和 `.moat-dot` 颜色类（dot-green / dot-amber / dot-red）。

规则：保留历史关键数据点，在前面插入新季度数据；护城河★评级仅在真正升降时更新。

若新季度触发警报，新增或更新 `.alert` 框：

```html
<div class="alert [amber/red]">
  <strong>[⚠/🔴] [标题，10字以内]</strong><br>
  [说明，聚焦护城河含义，≤80字]
</div>
```

### 4.3 「2026 指引」Tab

- 将上一季度的「指引」列更新为实际值（去掉指引样式）
- 新增下一季度的指引列（使用 `guide-col` 和虚线样式）
- 更新底部 `.prose` 战略解读文字

### 4.4 「Q1 2026 观察清单」Tab（动态更新）

财报发布后：
1. 已达标指标 → 更新 priority badge 为绿色「✓ 已验证」
2. 未达标指标 → 在 `.wl-interp` 末尾追加实际结果行
3. 季度标题和财报预计日期更新为下一季度
4. 按最新护城河判断（MODULE 2 输出）重写 9 个观察指标

### 4.5 「应用评分」Tab

更新每个 `platform-card` 的评分数值、评分数量和更新日期。

### 4.6 「情绪时间线」Tab

**评分历史快照**：在末行前插入新行（颜色规则：≥4.5→green, 4.0–4.4→amber, <4.0→red）

**情绪事件**（满足任一条件时添加）：
- 评分变化 ≥ 0.1 分
- Reddit 大规模情绪波动
- 重大产品变更引发明显社区反应
- 与护城河假设直接相关的用户反馈变化

新事件插入位置：`.snt-timeline` 中最后一个 `.tl-item` 之前。

**Reddit 热词标签**：替换整组 `<span>` 标签（绿=正面，红=负面，橙=争议）。

### 4.7 「数据来源」Tab

新增 SEC 季报链接行，并在校验记录中记录本次更新中发现的任何数据修正。

### 4.8 通用更新

```
□ footer 版本号递增（v2.X → v2.X+1）
□ footer 日期更新
□ notice 框（如有）在财报发布后移除或更新
□ Q1 指引列在实际值发布后取消「指引」样式
```

---

## 六、MODULE 5：质量检验与版本归档

### 5.1 数据一致性自检

```
财务数据
□ DAU/MAU ratio 自行计算，与原文数字一致？
□ EBITDA 利润率 = EBITDA ÷ Revenue，与财报一致？
□ 指引 DAU 估算：基准为上年同期，而非上季度末？
□ 指引列是否有「指引」样式标注（虚线/橙色）？

护城河判断
□ 四条护城河信号颜色与数据逻辑一致？
□ 观察清单中已验证指标全部标注？
□ 新季度观察清单基于最新指引重写？

情绪数据
□ 评分来自当前页面（非缓存）？
□ Trustpilot 低分注明投诉类型？
□ 新增情绪事件标注了数据来源？

页面完整性
□ 所有 Tab 可正常切换（switchTab 函数未被破坏）？
□ selQ() 循环范围与 q-card 数量一致？
□ footer 版本号已递增？
```

### 5.2 边界情况处理

| 情况 | 处理方式 |
|------|----------|
| 某项数据未披露 | HTML 填 `—（未披露）`，不估算 |
| 管理层 recast 历史数据 | 在来源 Tab 校验记录中记录，更新所有受影响历史行 |
| SEC URL 无法访问 | 用 `web_search` 找 IR 页面备用 PDF |
| Google Play 评分显示整数 | 来源 Tab 标注「精确到0.1分，部分渠道显示四舍五入值」 |
| MAU 低于上季度 | `mau_qoq_change` 填负值，HTML 用 `danger` 色标注 |

### 5.3 版本归档

在本文档「附录 D：版本历史」追加：

```
| v[X.X] | [YYYY-MM-DD] | [Q# YYYY] 财报更新 · [本次主要变化简述] |
```

---

## 附录 A：全部数据源速查

### 财务数据源（一级）

| 季度 | URL |
|------|-----|
| Q1 2025 | https://www.sec.gov/Archives/edgar/data/0001562088/000156208825000098/q1fy25duolingo3-31x25share.htm |
| Q2 2025 | https://www.sec.gov/Archives/edgar/data/0001562088/000156208825000165/q2fy25duolingo6-30x25share.htm |
| Q3 2025 | https://www.sec.gov/Archives/edgar/data/1562088/000162828025049514/q3fy25duolingo9-30x25share.htm |
| Q4 2025 | https://www.sec.gov/Archives/edgar/data/0001562088/000162828026012246/q4fy25duolingo12-31x25shar.htm |
| EDGAR 归档 | https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001562088&type=8-K&count=10 |
| IR 主页 | https://investors.duolingo.com |

### 情绪数据源

| 平台 | URL | 频率 |
|------|-----|------|
| App Store | https://apps.apple.com/us/app/duolingo-language-lessons/id570060128 | 每季度 |
| Google Play | https://play.google.com/store/apps/details?id=com.duolingo | 每季度 |
| Trustpilot | https://www.trustpilot.com/review/duolingo.com | 每季度 |
| Sitejabber | https://www.sitejabber.com/reviews/duolingo.com | 每季度 |
| Reddit 月度热帖 | https://www.reddit.com/r/duolingo/top/?t=month | 每月 |
| Google Trends | https://trends.google.com/trends/explore?q=duolingo,babbel,pimsleur&date=today+12-m | 每季度 |
| Sensor Tower | https://app.sensortower.com/overview/com.duolingo?country=US | 每季度 |
| Kimola | https://kimola.com/reports/comprehensive-duolingo-review-report-insights-feedback-google-play-en-us-142121 | 每半年 |
| Class Central | https://www.classcentral.com/report/duolingo-2025/ | 财报后 |

---

## 附录 B：护城河信号 → HTML 颜色映射

| 护城河 | 核心指标 | green 条件 | amber 条件 | red 条件 |
|--------|----------|------------|------------|----------|
| 行为锁定 | DAU/MAU ratio | ≥40% 且环比升 | 37–40% 或持平 | <37% 或连续下滑 |
| 数据飞轮 | 毛利率 | ≥72%（或符合指引） | 70–72% | <70% 且非战略选择 |
| 品牌资产 | S&M/Rev 比率趋势 | 比率降 + DAU 增速稳 | 比率持平 | 比率升 + DAU 仍降 |
| 网络效应 | 社区/Chess 信号 | 出现具体社区化证据 | 无新信号 | 热度消退 |

---

## 附录 C：HTML 结构索引（str_replace 定位用）

```
季度卡片区域       → id="qc0" 至 id="qcN"
数据表格           → class="data-table" 内的 class="data-row"
DAU 柱状图         → id="overview" 内第一个 class="bar-section"
EBITDA 柱状图      → id="overview" 内第二个 class="bar-section"
护城河卡片         → id="moat" 内的 class="moat-card"
护城河警报         → class="alert amber" 或 class="alert red"
指引表格           → id="outlook" 内的 class="detail"
观察清单           → id="watchlist" 内的 class="wl-block"
评分卡片           → id="sent_ratings" 内的 class="platform-card"
情绪时间线         → id="sent_timeline" 内的 class="snt-timeline"
评分历史快照       → id="sent_timeline" 内的评分快照 grid 区域
Reddit 热词        → id="sent_timeline" 内的 flex 热词 span 区域
来源表格           → id="sources" 内的 class="src-table"
数据校验记录       → id="sources" 内的 class="verify-grid"
页面版本号         → footer 内 class="footer-note"（右侧）
```

---

## 附录 D：版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-03 | 初始版本，仅覆盖情绪数据采集 |
| v2.0 | 2026-03 | 完整重写，新增财务采集（MODULE 1）、护城河判断（MODULE 2）、完整 HTML 更新规范（MODULE 4）、质量检验（MODULE 5） |

---

*配套 HTML 文件：`duolingo_moat_tracker.html`*
*最后更新：2026 年 3 月*
