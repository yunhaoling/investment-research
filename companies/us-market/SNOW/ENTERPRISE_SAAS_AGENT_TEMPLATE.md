# ENTERPRISE_SAAS_AGENT_TEMPLATE.md
# 企业级 B2B SaaS · 护城河分析框架 · 通用 Agent 模板 v1.0
# 适用范围：数据平台 / 云基础设施 / 企业软件
# 当前实例：Snowflake (SNOW) — 适配文件：snowflake_moat_tracker.html

---

## 一、B2B SaaS 与 B2C 产品的根本性差异

在使用本模板前，必须理解为什么 B2B SaaS 护城河的分析逻辑与 B2C 产品（如多邻国）完全不同：

| 维度 | B2C 产品（多邻国） | 企业级 B2B SaaS（Snowflake） |
|------|-------------------|------------------------------|
| **核心护城河** | 行为习惯 / 情感锁定 | 数据引力 / 迁移成本 |
| **关键用户指标** | DAU / MAU / DAU/MAU | NRR / RPO / $1M+ 客户数 |
| **收入模式** | 订阅制（固定费用）| 消费制（用多少付多少）|
| **竞争转换成本** | 低（换 App 只需几秒）| 极高（数据迁移以工程月计）|
| **增长信号** | 新用户获取 + 留存 | 存量客户消费扩张（NRR > 100%）|
| **风险来源** | 用户习惯改变 / 竞品获客 | 云厂商内置化 / 竞品分流特定工作负载 |
| **情绪信号** | App Store 评分 / Reddit | G2 / Gartner Peer Insights / 开发者社区 |

---

## 二、企业级 B2B SaaS 护城河通用框架

### 框架一：五类护城河强度评估

每次分析时，对以下五类护城河逐一评估，填写强度（★★★★★ 到 ★）和信号颜色（green/amber/red）：

#### 2.1 迁移成本护城河（Switching Costs）

**适用场景**：数据平台、ERP、CRM、安全工具、工作流平台

**强度驱动因素**：
- 数据量（TB/PB 级 → 迁移成本呈超线性增长）
- 工作流深度（ETL 管道数、下游依赖应用数）
- 团队技能绑定（员工培训成本）
- API 和集成数量

**核心可观测指标**：
```yaml
nrr: ~                    # 净收入留存率，直接体现迁移成本
rpq_growth_vs_rev_growth: ~ # RPO 增速 > 产品营收增速 = 客户在锁定更长期合同
churn_rate: ~             # 客户流失率（消费额口径，非客户数口径）
large_customer_growth: ~  # $1M+ 客户增速（深度依赖的代理指标）
contract_length_trend: ~  # 平均合同期限是否在延长
```

**健康基准**（以 Snowflake 为参考）：
- NRR ≥ 120% → 强护城河
- NRR 110–120% → 正常
- NRR < 110% 连续两季度 → 警报

#### 2.2 网络效应护城河（Network Effects）

**适用场景**：数据市场、协作平台、支付网络、API 平台

**两种形态**：
- **直接网络效应**：用户越多，产品对每个用户价值越高（如 Slack、LinkedIn）
- **数据网络效应**：更多数据/用户 → 更好的模型/匹配 → 吸引更多用户（如 Snowflake Data Marketplace）

**核心可观测指标**：
```yaml
marketplace_listings: ~       # 数据集/产品数量
cross_company_shares: ~       # 跨企业数据共享关系数
platform_customer_coverage: ~ # 如 Forbes G2000 覆盖率（作为市场渗透代理）
partner_ecosystem_size: ~     # 合作伙伴和集成数量
```

**盲区警告**：网络效应类指标往往是公司最不愿意披露的。若财报中完全缺失，需在电话会议中主动追问。

#### 2.3 平台生态锁定（Ecosystem Lock-in）

**适用场景**：云平台、开发者工具、数据平台、低代码平台

**强度驱动因素**：
- 工作负载类别多样性（每增加一个工作负载，锁定成本乘数增加）
- 应用/ISV 生态（第三方在平台上构建了多少产品）
- 开发者技能绑定（特有 API / SDK / 专有语言）

**核心可观测指标**：
```yaml
workload_categories_per_customer: ~ # 每客户工作负载类别（越多越难迁移）
native_apps_count: ~                # 平台上的原生应用数
isv_partner_count: ~                # 集成伙伴数量
developer_community_size: ~         # GitHub Stars / Stack Overflow 讨论量
```

