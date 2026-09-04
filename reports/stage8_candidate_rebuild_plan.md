# 阶段8 候选池重建方案（A 起草，提请 B/Reviewer 复核裁定）

- 起草：Annotator A（lyf-1213）
- 日期：2026-09-04
- 状态：**草案待复核**（不代 B 校验、不代 Reviewer 裁定；合入 PR#28 提请审阅）
- 关联阻塞项：`候选草稿模板重复`（v1.0 母体缺陷）

---

## 0. 背景与定性

试标母数据 `data/interim/gold_candidates_*.jsonl` 为 v1.0 时代 AI 按模板批量生成的自产合成候选（`source=team_authored`，`review_status=candidate_only`），存在**规则归一化后大规模重复**，实测证据：

| 任务 | 候选总量 | 规则归一化唯一 input 数 | 重复率 |
| --- | --- | --- | --- |
| precise_forgetting | 40 | 4 | 90% |
| knowledge_retrieval | 60 | 5 | 92% |
| conflict_resolution | 40 | 5 | 88% |
| preference_extraction | 60 | 2 模板（counter 递增仅上下文计数不同） | ~97% |
| end_to_end_session | 15 | 1 模板（version 递增） | 93% |

> 说明：字符串哈希因 `context/version` 计数器差异显示"唯一"，但对 `user_message/query/turns` 归一化后语义全同。此类候选：
>
> 1. 导致试标 Kappa 虚高（同句 A/B 标一致太容易，≥0.70 为假达标）；
> 2. 无法验证标注流程对多样化数据的判别力；
> 3. 8.2 量产（目标 400~500 条）不能靠模板复制满足。

**定性**：这是红线「数据质量硬校验 + 全链路禁 mock」的违规残留。候选池是权威 Gold 的种子，**候选池质量 = 权威数据质量**，必须返工重建。

---

## 1. 重建原则（红线约束下）

| 原则 | 内容 |
| --- | --- |
| P1 真实数据接地 | 优先从已冻结真实数据集派生候选（t2ranking / longmemeval_cleaned / longmemeval_v2 / multiwoz_2_2），每条保留 `raw_id/source_file/source_version` 溯源 |
| P2 自建多样化 | 麒麟 OS 特有场景（公开数据无法覆盖）由 A 手写多样化真实场景，**禁止模板×计数器批量复制**；每条 `candidate_only`，绝不进封存 |
| P3 规则归一化去重 | 候选池与试标集必须通过**规则归一化去重校验**（对 query/user_message/turns/forget_instruction 归一化后 hash，重复组=0） |
| P4 模板族与分布随包交付 | 每次交付附模板族清单 + 分布统计（红线 5） |
| P5 来源可溯源 | public_derived 样本 evidence 必须含 raw_id；team_authored 样本标注"真实场景手写"并记录场景来源 |
| P6 禁 mock 边界 | 合成/自建候选仅作 candidate_only；封存集（sealed_test）必须来自麒麟 VM 真实回放，重建不触碰 |

---

## 2. 各任务候选来源与多样化规则

| 任务 | 主要来源 | 多样化规则 | 说明 |
| --- | --- | --- | --- |
| knowledge_retrieval | t2ranking 真实 query（已冻结 200 条 public_derived） | 按 query 原文直接使用 + knowledge_type 分布采样；缺失的 OS 场景（workflow/template/failure_experience）由 A 按真实 OS 操作撰写 | 200 条真实 query 已是多样化基底 |
| preference_extraction | longmemeval 真实会话中的用户偏好表达（single-session-preference / 多轮偏好句）+ multiwoz 真实用户语句 + A 手写 OS 场景 | 每条取**真实原话**为 input，禁止改写模板；preference_key 按 KMA 受控前缀标注 | 公开数据为英文，需 A 转写为真实中文场景或双语并存 |
| conflict_resolution | longmemeval knowledge-update / temporal-reasoning 真实版本冲突 + A 手写 OS 冲突场景 | 冲突双方（old/new）必须来自真实事件链或真实场景，禁止占位"旧记忆/新指令" | 版本链可消解的走 superseded/version，不进 conflict |
| precise_forgetting | longmemeval 真实记忆条目（会话中的事实/偏好/事件）+ A 手写 OS 记忆场景 | forget_instruction 指向真实记忆条目，target/must_keep 可验证 | 必须能回答"删对+不误删" |
| end_to_end_session | longmemeval_v2 真实 question（procedure/dynamic-environment）+ longmemeval 会话链 | 事件序列取自真实任务链，禁止"第 N 次发布检查"式复制 | 封存集依赖麒麟 VM 回放（阶段 10）；试标/候选可先 candidate_only |
| tool_result | stabletoolbench 指令 + 麒麟 VM 回放（依赖阶段 10） | 本轮不产试标候选；登记为阶段 10 依赖项 | 红线 4：封存集必须真实回放 |

