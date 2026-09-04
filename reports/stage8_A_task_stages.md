# 阶段8 A 轨任务阶段表（Annotator A = lyf-1213）— 2026-09-04

- 依据：`reports/stage8_A_B_cooperation_steps.md`（B↔A 配合步骤表）、`reports/stage8_v2_followup_plan.md`、`worklog/20260903_KMA_FROZEN_pending_items.md`
- 分工：A 轨动作归 A（lyf-1213）执行；B 只做校验/审计/脚本/标注 B 份额。
- 当前闸口：**P1 全部受 #7 KMA→FROZEN 约束**（主仓库仍 CANDIDATE_FOR_FREEZE，2026-09-04）。FROZEN 前 A 不做破坏性重转/正式试标。

## 一、已闭环（A 已完成）

| # | 任务 | 产物 | 状态 |
| --- | --- | --- | --- |
| 0 | 六类 KMA canonical gold 口径草案 | reports/stage8_kma_gold_annotation_draft_A.md | ✅ |
| 0 | 标注手册 v2 草案 + P1/P2/minor 修订 | data/gold/annotation_guideline_v2.md | ✅ |
| 0 | Reviewer 裁定 #1-#4 落点进手册 | 手册 v2 §3/§4/§5/§6/§11 | ✅（d179ce9） |
| 0 | confidence/app-task 裁定支撑样例 | worklog/20260903_KMA_confidence_scope_samples_A.md | ✅ |
| 0 | FROZEN #1/#3 定稿建议 | worklog/20260904_KMA_FROZEN_1_3_A_recommendation.md | ✅ |
| 0 | FROZEN #6 D9 补档 | evidence/source/kma_unified_data_format_FREEZE_V1/D9…jsonl | ✅ |
| 0 | High-1 权威版入库 + provenance 修正 | KMA…MAIN_CANDIDATE.md + source_provenance.md | ✅ |
| 0 | 一致字段集单一来源（与 B field_mapping 独立） | registry/kappa_agreement_fields.json | ✅ |

## 二、当前可做（P0，不破坏，无 FROZEN 依赖）

| # | 任务 | A 动作 | 依赖 | 状态 |
| --- | --- | --- | --- | --- |
| 1 | **复核权威版差异**（配合步骤 #1） | 对比主仓库权威版（CANDIDATE）与本仓库编码，列出字段/枚举差异清单，供 P1-1 收口 | 权威版已入库 | ✅ 已完成（见下） |
| 2 | **复核 B labels 骨架设计 vs 手册 v2 一致性** | 交叉核对 reports/stage8_v2_labels_skeleton_design.md 与手册 v2 字段/枚举是否一致 | B 骨架设计已出 | ✅ 已完成（见下） |
| 3 | **复核 B 就绪工具收口清单** | 审 reports/stage8_P1_readiness_20260904.md 是否覆盖 P1-1 收口点 | B 已备 | ✅ 已完成（见下） |

### 复核结论（2026-09-04）

**任务1 权威版差异复核**：
- R-2（expression_type=explicit/implicit）→ schema.json 编码一致 ✅
- R-3（memory_status 6 值，生命周期唯一真值）→ 一致 ✅
- R-4（processing_status 正交；source_business_status 8 值业务结果）→ 一致 ✅
- R-5（canonical 用 `sensitivity`，sensitivity_level 仅注解层 alias）→ **⚠ 缺口**：本仓库 gold_enum_alignment 未含 sensitivity；手册 v2 未提。属 Tool Result/事件层字段（D9 检索集无，检索层不需）。**P1-1 收口时需确认**：评测 gold 是否需补 sensitivity（R-5），或属评测层不纳入（登记待裁定）。
- 其余枚举（preference_scope/conflict_type/knowledge_type/resolution_status）权威版不逐项列出 → 已由 B #9 核对 D3(L2) FROZEN_BUSINESS_SEMANTIC ✅。
- R-1（captured_at vs collected_at）→ 评测层时间用 created_at/updated_at（评测字段），不冲突。

**任务2 B labels 骨架一致性**：
- B 骨架设计（reports/stage8_v2_labels_skeleton_design.md）字段与手册 v2 §3-§8 一致：preference 含 expression_type/preference_scope/preference_key/confidence_score/should_persist/is_temporary/memory_status/version/evidence_event_ids ✅；Kappa 引用 registry 单源 ✅。
- 骨架示例（P1-4 readiness 第 3 行）与手册 v2 §3 字段一致 ✅。
- ⚠ 骨架 retrieval 部分字段名"随 D9 裁定"（#7 留位）——与 B P1-1 清单第 3 项（retrieval_ref 补 memory_id+version_id）一致，FROZEN 后落定。

**任务3 B 就绪清单**：
- P1-1 清单 5 项覆盖 schema/enum/retrieval_ref/物理命名/校验 ✅；
- P1-2/P1-3/P1-4/P1-6 就绪 ✅；
- 无 A 侧遗漏项；A 在 P1 各步动作与配合步骤表一致。

### P0 复核后新增 A 待办（P1 前登记）
- **R-5 sensitivity 收口确认**：评测 gold 是否补 sensitivity 字段（或标评测层不纳入）→ 交 Reviewer 裁定（P1-1 前）。

## 三、待 FROZEN（P1，闸口 #7 后执行）

| # | 步骤 | A 动作 | 验收 | 状态 |
| --- | --- | --- | --- | --- |
| 2 | P1-1 Schema 收口 | A 更新 schema/enum_dictionary/检索 ref | schema_drift_check exit 0 | ⬜ 待 FROZEN |
| 3 | P1-2 手册 v2 定稿 | A 去草案措辞定稿（§3/4/5/6/9/11） | A/B 双核 + Reviewer 批准 | ⬜ 待 FROZEN |
| 4 | P1-3 全量重转 | A 跑 KMA 化转换（raw→processed） | conversion_report + 校验 exit 0 | ⬜ 待 FROZEN |
| 5 | P1-4 labels v2 骨架 | A 确认字段口径 | 骨架 + label_check_v2 | ⬜ 待 FROZEN |
| 6 | P1-5 试标 v2 | A 独立标注 labels_A_trial_v2 | label_check_v2 通过 | ⬜ 待 FROZEN+真人 |
| 7 | P1-6 Kappa | 未达标配合修订规则 | stage8_kappa --format kma ≥0.70 | ⬜ 待 FROZEN |
| 8 | 8.2 候选草稿 | A 批量生成候选草稿 | 校验 exit 0 | ⬜ |
| 9 | 8.3 双标/裁决 | A 全量独立标注 | gold_draft/disagreement | ⬜ |
| 10 | Gate 8 收口 | 配合澄清 | Reviewer 批准 | ⬜ |

## 四、阻塞链（当前）
- 主仓库 KMA 仍 CANDIDATE_FOR_FREEZE（#7 未 FROZEN）→ P1-1~P1-7 全部待触发。
- 因此 A 当前只有"复核权威版差异/骨架一致性/就绪清单"三项 P0 可做，其余待 FROZEN 闸口放行。