#### 2.4 规模经济（Scale Economics）

**适用场景**：云基础设施、数据平台、AI 训练平台

**与 B2C 规模效应的区别**：B2B 规模经济更多体现在单位基础设施成本递减，而非用户边际成本递减。

**核心可观测指标**：
```yaml
product_gross_margin: ~        # 产品毛利率（排除服务）
infrastructure_cost_per_unit: ~ # 单位计算成本趋势
fcf_margin: ~                  # 自由现金流利润率（规模杠杆的综合体现）
r_and_d_as_pct_revenue: ~      # R&D 占收入比（是否在递减）
```

**健康基准**（Snowflake 参考）：
- 产品毛利率 ≥ 72% → 健康
- FCF Margin ≥ 20% → 达到规模效应
- 若毛利率下降 > 2ppt YoY → 需追问原因

#### 2.5 品牌 + 信任护城河（Brand / Trust）

**特殊性**：B2B 品牌护城河的核心不是消费者认知，而是企业 CTO / CDO 心目中的「默认选择」地位（category leader），以及安全/合规信任。

**核心可观测指标**：
```yaml
gartner_magic_quadrant_position: ~ # Gartner 魔力象限位置（Leader/Visionary）
g2_category_ranking: ~             # G2 企业评分排名
analyst_citations: ~               # 分析师报告引用频率
enterprise_security_certs: ~       # SOC2 / ISO 认证状态
logo_win_rate: ~                    # 竞争性 RFP 赢单率
```

---

## 三、MODULE 1：财务数据采集（B2B SaaS 版本）

**目标**：从 SEC EDGAR 获取最新季度的所有核心指标。

### 1.1 定位最新季报

```
web_search: "[公司名] quarterly earnings [季度] site:sec.gov"
```

Snowflake 特定：
- 财年截止 1 月 31 日（FY = 上一年2月–当年1月）
- EDGAR CIK：0001640147
- 文件命名规律：`fy[年]q[季度]earnings.htm`

### 1.2 消费制 vs 订阅制的采集差异

**消费制（Snowflake 类型）采集重点**：
```yaml
product_revenue: ~            # 产品营收（非总营收）
product_revenue_yoy: ~        # YoY 增速
professional_services_rev: ~  # 专业服务（通常低毛利，单独追踪）
```

**订阅制（传统 SaaS）采集重点**：
```yaml
arr: ~                    # 年化经常性收入
arr_growth_yoy: ~
new_arr: ~                # 新增 ARR
expansion_arr: ~          # 扩张 ARR（现有客户增加）
churn_arr: ~              # 流失 ARR
```

### 1.3 B2B SaaS 必须采集的字段

```yaml
# 留存与扩张（最重要）
nrr: ~                    # 净收入留存率
gross_retention_rate: ~   # 毛留存率（不含扩张）

# 前瞻性指标
rpo: ~                    # 剩余履约义务（已签未确认）
rpo_growth_yoy: ~
current_rpo: ~            # 12个月内将确认的 RPO
crpo_growth_yoy: ~

# 客户质量指标
customers_1m_plus: ~      # $1M+ TTM 产品营收客户数
customers_1m_yoy: ~
customers_10m_plus: ~     # $10M+ 客户数（战略依赖）
total_customers: ~
net_new_customers: ~
enterprise_penetration: ~ # 如 Forbes G2000 / Fortune 500 覆盖率

# 财务质量
product_gross_margin_non_gaap: ~
operating_margin_non_gaap: ~
fcf_margin: ~             # 自由现金流利润率
cash_and_investments: ~

# AI / 新产品（如适用）
ai_accounts: ~
ai_revenue_run_rate: ~
new_product_adoption: ~   # 新功能采用率
```

### 1.4 消费制特殊注意事项

消费制收入的核心特点是**实时可见性低于订阅制**。管理层使用消费预测模型，但季度内客户消费行为变化可能导致超出或低于指引。

**关键解读规则**：
- 产品营收**超出指引** = 存量客户消费加速（护城河加深信号）
- 产品营收**低于指引** = 消费放缓，追问原因：宏观环境？竞品分流？新功能导致效率提升（同样工作更少消耗）？
- RPO 增速 **持续 > 产品营收增速** = 客户在签更长期合同，护城河加深的领先指标