---

## 3. 产出物与验收

### 3.1 候选池（A 产出）
- 位置：`data/interim/gold_candidates_*_v2.jsonl`（新文件，不覆盖 v1 母体，保留可追溯）
- Schema：沿用统一 Schema（sample_id 前缀 task 族），`source` 标注 public_derived/team_authored，`raw_id/source_file` 溯源
- 规模：首轮重建每类任务 ≥12 条（含试标所需 8 条 + 缓冲），供重抽试标集

### 3.2 规则归一化去重校验（A 产出脚本 + B 复核）
- 脚本：`scripts/audit/stage8_semantic_dedup.py`
- 规则：对 `query`/`user_message`/`turns`(join)/`forget_instruction` 归一化（去空白/标点/计数器）后 hash；重复组必须为 0
- 验收：候选池与试标集均 exit 0；B 复核哈希口径

### 3.3 试标集重抽（A 产出）
- 位置：`data/interim/stage8_trial_set_v3.jsonl`
- 规模：40 条（5 任务 × 8），从重建后候选池抽样，先跑去重校验再定稿
- 特性：40 条规则归一化唯一；含真实数据派生 + OS 自建混合

### 3.4 阻断项登记（A 产出）
- 本方案即阻塞项登记载体；提请 Reviewer 在 PR#28 标记处置

---

## 4. 分工与 Gate

| 步骤 | A（lyf-1213） | B（DGXD01） | Reviewer（gaoyizhe） |
| --- | --- | --- | --- |
| 1 重建方案 | 起草本方案 ✅ | 复核去重口径/来源占比 | 裁定方向 + 标记阻断项处置 |
| 2 候选池重建 | 生成多样化候选（§2 规则） | 校验 schema/枚举/溯源 | — |
| 3 规则归一化去重 | 跑 dedup + 提交证据 | 复核 hash 口径 + exit 0 | — |
| 4 重抽试标集 | 抽样 40 + 去重定稿 | 结构校验 | 放行试标 |
| 5 A/B 试标 | 独立标注 labels_A | 独立标注 labels_B | 分歧裁决 |
| 6 Kappa | — | stage8_kappa --format kma（registry 单源）≥0.70 | 判定达标 |
| 7 量产 | 8.2 按此多样化方法批量生成 | 结构化/enum 校验 | 放行 |

**Gate 纪律**：本方案获 Reviewer 裁定后，A 才进入候选池重建与试标重抽；未裁定不量产、不重抽正式试标。

---

## 5. 待裁定清单（提请 Reviewer）

1. **当前 40 条试标集（v2）**：废弃（建议）——语义重复样本无法检验标注流程，也不具备权威数据价值；
2. **来源占比**：公开数据派生 vs 自建 OS 场景的合理比例（建议 ≥50% 公开数据接地，OS 特有场景自建补足）；
3. **语言策略**：公开数据（longmemeval/multiwoz）为英文，是否保留英文原样 + preference 双语标注，还是统一转写中文（转写存在语义漂移风险，建议保留原文 + evidence 溯源）；
4. **tool_result**：本轮不产试标候选，登记阶段 10 依赖；
5. **retrieval 版本引用**：KB/D9 就绪前，v2 试标检索字段按标注手册 §4 风险注执行（NOT production 显式标记）。

---

## 6. 结论

候选池是权威 Gold 的种子。本方案将 v1.0 模板母体返工为「真实数据接地 + 自建多样化 + 规则归一化去重 + 可溯源」的候选池，重抽试标集后 A/B 独立标注，得到真实 Kappa。全程遵守红线（禁 mock 只作 candidate_only、先标后产、Gate 纪律）。