---

## 四、MODULE 2：护城河信号判断（B2B SaaS 版本）

### 2.1 迁移成本护城河判断矩阵

| 指标组合 | 判断 | 颜色 |
|----------|------|------|
| NRR ≥ 120% + $1M+ 客户增速 > 25% | 强化中 | green |
| NRR 110–120% + $1M+ 客户稳定 | 稳定 | amber |
| NRR < 110% 连续两季 / $1M+ 客户增速放缓 | 受损 | red |
| RPO 增速 > 产品营收增速（持续） | 锁定加深（正向领先信号）| green |
| 产品营收增速加速 + NRR 上升 | 双重验证 | green（加权）|

### 2.2 平台生态护城河判断

**B2B 特有问题**：客户是在「深化」还是「分散化」使用？
- **深化**：每客户使用工作负载类别数增加，$1M+ 增速快于总客户增速
- **分散化**：客户把部分工作负载迁移到其他平台（AI 去 Databricks，查询留 Snowflake）

关注信号：管理层是否提及某类工作负载的使用增速明显快于其他类型？这是平台生态扩展的早期信号。

### 2.3 AI 对护城河的影响（通用框架）

| 场景 | 对现有护城河的影响 |
|------|-------------------|
| AI 需要企业数据 → 平台内训练 | 加深数据引力（正向）|
| AI 减少人工查询工作量 → 消费减少 | 短期消费下滑（但如果是因为效率提升，长期正向）|
| AI 原生竞争者更有吸引力 | 分流特定工作负载（威胁）|
| AI 功能货币化 = 新收入来源 | 扩展 NRR 基础（正向）|

---

## 五、MODULE 3：B2B 情绪与市场信号采集

**注意**：B2B 企业没有 App Store 评分，需要替代渠道。

### 3.1 企业用户评价平台

| 平台 | 采集内容 | URL 格式 | 频率 |
|------|----------|----------|------|
| G2 | 综合评分、功能评分、竞品比较 | `g2.com/products/[公司名]/reviews` | 每季度 |
| Gartner Peer Insights | 企业级评分、Gartner 象限 | `gartner.com/reviews/market/[类别]` | 每半年 |
| TrustRadius | 详细功能评价 | `trustradius.com/products/[公司名]/reviews` | 每半年 |

**Snowflake 特定链接**：
- G2: `https://www.g2.com/products/snowflake/reviews`
- Gartner: `https://www.gartner.com/reviews/market/cloud-database-management-systems/vendor/snowflake`

### 3.2 开发者社区信号

```
web_search: "snowflake vs databricks 2026 site:reddit.com"
web_search: "snowflake data cloud review stackoverflow"
web_search: "leaving snowflake switching databricks engineer"
```

**关键词监控**（以 Snowflake 为例）：
- 正面：`snowflake performance` / `snowflake data sharing` / `cortex ai great`
- 负面：`snowflake cost expensive` / `migrating from snowflake` / `databricks better`
- 警报：`snowflake outage` / `snowflake security breach` / `snowflake pricing increase`

### 3.3 分析师生态信号

```
web_search: "Gartner Magic Quadrant cloud data warehouse 2026"
web_search: "Forrester wave data platform 2026"
web_search: "IDC market share cloud data warehouse 2025"
```

对 B2B 企业，Gartner 魔力象限的位置变化（Leader → Visionary）是护城河受损的早期公开信号。

### 3.4 招聘信号（另类指标）

企业招聘 Snowflake 技能的岗位数量，是客户采用深度的代理指标：

```
web_search: "snowflake DBA engineer jobs 2026"
web_search: site:linkedin.com/jobs snowflake data engineer
```

若主要客户大规模招募 Databricks 工程师而非 Snowflake 工程师，是迁移意图的早期信号。

---

## 六、MODULE 4：HTML 文件更新规范

目标文件：`snowflake_moat_tracker.html`（或对应公司的 HTML 文件）

### 4.1 新增季度数据列

在 `.data-row` 表格中新增列，同时：
- 保持 `grid-template-columns` 与列数一致
- 更新右上角 KPI 卡片中的关键数字（NRR、RPO、$1M+、FCF）

### 4.2 护城河卡片更新规则

**只有以下情况触发卡片内容更新**：
- NRR 变化超过 2ppt
- $1M+ 客户增速明显加速或放缓（相较近 3 季度均值）
- AI 采用数据出现量级变化
- 竞争格局发生重大变化（主要竞争对手新产品发布、大客户公开迁移案例）
- 管理层在电话会议中明确表达战略转变

护城河★评级仅在上述条件满足时更新。

### 4.3 观察清单更新逻辑

每季度财报后：
1. 将上季度观察清单中的指标标记为「已验证」或「待观察」
2. 更新指引值（FY2027 Q1 → Q2 等）
3. 重新评估 P1/P2/P3 优先级（有时上季度 P3 在新季度变为 P1）
4. 如果某个指标连续两季度低于预期，升级为 P1 + 红色警报

---

## 七、企业级 B2B SaaS 关键指标阈值参考

以下阈值基于 2024–2026 年云数据平台行业基准：

| 指标 | 优秀 | 正常 | 警报 |
|------|------|------|------|
| NRR | ≥ 125% | 110–125% | < 110% |
| 毛留存率 | ≥ 95% | 90–95% | < 90% |
| 产品毛利率 | ≥ 75% | 70–75% | < 70% |
| FCF Margin | ≥ 25% | 15–25% | < 15% |
| RPO / TTM 营收比 | ≥ 2.0x | 1.5–2.0x | < 1.5x |
| $1M+ 客户占总营收 | ≥ 70% | 60–70% | < 60% |
| Non-GAAP 运营利润率 | ≥ 20% | 10–20% | < 5%（成熟期）|
| 产品营收增速 | ≥ 25% | 15–25% | < 15%（成熟期）|

**注意**：这些阈值会随公司成熟度变化——早期增长公司（ARR < $1B）和成熟公司（ARR > $3B）的基准不同。

---

## 八、Snowflake 专用数据源速查

### 财务数据（一级来源）

| 季度 | URL |
|------|-----|
| Q1 FY26 | https://www.sec.gov/Archives/edgar/data/0001640147/000164014725000094/fy2026q1earnings.htm |
| Q2 FY26 | https://www.sec.gov/Archives/edgar/data/0001640147/000164014725000177/fy2026q2earnings.htm |
| Q3 FY26 | https://www.sec.gov/Archives/edgar/data/0001640147/000164014725000207/fy2026q3earnings.htm |
| Q4 FY26 | https://www.sec.gov/Archives/edgar/data/0001640147/000162828026011631/fy2026q4earnings.htm |
| EDGAR 归档 | https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001640147&type=8-K&count=10 |
| IR 主页 | https://investors.snowflake.com |

### 情绪与市场数据

| 渠道 | URL | 频率 |
|------|-----|------|
| G2 评分 | https://www.g2.com/products/snowflake/reviews | 每季度 |
| Gartner Peer Insights | https://www.gartner.com/reviews/market/cloud-database-management-systems/vendor/snowflake | 每半年 |
| Reddit r/dataengineering | https://www.reddit.com/r/dataengineering/search/?q=snowflake&sort=top&t=month | 每月 |
| HN Snowflake 讨论 | https://hn.algolia.com/?q=snowflake&dateRange=pastMonth | 每月 |
| Gartner MQ | web_search: Gartner Magic Quadrant cloud data warehouse [年份] | 每半年 |

---

## 九、版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-03 | 初始版本，基于 Snowflake FY2026 分析建立通用 B2B SaaS 框架 |

---

## 附录：如何适配到其他公司

将此模板适配到其他 B2B SaaS 公司时，需要调整：

1. **财年日期**：Snowflake = 1 月 31 日；Salesforce = 1 月 31 日；ServiceNow = 12 月 31 日
2. **收入模式**：消费制 vs 订阅制 → 调整采集字段（ARR vs 产品营收）
3. **护城河权重**：不同行业主导护城河不同（ERP = 迁移成本极高；协作工具 = 网络效应）
4. **行业基准**：阈值因行业而异（安全软件 NRR 通常高于数据平台）
5. **竞争对手**：替换竞争格局 Tab 中的对手

**适配成功的标志**：五类护城河中，每条都能找到至少一个可以从财报中直接提取的可观测指标。

---

*本模板适用范围：数据平台 / 云基础设施 / 企业数据工具*
*最后更新：2026 年 3 月*
*实例文件：snowflake_moat_tracker.html*
*通用原则参考：DUOLINGO_AGENT_TEMPLATE.md（消费者产品对照版本）*
